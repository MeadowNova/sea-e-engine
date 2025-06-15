#!/usr/bin/env python3
"""
Test script to verify mockup placement fixes are working correctly.
This script generates test mockups and validates the placement accuracy.
"""

import sys
import os
from pathlib import Path
import json
from PIL import Image, ImageDraw

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.custom_mockup_generator import CustomMockupGenerator

def create_test_design(output_path: str, size: tuple = (800, 800)) -> str:
    """
    Create a test design with visible grid and center marker for placement testing.
    
    Args:
        output_path: Path to save the test design
        size: Size of the test design
        
    Returns:
        Path to created test design
    """
    # Create a test design with grid and center marker
    img = Image.new('RGBA', size, (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(img)
    
    # Draw a bright colored rectangle with border
    border_width = 10
    fill_color = (255, 100, 100, 255)  # Bright red
    border_color = (0, 0, 0, 255)  # Black border
    
    # Draw border
    draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=border_color, width=border_width)
    
    # Draw fill
    draw.rectangle([border_width, border_width, size[0]-border_width-1, size[1]-border_width-1], 
                  fill=fill_color)
    
    # Draw center crosshairs
    center_x, center_y = size[0] // 2, size[1] // 2
    line_length = 100
    line_width = 5
    
    # Horizontal line
    draw.line([center_x - line_length, center_y, center_x + line_length, center_y], 
              fill=(255, 255, 255, 255), width=line_width)
    
    # Vertical line
    draw.line([center_x, center_y - line_length, center_x, center_y + line_length], 
              fill=(255, 255, 255, 255), width=line_width)
    
    # Draw corner markers
    corner_size = 50
    corner_color = (255, 255, 0, 255)  # Yellow corners
    
    # Top-left
    draw.rectangle([border_width, border_width, border_width + corner_size, border_width + corner_size], 
                  fill=corner_color)
    
    # Top-right
    draw.rectangle([size[0] - border_width - corner_size, border_width, 
                   size[0] - border_width, border_width + corner_size], fill=corner_color)
    
    # Bottom-left
    draw.rectangle([border_width, size[1] - border_width - corner_size, 
                   border_width + corner_size, size[1] - border_width], fill=corner_color)
    
    # Bottom-right
    draw.rectangle([size[0] - border_width - corner_size, size[1] - border_width - corner_size, 
                   size[0] - border_width, size[1] - border_width], fill=corner_color)
    
    # Save the test design
    img.save(output_path, "PNG")
    print(f"✅ Created test design: {output_path}")
    
    return output_path

def test_template_coordinates():
    """Test that templates are using the correct VIA coordinates."""
    print("🔍 Testing template coordinate accuracy...")
    
    # Load the extracted coordinates
    coord_file = "config/extracted_via_coordinates.json"
    if not os.path.exists(coord_file):
        print(f"❌ Coordinate file not found: {coord_file}")
        return False
    
    with open(coord_file, 'r') as f:
        coord_data = json.load(f)
    
    # Initialize generator
    generator = CustomMockupGenerator()
    
    # Test each template
    success_count = 0
    total_count = 0
    
    for template_name, expected_data in coord_data['template_updates'].items():
        total_count += 1
        expected_area = expected_data['design_area']
        
        # Get template info from generator
        template_info = generator.get_template_info('tshirts', template_name)
        
        if 'error' in template_info:
            print(f"❌ Template '{template_name}' not found in generator")
            continue
        
        actual_area = list(template_info['design_area'])
        
        if actual_area == expected_area:
            print(f"✅ Template '{template_name}': Coordinates match VIA annotations")
            success_count += 1
        else:
            print(f"❌ Template '{template_name}': Coordinate mismatch!")
            print(f"   Expected: {expected_area}")
            print(f"   Actual:   {actual_area}")
    
    print(f"\n📊 Coordinate Test Results: {success_count}/{total_count} templates correct")
    return success_count == total_count

def test_blend_modes():
    """Test that blend modes are correctly configured."""
    print("\n🎨 Testing blend mode configurations...")
    
    generator = CustomMockupGenerator()
    
    # Expected blend modes based on our fixes
    expected_blend_modes = {
        "1": "screen",  # Black hanger - should use screen
        "3- Black": "screen",  # Black lifestyle - should use screen
        "2": "multiply",  # White flat lay - should use multiply
        "2 - Natural": "multiply",  # Natural lifestyle - should use multiply
        "5 - Athletic Heather": "multiply",
        "7 - Soft Pink": "multiply",
        "9 - Light Blue": "multiply",
        "10 - Tan": "multiply"
    }
    
    success_count = 0
    total_count = len(expected_blend_modes)
    
    for template_name, expected_blend in expected_blend_modes.items():
        template_info = generator.get_template_info('tshirts', template_name)
        
        if 'error' in template_info:
            print(f"❌ Template '{template_name}' not found")
            continue
        
        actual_blend = template_info['blend_mode']
        
        if actual_blend == expected_blend:
            print(f"✅ Template '{template_name}': Blend mode '{actual_blend}' correct")
            success_count += 1
        else:
            print(f"❌ Template '{template_name}': Blend mode mismatch!")
            print(f"   Expected: {expected_blend}")
            print(f"   Actual:   {actual_blend}")
    
    print(f"\n📊 Blend Mode Test Results: {success_count}/{total_count} templates correct")
    return success_count == total_count

def test_mockup_generation():
    """Test actual mockup generation with the fixes."""
    print("\n🖼️ Testing mockup generation with placement fixes...")
    
    # Create test design
    test_design_path = "output/test_placement_design.png"
    os.makedirs("output", exist_ok=True)
    create_test_design(test_design_path)
    
    # Initialize generator
    generator = CustomMockupGenerator()
    
    # Test key templates
    test_templates = ["1", "2 - Natural", "3- Black"]
    
    success_count = 0
    total_count = len(test_templates)
    
    for template_name in test_templates:
        print(f"\n🔧 Testing template: {template_name}")
        
        result = generator.generate_mockup(
            product_type="tshirts",
            design_path=test_design_path,
            template_name=template_name
        )
        
        if result['success']:
            print(f"✅ Generated mockup: {result['mockup_path']}")
            print(f"   Template: {result['template_used']}")
            print(f"   Position: {result['design_position']}")
            print(f"   Size: {result['output_size']}")
            success_count += 1
        else:
            print(f"❌ Failed to generate mockup: {result.get('error', 'Unknown error')}")
    
    print(f"\n📊 Generation Test Results: {success_count}/{total_count} mockups generated successfully")
    return success_count == total_count

def main():
    """Run all placement fix tests."""
    print("🚀 Starting Mockup Placement Fix Tests")
    print("=" * 50)
    
    # Change to project root directory
    os.chdir(Path(__file__).parent.parent)
    
    # Run tests
    coord_test = test_template_coordinates()
    blend_test = test_blend_modes()
    generation_test = test_mockup_generation()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    tests = [
        ("Coordinate Accuracy", coord_test),
        ("Blend Mode Configuration", blend_test),
        ("Mockup Generation", generation_test)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All placement fixes are working correctly!")
        return True
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
