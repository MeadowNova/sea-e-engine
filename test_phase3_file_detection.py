#!/usr/bin/env python3
"""
Test Phase 3 Enhanced File Detection System
Tests the new dual PNG+SVG file detection for premium digital products.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modules.digital_download_pipeline import DigitalDownloadPipeline

def test_file_detection():
    """Test the enhanced file detection system."""
    print("🧪 Testing Phase 3 Enhanced File Detection System")
    print("=" * 60)
    
    # Initialize pipeline
    mockups_dir = Path("assets/mockups/posters/Designs for Mockups")
    
    if not mockups_dir.exists():
        print(f"❌ Mockups directory not found: {mockups_dir}")
        return False
    
    try:
        # Create pipeline instance
        pipeline = DigitalDownloadPipeline(
            mockups_directory=str(mockups_dir),
            mode="validate"
        )
        
        # Test file discovery
        print(f"📁 Scanning directory: {mockups_dir}")
        design_files = pipeline.discover_design_files()
        
        print(f"\n📊 Discovery Results:")
        print(f"   Total design files found: {len(design_files)}")
        
        # Analyze file types
        png_only = []
        png_svg_pairs = []
        
        for design_file in design_files:
            if design_file.svg_filepath:
                png_svg_pairs.append(design_file)
            else:
                png_only.append(design_file)
        
        print(f"   PNG+SVG pairs: {len(png_svg_pairs)} (premium digital products)")
        print(f"   PNG only: {len(png_only)} (standard workflow)")
        
        # Detailed breakdown
        print(f"\n📋 Detailed File Analysis:")
        
        for i, design_file in enumerate(design_files, 1):
            print(f"\n{i}. Design: {design_file.design_slug}")
            print(f"   PNG File: {design_file.filename}")
            
            if design_file.svg_filepath:
                print(f"   SVG File: {design_file.svg_filepath.name}")
                print(f"   Type: 🌟 Premium Digital Product (PNG+SVG)")
            else:
                print(f"   SVG File: None")
                print(f"   Type: 📄 Standard Workflow (PNG only)")
            
            print(f"   Dimensions: {design_file.width}x{design_file.height}")
            print(f"   Slug: {design_file.design_slug}")
        
        # Validation
        print(f"\n✅ File Detection Test Results:")
        
        expected_designs = [
            "black_cat_in_shower_japanese_floral",
            "coffee cat_barista_coffee cat lover", 
            "cubist_geometric_cat"
        ]
        
        found_designs = [df.design_slug.replace('_', ' ') for df in design_files]
        
        for expected in expected_designs:
            expected_slug = expected.replace(' ', '_')
            if any(df.design_slug == expected_slug for df in design_files):
                design_file = next(df for df in design_files if df.design_slug == expected_slug)
                if design_file.svg_filepath:
                    print(f"   ✅ {expected}: PNG+SVG pair detected")
                else:
                    print(f"   ⚠️  {expected}: PNG only (missing SVG)")
            else:
                print(f"   ❌ {expected}: Not found")
        
        # Success summary
        if len(png_svg_pairs) > 0:
            print(f"\n🎉 SUCCESS: Enhanced file detection working!")
            print(f"   Ready for Phase 3 premium digital product processing")
            print(f"   {len(png_svg_pairs)} designs will get full premium treatment")
            return True
        else:
            print(f"\n⚠️  WARNING: No PNG+SVG pairs found")
            print(f"   All designs will use standard workflow")
            return False
            
    except Exception as e:
        print(f"❌ Error testing file detection: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_file_detection()
    sys.exit(0 if success else 1)
