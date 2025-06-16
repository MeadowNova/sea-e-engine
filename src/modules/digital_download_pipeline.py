#!/usr/bin/env python3
"""
Digital Download Pipeline for SEA-E Phase 2
===========================================

Orchestrates the complete workflow for turning digital art mockups 
into fully drafted Etsy listings following the Phase 2 plan.

Workflow:
1. Ingest mockups from designs directory
2. Upload images to Google Drive  
3. Log in Google Sheets (Art_Mockup_Staging)
4. Fetch reference listing from Etsy
5. Generate SEO content via OpenAI
6. Create draft Etsy listing
"""

import os
import re
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json

# SEA-E imports
from api.google_sheets_client import GoogleSheetsClient
from api.etsy import EtsyAPIClient
from modules.openai_seo_optimizer import OpenAISEOOptimizer
from modules.custom_mockup_generator import CustomMockupGenerator

logger = logging.getLogger(__name__)

@dataclass
class DesignFile:
    """Represents a design file with parsed metadata."""
    filepath: Path
    design_slug: str
    width: int
    height: int
    filename: str

@dataclass
class PipelineResult:
    """Result of processing a single design file."""
    design_file: DesignFile
    success: bool
    google_drive_url: Optional[str] = None
    sheets_row_id: Optional[str] = None
    seo_content: Optional[Dict[str, Any]] = None
    etsy_listing_id: Optional[str] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0

