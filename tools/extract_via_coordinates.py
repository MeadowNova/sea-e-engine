#!/usr/bin/env python3
"""
Extract precise design area coordinates from VIA annotation files.
This tool parses VIA JSON files and extracts the exact coordinates for mockup placement.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any

def extract_via_coordinates(via_file_path: str) -> Dict[str, Any]:
    """
    Extract coordinates from a VIA annotation file.
    
    Args:
        via_file_path: Path to VIA JSON file
        
    Returns:
        Dictionary with template info and coordinates
    """
    with open(via_file_path, 'r') as f:
        via_data = json.load(f)
    
    # VIA files have a single key with filename and size info
    file_key = list(via_data.keys())[0]
    file_info = via_data[file_key]
    
    filename = file_info['filename']
    template_name = filename.split('.')[0]  # Remove extension
    
    # Extract region coordinates
    regions = file_info.get('regions', [])
    if not regions:
        raise ValueError(f"No regions found in {via_file_path}")
    
    # Get the first (and typically only) region
    region = regions[0]
    shape_attrs = region['shape_attributes']
    
    if shape_attrs['name'] != 'rect':
        raise ValueError(f"Expected rectangle, got {shape_attrs['name']}")
    
    x = shape_attrs['x']
    y = shape_attrs['y']
    width = shape_attrs['width']
    height = shape_attrs['height']
    
    # Convert to design_area format [x1, y1, x2, y2]
    design_area = [x, y, x + width, y + height]
    
    return {
        'template_name': template_name,
        'filename': filename,
        'design_area': design_area,
        'via_coordinates': {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
    }

def process_all_via_files(mockups_dir: str) -> Dict[str, Dict[str, Any]]:
    """
    Process all VIA annotation files in the mockups directory.
    
    Args:
        mockups_dir: Path to mockups directory
        
    Returns:
        Dictionary mapping template names to coordinate data
    """
    mockups_path = Path(mockups_dir)
    via_files = list(mockups_path.glob("via_project_*.json"))
    
    coordinates_data = {}
    
    for via_file in via_files:
        try:
            coord_data = extract_via_coordinates(str(via_file))
            template_name = coord_data['template_name']
            coordinates_data[template_name] = coord_data
            print(f"✅ Extracted coordinates for template: {template_name}")
            print(f"   Design area: {coord_data['design_area']}")
        except Exception as e:
            print(f"❌ Error processing {via_file}: {e}")
    
    return coordinates_data

def generate_template_config_updates(coordinates_data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Generate template configuration updates based on extracted coordinates.
    
    Args:
        coordinates_data: Extracted coordinate data
        
    Returns:
        Dictionary with template configuration updates
    """
    template_updates = {}
    
    # Define blend modes and other settings based on analysis
    template_settings = {
        "1": {
            "name": "Black T-Shirt - Hanger",
            "blend_mode": "screen",  # Fix for dark fabric
            "color_base": "black",
            "opacity": 0.95,
            "padding_factor": 1.0  # Edge-to-edge placement
        },
        "2 - Natural": {
            "name": "Natural Beige T-Shirt - Lifestyle",
            "blend_mode": "multiply",
            "color_base": "natural",
            "opacity": 0.88,
            "padding_factor": 1.0
        },
        "2": {
            "name": "White T-Shirt - Flat Lay",
            "blend_mode": "multiply",
            "color_base": "white",
            "opacity": 0.95,
            "padding_factor": 1.0
        },
        "3- Black": {
            "name": "Black T-Shirt - Lifestyle",
            "blend_mode": "screen",
            "color_base": "black",
            "opacity": 1.0,
            "padding_factor": 1.0
        },
        "5 - Athletic Heather": {
            "name": "Athletic Heather T-Shirt",
            "blend_mode": "multiply",
            "color_base": "heather",
            "opacity": 0.9,
            "padding_factor": 1.0
        },
        "7 - Soft Pink": {
            "name": "Soft Pink T-Shirt",
            "blend_mode": "multiply",
            "color_base": "pink",
            "opacity": 0.9,
            "padding_factor": 1.0
        },
        "9 - Light Blue": {
            "name": "Light Blue T-Shirt",
            "blend_mode": "multiply",
            "color_base": "blue",
            "opacity": 0.9,
            "padding_factor": 1.0
        },
        "10 - Tan": {
            "name": "Tan T-Shirt",
            "blend_mode": "multiply",
            "color_base": "tan",
            "opacity": 0.9,
            "padding_factor": 1.0
        }
    }
    
    for template_name, coord_data in coordinates_data.items():
        if template_name in template_settings:
            config = template_settings[template_name].copy()
            config['design_area'] = coord_data['design_area']
            template_updates[template_name] = config
        else:
            # Default settings for unknown templates
            template_updates[template_name] = {
                "name": f"T-Shirt Template {template_name}",
                "design_area": coord_data['design_area'],
                "blend_mode": "multiply",
                "opacity": 0.9,
                "padding_factor": 1.0
            }
    
    return template_updates

if __name__ == "__main__":
    # Process VIA files
    mockups_dir = "assets/mockups/tshirts"
    print("🔍 Extracting coordinates from VIA annotation files...")
    
    coordinates_data = process_all_via_files(mockups_dir)
    
    if coordinates_data:
        print(f"\n📊 Successfully extracted coordinates for {len(coordinates_data)} templates:")
        
        # Generate template updates
        template_updates = generate_template_config_updates(coordinates_data)
        
        # Save results
        output_file = "config/extracted_via_coordinates.json"
        with open(output_file, 'w') as f:
            json.dump({
                'coordinates_data': coordinates_data,
                'template_updates': template_updates
            }, f, indent=2)
        
        print(f"💾 Saved coordinate data to: {output_file}")
        
        # Print summary table
        print("\n📋 Coordinate Summary:")
        print("Template Name".ljust(25) + "Design Area [x1, y1, x2, y2]")
        print("-" * 60)
        for name, data in coordinates_data.items():
            area_str = str(data['design_area'])
            print(f"{name}".ljust(25) + area_str)
    else:
        print("❌ No coordinate data extracted!")
