#!/usr/bin/env python3
"""
Fix Template 1 Poster Mockup Issues
===================================

Specifically targets and fixes issues with the 24x36_TEMPLATE_AUTO_VIA_1.png mockup
based on visual analysis and VIA coordinate optimization.
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw
import json

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from modules.perspective_mockup_generator import PerspectiveMockupGenerator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def analyze_current_coordinates():
    """Analyze the current VIA coordinates for Template 1."""
    logger.info("🔍 Analyzing Current Template 1 Coordinates")
    
    # Current VIA coordinates for Template 1 (1.jpg)
    current_coords = [(568, 170), (1510, 170), (1510, 1649), (568, 1649)]
    
    # Calculate dimensions
    width = current_coords[1][0] - current_coords[0][0]  # 1510 - 568 = 942
    height = current_coords[2][1] - current_coords[1][1]  # 1649 - 170 = 1479
    aspect_ratio = width / height
    
    logger.info(f"📐 Current frame dimensions: {width} x {height}")
    logger.info(f"📏 Current aspect ratio: {aspect_ratio:.3f}")
    logger.info(f"🎯 24x36 target ratio: {24/36:.3f} = 0.667")
    
    return {
        'current_coords': current_coords,
        'width': width,
        'height': height,
        'aspect_ratio': aspect_ratio,
        'target_ratio': 24/36
    }


def create_optimized_coordinates(analysis):
    """Create optimized coordinates for better design placement."""
    logger.info("🛠️ Creating Optimized Coordinates")
    
    # Strategy 1: Expand the frame slightly for better design visibility
    expansion_factor = 1.1  # 10% larger frame
    
    current = analysis['current_coords']
    center_x = (current[0][0] + current[1][0]) / 2
    center_y = (current[0][1] + current[2][1]) / 2
    
    new_width = analysis['width'] * expansion_factor
    new_height = analysis['height'] * expansion_factor
    
    # Keep aspect ratio closer to 24x36 (2:3 ratio)
    target_ratio = analysis['target_ratio']
    if new_width / new_height > target_ratio:
        # Frame is too wide, reduce width
        new_width = new_height * target_ratio
    else:
        # Frame is too tall, reduce height  
        new_height = new_width / target_ratio
    
    # Calculate new corners centered on the original position
    half_width = new_width / 2
    half_height = new_height / 2
    
    optimized_coords = [
        (int(center_x - half_width), int(center_y - half_height)),    # Top-left
        (int(center_x + half_width), int(center_y - half_height)),    # Top-right
        (int(center_x + half_width), int(center_y + half_height)),    # Bottom-right
        (int(center_x - half_width), int(center_y + half_height))     # Bottom-left
    ]
    
    logger.info(f"✅ Optimized coordinates: {optimized_coords}")
    logger.info(f"📐 New dimensions: {int(new_width)} x {int(new_height)}")
    logger.info(f"📏 New aspect ratio: {new_width/new_height:.3f}")
    
    return optimized_coords


def create_alternative_coordinates(analysis):
    """Create alternative coordinate sets for testing."""
    logger.info("🔄 Creating Alternative Coordinate Sets")
    
    current = analysis['current_coords']
    
    # Alternative 1: Slightly smaller frame (more padding)
    padding = 20
    alt1_coords = [
        (current[0][0] + padding, current[0][1] + padding),
        (current[1][0] - padding, current[1][1] + padding),
        (current[2][0] - padding, current[2][1] - padding),
        (current[3][0] + padding, current[3][1] - padding)
    ]
    
    # Alternative 2: Vertically centered adjustment
    vertical_shift = -30  # Move up slightly
    alt2_coords = [
        (current[0][0], current[0][1] + vertical_shift),
        (current[1][0], current[1][1] + vertical_shift),
        (current[2][0], current[2][1] + vertical_shift),
        (current[3][0], current[3][1] + vertical_shift)
    ]
    
    # Alternative 3: Proportional scaling
    scale_factor = 0.95
    center_x = (current[0][0] + current[1][0]) / 2
    center_y = (current[0][1] + current[2][1]) / 2
    
    alt3_coords = []
    for x, y in current:
        new_x = center_x + (x - center_x) * scale_factor
        new_y = center_y + (y - center_y) * scale_factor
        alt3_coords.append((int(new_x), int(new_y)))
    
    return {
        'smaller_frame': alt1_coords,
        'vertical_adjusted': alt2_coords,
        'proportional_scaled': alt3_coords
    }


def generate_fixed_mockups():
    """Generate multiple fixed versions of Template 1 mockup."""
    logger.info("🎨 Generating Fixed Template 1 Mockups")
    logger.info("=" * 60)
    
    # Design file
    design_file = "assets/mockups/posters/Designs for Mockups/24x36 TEMPLATE.png"
    template_file = "1.jpg"
    
    if not Path(design_file).exists():
        logger.error(f"❌ Design file not found: {design_file}")
        return []
    
    # Analyze current setup
    analysis = analyze_current_coordinates()
    
    # Create coordinate variations
    optimized_coords = create_optimized_coordinates(analysis)
    alternative_coords = create_alternative_coordinates(analysis)
    
    # Initialize generator
    generator = PerspectiveMockupGenerator()
    
    results = []
    
    # Test different coordinate sets
    coordinate_tests = {
        'OPTIMIZED': optimized_coords,
        'SMALLER_FRAME': alternative_coords['smaller_frame'],
        'VERTICAL_ADJUSTED': alternative_coords['vertical_adjusted'],
        'PROPORTIONAL_SCALED': alternative_coords['proportional_scaled'],
        'ORIGINAL_VIA': analysis['current_coords']
    }
    
    for test_name, coords in coordinate_tests.items():
        logger.info(f"\n🖼️ Testing {test_name} coordinates: {coords}")
        
        result = generator.generate_perspective_mockup(
            design_path=design_file,
            template_name=template_file,
            custom_corners=coords
        )
        
        if result['success']:
            # Rename with descriptive name
            original_path = Path(result['mockup_path'])
            new_name = f"24x36_TEMPLATE_FIXED_{test_name}_1.png"
            new_path = original_path.parent / new_name
            original_path.rename(new_path)
            
            logger.info(f"  ✅ Generated: {new_name}")
            logger.info(f"  📐 Coordinates used: {coords}")
            
            results.append({
                'test_name': test_name,
                'path': str(new_path),
                'coordinates': coords,
                'success': True
            })
        else:
            logger.error(f"  ❌ Failed {test_name}: {result['error']}")
            results.append({
                'test_name': test_name,
                'success': False,
                'error': result['error']
            })
    
    return results


def main():
    """Run Template 1 mockup fixes."""
    logger.info("🎯 Template 1 Mockup Fix - Multiple Coordinate Tests")
    logger.info("=" * 70)
    
    # Check OpenCV availability
    try:
        import cv2
        logger.info(f"✅ OpenCV available: {cv2.__version__}")
    except ImportError:
        logger.error("❌ OpenCV required for perspective transformation")
        return
    
    # Generate fixed mockups
    results = generate_fixed_mockups()
    
    if not results:
        logger.error("❌ No fixed mockups were generated")
        return
    
    # Summary
    successful_fixes = [r for r in results if r['success']]
    failed_fixes = [r for r in results if not r['success']]
    
    logger.info(f"\n🎉 Template 1 Fix Testing Complete!")
    logger.info(f"📊 Generated {len(successful_fixes)}/{len(results)} fixed versions")
    
    if successful_fixes:
        logger.info(f"\n📁 Generated Fixed Mockups:")
        for result in successful_fixes:
            logger.info(f"  ✅ {result['test_name']}: {Path(result['path']).name}")
    
    if failed_fixes:
        logger.info(f"\n⚠️ Failed Fixes:")
        for result in failed_fixes:
            logger.info(f"  ❌ {result['test_name']}: {result.get('error', 'Unknown error')}")
    
    logger.info(f"\n🎯 Recommended Next Steps:")
    logger.info(f"  1. Review all generated fixed versions")
    logger.info(f"  2. Compare with original mockup")
    logger.info(f"  3. Select the best coordinate set")
    logger.info(f"  4. Update VIA annotations if needed")
    
    logger.info(f"\n📁 Check 'output' directory for fixed mockups!")


if __name__ == "__main__":
    main()
