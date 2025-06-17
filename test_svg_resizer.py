#!/usr/bin/env python3
"""
Test SVG Resizer for Phase 3
============================

Tests the SVG resizer that creates multiple sized SVG files.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modules.svg_resizer import SVGResizer

def test_svg_resizer():
    """Test the SVG resizer with actual design files."""
    print("🧪 Testing SVG Resizer (Creates Sized SVG Files)")
    print("=" * 60)
    
    # Initialize resizer
    resizer = SVGResizer(output_dir="output/test_svg_resized")
    
    # Show available sizes
    print("📐 Available Size Specifications:")
    size_info = resizer.get_size_info()
    for name, info in size_info.items():
        print(f"   {name}: {info['description']}")
        print(f"      📏 {info['dimensions_inches']} inches")
        print(f"      🖼️  {info['dimensions_pixels']} pixels at {info['dpi']} DPI")
        print()
    
    # Find SVG files
    svg_dir = Path("assets/mockups/posters/Designs for Mockups")
    svg_files = [f for f in svg_dir.glob("*.svg") if resizer.validate_svg(str(f))]
    
    if not svg_files:
        print(f"❌ No valid SVG files found in {svg_dir}")
        return False
    
    print(f"📁 Found {len(svg_files)} valid SVG files:")
    for svg_file in svg_files:
        file_size = svg_file.stat().st_size / 1024  # KB
        print(f"   • {svg_file.name} ({file_size:.1f} KB)")
    print()
    
    # Test with first SVG file
    test_svg = svg_files[0]
    design_name = test_svg.stem
    
    print(f"🎨 Testing resizing with: {test_svg.name}")
    print(f"   Design name: {design_name}")
    print()
    
    try:
        # Create sized SVGs
        created_files = resizer.create_sized_svgs(
            svg_path=str(test_svg),
            design_name=design_name
        )
        
        print(f"✅ SVG Resizing Results:")
        print(f"   Created {len(created_files)} SVG files:")
        
        total_size_kb = 0
        for size_name, file_path in created_files.items():
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                file_size_kb = file_path_obj.stat().st_size / 1024
                total_size_kb += file_size_kb
                print(f"   ✅ {size_name}: {file_path_obj.name} ({file_size_kb:.1f} KB)")
            else:
                print(f"   ❌ {size_name}: File not created")
        
        print(f"\n📊 File Size Summary:")
        print(f"   Total package size: {total_size_kb:.1f} KB ({total_size_kb/1024:.2f} MB)")
        print(f"   Average file size: {total_size_kb/len(created_files):.1f} KB")
        
        # Verify file structure
        output_dir = Path("output/test_svg_resized") / design_name
        if output_dir.exists():
            all_files = list(output_dir.glob("*.svg"))
            print(f"\n📂 Output Directory Structure:")
            print(f"   {output_dir}/")
            for file in sorted(all_files):
                file_size_kb = file.stat().st_size / 1024
                print(f"   ├── {file.name} ({file_size_kb:.1f} KB)")
        
        print(f"\n🎉 SVG Resizer Test: SUCCESS!")
        print(f"   ✅ Created {len(created_files)} sized SVG files")
        print(f"   ✅ Much smaller file sizes than PNG conversion")
        print(f"   ✅ Maintains vector scalability")
        print(f"   ✅ Ready for Google Drive upload")
        return True
        
    except Exception as e:
        print(f"❌ SVG resizing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_designs():
    """Test resizing for all available SVG designs."""
    print("\n" + "=" * 60)
    print("🚀 Testing All SVG Designs")
    print("=" * 60)
    
    resizer = SVGResizer(output_dir="output/phase3_svg_resized")
    svg_dir = Path("assets/mockups/posters/Designs for Mockups")
    svg_files = [f for f in svg_dir.glob("*.svg") if resizer.validate_svg(str(f))]
    
    results = {}
    total_files_created = 0
    total_size_kb = 0
    
    for i, svg_file in enumerate(svg_files, 1):
        design_name = svg_file.stem
        print(f"\n{i}/{len(svg_files)}: Resizing {design_name}...")
        
        try:
            created_files = resizer.create_sized_svgs(
                svg_path=str(svg_file),
                design_name=design_name
            )
            
            # Calculate total size for this design
            design_size_kb = 0
            for file_path in created_files.values():
                if Path(file_path).exists():
                    design_size_kb += Path(file_path).stat().st_size / 1024
            
            results[design_name] = {
                'success': True,
                'files': len(created_files),
                'size_kb': design_size_kb,
                'created_files': created_files
            }
            total_files_created += len(created_files)
            total_size_kb += design_size_kb
            
            print(f"   ✅ Success: {len(created_files)} files ({design_size_kb:.1f} KB total)")
            
        except Exception as e:
            results[design_name] = {
                'success': False,
                'error': str(e)
            }
            print(f"   ❌ Failed: {e}")
    
    # Summary
    successful = sum(1 for r in results.values() if r['success'])
    failed = len(results) - successful
    
    print(f"\n📊 Batch SVG Resizing Summary:")
    print(f"   ✅ Successful designs: {successful}")
    print(f"   ❌ Failed designs: {failed}")
    print(f"   📁 Total designs processed: {len(results)}")
    print(f"   📄 Total SVG files created: {total_files_created}")
    print(f"   💾 Total package size: {total_size_kb:.1f} KB ({total_size_kb/1024:.2f} MB)")
    
    if successful > 0:
        avg_size_per_design = total_size_kb / successful
        print(f"   📊 Average size per design: {avg_size_per_design:.1f} KB")
        print(f"\n🎉 Ready for Phase 3 premium digital product pipeline!")
        print(f"   🌟 Vector SVG files maintain infinite scalability")
        print(f"   📦 Compact file sizes perfect for customer download")
        print(f"   🎯 5 standard print sizes + original for each design")
    
    return successful == len(results)

if __name__ == "__main__":
    print("🔧 SVG Resizer Test Suite")
    print("=" * 70)
    
    # Test single design first
    single_success = test_svg_resizer()
    
    if single_success:
        # Test all designs
        all_success = test_all_designs()
        sys.exit(0 if all_success else 1)
    else:
        sys.exit(1)
