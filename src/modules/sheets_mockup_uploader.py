#!/usr/bin/env python3
"""
Google Sheets Mockup Uploader for SEA-E Engine
==============================================

Orchestrates the upload of generated mockups to Google Sheets and 
integration with Airtable for the complete SEA-E workflow.

Features:
- Batch upload of mockups to Google Sheets
- Integration with existing mockup generators
- Airtable synchronization for shareable URLs
- Progress tracking and error handling
- Configurable organization and naming
"""

import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from api.google_sheets_client import GoogleSheetsClient, MockupUploadResult
from api.airtable_client import AirtableClient

# Set up logging
logger = logging.getLogger("sheets_mockup_uploader")


@dataclass
class MockupUploadJob:
    """Represents a mockup upload job."""
    mockup_path: str
    product_name: str
    variation_info: Dict[str, str]
    airtable_record_id: Optional[str] = None
    priority: int = 1


@dataclass
class BatchUploadResult:
    """Result of a batch upload operation."""
    total_jobs: int
    successful_uploads: int
    failed_uploads: int
    upload_results: List[MockupUploadResult]
    errors: List[str]
    execution_time: float


class SheetsUploadError(Exception):
    """Custom exception for sheets upload errors."""
    pass


class SheetsMockupUploader:
    """
    Orchestrates mockup uploads to Google Sheets with Airtable integration.
    """
    
    def __init__(self, config_file: str = "config/google_sheets_config.json",
                 credentials_path: str = None, airtable_client: AirtableClient = None):
        """
        Initialize the sheets mockup uploader.
        
        Args:
            config_file: Path to configuration file
            credentials_path: Path to Google service account credentials
            airtable_client: Existing Airtable client instance
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
        # Initialize Google Sheets client
        self.sheets_client = GoogleSheetsClient(credentials_path)
        
        # Initialize or use existing Airtable client
        self.airtable_client = airtable_client or AirtableClient()
        
        # Upload tracking
        self.upload_queue: List[MockupUploadJob] = []
        self.completed_uploads: List[MockupUploadResult] = []
        
        logger.info("SheetsMockupUploader initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Config file not found: {self.config_file}, using defaults")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "spreadsheet_settings": {
                "naming_convention": "SEA-E Mockups - {product_name}",
                "auto_organize": True
            },
            "upload_settings": {
                "max_file_size_mb": 10,
                "supported_formats": [".png", ".jpg", ".jpeg"]
            },
            "batch_settings": {
                "max_concurrent_uploads": 5,
                "retry_attempts": 3
            },
            "integration_settings": {
                "update_airtable": True,
                "airtable_url_field": "google_sheets_url"
            }
        }
    
    def add_upload_job(self, mockup_path: str, product_name: str, 
                      variation_info: Dict[str, str] = None,
                      airtable_record_id: str = None, priority: int = 1) -> bool:
        """
        Add a mockup upload job to the queue.
        
        Args:
            mockup_path: Path to the mockup file
            product_name: Name of the product
            variation_info: Variation details (color, size, etc.)
            airtable_record_id: Associated Airtable record ID
            priority: Upload priority (1=highest, 5=lowest)
            
        Returns:
            bool: True if job added successfully
        """
        try:
            # Validate file exists and format
            mockup_path_obj = Path(mockup_path)
            if not mockup_path_obj.exists():
                raise FileNotFoundError(f"Mockup file not found: {mockup_path}")
            
            if mockup_path_obj.suffix.lower() not in self.config["upload_settings"]["supported_formats"]:
                raise ValueError(f"Unsupported file format: {mockup_path_obj.suffix}")
            
            # Check file size
            file_size_mb = mockup_path_obj.stat().st_size / (1024 * 1024)
            max_size = self.config["upload_settings"]["max_file_size_mb"]
            if file_size_mb > max_size:
                raise ValueError(f"File too large: {file_size_mb:.1f}MB > {max_size}MB")
            
            # Create upload job
            job = MockupUploadJob(
                mockup_path=str(mockup_path),
                product_name=product_name,
                variation_info=variation_info or {},
                airtable_record_id=airtable_record_id,
                priority=priority
            )
            
            self.upload_queue.append(job)
            logger.info(f"Added upload job for: {mockup_path_obj.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add upload job: {e}")
            return False
    
    def upload_single_mockup(self, job: MockupUploadJob) -> MockupUploadResult:
        """
        Upload a single mockup to Google Sheets.
        
        Args:
            job: Upload job details
            
        Returns:
            MockupUploadResult: Upload result
        """
        try:
            logger.info(f"Uploading mockup: {Path(job.mockup_path).name}")
            
            # Upload to Google Sheets
            result = self.sheets_client.upload_mockup_to_sheets(
                image_path=job.mockup_path,
                product_name=job.product_name,
                variation_info=job.variation_info
            )
            
            # Update Airtable if successful and enabled
            if (result.success and 
                self.config["integration_settings"]["update_airtable"] and 
                job.airtable_record_id):
                
                self._update_airtable_record(job.airtable_record_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload mockup {job.mockup_path}: {e}")
            return MockupUploadResult(
                success=False,
                error_message=str(e)
            )
    
    def _update_airtable_record(self, record_id: str, upload_result: MockupUploadResult):
        """
        Update Airtable record with Google Sheets URL.
        
        Args:
            record_id: Airtable record ID
            upload_result: Upload result with URL
        """
        try:
            url_field = self.config["integration_settings"]["airtable_url_field"]
            status_field = self.config["integration_settings"].get("airtable_status_field")
            date_field = self.config["integration_settings"].get("airtable_date_field")
            
            update_fields = {
                url_field: upload_result.shareable_url
            }
            
            if status_field:
                update_fields[status_field] = "Uploaded" if upload_result.success else "Failed"
            
            if date_field:
                from datetime import datetime
                update_fields[date_field] = datetime.now().isoformat()
            
            self.airtable_client.update_record("mockups", record_id, update_fields)
            logger.info(f"Updated Airtable record {record_id} with Google Sheets URL")
            
        except Exception as e:
            logger.error(f"Failed to update Airtable record {record_id}: {e}")
    
    def process_upload_queue(self, max_workers: int = None) -> BatchUploadResult:
        """
        Process all jobs in the upload queue with concurrent execution.
        
        Args:
            max_workers: Maximum number of concurrent uploads
            
        Returns:
            BatchUploadResult: Batch upload results
        """
        import time
        start_time = time.time()
        
        if not self.upload_queue:
            logger.warning("No upload jobs in queue")
            return BatchUploadResult(0, 0, 0, [], [], 0.0)
        
        # Sort queue by priority
        self.upload_queue.sort(key=lambda x: x.priority)
        
        # Determine max workers
        if max_workers is None:
            max_workers = self.config["batch_settings"]["max_concurrent_uploads"]
        
        logger.info(f"Processing {len(self.upload_queue)} upload jobs with {max_workers} workers")
        
        upload_results = []
        errors = []
        
        # Process uploads concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_job = {
                executor.submit(self.upload_single_mockup, job): job 
                for job in self.upload_queue
            }
            
            # Collect results
            for future in as_completed(future_to_job):
                job = future_to_job[future]
                try:
                    result = future.result()
                    upload_results.append(result)
                    
                    if result.success:
                        logger.info(f"✅ Successfully uploaded: {Path(job.mockup_path).name}")
                    else:
                        logger.error(f"❌ Failed to upload: {Path(job.mockup_path).name}")
                        errors.append(f"{job.mockup_path}: {result.error_message}")
                        
                except Exception as e:
                    error_msg = f"{job.mockup_path}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"❌ Upload job failed: {error_msg}")
                    
                    upload_results.append(MockupUploadResult(
                        success=False,
                        error_message=str(e)
                    ))
        
        # Calculate results
        successful_uploads = sum(1 for r in upload_results if r.success)
        failed_uploads = len(upload_results) - successful_uploads
        execution_time = time.time() - start_time
        
        # Clear the queue
        self.upload_queue.clear()
        
        # Store completed uploads
        self.completed_uploads.extend(upload_results)
        
        logger.info(f"Batch upload completed: {successful_uploads}/{len(upload_results)} successful in {execution_time:.1f}s")
        
        return BatchUploadResult(
            total_jobs=len(upload_results),
            successful_uploads=successful_uploads,
            failed_uploads=failed_uploads,
            upload_results=upload_results,
            errors=errors,
            execution_time=execution_time
        )
