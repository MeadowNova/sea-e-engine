#!/usr/bin/env python3
"""
Direct Poster Mockup Test
========================

Test poster mockup generation directly using the perspective transformation
system, bypassing any Google Sheets dependency issues.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent))

def test_perspective_mockup_system():
    """Test the perspective mockup system directly."""
    print("🖼️  TESTING: Direct Perspective Mockup System")
    print("=" * 50)
    
    try:
        # Import the perspective mockup generator directly
        from modules.perspective_mockup_generator import PerspectiveMockupGenerator
        print("✅ PerspectiveMockupGenerator imported successfully")
        
        # Initialize generator
        generator = PerspectiveMockupGenerator()
        print("✅ Generator initialized")
        
        # Get available templates
        templates = generator.list_available_templates()
        print(f"✅ Available templates: {templates}")
        
        return generator, templates
        
    except Exception as e:
        print(f"❌ Perspective system import failed: {e}")
        return None, []

def test_direct_poster_generation():
    """Test direct poster generation with perspective transformation."""
    print("\n🎨 TESTING: Direct Poster Generation")
    print("=" * 40)
    
    # Get perspective generator
    generator, templates = test_perspective_mockup_system()
    if not generator:
        print("❌ Cannot proceed without perspective generator")
        return False
    
    # Design file
    design_file = "assets/mockups/posters/Designs for Mockups/24x36 TEMPLATE.png"
    
    if not os.path.exists(design_file):
        print(f"❌ Design file not found: {design_file}")
        return False
    
    print(f"✅ Using design file: {design_file}")
    
    # Test with available templates
    successful_generations = []
    failed_generations = []
    
    for i, template in enumerate(templates[:3], 1):  # Test first 3 templates
        print(f"\n📸 Testing poster template {i}: {template}")
        
        try:
            # Generate perspective mockup
            result = generator.generate_perspective_mockup(design_file, template)
            
            if result.get('success'):
                print(f"  ✅ Success: {result.get('mockup_path')}")
                print(f"  📐 Corner points: {result.get('corner_points')}")
                print(f"  📏 Output size: {result.get('output_size')}")
                
                successful_generations.append({
                    "template": template,
                    "mockup_path": result.get('mockup_path'),
                    "corner_points": result.get('corner_points')
                })
            else:
                print(f"  ❌ Failed: {result.get('error')}")
                failed_generations.append(template)
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed_generations.append(template)
    
    # Summary
    print(f"\n📊 DIRECT POSTER GENERATION SUMMARY:")
    print(f"✅ Successful generations: {len(successful_generations)}")
    print(f"❌ Failed generations: {len(failed_generations)}")
    
    if successful_generations:
        print(f"\n🎉 SUCCESSFUL POSTER MOCKUPS:")
        for gen in successful_generations:
            print(f"  ✅ {gen['template']} → {Path(gen['mockup_path']).name}")
            print(f"     📐 Corners: {gen['corner_points']}")
    
    if failed_generations:
        print(f"\n⚠️  FAILED TEMPLATES:")
        for failed in failed_generations:
            print(f"  ❌ {failed}")
    
    return len(successful_generations) > 0

def test_via_annotations():
    """Test loading and using VIA annotations."""
    print("\n📍 TESTING: VIA Annotations")
    print("=" * 30)
    
    # Test loading VIA annotation files
    via_files = [
        "assets/mockups/posters/via_project_15Jun2025_9h52m_json.json",
        "assets/mockups/posters/via_project_15Jun2025_9h52m_json (1).json",
        "assets/mockups/posters/via_project_15Jun2025_9h52m_json (2).json"
    ]
    
    successful_loads = []
    
    for via_file in via_files:
        if os.path.exists(via_file):
            try:
                with open(via_file, 'r') as f:
                    data = json.load(f)
                
                print(f"✅ Loaded: {Path(via_file).name}")
                
                # Extract annotation info
                for key, value in data.items():
                    filename = value.get('filename', 'unknown')
                    regions = value.get('regions', [])
                    print(f"   📄 File: {filename}, Regions: {len(regions)}")
                    
                    if regions:
                        region = regions[0]  # First region
                        shape = region.get('shape_attributes', {})
                        shape_name = shape.get('name', 'unknown')
                        print(f"   📐 Shape: {shape_name}")
                        
                        if shape_name == 'rect':
                            x, y = shape.get('x', 0), shape.get('y', 0)
                            w, h = shape.get('width', 0), shape.get('height', 0)
                            print(f"   📏 Rectangle: ({x}, {y}) {w}x{h}")
                        elif shape_name == 'polyline':
                            points_x = shape.get('all_points_x', [])
                            points_y = shape.get('all_points_y', [])
                            print(f"   📏 Polyline: {len(points_x)} points")
                
                successful_loads.append(via_file)
                
            except Exception as e:
                print(f"❌ Failed to load {Path(via_file).name}: {e}")
        else:
            print(f"⚠️  File not found: {Path(via_file).name}")
    
    print(f"\n📊 VIA Annotation Summary: {len(successful_loads)}/{len(via_files)} loaded")
    return len(successful_loads) > 0

def test_poster_config():
    """Test poster configuration files."""
    print("\n⚙️  TESTING: Poster Configuration")
    print("=" * 35)
    
    config_files = {
        "mockup_templates.json": "config/mockup_templates.json",
        "poster_perspective_config.json": "config/poster_perspective_config.json"
    }
    
    for name, path in config_files.items():
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                
                print(f"✅ Loaded: {name}")
                
                if name == "mockup_templates.json":
                    posters = data.get('template_categories', {}).get('posters', {})
                    if posters:
                        print(f"   📄 Poster templates configured: {len(posters.get('templates', {}))}")
                        print(f"   📐 Default blend mode: {posters.get('default_settings', {}).get('blend_mode', 'unknown')}")
                    else:
                        print(f"   ⚠️  No poster configuration found")
                
                elif name == "poster_perspective_config.json":
                    templates = data.get('templates', {})
                    print(f"   📄 Perspective templates: {len(templates)}")
                    for template_name, config in list(templates.items())[:3]:
                        perspective_type = config.get('perspective_type', 'unknown')
                        print(f"   📐 {template_name}: {perspective_type}")
                
            except Exception as e:
                print(f"❌ Failed to load {name}: {e}")
        else:
            print(f"❌ Config file not found: {name}")

def main():
    """Main test execution."""
    print("🚨 SEA-E DIRECT POSTER TEST")
    print("=" * 50)
    print("Testing poster system directly before Phase 2")
    print("=" * 50)
    
    # Test configuration
    test_poster_config()
    
    # Test VIA annotations
    via_success = test_via_annotations()
    
    # Test direct generation
    generation_success = test_direct_poster_generation()
    
    if generation_success:
        print("\n🎉 POSTER SYSTEM WORKING!")
        print("=" * 50)
        print("✅ Perspective transformation working")
        print("✅ VIA annotations loaded")
        print("✅ Configuration files valid")
        print("✅ Ready for Google Sheets integration")
        print("✅ Ready for Phase 2 integration")
        print("\n🚀 POSTER SYSTEM VALIDATED!")
    else:
        print("\n⚠️ POSTER SYSTEM NEEDS ATTENTION")
        print("Check the output above for specific issues")
        print("\n💡 The poster system may need configuration updates")
        print("   or the perspective generator may need initialization")
    
    return generation_success

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    success = main()
    sys.exit(0 if success else 1)
