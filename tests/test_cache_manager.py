#!/usr/bin/env python3
"""
Test Cache Manager functionality
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.append('src')

from modules.cache_manager import CacheManager


def create_test_files(cache_dir: str, design_name: str, file_count: int = 5):
    """Create test files for a design."""
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    for i in range(file_count):
        file_path = cache_path / f"{design_name}_mockup_{i}.png"
        # Create a dummy file with some content
        with open(file_path, 'w') as f:
            f.write("dummy mockup content " * 1000)  # ~20KB file
        created_files.append(file_path)
    
    return created_files


def test_cache_manager():
    """Test the cache manager functionality."""
    print("🧪 Testing Cache Manager...")
    
    # Create temporary cache directories
    temp_dir = tempfile.mkdtemp()
    cache_dirs = [
        os.path.join(temp_dir, "mockups"),
        os.path.join(temp_dir, "pdfs"),
        os.path.join(temp_dir, "jpegs")
    ]
    
    try:
        # Initialize cache manager
        cache_manager = CacheManager(
            cache_dirs=cache_dirs,
            retention_count=3,
            max_cache_size_mb=1,  # Low limit for testing
            cleanup_on_success=True
        )
        
        print("\n📊 Initial cache status:")
        cache_manager.log_cache_status()
        
        # Simulate processing multiple designs
        designs = ["design_1", "design_2", "design_3", "design_4", "design_5"]
        
        for design in designs:
            print(f"\n🎨 Processing {design}...")
            
            # Register design
            cache_manager.register_design_processing(design)
            
            # Create test files
            for cache_dir in cache_dirs:
                create_test_files(cache_dir, design, 3)
            
            print(f"📊 Cache status after creating files for {design}:")
            cache_manager.log_cache_status()
            
            # Mark as successful (triggers cleanup with retention)
            cache_manager.mark_design_success(design)
        
        print("\n📊 Final cache status:")
        cache_manager.log_cache_status()
        
        # Test failed design cleanup
        print(f"\n❌ Testing failed design cleanup...")
        failed_design = "failed_design"
        cache_manager.register_design_processing(failed_design)
        
        # Create files for failed design
        for cache_dir in cache_dirs:
            create_test_files(cache_dir, failed_design, 2)
        
        print(f"📊 Cache status before failed cleanup:")
        cache_manager.log_cache_status()
        
        # Mark as failed (should clean up immediately)
        cache_manager.mark_design_failed(failed_design)
        
        print(f"📊 Cache status after failed cleanup:")
        cache_manager.log_cache_status()
        
        # Test force cleanup
        print(f"\n🗑️  Testing force cleanup...")
        cache_manager.force_cleanup_all(confirm=True)
        
        print(f"📊 Cache status after force cleanup:")
        cache_manager.log_cache_status()
        
        print("\n✅ Cache Manager test completed successfully!")
        
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up test directory: {temp_dir}")


if __name__ == "__main__":
    test_cache_manager()
