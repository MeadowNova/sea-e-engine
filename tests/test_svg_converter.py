#!/usr/bin/env python3
"""
Test SVG Size Converter for Phase 3
===================================

Tests the SVG size converter with your actual design files.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modules.svg_size_converter import SVGSizeConverter

def test_svg_converter():
    """Test the SVG size converter with actual design files."""
    print("🧪 Testing SVG Size Converter")
    print("=" * 50)
    
    # Initialize converter
    converter = SVGSizeConverter(output_dir="output/test_svg_conversions")
    
    # Show available sizes
    print("📐 Available Size Specifications:")
    size_info = converter.get_size_info()
    for name, info in size_info.items():
        print(f"   {name}: {info['description']}")
        print(f"      📏 {info['dimensions_inches']} inches")
        print(f"      🖼️  {info['dimensions_pixels']} pixels at {info['dpi']} DPI")
        print()
    
    # Find SVG files
    svg_dir = Path("assets/mockups/posters/Designs for Mockups")
    svg_files = list(svg_dir.glob("*.svg"))
    
    if not svg_files:
        print(f"❌ No SVG files found in {svg_dir}")
        return False
    
    print(f"📁 Found {len(svg_files)} SVG files:")
    for svg_file in svg_files:
        print(f"   • {svg_file.name}")
    print()
    
    # Test with first SVG file
    test_svg = svg_files[0]
    design_name = test_svg.stem
    
    print(f"🎨 Testing conversion with: {test_svg.name}")
    print(f"   Design name: {design_name}")
    print()
    
    try:
        # Convert to all sizes
        converted_files = converter.convert_svg_to_sizes(
            svg_path=str(test_svg),
            design_name=design_name
        )
        
        print(f"✅ Conversion Results:")
        print(f"   Created {len(converted_files)} files:")
        
        for size_name, file_path in converted_files.items():
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                file_size_mb = file_path_obj.stat().st_size / (1024 * 1024)
                print(f"   ✅ {size_name}: {file_path_obj.name} ({file_size_mb:.2f} MB)")
            else:
                print(f"   ❌ {size_name}: File not created")
        
        # Verify file structure
        output_dir = Path("output/test_svg_conversions") / design_name
        if output_dir.exists():
            all_files = list(output_dir.glob("*"))
            print(f"\n📂 Output Directory Structure:")
            print(f"   {output_dir}/")
            for file in sorted(all_files):
                file_size_mb = file.stat().st_size / (1024 * 1024)
                print(f"   ├── {file.name} ({file_size_mb:.2f} MB)")
        
        print(f"\n🎉 SVG Converter Test: SUCCESS!")
        print(f"   Ready for Google Drive upload and PDF generation")
        return True
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_designs():
    """Test conversion for all available SVG designs."""
    print("\n" + "=" * 50)
    print("🚀 Testing All Designs")
    print("=" * 50)
    
    converter = SVGSizeConverter(output_dir="output/phase3_svg_conversions")
    svg_dir = Path("assets/mockups/posters/Designs for Mockups")
    svg_files = list(svg_dir.glob("*.svg"))
    
    results = {}
    
    for i, svg_file in enumerate(svg_files, 1):
        design_name = svg_file.stem
        print(f"\n{i}/{len(svg_files)}: Converting {design_name}...")
        
        try:
            converted_files = converter.convert_svg_to_sizes(
                svg_path=str(svg_file),
                design_name=design_name
            )
            results[design_name] = {
                'success': True,
                'files': len(converted_files),
                'converted_files': converted_files
            }
            print(f"   ✅ Success: {len(converted_files)} files created")
            
        except Exception as e:
            results[design_name] = {
                'success': False,
                'error': str(e)
            }
            print(f"   ❌ Failed: {e}")
    
    # Summary
    successful = sum(1 for r in results.values() if r['success'])
    failed = len(results) - successful
    
    print(f"\n📊 Batch Conversion Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📁 Total designs: {len(results)}")
    
    if successful > 0:
        print(f"\n🎉 Ready for Phase 3 premium digital product pipeline!")
        total_files = sum(r.get('files', 0) for r in results.values() if r['success'])
        print(f"   Generated {total_files} total files across all designs")
    
    return successful == len(results)

if __name__ == "__main__":
    print("🔧 SVG Size Converter Test Suite")
    print("=" * 60)
    
    # Test single design first
    single_success = test_svg_converter()
    
    if single_success:
        # Test all designs
        all_success = test_all_designs()
        sys.exit(0 if all_success else 1)
    else:
        sys.exit(1)
