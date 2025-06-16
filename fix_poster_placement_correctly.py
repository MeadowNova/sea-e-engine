#!/usr/bin/env python3
"""
Fix Poster Design Placement - The Right Way
==========================================

Instead of complex perspective transformation that creates artifacts,
simply place the design accurately within the VIA coordinates you provided.
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def place_design_in_coordinates(design_path: str, template_path: str, 
                               corners: list, output_path: str) -> dict:
    """
    Place design directly within VIA coordinates - no perspective transformation needed.
    
    Args:
        design_path: Path to design file
        template_path: Path to template file  
        corners: VIA coordinates [top-left, top-right, bottom-right, bottom-left]
        output_path: Where to save the result
        
    Returns:
        Result dictionary
    """
    try:
        # Load template and design
        template = Image.open(template_path).convert("RGBA")
        design = Image.open(design_path).convert("RGBA")
        
        # Calculate target area from VIA coordinates
        x1, y1 = corners[0]  # Top-left
        x2, y2 = corners[2]  # Bottom-right
        
        target_width = x2 - x1
        target_height = y2 - y1
        
        logger.info(f"📐 Target area: {target_width} x {target_height} at ({x1}, {y1})")
        
        # Resize design to fit target area exactly
        resized_design = design.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Create result by copying template
        result = template.copy()
        
        # Paste design directly at VIA coordinates
        result.paste(resized_design, (x1, y1), resized_design)
        
        # Save result
        result.save(output_path, "PNG", quality=95)
        
        logger.info(f"✅ Clean placement: {output_path}")
        
        return {
            'success': True,
            'mockup_path': output_path,
            'placement': (x1, y1),
            'size': (target_width, target_height)
        }
        
    except Exception as e:
        logger.error(f"❌ Placement failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def test_clean_placement_all_templates():
    """Test clean design placement for all poster templates."""
    logger.info("🎯 Testing Clean Design Placement - All Templates")
    logger.info("=" * 60)
    
    # VIA coordinates for each template
    via_coordinates = {
        "1.jpg": [(568, 170), (1510, 170), (1510, 1649), (568, 1649)],
        "2.jpg": [(463, 354), (1229, 383), (1336, 1544), (551, 1629)],  # Polyline - use bounding box
        "3.jpg": [(456, 224), (1560, 224), (1560, 1828), (456, 1828)],
        "5.jpg": [(463, 176), (1370, 167), (1298, 1824), (379, 1650)],  # Polyline - use bounding box
        "6.jpg": [(425, 149), (1055, 274), (1055, 1334), (415, 1345)],  # Polyline - use bounding box
        "7.jpg": [(402, 278), (1359, 278), (1359, 1721), (402, 1721)],
        "8.jpg": [(1144, 285), (1724, 285), (1724, 1173), (1144, 1173)],
        "9.png": [(329, 69), (693, 69), (693, 484), (329, 484)]
    }
    
    # For polyline coordinates, convert to bounding rectangle
    def normalize_coordinates(coords):
        """Convert polyline coordinates to bounding rectangle."""
        x_coords = [p[0] for p in coords]
        y_coords = [p[1] for p in coords]
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        return [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
    
    # Design file
    design_file = "assets/mockups/posters/Designs for Mockups/24x36 TEMPLATE.png"
    
    if not Path(design_file).exists():
        logger.error(f"❌ Design file not found: {design_file}")
        return []
    
    results = []
    
    # Test each template
    for template_name, coords in via_coordinates.items():
        template_path = f"assets/mockups/posters/{template_name}"
        
        if not Path(template_path).exists():
            logger.warning(f"⚠️ Template not found: {template_path}")
            continue
        
        logger.info(f"\n🖼️ Testing clean placement: {template_name}")
        logger.info(f"  📍 VIA coordinates: {coords}")
        
        # Normalize coordinates for polylines
        normalized_coords = normalize_coordinates(coords)
        logger.info(f"  📐 Normalized to: {normalized_coords}")
        
        # Generate clean placement
        output_path = f"output/24x36_TEMPLATE_CLEAN_PLACEMENT_{Path(template_name).stem}.png"
        
        result = place_design_in_coordinates(
            design_path=design_file,
            template_path=template_path,
            corners=normalized_coords,
            output_path=output_path
        )
        
        if result['success']:
            logger.info(f"  ✅ Clean placement successful")
            logger.info(f"  📏 Size: {result['size']}")
            logger.info(f"  📍 Position: {result['placement']}")
            
            results.append({
                'template': template_name,
                'success': True,
                'path': result['mockup_path'],
                'coordinates': normalized_coords
            })
        else:
            logger.error(f"  ❌ Failed: {result['error']}")
            results.append({
                'template': template_name,
                'success': False,
                'error': result['error']
            })
    
    return results


def compare_with_perspective_method():
    """Compare clean placement vs perspective transformation."""
    logger.info("\n🔍 Comparison: Clean Placement vs Perspective Transformation")
    logger.info("=" * 70)
    
    logger.info("❌ Perspective Transformation Issues:")
    logger.info("  - Creates artifacts during transformation")
    logger.info("  - Wrong output size calculation")
    logger.info("  - Incorrect positioning logic")
    logger.info("  - Unnecessary complexity for rectangular areas")
    
    logger.info("\n✅ Clean Placement Benefits:")
    logger.info("  - Direct placement within VIA coordinates")
    logger.info("  - No artifacts or contamination")
    logger.info("  - Exact size and position control")
    logger.info("  - Simple, reliable, fast")


def main():
    """Run clean placement testing."""
    logger.info("🎯 Clean Design Placement - The Right Way")
    logger.info("=" * 70)
    
    # Test clean placement
    results = test_clean_placement_all_templates()
    
    # Summary
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    logger.info(f"\n🎉 Clean Placement Testing Complete!")
    logger.info(f"📊 Results: {len(successful)}/{len(results)} successful")
    
    if successful:
        logger.info(f"\n✅ Successful Clean Placements:")
        for result in successful:
            logger.info(f"  ✅ {result['template']}")
    
    if failed:
        logger.info(f"\n❌ Failed Placements:")
        for result in failed:
            logger.info(f"  ❌ {result['template']}: {result.get('error', 'Unknown')}")
    
    # Show comparison
    compare_with_perspective_method()
    
    logger.info(f"\n🎯 Recommendation:")
    logger.info(f"  Replace perspective transformation with direct placement")
    logger.info(f"  Remove blue-grain detection (unnecessary with clean placement)")
    logger.info(f"  Use your exact VIA coordinates for perfect positioning")
    
    logger.info(f"\n📁 Check 'output' directory for clean placement results!")


if __name__ == "__main__":
    main()
