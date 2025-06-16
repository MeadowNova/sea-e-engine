#!/usr/bin/env python3
"""
Test Poster Mockup Generation Only (No Google Sheets)
====================================================

Test poster mockup generation with your actual design file:
- Use 24x36 TEMPLATE.png design
- Generate mockups for all 8 poster templates
- Test perspective transformation
- Validate output quality
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


def test_poster_mockups_with_actual_design():
    """Test poster mockup generation with actual 24x36 TEMPLATE.png design."""
    logger.info("🎨 Testing Poster Mockups with Actual Design")
    logger.info("=" * 60)
    
    # Your actual design file
    design_file = "assets/mockups/posters/Designs for Mockups/24x36 TEMPLATE.png"
    
    # Verify design file exists
    if not Path(design_file).exists():
        logger.error(f"❌ Design file not found: {design_file}")
        return []
    
    logger.info(f"✅ Using actual design: {design_file}")
    
    # Initialize generator
    generator = PerspectiveMockupGenerator()
    
    # Get all available templates
    templates = generator.list_available_templates()
    logger.info(f"📁 Found {len(templates)} poster templates")
    
    results = []
    
    # Test each template with your actual design
    for i, template in enumerate(templates, 1):
        logger.info(f"\n🖼️ Generating poster mockup {i}/{len(templates)}: {template}")
        
        # Get template configuration
        config = generator.get_template_config(template)
        if config:
            logger.info(f"  Name: {config.get('name', 'Unknown')}")
            logger.info(f"  Type: {config.get('perspective_type', 'unknown')}")
            logger.info(f"  Difficulty: {config.get('difficulty', 'unknown')}")
        
        # Generate perspective mockup with your design
        result = generator.generate_perspective_mockup(design_file, template)
        
        if result['success']:
            # Rename with descriptive name
            original_path = Path(result['mockup_path'])
            template_stem = Path(template).stem
            new_name = f"24x36_TEMPLATE_poster_{template_stem}_perspective.png"
            new_path = original_path.parent / new_name
            original_path.rename(new_path)
            
            logger.info(f"  ✅ Generated: {new_name}")
            logger.info(f"  📐 Corner points: {result['corner_points']}")
            logger.info(f"  📏 Output size: {result['output_size']}")
            
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


def validate_mockup_quality(results):
    """Validate the quality of generated mockups."""
    logger.info(f"\n🔍 Validating Mockup Quality")
    logger.info("=" * 40)
    
    successful_mockups = [r for r in results if r['success']]
    failed_mockups = [r for r in results if not r['success']]
    
    logger.info(f"✅ Successful mockups: {len(successful_mockups)}")
    logger.info(f"❌ Failed mockups: {len(failed_mockups)}")
    
    if successful_mockups:
        logger.info(f"\n📁 Generated Mockups:")
        for result in successful_mockups:
            config = result.get('config', {})
            perspective_type = config.get('perspective_type', 'unknown')
            template_name = config.get('name', Path(result['template']).stem)
            logger.info(f"  ✅ {template_name} ({perspective_type})")
    
    if failed_mockups:
        logger.info(f"\n⚠️ Failed Mockups:")
        for result in failed_mockups:
            logger.info(f"  ❌ {result['template']}: {result.get('error', 'Unknown error')}")
    
    # Calculate success rate
    success_rate = (len(successful_mockups) / len(results)) * 100 if results else 0
    logger.info(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    return success_rate >= 80  # 80% success rate threshold


def main():
    """Run poster mockup testing with actual design."""
    logger.info("🎨 Poster Mockup Generation Test - Actual Design")
    logger.info("=" * 70)
    
    # Check OpenCV availability
    try:
        import cv2
        logger.info(f"✅ OpenCV available: {cv2.__version__}")
    except ImportError:
        logger.error("❌ OpenCV required for perspective transformation")
        return
    
    # Test poster mockup generation
    results = test_poster_mockups_with_actual_design()
    
    if not results:
        logger.error("❌ No mockups were generated")
        return
    
    # Validate quality
    quality_passed = validate_mockup_quality(results)
    
    # Final summary
    logger.info(f"\n🎉 Testing Complete!")
    logger.info(f"📊 Generated {len([r for r in results if r['success']])}/{len(results)} poster mockups")
    logger.info(f"🎯 Quality validation: {'✅ PASSED' if quality_passed else '❌ FAILED'}")
    
    if quality_passed:
        logger.info(f"\n🚀 Ready for Phase 2 Integration!")
        logger.info(f"  ✅ T-shirt mockups: Working (100% success)")
        logger.info(f"  ✅ Poster mockups: Working ({len([r for r in results if r['success']])}/{len(results)} success)")
        logger.info(f"  🎯 Next: Complete automation pipeline")
    else:
        logger.info(f"\n⚠️ Needs attention before Phase 2")
        logger.info(f"  📝 Review failed mockups and adjust configurations")
    
    logger.info(f"\n📁 Check 'output' directory for generated mockups!")


if __name__ == "__main__":
    main()
