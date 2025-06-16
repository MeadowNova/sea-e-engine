#!/usr/bin/env python3
"""
Test script for Perspective Mockup Generator
===========================================

Tests perspective transformation for art prints and posters.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.perspective_mockup_generator import PerspectiveMockupGenerator, create_test_art_design
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_perspective_generation():
    """Test perspective mockup generation."""
    logger.info("🎨 Testing Perspective Mockup Generation")
    logger.info("=" * 50)
    
    # Initialize generator
    generator = PerspectiveMockupGenerator()
    
    # List available templates
    templates = generator.list_available_templates()
    logger.info(f"📁 Available poster templates: {templates}")
    
    if not templates:
        logger.warning("⚠️ No poster templates found in assets/mockups/posters/")
        return []
    
    # Create test art design
    test_design_path = "test_art_design.png"
    create_test_art_design(test_design_path)
    logger.info(f"Created test art design: {test_design_path}")
    
    results = []
    
    # Test each available template
    for template in templates[:3]:  # Test first 3 templates
        logger.info(f"\n🖼️ Testing template: {template}")
        
        # Get template configuration
        config = generator.get_template_config(template)
        if config:
            logger.info(f"  Perspective type: {config.get('perspective_type', 'unknown')}")
            logger.info(f"  Corner points: {config.get('corners', 'default')}")
        
        # Generate perspective mockup
        result = generator.generate_perspective_mockup(test_design_path, template)
        
        if result['success']:
            logger.info(f"✅ Success: {result['mockup_path']}")
            logger.info(f"  Corner points used: {result['corner_points']}")
            logger.info(f"  Output size: {result['output_size']}")
            results.append(result)
        else:
            logger.error(f"❌ Failed: {result['error']}")
    
    # Clean up test design
    try:
        Path(test_design_path).unlink()
        logger.info(f"Cleaned up test design: {test_design_path}")
    except:
        pass
    
    return results


def test_corner_calibration():
    """Test corner calibration for fine-tuning."""
    logger.info("\n🎯 Testing Corner Calibration")
    logger.info("=" * 40)
    
    generator = PerspectiveMockupGenerator()
    templates = generator.list_available_templates()
    
    if not templates:
        logger.warning("No templates available for calibration")
        return
    
    # Test calibration on first template
    template = templates[0]
    logger.info(f"Calibrating template: {template}")
    
    result = generator.calibrate_corners(template)
    
    if result['success']:
        logger.info(f"✅ Calibration mockup generated: {result['mockup_path']}")
        logger.info("📝 To adjust corners:")
        logger.info("  1. Open the generated calibration mockup")
        logger.info("  2. Note where the white corner circles should be positioned")
        logger.info("  3. Update corner coordinates in the generator")
        logger.info("  4. Regenerate to test alignment")
    else:
        logger.error(f"❌ Calibration failed: {result['error']}")


def test_custom_corners():
    """Test custom corner specification."""
    logger.info("\n⚙️ Testing Custom Corner Specification")
    logger.info("=" * 40)
    
    generator = PerspectiveMockupGenerator()
    templates = generator.list_available_templates()
    
    if not templates:
        logger.warning("No templates available for custom corner testing")
        return
    
    # Create test design
    test_design_path = "custom_corner_test.png"
    create_test_art_design(test_design_path)
    
    # Test with custom corners (example for angled poster)
    custom_corners = [
        (450, 350),   # Top-left
        (1550, 300),  # Top-right
        (1600, 1700), # Bottom-right
        (400, 1750)   # Bottom-left
    ]
    
    template = templates[0]
    logger.info(f"Testing custom corners on {template}")
    logger.info(f"Custom corners: {custom_corners}")
    
    result = generator.generate_perspective_mockup(
        test_design_path, 
        template, 
        custom_corners=custom_corners
    )
    
    if result['success']:
        # Rename with custom indicator
        original_path = Path(result['mockup_path'])
        new_name = f"custom_corners_{original_path.name}"
        new_path = original_path.parent / new_name
        original_path.rename(new_path)
        
        logger.info(f"✅ Custom corners test: {new_name}")
    else:
        logger.error(f"❌ Custom corners failed: {result['error']}")
    
    # Clean up
    try:
        Path(test_design_path).unlink()
    except:
        pass


def demonstrate_perspective_workflow():
    """Demonstrate the complete perspective workflow."""
    logger.info("\n🚀 Perspective Mockup Workflow Demonstration")
    logger.info("=" * 50)
    
    logger.info("📋 Workflow Steps:")
    logger.info("1. 🎨 Create/load art design")
    logger.info("2. 📐 Load poster template with angle")
    logger.info("3. 🎯 Define corner points for perspective")
    logger.info("4. 🔄 Apply perspective transformation")
    logger.info("5. 🖼️ Overlay on template")
    logger.info("6. 💾 Save final mockup")
    
    generator = PerspectiveMockupGenerator()
    
    # Create artistic design
    art_design_path = "workflow_art.png"
    create_test_art_design(art_design_path)
    
    templates = generator.list_available_templates()
    
    if templates:
        # Generate mockup with workflow
        template = templates[0]
        logger.info(f"\n🎬 Generating mockup with {template}...")
        
        result = generator.generate_perspective_mockup(art_design_path, template)
        
        if result['success']:
            logger.info(f"🎉 Workflow complete!")
            logger.info(f"📁 Final mockup: {result['mockup_path']}")
            logger.info(f"📐 Perspective applied with corners: {result['corner_points']}")
            
            # Show comparison info
            logger.info(f"\n📊 Comparison:")
            logger.info(f"  Original design: Flat rectangle")
            logger.info(f"  Final mockup: Perspective-corrected to match frame angle")
            logger.info(f"  Result: Realistic art print mockup!")
        else:
            logger.error(f"❌ Workflow failed: {result['error']}")
    
    # Clean up
    try:
        Path(art_design_path).unlink()
    except:
        pass


def main():
    """Run all perspective mockup tests."""
    logger.info("🎨 Perspective Mockup Generator Testing")
    logger.info("=" * 60)
    
    # Check if OpenCV is available
    try:
        import cv2
        logger.info("✅ OpenCV available for perspective transformation")
    except ImportError:
        logger.error("❌ OpenCV not available. Install with: pip install opencv-python")
        logger.info("Perspective transformation requires OpenCV for advanced image processing")
        return
    
    # Run tests
    perspective_results = test_perspective_generation()
    test_corner_calibration()
    test_custom_corners()
    demonstrate_perspective_workflow()
    
    # Summary
    logger.info(f"\n🎉 Testing Complete!")
    logger.info(f"Generated {len(perspective_results)} perspective mockups")
    
    if perspective_results:
        logger.info("📁 Generated files:")
        for result in perspective_results:
            logger.info(f"  - {Path(result['mockup_path']).name}")
    
    logger.info(f"\n💡 Key Benefits of Perspective Transformation:")
    logger.info(f"  ✅ Realistic angled poster mockups")
    logger.info(f"  ✅ Perfect alignment with frame perspective")
    logger.info(f"  ✅ Professional-quality art print previews")
    logger.info(f"  ✅ Customizable corner points for any angle")
    
    logger.info(f"\nCheck the 'output' directory for perspective-corrected mockups!")


if __name__ == "__main__":
    main()
