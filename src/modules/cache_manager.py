"""
Cache Manager for SEA-E Pipeline
Manages mockup file caching and cleanup to prevent storage bloat.
"""

import os
import shutil
import time
from pathlib import Path
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching and cleanup of pipeline-generated files."""
    
    def __init__(self, 
                 cache_dirs: List[str] = None,
                 retention_count: int = 5,
                 max_cache_size_mb: int = 1000,
                 cleanup_on_success: bool = True):
        """Initialize Cache Manager.
        
        Args:
            cache_dirs: List of directories to manage
            retention_count: Number of recent designs to keep for debugging
            max_cache_size_mb: Maximum cache size in MB before warning
            cleanup_on_success: Whether to auto-cleanup after successful processing
        """
        self.cache_dirs = cache_dirs or [
            "output/phase3_mockups",
            "output/phase3_custom_pdfs", 
            "output/phase3_jpeg_files"
        ]
        self.retention_count = retention_count
        self.max_cache_size_mb = max_cache_size_mb
        self.cleanup_on_success = cleanup_on_success
        
        # Track processed designs for retention
        self.processed_designs = []
        
        logger.info(f"🗂️  Cache Manager initialized")
        logger.info(f"   Cache directories: {len(self.cache_dirs)}")
        logger.info(f"   Retention count: {retention_count} designs")
        logger.info(f"   Max cache size: {max_cache_size_mb} MB")
        logger.info(f"   Auto-cleanup: {cleanup_on_success}")
    
    def get_cache_size(self) -> Dict[str, float]:
        """Get current cache size for each directory.
        
        Returns:
            Dict mapping directory to size in MB
        """
        sizes = {}
        total_size = 0
        
        for cache_dir in self.cache_dirs:
            dir_path = Path(cache_dir)
            if not dir_path.exists():
                sizes[cache_dir] = 0.0
                continue
                
            dir_size = 0
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    dir_size += file_path.stat().st_size
            
            size_mb = dir_size / (1024 * 1024)
            sizes[cache_dir] = size_mb
            total_size += size_mb
        
        sizes['total'] = total_size
        return sizes
    
    def log_cache_status(self):
        """Log current cache status."""
        sizes = self.get_cache_size()
        total_size = sizes.pop('total')
        
        logger.info(f"📊 Cache Status:")
        logger.info(f"   Total size: {total_size:.1f} MB")
        
        for cache_dir, size in sizes.items():
            if size > 0:
                logger.info(f"   {cache_dir}: {size:.1f} MB")
        
        if total_size > self.max_cache_size_mb:
            logger.warning(f"⚠️  Cache size ({total_size:.1f} MB) exceeds limit ({self.max_cache_size_mb} MB)")
    
    def cleanup_design_files(self, design_name: str, keep_pdfs: bool = True):
        """Clean up files for a specific design.
        
        Args:
            design_name: Name of the design to clean up
            keep_pdfs: Whether to keep PDF files (useful for debugging)
        """
        cleaned_files = 0
        cleaned_size = 0
        
        for cache_dir in self.cache_dirs:
            dir_path = Path(cache_dir)
            if not dir_path.exists():
                continue
            
            # Skip PDF cleanup if requested
            if keep_pdfs and 'pdf' in cache_dir.lower():
                continue
                
            # Find files matching the design name
            pattern = f"*{design_name}*"
            matching_files = list(dir_path.glob(pattern))
            
            for file_path in matching_files:
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    try:
                        file_path.unlink()
                        cleaned_files += 1
                        cleaned_size += file_size
                        logger.debug(f"🗑️  Cleaned: {file_path.name}")
                    except Exception as e:
                        logger.warning(f"Failed to clean {file_path}: {e}")
        
        if cleaned_files > 0:
            size_mb = cleaned_size / (1024 * 1024)
            logger.info(f"🧹 Cleaned {cleaned_files} files for {design_name} ({size_mb:.1f} MB freed)")
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up files older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned_files = 0
        cleaned_size = 0
        
        for cache_dir in self.cache_dirs:
            dir_path = Path(cache_dir)
            if not dir_path.exists():
                continue
                
            for file_path in dir_path.rglob('*'):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_size = file_path.stat().st_size
                    try:
                        file_path.unlink()
                        cleaned_files += 1
                        cleaned_size += file_size
                    except Exception as e:
                        logger.warning(f"Failed to clean old file {file_path}: {e}")
        
        if cleaned_files > 0:
            size_mb = cleaned_size / (1024 * 1024)
            logger.info(f"🧹 Cleaned {cleaned_files} old files ({size_mb:.1f} MB freed)")
    
    def register_design_processing(self, design_name: str):
        """Register that a design is being processed.
        
        Args:
            design_name: Name of the design being processed
        """
        self.processed_designs.append({
            'name': design_name,
            'timestamp': datetime.now(),
            'status': 'processing'
        })
        logger.debug(f"📝 Registered design for processing: {design_name}")
    
    def mark_design_success(self, design_name: str):
        """Mark a design as successfully processed and trigger cleanup.
        
        Args:
            design_name: Name of the successfully processed design
        """
        # Update status
        for design in self.processed_designs:
            if design['name'] == design_name:
                design['status'] = 'success'
                design['completed'] = datetime.now()
                break
        
        logger.info(f"✅ Design marked as successful: {design_name}")
        
        # Trigger cleanup if enabled
        if self.cleanup_on_success:
            self._cleanup_with_retention(design_name)
    
    def mark_design_failed(self, design_name: str):
        """Mark a design as failed and clean up immediately.
        
        Args:
            design_name: Name of the failed design
        """
        # Update status
        for design in self.processed_designs:
            if design['name'] == design_name:
                design['status'] = 'failed'
                design['completed'] = datetime.now()
                break
        
        logger.warning(f"❌ Design marked as failed: {design_name}")
        
        # Clean up failed processing files immediately
        self.cleanup_design_files(design_name, keep_pdfs=False)
    
    def _cleanup_with_retention(self, current_design: str):
        """Clean up old designs while keeping recent ones for debugging.
        
        Args:
            current_design: The design that just completed successfully
        """
        # Get successful designs sorted by completion time
        successful_designs = [
            d for d in self.processed_designs 
            if d.get('status') == 'success' and 'completed' in d
        ]
        successful_designs.sort(key=lambda x: x['completed'], reverse=True)
        
        # Keep only the most recent designs (including current)
        designs_to_keep = set()
        for i, design in enumerate(successful_designs):
            if i < self.retention_count:
                designs_to_keep.add(design['name'])
        
        # Clean up designs not in retention list
        designs_to_cleanup = [
            d['name'] for d in successful_designs[self.retention_count:]
        ]
        
        for design_name in designs_to_cleanup:
            if design_name != current_design:  # Don't clean up current design
                self.cleanup_design_files(design_name, keep_pdfs=True)
        
        if designs_to_cleanup:
            logger.info(f"🗂️  Retention cleanup: kept {len(designs_to_keep)} recent designs")
    
    def force_cleanup_all(self, confirm: bool = False):
        """Force cleanup of all cache directories.
        
        Args:
            confirm: Must be True to actually perform cleanup
        """
        if not confirm:
            logger.warning("⚠️  Force cleanup requires confirm=True")
            return
        
        total_cleaned = 0
        total_size = 0
        
        for cache_dir in self.cache_dirs:
            dir_path = Path(cache_dir)
            if dir_path.exists():
                # Calculate size before cleanup
                dir_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                file_count = len([f for f in dir_path.rglob('*') if f.is_file()])
                
                # Remove all files
                shutil.rmtree(dir_path)
                dir_path.mkdir(parents=True, exist_ok=True)
                
                total_cleaned += file_count
                total_size += dir_size
                
                size_mb = dir_size / (1024 * 1024)
                logger.info(f"🧹 Cleaned {cache_dir}: {file_count} files ({size_mb:.1f} MB)")
        
        total_size_mb = total_size / (1024 * 1024)
        logger.info(f"🗑️  Force cleanup complete: {total_cleaned} files ({total_size_mb:.1f} MB freed)")
        
        # Clear processed designs list
        self.processed_designs.clear()
