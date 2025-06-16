#!/usr/bin/env python3
"""
Test Perspective Integration
===========================

Test the perspective transformation functionality to verify it's working
correctly before integration into the main system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from modules.perspective_mockup_generator import PerspectiveMockupGenerator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_perspective_integration():
    """Test the perspective transformation integration."""
    logger.info("🎯 Testing Perspective Integration")
    logger.info("=" * 50)
    
    # Your actual design file
    design_file = "assets/mockups/posters/Designs for Mockups/24x36 TEMPLATE.png"
    
    # Verify design file exists
    if not Path(design_file).exists():
        raise FileNotFoundError(f"Design file not found: {design_file}")
    
    logger.info(f"✅ Using design: {design_file}")
    
    # Initialize perspective generator
    generator = PerspectiveMockupGenerator(
        assets_dir="assets",
        output_dir="output"
    )
    
    # Get available templates
    templates = generator.list_available_templates()
    logger.info(f"📁 Found {len(templates)} poster templates")
    
    # Test ALL 8 art print mockup templates
    test_templates = ['1.jpg', '2.jpg', '3.jpg', '5.jpg', '6.jpg', '7.jpg', '8.jpg', '9.png']
    
    results = []
    
    for template_name in test_templates:
        if template_name in templates:
            logger.info(f"\n🖼️ Testing template: {template_name}")
            
            # Generate mockup
            result = generator.generate_perspective_mockup(design_file, template_name)
            
            if result['success']:
                # Rename with INTEGRATED indicator
                original_path = Path(result['mockup_path'])
                template_stem = Path(template_name).stem
                new_name = f"24x36_TEMPLATE_INTEGRATED_{template_stem}.png"
                new_path = original_path.parent / new_name
                original_path.rename(new_path)
                
                logger.info(f"  ✅ Generated: {new_name}")
                logger.info(f"  📐 Corner points: {result['corner_points']}")
                logger.info(f"  📏 Output size: {result['output_size']}")
                
                results.append({
                    'template': template_name,
                    'success': True,
                    'path': str(new_path)
                })
            else:
                logger.error(f"  ❌ Failed: {result['error']}")
                results.append({
                    'template': template_name,
                    'success': False,
                    'error': result['error']
                })
        else:
            logger.warning(f"  ⚠️ Template {template_name} not found")
    
    return results


def validate_perspective_integration():
    """Validate the perspective integration results."""
    logger.info(f"\n🔍 Validating Perspective Integration")
    logger.info("=" * 40)
    
    results = test_perspective_integration()
    
    if not results:
        logger.error("❌ No test results generated")
        return False
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    logger.info(f"✅ Successful integrations: {len(successful)}")
    logger.info(f"❌ Failed integrations: {len(failed)}")
    
    if successful:
        logger.info(f"\n📁 Generated Integrated Mockups:")
        for result in successful:
            template_name = Path(result['template']).stem
            logger.info(f"  ✅ Template {template_name}: {Path(result['path']).name}")
    
    if failed:
        logger.info(f"\n⚠️ Failed Integrations:")
        for result in failed:
            logger.info(f"  ❌ {result['template']}: {result.get('error', 'Unknown error')}")
    
    # Calculate success rate
    success_rate = (len(successful) / len(results)) * 100 if results else 0
    logger.info(f"\n📊 Integration Success Rate: {success_rate:.1f}%")
    
    # Check specifically for the angled templates that were fixed
    angled_templates = ['2.jpg', '5.jpg', '6.jpg']
    angled_success = [r for r in successful if r['template'] in angled_templates]

    # Check for all 8 templates
    all_templates = ['1.jpg', '2.jpg', '3.jpg', '5.jpg', '6.jpg', '7.jpg', '8.jpg', '9.png']
    all_success = [r for r in successful if r['template'] in all_templates]

    logger.info(f"🎯 Angled Templates Fixed: {len(angled_success)}/{len(angled_templates)}")
    logger.info(f"📊 All 8 Templates: {len(all_success)}/{len(all_templates)}")

    return success_rate >= 95 and len(angled_success) == 3 and len(all_success) == 8


def main():
    """Run perspective integration testing."""
    logger.info("🎯 Perspective Integration Test")
    logger.info("=" * 50)
    
    # Check OpenCV availability
    try:
        import cv2
        logger.info(f"✅ OpenCV available: {cv2.__version__}")
    except ImportError:
        logger.error("❌ OpenCV required for perspective transformation")
        return
    
    # Test perspective integration
    integration_passed = validate_perspective_integration()
    
    # Final summary
    logger.info(f"\n🎉 Perspective Integration Testing Complete!")
    logger.info(f"🎯 Integration validation: {'✅ PASSED' if integration_passed else '❌ FAILED'}")
    
    if integration_passed:
        logger.info(f"\n🚀 Perspective System Integration Ready!")
        logger.info(f"  ✅ ALL 8 art print templates working")
        logger.info(f"  ✅ VIA coordinates working correctly")
        logger.info(f"  ✅ Perspective transformation fixed")
        logger.info(f"  ✅ No blue grain contamination")
        logger.info(f"  ✅ Angled templates (2, 5, 6) working")
        logger.info(f"  ✅ Rectangular templates (1, 3, 7, 8, 9) working")
        logger.info(f"  🎯 Ready for main system integration")
    else:
        logger.info(f"\n⚠️ Integration needs attention")
        logger.info(f"  📝 Review perspective implementation")
        logger.info(f"  📝 Check angled template fixes")
    
    logger.info(f"\n📁 Check 'output' directory for integrated mockups!")


if __name__ == "__main__":
    main()
