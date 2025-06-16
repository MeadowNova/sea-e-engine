#!/usr/bin/env python3
"""
Test Design File Naming System
==============================

Test the enhanced design file discovery and SEO optimization 
with your descriptive naming system.
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
env_path = Path(".env")
if env_path.exists():
    print("📁 Loading environment variables from .env file...")
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    print("✅ Environment variables loaded")

# Add src to path for imports
sys.path.append(str(Path("src")))

try:
    from modules.digital_download_pipeline import DigitalDownloadPipeline
    from modules.openai_seo_optimizer import OpenAISEOOptimizer
    print("✅ Successfully imported modules")
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)

def test_design_discovery():
    """Test design file discovery with your naming system."""
    print("\n🔍 Testing Design File Discovery")
    print("="*50)
    
    try:
        pipeline = DigitalDownloadPipeline(mode="validate")
        design_files = pipeline.discover_design_files()
        
        print(f"📁 Found {len(design_files)} design files in:")
        print(f"   {pipeline.mockups_dir}")
        
        for i, design in enumerate(design_files, 1):
            print(f"\n{i}. 📄 {design.filename}")
            print(f"   🏷️  Slug: {design.design_slug}")
            print(f"   📐 Dimensions: {design.width}x{design.height}")
            print(f"   📍 Path: {design.filepath}")
        
        return design_files
        
    except Exception as e:
        print(f"❌ Design discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_seo_optimization(design_files):
    """Test SEO optimization with descriptive file names."""
    if not design_files:
        print("⚠️  No design files to test")
        return
    
    print(f"\n📝 Testing SEO Optimization")
    print("="*50)
    
    try:
        optimizer = OpenAISEOOptimizer()
        
        for i, design_file in enumerate(design_files, 1):
            print(f"\n{i}. 🎨 Processing: {design_file.filename}")
            print(f"   🏷️  Design Slug: {design_file.design_slug}")
            
            # Extract context
            context = optimizer._extract_design_context(design_file.design_slug)
            print(f"   🧠 Extracted Context:")
            for part in context.split('; '):
                print(f"      • {part}")
            
            # Generate SEO content
            print(f"   🚀 Generating SEO content...")
            seo_content = optimizer.generate_seo_content(design_file.design_slug)
            
            print(f"   📋 Generated Content:")
            print(f"      Title ({len(seo_content['title'])} chars): {seo_content['title']}")
            print(f"      Tags ({len(seo_content['tags'])}): {', '.join(seo_content['tags'][:5])}...")
            print(f"      Description: {seo_content['description'][:150]}...")
            
            # Validate
            validation = optimizer.validate_seo_content(seo_content)
            all_valid = validation['all_valid']
            print(f"      Validation: {'✅ PASSED' if all_valid else '❌ FAILED'}")
            
            if not all_valid:
                failed_checks = [k for k, v in validation.items() if not v and k != 'all_valid']
                print(f"      Failed checks: {', '.join(failed_checks)}")
            
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ SEO optimization failed: {e}")
        import traceback
        traceback.print_exc()

def test_file_naming_recommendations():
    """Provide recommendations for optimal file naming."""
    print(f"\n💡 File Naming Recommendations")
    print("="*50)
    
    print(f"✅ Current naming examples (GOOD):")
    print(f"   • black_cat_in_shower_japanese_floral.png")
    print(f"   • coffee cat_barista_coffee cat lover.png") 
    print(f"   • cubist_geometric_cat.png")
    
    print(f"\n🎯 Optimal naming patterns:")
    print(f"   • [subject]_[style]_[theme]_[context].png")
    print(f"   • [color]_[animal]_[activity]_[style].png")
    print(f"   • [theme]_[subject]_[audience].png")
    
    print(f"\n📝 SEO-friendly examples:")
    print(f"   • zen_cat_meditation_minimalist_art.png")
    print(f"   • vintage_coffee_shop_cat_barista.png")
    print(f"   • boho_floral_cat_bathroom_decor.png")
    print(f"   • geometric_abstract_cat_modern_art.png")
    print(f"   • japanese_cherry_blossom_cat_zen.png")
    
    print(f"\n🔍 Keywords that boost SEO:")
    print(f"   Subjects: cat, dog, coffee, floral, nature")
    print(f"   Styles: boho, vintage, modern, minimalist, geometric")
    print(f"   Themes: zen, cozy, cute, funny, artistic")
    print(f"   Contexts: bathroom, kitchen, office, bedroom")
    print(f"   Audiences: lover, enthusiast, owner, decorator")

if __name__ == "__main__":
    print("🧪 Design File Naming System Test")
    print("="*60)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found!")
        print("   SEO testing will be skipped.")
        test_seo = False
    else:
        test_seo = True
    
    # Test design discovery
    design_files = test_design_discovery()
    
    # Test SEO optimization if API key available
    if test_seo and design_files:
        test_seo_optimization(design_files)
    
    # Show recommendations
    test_file_naming_recommendations()
    
    print(f"\n🎉 Testing Complete!")
    print(f"Your descriptive naming system is perfect for SEO optimization.")
    print(f"The more descriptive your filenames, the better the SEO content!")
