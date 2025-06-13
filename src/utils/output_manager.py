#!/usr/bin/env python3
"""
Output Manager for SEA-E Engine
==============================

Manages generated mockup files with smart caching, cleanup, and storage optimization.

Features:
- Automatic cleanup of old test files
- Size-based cache management
- Production vs test file separation
- Configurable retention policies
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger("output_manager")


class OutputManager:
    """
    Manages output files with smart caching and cleanup.
    """
    
    def __init__(self, output_dir: str = "output", config_file: str = "config/output_config.json"):
        """
        Initialize output manager.
        
        Args:
            output_dir: Base output directory
            config_file: Configuration file path
        """
        self.output_dir = Path(output_dir)
        self.config_file = Path(config_file)
        
        # Load configuration
        self.config = self._load_config()
        
        # Create directory structure
        self._setup_directories()
        
        logger.info(f"OutputManager initialized for {self.output_dir}")
    
    def _load_config(self) -> Dict:
        """Load output management configuration."""
        default_config = {
            "cache_settings": {
                "max_total_size_mb": 500,
                "max_test_files": 50,
                "max_age_days": 7,
                "cleanup_on_startup": True
            },
            "file_categories": {
                "test": {
                    "patterns": ["test_*", "*_test_*", "calibration_*", "position_*", "blend_test_*"],
                    "max_age_hours": 24,
                    "max_count": 20
                },
                "production": {
                    "patterns": ["prod_*", "*_final_*"],
                    "max_age_days": 30,
                    "max_count": 100
                },
                "temp": {
                    "patterns": ["temp_*", "*_temp_*", "workflow_*"],
                    "max_age_hours": 2,
                    "max_count": 10
                }
            },
            "directories": {
                "test": "test_outputs",
                "production": "production",
                "temp": "temp",
                "archive": "archive"
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.warning(f"Could not load config file: {e}")
        
        return default_config
    
    def _setup_directories(self):
        """Create organized directory structure."""
        directories = self.config.get("directories", {})
        
        for dir_type, dir_name in directories.items():
            dir_path = self.output_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            setattr(self, f"{dir_type}_dir", dir_path)
        
        # Ensure main output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def categorize_file(self, filename: str) -> str:
        """
        Categorize a file based on its name pattern.
        
        Args:
            filename: Name of the file
            
        Returns:
            Category name ('test', 'production', 'temp', or 'unknown')
        """
        file_categories = self.config.get("file_categories", {})
        
        for category, settings in file_categories.items():
            patterns = settings.get("patterns", [])
            for pattern in patterns:
                # Simple pattern matching (could be enhanced with regex)
                if pattern.replace("*", "") in filename:
                    return category
        
        return "unknown"
    
    def organize_file(self, file_path: Path, category: str = None) -> Path:
        """
        Move file to appropriate directory based on category.
        
        Args:
            file_path: Path to file to organize
            category: Override category (optional)
            
        Returns:
            New file path after organization
        """
        if not file_path.exists():
            return file_path
        
        if category is None:
            category = self.categorize_file(file_path.name)
        
        # Get target directory
        target_dir = getattr(self, f"{category}_dir", self.output_dir)
        target_path = target_dir / file_path.name
        
        # Move file if not already in correct location
        if file_path.parent != target_dir:
            try:
                shutil.move(str(file_path), str(target_path))
                logger.info(f"Organized {file_path.name} to {category} directory")
                return target_path
            except Exception as e:
                logger.warning(f"Could not organize file {file_path}: {e}")
        
        return file_path
    
    def cleanup_old_files(self, force: bool = False) -> Dict[str, int]:
        """
        Clean up old files based on age and count limits.
        
        Args:
            force: Force cleanup regardless of settings
            
        Returns:
            Dictionary with cleanup statistics
        """
        if not force and not self.config.get("cache_settings", {}).get("cleanup_on_startup", True):
            return {"skipped": True}
        
        stats = {"deleted_files": 0, "freed_mb": 0, "categories": {}}
        
        file_categories = self.config.get("file_categories", {})
        
        for category, settings in file_categories.items():
            category_dir = getattr(self, f"{category}_dir", None)
            if not category_dir or not category_dir.exists():
                continue
            
            category_stats = {"deleted": 0, "freed_mb": 0}
            
            # Get all files in category directory
            files = list(category_dir.glob("*"))
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)  # Newest first
            
            # Age-based cleanup
            max_age_hours = settings.get("max_age_hours")
            max_age_days = settings.get("max_age_days")
            
            if max_age_hours or max_age_days:
                max_age = max_age_hours / 24 if max_age_hours else max_age_days
                cutoff_time = datetime.now() - timedelta(days=max_age)
                
                for file_path in files:
                    if file_path.is_file():
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_time:
                            size_mb = file_path.stat().st_size / (1024 * 1024)
                            file_path.unlink()
                            category_stats["deleted"] += 1
                            category_stats["freed_mb"] += size_mb
            
            # Count-based cleanup
            max_count = settings.get("max_count", 0)
            if max_count > 0 and len(files) > max_count:
                files_to_delete = files[max_count:]
                for file_path in files_to_delete:
                    if file_path.is_file():
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        file_path.unlink()
                        category_stats["deleted"] += 1
                        category_stats["freed_mb"] += size_mb
            
            stats["categories"][category] = category_stats
            stats["deleted_files"] += category_stats["deleted"]
            stats["freed_mb"] += category_stats["freed_mb"]
        
        if stats["deleted_files"] > 0:
            logger.info(f"Cleanup completed: {stats['deleted_files']} files, {stats['freed_mb']:.1f}MB freed")
        
        return stats
    
    def get_storage_stats(self) -> Dict[str, any]:
        """Get current storage statistics."""
        stats = {
            "total_size_mb": 0,
            "total_files": 0,
            "categories": {}
        }
        
        # Check each category directory
        directories = self.config.get("directories", {})
        for category, dir_name in directories.items():
            category_dir = getattr(self, f"{category}_dir", None)
            if category_dir and category_dir.exists():
                files = list(category_dir.glob("*"))
                size_mb = sum(f.stat().st_size for f in files if f.is_file()) / (1024 * 1024)
                
                stats["categories"][category] = {
                    "files": len(files),
                    "size_mb": size_mb
                }
                stats["total_files"] += len(files)
                stats["total_size_mb"] += size_mb
        
        # Check main output directory for uncategorized files
        main_files = [f for f in self.output_dir.glob("*") if f.is_file()]
        if main_files:
            size_mb = sum(f.stat().st_size for f in main_files) / (1024 * 1024)
            stats["categories"]["uncategorized"] = {
                "files": len(main_files),
                "size_mb": size_mb
            }
            stats["total_files"] += len(main_files)
            stats["total_size_mb"] += size_mb
        
        return stats
    
    def organize_existing_files(self) -> Dict[str, int]:
        """Organize all existing files in output directory."""
        stats = {"organized": 0, "categories": {}}
        
        # Get all files in main output directory
        files = [f for f in self.output_dir.glob("*") if f.is_file()]
        
        for file_path in files:
            category = self.categorize_file(file_path.name)
            if category != "unknown":
                new_path = self.organize_file(file_path, category)
                if new_path != file_path:
                    stats["organized"] += 1
                    stats["categories"][category] = stats["categories"].get(category, 0) + 1
        
        return stats
    
    def save_production_file(self, source_path: Path, final_name: str = None) -> Path:
        """
        Save a file as a production file with proper naming.
        
        Args:
            source_path: Source file path
            final_name: Final production name (optional)
            
        Returns:
            Path to saved production file
        """
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Generate production filename
        if final_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_name = f"prod_{timestamp}_{source_path.name}"
        
        # Ensure it has production prefix
        if not final_name.startswith("prod_"):
            final_name = f"prod_{final_name}"
        
        # Copy to production directory
        production_path = self.production_dir / final_name
        shutil.copy2(str(source_path), str(production_path))
        
        logger.info(f"Saved production file: {production_path}")
        return production_path


def cleanup_output_directory(output_dir: str = "output", dry_run: bool = False) -> Dict[str, any]:
    """
    Convenience function to clean up output directory.
    
    Args:
        output_dir: Output directory path
        dry_run: If True, only report what would be deleted
        
    Returns:
        Cleanup statistics
    """
    manager = OutputManager(output_dir)
    
    if dry_run:
        stats = manager.get_storage_stats()
        logger.info(f"DRY RUN - Current storage: {stats['total_size_mb']:.1f}MB, {stats['total_files']} files")
        return stats
    else:
        # Organize existing files
        organize_stats = manager.organize_existing_files()
        logger.info(f"Organized {organize_stats['organized']} files")
        
        # Clean up old files
        cleanup_stats = manager.cleanup_old_files(force=True)
        
        # Get final stats
        final_stats = manager.get_storage_stats()
        
        return {
            "organized": organize_stats,
            "cleanup": cleanup_stats,
            "final_stats": final_stats
        }


if __name__ == "__main__":
    # Command line usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage SEA-E output files")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old files")
    parser.add_argument("--organize", action="store_true", help="Organize existing files")
    parser.add_argument("--stats", action="store_true", help="Show storage statistics")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--output-dir", default="output", help="Output directory path")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    if args.stats or args.dry_run:
        result = cleanup_output_directory(args.output_dir, dry_run=True)
        print(f"Storage Statistics:")
        print(f"Total: {result['total_size_mb']:.1f}MB, {result['total_files']} files")
        for category, stats in result['categories'].items():
            print(f"  {category}: {stats['size_mb']:.1f}MB, {stats['files']} files")
    
    if args.cleanup or args.organize:
        result = cleanup_output_directory(args.output_dir, dry_run=args.dry_run)
        if not args.dry_run:
            print(f"Cleanup completed:")
            print(f"  Organized: {result['organized']['organized']} files")
            print(f"  Deleted: {result['cleanup']['deleted_files']} files")
            print(f"  Freed: {result['cleanup']['freed_mb']:.1f}MB")
