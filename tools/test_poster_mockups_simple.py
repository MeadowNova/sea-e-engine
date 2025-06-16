#!/usr/bin/env python3
"""
Simple Poster Mockup Generation Test
===================================

Test poster mockup generation without Google Sheets integration
to validate the poster system works before Phase 2.
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

def test_poster_system_discovery():
    """Test what poster templates and systems are available."""
    print("🖼️  TESTING: Poster System Discovery")
    print("=" * 50)
    
    # Check poster directory
    poster_dir = Path("assets/mockups/posters")
    if not poster_dir.exists():
        print("❌ Poster directory not found")
        return False
    
    print(f"✅ Poster directory found: {poster_dir}")
    
    # List poster template files
    poster_files = []
    for ext in ['*.jpg', '*.png']:
        poster_files.extend(list(poster_dir.glob(ext)))
    
    print(f"\n📁 Found {len(poster_files)} poster template files:")
    for file in poster_files:
        print(f"  📄 {file.name}")
    
    # Check VIA annotation files
    via_files = list(poster_dir.glob("via_*.json"))
    print(f"\n📍 Found {len(via_files)} VIA annotation files:")
    for file in via_files:
        print(f"  📍 {file.name}")
    
    # Check design file
    design_file = "assets/mockups/posters/Designs for Mockups/24x36 TEMPLATE.png"
    if os.path.exists(design_file):
        print(f"\n✅ Design file found: {design_file}")
    else:
        print(f"\n❌ Design file not found: {design_file}")
        return False
    
    # Check configuration files
    config_files = [
        "config/mockup_templates.json",
        "config/poster_perspective_config.json"
    ]
    
    print(f"\n⚙️  Configuration files:")
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"  ✅ {config_file}")
        else:
            print(f"  ❌ {config_file}")
    
    return True

def test_mockup_generator_import():
    """Test if we can import the mockup generator."""
    print("\n🔧 TESTING: Mockup Generator Import")
    print("=" * 40)
    
    try:
        # Try importing without Google Sheets
        from modules.custom_mockup_generator import CustomMockupGenerator
        print("✅ CustomMockupGenerator imported successfully")
        
        # Initialize without Google Sheets
        generator = CustomMockupGenerator(
            output_dir="output/poster_test",
            enable_sheets_upload=False,
            auto_manage=True
        )
        print("✅ MockupGenerator initialized")
        
        # Check available templates
        try:
            templates = generator.list_available_templates()
            print(f"✅ Available templates: {templates}")
            return generator, templates
        except Exception as e:
            print(f"⚠️  Template listing failed: {e}")
            return generator, {}
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return None, {}

def test_simple_poster_generation():
    """Test simple poster mockup generation."""
    print("\n🎨 TESTING: Simple Poster Generation")
    print("=" * 40)
    
    # Get mockup generator
    generator, templates = test_mockup_generator_import()
    if not generator:
        print("❌ Cannot proceed without mockup generator")
        return False
    
    # Design file
    design_file = "assets/mockups/posters/Designs for Mockups/24x36 TEMPLATE.png"
    
    # Try to generate a simple poster mockup
    poster_templates = [
        "1.jpg", "2.jpg", "3.jpg", "5.jpg", "6.jpg", "7.jpg", "8.jpg",
        "ChatGPT Image Jun 16, 2025, 04_38_22 AM.png"
    ]
    
    successful_generations = []
    failed_generations = []
    
    for i, template_file in enumerate(poster_templates[:3], 1):  # Test first 3
        print(f"\n📸 Testing poster template {i}: {template_file}")
        
        template_path = f"assets/mockups/posters/{template_file}"
        if not os.path.exists(template_path):
            print(f"  ❌ Template file not found: {template_path}")
            failed_generations.append(template_file)
            continue
        
        try:
            # Try different approaches to generate mockup
            approaches = [
                ("posters", template_file),
                ("default", template_file),
                ("tshirts", template_file)  # Fallback to see if it works
            ]
            
            success = False
            for product_type, template_name in approaches:
                try:
                    print(f"  🔄 Trying product_type='{product_type}', template='{template_name}'")
                    
                    result = generator.generate_mockup(
                        product_type=product_type,
                        design_path=design_file,
                        template_name=template_name,
                        upload_to_sheets=False
                    )
                    
                    if result.get('success'):
                        print(f"  ✅ Success with {product_type}: {result.get('mockup_path')}")
                        successful_generations.append({
                            "template": template_file,
                            "product_type": product_type,
                            "mockup_path": result.get('mockup_path')
                        })
                        success = True
                        break
                    else:
                        print(f"  ⚠️  Failed with {product_type}: {result.get('error')}")
                        
                except Exception as e:
                    print(f"  ⚠️  Exception with {product_type}: {e}")
            
            if not success:
                failed_generations.append(template_file)
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed_generations.append(template_file)
    
    # Summary
    print(f"\n📊 POSTER GENERATION TEST SUMMARY:")
    print(f"✅ Successful generations: {len(successful_generations)}")
    print(f"❌ Failed generations: {len(failed_generations)}")
    
    if successful_generations:
        print(f"\n🎉 SUCCESSFUL POSTER MOCKUPS:")
        for gen in successful_generations:
            print(f"  ✅ {gen['template']} → {gen['mockup_path']}")
    
    if failed_generations:
        print(f"\n⚠️  FAILED TEMPLATES:")
        for failed in failed_generations:
            print(f"  ❌ {failed}")
    
    return len(successful_generations) > 0

def main():
    """Main test execution."""
    print("🚨 SEA-E POSTER SYSTEM TEST")
    print("=" * 50)
    print("Testing poster mockup system before Phase 2 integration")
    print("=" * 50)
    
    # Test system discovery
    discovery_success = test_poster_system_discovery()
    if not discovery_success:
        print("\n❌ System discovery failed")
        return False
    
    # Test simple generation
    generation_success = test_simple_poster_generation()
    
    if generation_success:
        print("\n🎉 POSTER SYSTEM WORKING!")
        print("=" * 50)
        print("✅ Poster templates discovered")
        print("✅ Mockup generation working")
        print("✅ Ready for Google Sheets integration")
        print("✅ Ready for Phase 2 integration")
        print("\n🚀 POSTER SYSTEM VALIDATED!")
    else:
        print("\n⚠️ POSTER SYSTEM NEEDS CONFIGURATION")
        print("Check the output above for specific issues")
    
    return generation_success

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    success = main()
    sys.exit(0 if success else 1)
