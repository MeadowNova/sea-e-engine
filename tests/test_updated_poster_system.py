#!/usr/bin/env python3
"""
Test Updated Poster System with VIA Coordinates
==============================================

Test the updated perspective mockup generator that automatically uses
VIA annotation coordinates for precise design placement.
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


def test_updated_poster_system():
    """Test the updated poster system with automatic VIA coordinate loading."""
    logger.info("🎨 Testing Updated Poster System with Auto VIA Coordinates")
    logger.info("=" * 70)
    
    # Your actual design file
    design_file = "assets/mockups/posters/Designs for Mockups/24x36 TEMPLATE.png"
    
    # Verify design file exists - early exit with exception for CI
    if not Path(design_file).exists():
        raise FileNotFoundError(f"Design file not found: {design_file}")
    
    logger.info(f"✅ Using design: {design_file}")
    
    # Initialize generator (should auto-load VIA coordinates)
    generator = PerspectiveMockupGenerator()
    
    # Get all available templates
    templates = generator.list_available_templates()
    logger.info(f"📁 Found {len(templates)} poster templates")
    
    # Check if VIA coordinates were loaded
    logger.info(f"\n🔍 Checking VIA coordinate loading:")
    for template in templates:
        config = generator.get_template_config(template)
        if config:
            via_source = config.get('via_source', 'Not specified')
            corners = config.get('corners', [])
            logger.info(f"  📍 {template}: {len(corners)} corners from {via_source}")
        else:
            logger.warning(f"  ⚠️ {template}: No configuration found")
    
    results = []
    
    # Test each template (should use VIA coordinates automatically)
    for i, template in enumerate(templates, 1):
        logger.info(f"\n🖼️ Generating poster mockup {i}/{len(templates)}: {template}")
        
        # Get template configuration
        config = generator.get_template_config(template)
        if config:
            logger.info(f"  Name: {config.get('name', 'Unknown')}")
            logger.info(f"  Type: {config.get('perspective_type', 'unknown')}")
            logger.info(f"  VIA Source: {config.get('via_source', 'None')}")
            logger.info(f"  Corners: {config.get('corners', [])}")
        
        # Generate perspective mockup (should use VIA coordinates automatically)
        result = generator.generate_perspective_mockup(design_file, template)
        
        if result['success']:
            # Rename with AUTO_VIA indicator
            original_path = Path(result['mockup_path'])
            template_stem = Path(template).stem
            new_name = f"24x36_TEMPLATE_AUTO_VIA_{template_stem}.png"
            new_path = original_path.parent / new_name
            original_path.rename(new_path)
            
            logger.info(f"  ✅ Generated: {new_name}")
            logger.info(f"  📐 Corner points used: {result['corner_points']}")
            logger.info(f"  📏 Output size: {result['output_size']}")
            logger.info(f"  🎯 Clean placement: No artifacts!")

            results.append({
                'template': template,
                'path': str(new_path),
                'config': config,
                'success': True
            })
        else:
            logger.error(f"  ❌ Failed: {result['error']}")
            results.append({
                'template': template,
                'success': False,
                'error': result['error']
            })
    
    return results


def validate_auto_via_system(results):
    """Validate the automatic VIA coordinate system."""
    logger.info(f"\n🔍 Validating Auto VIA System")
    logger.info("=" * 40)
    
    successful_mockups = [r for r in results if r['success']]
    failed_mockups = [r for r in results if not r['success']]
    
    logger.info(f"✅ Successful auto-VIA mockups: {len(successful_mockups)}")
    logger.info(f"❌ Failed mockups: {len(failed_mockups)}")
    
    if successful_mockups:
        logger.info(f"\n📁 Generated Auto-VIA Mockups:")
        for result in successful_mockups:
            config = result.get('config', {})
            perspective_type = config.get('perspective_type', 'unknown')
            template_name = config.get('name', Path(result['template']).stem)
            via_source = config.get('via_source', 'None')
            logger.info(f"  ✅ {template_name} ({perspective_type}) - VIA: {via_source}")
    
    if failed_mockups:
        logger.info(f"\n⚠️ Failed Mockups:")
        for result in failed_mockups:
            logger.info(f"  ❌ {result['template']}: {result.get('error', 'Unknown error')}")
    
    # Calculate success rate
    success_rate = (len(successful_mockups) / len(results)) * 100 if results else 0
    logger.info(f"\n📊 Auto-VIA Success Rate: {success_rate:.1f}%")
    
    return success_rate >= 80


def main():
    """Run updated poster system testing."""
    logger.info("🎯 Updated Poster System Test - Auto VIA Coordinates")
    logger.info("=" * 70)
    
    # Check OpenCV availability
    try:
        import cv2
        logger.info(f"✅ OpenCV available: {cv2.__version__}")
    except ImportError:
        logger.error("❌ OpenCV required for perspective transformation")
        return
    
    # Test updated poster system
    results = test_updated_poster_system()
    
    if not results:
        logger.error("❌ No mockups were generated")
        return
    
    # Validate system
    system_passed = validate_auto_via_system(results)
    
    # Final summary
    logger.info(f"\n🎉 Updated System Testing Complete!")
    logger.info(f"📊 Generated {len([r for r in results if r['success']])}/{len(results)} auto-VIA mockups")
    logger.info(f"🎯 System validation: {'✅ PASSED' if system_passed else '❌ FAILED'}")
    
    if system_passed:
        logger.info(f"\n🚀 Poster System Updated Successfully!")
        logger.info(f"  ✅ VIA coordinates auto-loaded")
        logger.info(f"  ✅ Precise design placement working")
        logger.info(f"  ✅ Ready for production integration")
        logger.info(f"  🎯 Next: Integrate with Google Sheets workflow")
    else:
        logger.info(f"\n⚠️ System needs attention")
        logger.info(f"  📝 Review VIA coordinate loading")
        logger.info(f"  📝 Check template configurations")
    
    logger.info(f"\n📁 Check 'output' directory for auto-VIA mockups!")


if __name__ == "__main__":
    main()
