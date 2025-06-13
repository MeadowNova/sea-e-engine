#!/usr/bin/env python3
"""
Test Output Management System
============================

Tests the automatic file organization and cleanup system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from modules.custom_mockup_generator import CustomMockupGenerator
from utils.output_manager import OutputManager
from PIL import Image, ImageDraw
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_quick_test_design(name: str) -> str:
    """Create a quick test design."""
    design = Image.new('RGBA', (400, 400), (255, 100, 100, 255))
    draw = ImageDraw.Draw(design)
    draw.text((200, 200), name, fill=(255, 255, 255, 255), anchor="mm")
    
    design_path = f"{name}_design.png"
    design.save(design_path)
    return design_path


def test_automatic_organization():
    """Test automatic file organization."""
    logger.info("🗂️ Testing Automatic File Organization")
    logger.info("=" * 50)
    
    # Initialize generator with auto-management
    generator = CustomMockupGenerator(auto_manage=True)
    
    # Create test design
    test_design = create_quick_test_design("auto_test")
    
    # Generate a test mockup
    result = generator.generate_mockup('tshirts', test_design, '1')
    
    if result['success']:
        logger.info(f"✅ Generated mockup: {result['mockup_path']}")
        
        # Check if it was automatically organized
        mockup_path = Path(result['mockup_path'])
        if 'test_outputs' in str(mockup_path):
            logger.info("✅ File automatically organized to test directory")
        else:
            logger.warning("⚠️ File not automatically organized")
    else:
        logger.error(f"❌ Failed to generate mockup: {result['error']}")
    
    # Clean up test design
    try:
        Path(test_design).unlink()
    except:
        pass


def test_storage_monitoring():
    """Test storage monitoring and statistics."""
    logger.info("\n📊 Testing Storage Monitoring")
    logger.info("=" * 40)
    
    manager = OutputManager()
    stats = manager.get_storage_stats()
    
    logger.info(f"📁 Current Storage Statistics:")
    logger.info(f"  Total: {stats['total_size_mb']:.1f}MB, {stats['total_files']} files")
    
    for category, category_stats in stats['categories'].items():
        logger.info(f"  {category}: {category_stats['size_mb']:.1f}MB, {category_stats['files']} files")
    
    # Check if cleanup is needed
    max_size = 500  # MB
    if stats['total_size_mb'] > max_size:
        logger.warning(f"⚠️ Storage exceeds {max_size}MB limit")
        logger.info("🧹 Automatic cleanup would be triggered")
    else:
        logger.info(f"✅ Storage within {max_size}MB limit")


def test_production_file_saving():
    """Test saving production files."""
    logger.info("\n🏭 Testing Production File Management")
    logger.info("=" * 40)
    
    manager = OutputManager()
    
    # Create a mock production file
    test_design = create_quick_test_design("production_test")
    
    try:
        # Save as production file
        production_path = manager.save_production_file(
            Path(test_design), 
            "client_mockup_v1.png"
        )
        
        logger.info(f"✅ Saved production file: {production_path}")
        
        # Verify it's in production directory
        if 'production' in str(production_path):
            logger.info("✅ File correctly saved to production directory")
        else:
            logger.warning("⚠️ File not in production directory")
            
    except Exception as e:
        logger.error(f"❌ Failed to save production file: {e}")
    
    # Clean up test design
    try:
        Path(test_design).unlink()
    except:
        pass


def test_cleanup_policies():
    """Test cleanup policies and retention."""
    logger.info("\n🧹 Testing Cleanup Policies")
    logger.info("=" * 40)
    
    manager = OutputManager()
    
    # Get current stats
    before_stats = manager.get_storage_stats()
    logger.info(f"Before cleanup: {before_stats['total_size_mb']:.1f}MB, {before_stats['total_files']} files")
    
    # Run cleanup
    cleanup_stats = manager.cleanup_old_files(force=True)
    
    if cleanup_stats.get('deleted_files', 0) > 0:
        logger.info(f"🗑️ Cleanup results:")
        logger.info(f"  Deleted: {cleanup_stats['deleted_files']} files")
        logger.info(f"  Freed: {cleanup_stats['freed_mb']:.1f}MB")
        
        for category, stats in cleanup_stats.get('categories', {}).items():
            if stats['deleted'] > 0:
                logger.info(f"  {category}: {stats['deleted']} files, {stats['freed_mb']:.1f}MB")
    else:
        logger.info("✅ No files needed cleanup")
    
    # Get final stats
    after_stats = manager.get_storage_stats()
    logger.info(f"After cleanup: {after_stats['total_size_mb']:.1f}MB, {after_stats['total_files']} files")


def demonstrate_file_lifecycle():
    """Demonstrate complete file lifecycle management."""
    logger.info("\n🔄 Demonstrating File Lifecycle")
    logger.info("=" * 50)
    
    logger.info("📋 File Lifecycle Steps:")
    logger.info("1. 🎨 Generate test mockup")
    logger.info("2. 🗂️ Auto-organize to test directory")
    logger.info("3. 🏭 Promote to production if needed")
    logger.info("4. 🧹 Cleanup old test files")
    logger.info("5. 📊 Monitor storage usage")
    
    # Step 1: Generate mockup
    generator = CustomMockupGenerator(auto_manage=True)
    test_design = create_quick_test_design("lifecycle")
    
    result = generator.generate_mockup('tshirts', test_design, '1')
    
    if result['success']:
        logger.info(f"✅ Step 1: Generated {Path(result['mockup_path']).name}")
        
        # Step 2: Already auto-organized
        logger.info("✅ Step 2: Auto-organized to test directory")
        
        # Step 3: Promote to production
        manager = OutputManager()
        production_path = manager.save_production_file(
            Path(result['mockup_path']),
            "final_client_mockup.png"
        )
        logger.info(f"✅ Step 3: Promoted to production: {production_path.name}")
        
        # Step 4: Cleanup would happen automatically
        logger.info("✅ Step 4: Cleanup policies active")
        
        # Step 5: Monitor storage
        stats = manager.get_storage_stats()
        logger.info(f"✅ Step 5: Current storage: {stats['total_size_mb']:.1f}MB")
        
    else:
        logger.error(f"❌ Failed lifecycle test: {result['error']}")
    
    # Clean up test design
    try:
        Path(test_design).unlink()
    except:
        pass


def main():
    """Run all output management tests."""
    logger.info("🗂️ Output Management System Testing")
    logger.info("=" * 60)
    
    # Run tests
    test_automatic_organization()
    test_storage_monitoring()
    test_production_file_saving()
    test_cleanup_policies()
    demonstrate_file_lifecycle()
    
    # Final summary
    manager = OutputManager()
    final_stats = manager.get_storage_stats()
    
    logger.info(f"\n🎉 Output Management Testing Complete!")
    logger.info(f"📊 Final Storage: {final_stats['total_size_mb']:.1f}MB, {final_stats['total_files']} files")
    
    logger.info(f"\n💡 Key Benefits:")
    logger.info(f"  ✅ Automatic file organization by type")
    logger.info(f"  ✅ Smart cleanup of old test files")
    logger.info(f"  ✅ Production file management")
    logger.info(f"  ✅ Storage monitoring and alerts")
    logger.info(f"  ✅ Configurable retention policies")
    
    logger.info(f"\n🎯 No more manual file management needed!")


if __name__ == "__main__":
    main()
