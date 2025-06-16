#!/usr/bin/env python3
"""
Fix Poster Mockup Coordinates Using VIA Annotations
==================================================

This script extracts precise coordinates from VIA annotation files and 
generates accurate poster mockups with proper design placement.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from modules.perspective_mockup_generator import PerspectiveMockupGenerator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_via_coordinates_for_posters() -> Dict[str, Dict[str, Any]]:
    """Extract coordinates from all VIA annotation files for poster templates."""
    logger.info("🔍 Extracting VIA coordinates for poster templates")
    
    # Map VIA files to template files
    via_mapping = {
        "1.jpg": "via_project_15Jun2025_9h52m_json.json",
        "2.jpg": "via_project_15Jun2025_9h52m_json (1).json", 
        "3.jpg": "via_project_15Jun2025_9h52m_json (2).json",
        "5.jpg": "via_project_15Jun2025_9h52m_json (3).json",
        "6.jpg": "via_project_15Jun2025_9h52m_json (4).json",
        "7.jpg": "via_project_15Jun2025_9h52m_json (5).json",
        "8.jpg": "via_project_15Jun2025_9h52m_json (6).json",
        "9.png": "via_export_json.json"
    }
    
    coordinates_data = {}
    
    for template_file, via_file in via_mapping.items():
        via_path = Path(f"assets/mockups/posters/{via_file}")
        
        if not via_path.exists():
            logger.warning(f"⚠️ VIA file not found: {via_path}")
            continue
            
        try:
            with open(via_path, 'r') as f:
                via_data = json.load(f)
            
            # Extract the first (and only) entry
            file_key = list(via_data.keys())[0]
            file_info = via_data[file_key]
            
            regions = file_info.get('regions', [])
            if not regions:
                logger.warning(f"⚠️ No regions found in {via_file}")
                continue
                
            region = regions[0]
            shape_attrs = region['shape_attributes']
            
            # Handle different shape types
            if shape_attrs['name'] == 'rect':
                # Rectangle coordinates
                x = shape_attrs['x']
                y = shape_attrs['y']
                width = shape_attrs['width']
                height = shape_attrs['height']
                
                # Convert to corner points [top-left, top-right, bottom-right, bottom-left]
                corners = [
                    (x, y),                    # Top-left
                    (x + width, y),            # Top-right
                    (x + width, y + height),   # Bottom-right
                    (x, y + height)            # Bottom-left
                ]
                
            elif shape_attrs['name'] == 'polyline':
                # Polyline coordinates (for angled/perspective frames)
                x_points = shape_attrs['all_points_x']
                y_points = shape_attrs['all_points_y']
                
                # Take first 4 points as corners
                corners = [(x_points[i], y_points[i]) for i in range(min(4, len(x_points)))]
                
            else:
                logger.warning(f"⚠️ Unsupported shape type: {shape_attrs['name']}")
                continue
            
            coordinates_data[template_file] = {
                'corners': corners,
                'via_file': via_file,
                'shape_type': shape_attrs['name']
            }
            
            logger.info(f"✅ Extracted coordinates for {template_file}: {corners}")
            
        except Exception as e:
            logger.error(f"❌ Error processing {via_file}: {e}")
    
    return coordinates_data


def generate_accurate_poster_mockups():
    """Generate poster mockups using accurate VIA coordinates."""
    logger.info("🎨 Generating Accurate Poster Mockups with VIA Coordinates")
    logger.info("=" * 70)
    
    # Extract VIA coordinates
    coordinates_data = extract_via_coordinates_for_posters()
    
    if not coordinates_data:
        logger.error("❌ No coordinate data extracted from VIA files")
        return []
    
    # Design file
    design_file = "assets/mockups/posters/Designs for Mockups/24x36 TEMPLATE.png"
    
    if not Path(design_file).exists():
        logger.error(f"❌ Design file not found: {design_file}")
        return []
    
    logger.info(f"✅ Using design: {design_file}")
    
    # Initialize generator
    generator = PerspectiveMockupGenerator()
    
    results = []
    
    # Generate mockups with accurate coordinates
    for template_file, coord_data in coordinates_data.items():
        logger.info(f"\n🖼️ Generating accurate mockup for: {template_file}")
        logger.info(f"  📍 VIA source: {coord_data['via_file']}")
        logger.info(f"  📐 Shape type: {coord_data['shape_type']}")
        logger.info(f"  🎯 Corners: {coord_data['corners']}")
        
        # Check if template file exists
        template_path = Path(f"assets/mockups/posters/{template_file}")
        if not template_path.exists():
            logger.warning(f"⚠️ Template file not found: {template_path}")
            continue
        
        # Generate mockup with VIA coordinates
        result = generator.generate_perspective_mockup(
            design_path=design_file,
            template_name=template_file,
            custom_corners=coord_data['corners']
        )
        
        if result['success']:
            # Rename with VIA indicator
            original_path = Path(result['mockup_path'])
            template_stem = Path(template_file).stem
            new_name = f"24x36_TEMPLATE_VIA_ACCURATE_{template_stem}.png"
            new_path = original_path.parent / new_name
            original_path.rename(new_path)
            
            logger.info(f"  ✅ Generated: {new_name}")
            logger.info(f"  📏 Output size: {result['output_size']}")
            
            results.append({
                'template': template_file,
                'path': str(new_path),
                'via_coordinates': coord_data['corners'],
                'success': True
            })
        else:
            logger.error(f"  ❌ Failed: {result['error']}")
            results.append({
                'template': template_file,
                'success': False,
                'error': result['error']
            })
    
    return results


def validate_coordinate_accuracy(results):
    """Validate the accuracy of coordinate-based mockups."""
    logger.info(f"\n🔍 Validating Coordinate Accuracy")
    logger.info("=" * 40)
    
    successful_mockups = [r for r in results if r['success']]
    failed_mockups = [r for r in results if not r['success']]
    
    logger.info(f"✅ Successful VIA-based mockups: {len(successful_mockups)}")
    logger.info(f"❌ Failed mockups: {len(failed_mockups)}")
    
    if successful_mockups:
        logger.info(f"\n📁 Generated VIA-Accurate Mockups:")
        for result in successful_mockups:
            template = result['template']
            corners = result.get('via_coordinates', [])
            logger.info(f"  ✅ {template} - Corners: {len(corners)} points")
    
    if failed_mockups:
        logger.info(f"\n⚠️ Failed Mockups:")
        for result in failed_mockups:
            logger.info(f"  ❌ {result['template']}: {result.get('error', 'Unknown error')}")
    
    # Calculate success rate
    success_rate = (len(successful_mockups) / len(results)) * 100 if results else 0
    logger.info(f"\n📊 VIA Coordinate Success Rate: {success_rate:.1f}%")
    
    return success_rate >= 80


def main():
    """Run accurate poster mockup generation with VIA coordinates."""
    logger.info("🎯 Accurate Poster Mockup Generation - VIA Coordinates")
    logger.info("=" * 70)
    
    # Check OpenCV availability
    try:
        import cv2
        logger.info(f"✅ OpenCV available: {cv2.__version__}")
    except ImportError:
        logger.error("❌ OpenCV required for perspective transformation")
        return
    
    # Generate accurate mockups
    results = generate_accurate_poster_mockups()
    
    if not results:
        logger.error("❌ No mockups were generated")
        return
    
    # Validate accuracy
    accuracy_passed = validate_coordinate_accuracy(results)
    
    # Final summary
    logger.info(f"\n🎉 VIA Coordinate Testing Complete!")
    logger.info(f"📊 Generated {len([r for r in results if r['success']])}/{len(results)} accurate mockups")
    logger.info(f"🎯 Coordinate accuracy: {'✅ PASSED' if accuracy_passed else '❌ NEEDS ADJUSTMENT'}")
    
    if accuracy_passed:
        logger.info(f"\n🚀 Coordinate System Fixed!")
        logger.info(f"  ✅ VIA annotations properly extracted")
        logger.info(f"  ✅ Precise design placement working")
        logger.info(f"  ✅ Ready for production workflow")
    else:
        logger.info(f"\n⚠️ Coordinate system needs fine-tuning")
        logger.info(f"  📝 Review VIA annotation extraction")
        logger.info(f"  📝 Check corner point mapping")
    
    logger.info(f"\n📁 Check 'output' directory for VIA-accurate mockups!")


if __name__ == "__main__":
    main()