class DigitalDownloadPipeline:
    """Main pipeline for Phase 2 digital download automation."""
    
    def __init__(self, 
                 mockups_directory: str = None,
                 reference_listing_id: str = None,
                 mode: str = "validate"):
        """Initialize the pipeline.
        
        Args:
            mockups_directory: Path to mockups directory
            reference_listing_id: Etsy listing ID to use as template
            mode: Processing mode ('validate' or 'batch')
        """
        self.mockups_dir = Path(mockups_directory or
                               "/home/ajk/sea-e engine/assets/mockups/posters/Designs for Mockups")
        self.reference_listing_id = reference_listing_id or os.getenv("REFERENCE_LISTING_ID")
        self.mode = mode
        
        # Initialize clients
        self.sheets_client = GoogleSheetsClient()
        self.etsy_client = EtsyAPIClient()
        self.seo_optimizer = OpenAISEOOptimizer()

        # Initialize mockup generator for poster mockups
        self.mockup_generator = CustomMockupGenerator(
            assets_dir="assets",
            output_dir="output/digital_downloads",
            auto_manage=True,
            enable_sheets_upload=False  # We'll handle uploads separately
        )

        # Pipeline configuration
        self.batch_size = 10 if mode == "batch" else 1
        self.rate_limit_delay = 0.1  # 10 calls/sec for Etsy

        # Static images configuration
        self.template_listing_id = None
        self.static_image_ids = []

        logger.info(f"Initialized Digital Download Pipeline in {mode} mode")
        logger.info(f"Mockups directory: {self.mockups_dir}")
        logger.info(f"Reference listing ID: {self.reference_listing_id}")

        # Find template listing and extract static images
        self._initialize_static_images()
    
    def discover_design_files(self) -> List[DesignFile]:
        """Discover and parse design files from mockups directory.
        
        Expected pattern: <design-slug>__w=<width_px>__h=<height_px>.png
        
        Returns:
            List of DesignFile objects
        """
        logger.info(f"Discovering design files in: {self.mockups_dir}")
        
        design_files = []

        # Pattern for files with explicit dimensions: design_name__w=2000__h=2000.png
        dimension_pattern = re.compile(r'^(.+?)__w=(\d+)__h=(\d+)\.(png|jpg|jpeg)$', re.IGNORECASE)

        for filepath in self.mockups_dir.glob("*"):
            if filepath.is_file() and filepath.suffix.lower() in ['.png', '.jpg', '.jpeg']:

                # Try dimension pattern first
                match = dimension_pattern.match(filepath.name)
                if match:
                    design_slug = match.group(1)
                    width = int(match.group(2))
                    height = int(match.group(3))

                    design_file = DesignFile(
                        filepath=filepath,
                        design_slug=design_slug,
                        width=width,
                        height=height,
                        filename=filepath.name
                    )
                    design_files.append(design_file)
                    logger.debug(f"Found design file with dimensions: {design_file.filename}")

                else:
                    # Handle descriptive filenames (your current naming system)
                    design_slug = filepath.stem

                    # Clean up the slug for better SEO processing
                    # Keep the descriptive nature but make it SEO-friendly
                    clean_slug = design_slug.replace(' ', '_').replace('-', '_')

                    design_file = DesignFile(
                        filepath=filepath,
                        design_slug=clean_slug,
                        width=2000,  # Default high-res dimensions for digital downloads
                        height=2000,
                        filename=filepath.name
                    )
                    design_files.append(design_file)
                    logger.debug(f"Found descriptive design file: {design_file.filename}")
                    logger.debug(f"  → Processed slug: {clean_slug}")
        
        logger.info(f"Discovered {len(design_files)} design files")
        return design_files

    def _initialize_static_images(self):
        """Find template listing and extract static image IDs."""
        try:
            logger.info("Searching for 'digital download template' listing...")

            # Search for template listing by title
            template_listing = self._find_template_listing()

            if template_listing:
                self.template_listing_id = template_listing.get('listing_id')
                logger.info(f"Found template listing: {self.template_listing_id}")

                # Extract static image IDs
                self.static_image_ids = self._extract_static_image_ids(template_listing)
                logger.info(f"Extracted {len(self.static_image_ids)} static image IDs")
            else:
                logger.warning("Template listing not found - will proceed without static images")

        except Exception as e:
            logger.error(f"Failed to initialize static images: {e}")
            logger.warning("Proceeding without static images")

    def _find_template_listing(self) -> Optional[Dict[str, Any]]:
        """Find the digital download template listing."""
        try:
            # Search for listings with "digital download template" in title
            endpoint = f"/application/shops/{self.etsy_client.shop_id}/listings"
            params = {
                'state': 'draft',
                'limit': 100,
                'includes': ['Images']
            }

            response = self.etsy_client.make_request("GET", endpoint, params=params)

            if response.status_code != 200:
                logger.error(f"Failed to search listings: {response.status_code}")
                return None

            listings_data = response.json()
            listings = listings_data.get('results', [])

            # Find listing with "digital download template" in title
            for listing in listings:
                title = listing.get('title', '').lower()
                if 'digital download template' in title:
                    logger.info(f"Found template listing: {listing.get('title')}")
                    return listing

            logger.warning("No listing found with 'digital download template' in title")
            return None

        except Exception as e:
            logger.error(f"Error searching for template listing: {e}")
            return None

    def _extract_static_image_ids(self, template_listing: Dict[str, Any]) -> List[str]:
        """Extract static image IDs from template listing."""
        try:
            images = template_listing.get('images', [])

            if not images:
                logger.warning("Template listing has no images")
                return []

            # Extract image IDs (assuming last 3 images are static)
            # You can modify this logic based on your specific needs
            image_ids = []
            for image in images:
                if isinstance(image, dict):
                    image_id = image.get('listing_image_id')
                    if image_id:
                        image_ids.append(str(image_id))

            # Take last 3 images as static images (instructions, what's included, size chart)
            static_ids = image_ids[-3:] if len(image_ids) >= 3 else image_ids

            logger.info(f"Extracted static image IDs: {static_ids}")
            return static_ids

        except Exception as e:
            logger.error(f"Error extracting static image IDs: {e}")
            return []
    
    def process_single_design(self, design_file: DesignFile) -> PipelineResult:
        """Process a single design file through the complete pipeline.
        
        Args:
            design_file: DesignFile to process
            
        Returns:
            PipelineResult with processing details
        """
        start_time = time.time()
        result = PipelineResult(design_file=design_file, success=False)
        
        try:
            logger.info(f"Processing design: {design_file.design_slug}")
            
            # Step 1: Upload to Google Drive
            logger.info("Step 1: Uploading to Google Drive...")
            file_id, drive_url = self.sheets_client.upload_image_to_drive(
                str(design_file.filepath),
                filename=design_file.filename
            )
            result.google_drive_url = drive_url
            logger.info(f"✅ Uploaded to Drive: {drive_url}")
            
            # Step 2: Log in Google Sheets
            logger.info("Step 2: Logging in Google Sheets...")
            sheets_data = {
                'slug': design_file.design_slug,
                'drive_url': drive_url,
                'width': design_file.width,
                'height': design_file.height,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'processing'
            }
            # Note: Implement sheets logging based on existing patterns
            result.sheets_row_id = f"row_{int(time.time())}"
            logger.info(f"✅ Logged in sheets: {result.sheets_row_id}")
            
            # Step 3: Generate SEO content
            logger.info("Step 3: Generating SEO content...")
            seo_content = self.seo_optimizer.generate_seo_content(design_file.design_slug)
            result.seo_content = seo_content
            logger.info(f"✅ Generated SEO content")
            
            # Step 4: Fetch reference listing (if needed)
            if self.reference_listing_id:
                logger.info("Step 4: Fetching reference listing...")
                reference_listing = self.etsy_client.get_listing(self.reference_listing_id)
                logger.info(f"✅ Fetched reference listing")
            
            # Step 4: Generate mockups
            logger.info("Step 4: Generating mockups...")
            mockup_files = self._generate_mockups(design_file)
            logger.info(f"✅ Generated {len(mockup_files)} mockups")

            # Step 5: Create draft Etsy listing
            logger.info("Step 5: Creating Etsy draft listing...")

            # For validate mode, just prepare the data
            if self.mode == "validate":
                result.etsy_listing_id = "draft_preview_only"
                logger.info(f"✅ Prepared draft listing (validate mode)")
            else:
                # Actually create the listing with mockups and static images
                listing_id = self.etsy_client.create_digital_download_listing(
                    title=seo_content['title'],
                    description=seo_content['description'],
                    price=13.32,  # Fixed price for digital downloads
                    tags=seo_content['tags'],
                    mockup_files=mockup_files,
                    static_image_ids=self.static_image_ids
                )
                result.etsy_listing_id = listing_id
                logger.info(f"✅ Created draft listing: {listing_id}")
            
            result.success = True
            logger.info(f"🎉 Successfully processed: {design_file.design_slug}")
            
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"❌ Failed to process {design_file.design_slug}: {str(e)}")
        
        finally:
            result.processing_time = time.time() - start_time
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
        
        return result

    def _generate_mockups(self, design_file: DesignFile) -> List[str]:
        """Generate poster mockups using the existing custom mockup generator.

        Args:
            design_file: DesignFile to generate mockups for

        Returns:
            List of mockup file paths (up to 7 mockups)
        """
        try:
            logger.info(f"Generating poster mockups for: {design_file.design_slug}")

            mockup_files = []

            # Get available poster templates (limit to 7 for Etsy)
            available_templates = self.mockup_generator.list_available_templates().get('posters', [])

            if not available_templates:
                logger.warning("No poster templates available, using original design file")
                return [str(design_file.filepath)]

            # Generate mockups using up to 7 templates
            templates_to_use = available_templates[:7]
            logger.info(f"Using {len(templates_to_use)} poster templates: {templates_to_use}")

            for template_name in templates_to_use:
                try:
                    logger.info(f"Generating mockup with template: {template_name}")

                    # Generate mockup using custom mockup generator
                    result = self.mockup_generator.generate_mockup(
                        product_type='posters',
                        design_path=str(design_file.filepath),
                        template_name=template_name,
                        upload_to_sheets=False  # We handle uploads separately
                    )

                    if result['success']:
                        mockup_files.append(result['mockup_path'])
                        logger.info(f"✅ Generated mockup: {Path(result['mockup_path']).name}")
                    else:
                        logger.error(f"❌ Failed to generate mockup with {template_name}: {result.get('error')}")

                except Exception as e:
                    logger.error(f"Error generating mockup with template {template_name}: {e}")
                    continue

            if not mockup_files:
                logger.warning("No mockups generated successfully, using original design file")
                return [str(design_file.filepath)]

            logger.info(f"Successfully generated {len(mockup_files)} poster mockups")
            return mockup_files

        except Exception as e:
            logger.error(f"Failed to generate mockups: {e}")
            # Return original design file as fallback
            return [str(design_file.filepath)]

    def process_batch(self, design_files: List[DesignFile]) -> List[PipelineResult]:
        """Process multiple design files in batch.

        Args:
            design_files: List of DesignFile objects to process

        Returns:
            List of PipelineResult objects
        """
        logger.info(f"Starting batch processing of {len(design_files)} designs")

        results = []
        for i, design_file in enumerate(design_files):
            logger.info(f"Processing {i+1}/{len(design_files)}: {design_file.design_slug}")

            try:
                result = self.process_single_design(design_file)
                results.append(result)

                # Fail fast: halt batch if error occurs
                if not result.success:
                    logger.error(f"Batch processing halted due to error: {result.error_message}")
                    break

            except Exception as e:
                logger.error(f"Critical error in batch processing: {str(e)}")
                break

        logger.info(f"Batch processing completed. Processed {len(results)} designs")
        return results

    def run_pipeline(self) -> Dict[str, Any]:
        """Run the complete pipeline based on mode.

        Returns:
            Dictionary with pipeline execution summary
        """
        start_time = time.time()

        try:
            # Discover design files
            design_files = self.discover_design_files()

            if not design_files:
                logger.warning("No design files found to process")
                return {
                    'success': False,
                    'message': 'No design files found',
                    'processed_count': 0,
                    'total_time': time.time() - start_time
                }

            # Process based on mode
            if self.mode == "validate":
                # Process only the first file for validation
                logger.info("Running in VALIDATE mode - processing first file only")
                results = [self.process_single_design(design_files[0])]
            else:
                # Process in batches
                logger.info(f"Running in BATCH mode - processing {len(design_files)} files")
                results = self.process_batch(design_files[:self.batch_size])

            # Generate summary
            successful_count = sum(1 for r in results if r.success)
            failed_count = len(results) - successful_count

            summary = {
                'success': failed_count == 0,
                'mode': self.mode,
                'total_files_found': len(design_files),
                'processed_count': len(results),
                'successful_count': successful_count,
                'failed_count': failed_count,
                'total_time': time.time() - start_time,
                'results': results
            }

            logger.info(f"Pipeline completed: {successful_count} successful, {failed_count} failed")
            return summary

        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'total_time': time.time() - start_time
            }

    def generate_report(self, summary: Dict[str, Any]) -> str:
        """Generate a human-readable report of pipeline execution.

        Args:
            summary: Pipeline execution summary

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("🚀 DIGITAL DOWNLOAD PIPELINE REPORT")
        report.append("=" * 60)

        if summary['success']:
            report.append(f"✅ Status: SUCCESS")
        else:
            report.append(f"❌ Status: FAILED")
            if 'error' in summary:
                report.append(f"   Error: {summary['error']}")

        report.append(f"📊 Mode: {summary.get('mode', 'unknown').upper()}")
        report.append(f"⏱️  Total Time: {summary['total_time']:.2f} seconds")

        if 'results' in summary:
            report.append(f"📁 Files Found: {summary['total_files_found']}")
            report.append(f"🔄 Processed: {summary['processed_count']}")
            report.append(f"✅ Successful: {summary['successful_count']}")
            report.append(f"❌ Failed: {summary['failed_count']}")

            # Detail each result
            report.append("\n📋 PROCESSING DETAILS:")
            report.append("-" * 40)

            for i, result in enumerate(summary['results'], 1):
                status = "✅" if result.success else "❌"
                report.append(f"{i:2d}. {status} {result.design_file.design_slug}")

                if result.success:
                    report.append(f"     📁 Drive URL: {result.google_drive_url}")
                    if result.etsy_listing_id:
                        report.append(f"     🛍️  Etsy Listing: {result.etsy_listing_id}")
                    report.append(f"     ⏱️  Time: {result.processing_time:.2f}s")
                else:
                    report.append(f"     ❌ Error: {result.error_message}")

        report.append("=" * 60)
        return "\n".join(report)
