#!/usr/bin/env python3
"""
Design File Optimizer for Printify Uploads
==========================================

Optimizes design files for reliable Printify API uploads while maintaining print quality.
Reduces file size through smart compression and resizing.

Usage:
    python tools/optimize_design_for_upload.py <input_file> [output_file]
    
Example:
    python tools/optimize_design_for_upload.py assets/designs_printify/large_design.png
    python tools/optimize_design_for_upload.py input.png optimized_output.png
"""

import sys
import os
from pathlib import Path
from PIL import Image
import argparse

def optimize_design_file(input_path: str, output_path: str = None, max_size_mb: float = 8.0) -> bool:
    """
    Optimize a design file for Printify upload.
    
    Args:
        input_path: Path to input design file
        output_path: Path for optimized output (optional)
        max_size_mb: Target maximum file size in MB
        
    Returns:
        bool: True if optimization successful
    """
    try:
        if not os.path.exists(input_path):
            print(f"❌ Input file not found: {input_path}")
            return False
        
        # Generate output path if not provided
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_optimized{input_file.suffix}")
        
        print(f"🔧 Optimizing: {input_path}")
        print(f"📁 Output: {output_path}")
        
        with Image.open(input_path) as img:
            original_size_mb = os.path.getsize(input_path) / (1024 * 1024)
            print(f"📊 Original: {img.size}, Mode: {img.mode}, Size: {original_size_mb:.1f}MB")
            
            # Ensure RGBA for transparency support
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
                print("🔄 Converted to RGBA for transparency support")
            
            # Smart resizing based on print quality requirements
            max_dimension = 4000  # Good balance of print quality vs file size
            if max(img.size) > max_dimension:
                ratio = max_dimension / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"📏 Resized to: {new_size} (maintaining aspect ratio)")
            
            # Try different compression levels to hit target size
            compression_levels = [6, 7, 8, 9]  # Progressive compression
            
            for compress_level in compression_levels:
                # Test compression level
                test_buffer = io.BytesIO()
                img.save(test_buffer, format='PNG', optimize=True, compress_level=compress_level)
                test_size_mb = len(test_buffer.getvalue()) / (1024 * 1024)
                
                if test_size_mb <= max_size_mb:
                    # Save with this compression level
                    img.save(output_path, format='PNG', optimize=True, compress_level=compress_level)
                    
                    final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    reduction_percent = ((original_size_mb - final_size_mb) / original_size_mb) * 100
                    
                    print(f"✅ Optimized successfully!")
                    print(f"📉 Size: {original_size_mb:.1f}MB → {final_size_mb:.1f}MB ({reduction_percent:.1f}% reduction)")
                    print(f"🗜️  Compression level: {compress_level}")
                    print(f"🎯 Target achieved: {final_size_mb:.1f}MB ≤ {max_size_mb}MB")
                    
                    return True
            
            # If we get here, even max compression didn't work
            print(f"⚠️  Warning: Could not reduce file below {max_size_mb}MB target")
            print(f"💡 Consider manually reducing image dimensions or using JPEG format")
            
            # Save with maximum compression anyway
            img.save(output_path, format='PNG', optimize=True, compress_level=9)
            final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"📁 Saved with max compression: {final_size_mb:.1f}MB")
            
            return True
            
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Optimize design files for Printify uploads")
    parser.add_argument("input_file", help="Input design file path")
    parser.add_argument("output_file", nargs="?", help="Output file path (optional)")
    parser.add_argument("--max-size", type=float, default=8.0, 
                       help="Target maximum file size in MB (default: 8.0)")
    
    args = parser.parse_args()
    
    print("🎨 Design File Optimizer for Printify Uploads")
    print("=" * 50)
    
    success = optimize_design_file(args.input_file, args.output_file, args.max_size)
    
    if success:
        print("\n🚀 Ready for Printify upload!")
        print("💡 Tip: Test upload with optimized file first")
    else:
        print("\n❌ Optimization failed")
        sys.exit(1)

if __name__ == "__main__":
    import io  # Import here to avoid issues if imported as module
    main()
