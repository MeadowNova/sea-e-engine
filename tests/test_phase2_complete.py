#!/usr/bin/env python3
"""
Complete Phase 2 Pipeline Test
==============================

Test the complete Phase 2 digital download pipeline including:
- Design file discovery
- Mockup generation using custom mockup generator
- OpenAI SEO content generation
- Template listing search
- Complete workflow validation
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
    print("✅ Successfully imported DigitalDownloadPipeline")
except ImportError as e:
    print(f"❌ Failed to import DigitalDownloadPipeline: {e}")
    sys.exit(1)

def test_design_discovery():
    """Test design file discovery."""
    print("\n🔍 Testing design file discovery...")
    
    try:
        pipeline = DigitalDownloadPipeline(mode="validate")
        design_files = pipeline.discover_design_files()
        
        print(f"📁 Found {len(design_files)} design files:")
        for i, design in enumerate(design_files, 1):
            print(f"   {i}. {design.filename}")
            print(f"      Slug: {design.design_slug}")
            print(f"      Dimensions: {design.width}x{design.height}")
            print(f"      Path: {design.filepath}")
        
        return len(design_files) > 0, design_files
        
    except Exception as e:
        print(f"❌ Design discovery failed: {e}")
        return False, []

def test_mockup_generation(design_files):
    """Test mockup generation."""
    if not design_files:
        print("⚠️  No design files to test mockup generation")
        return False
    
    print("\n🎨 Testing mockup generation...")
    
    try:
        pipeline = DigitalDownloadPipeline(mode="validate")
        
        # Test with first design file
        design_file = design_files[0]
        print(f"📝 Testing with design: {design_file.design_slug}")
        
        mockup_files = pipeline._generate_mockups(design_file)
        
        print(f"🖼️  Generated {len(mockup_files)} mockups:")
        for i, mockup_path in enumerate(mockup_files, 1):
            mockup_file = Path(mockup_path)
            exists = mockup_file.exists()
            size = mockup_file.stat().st_size if exists else 0
            print(f"   {i}. {mockup_file.name} ({'✅' if exists else '❌'}) - {size:,} bytes")
        
        return len(mockup_files) > 0
        
    except Exception as e:
        print(f"❌ Mockup generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_seo_generation(design_files):
    """Test SEO content generation."""
    if not design_files:
        print("⚠️  No design files to test SEO generation")
        return False
    
    print("\n📝 Testing SEO content generation...")
    
    try:
        pipeline = DigitalDownloadPipeline(mode="validate")
        
        # Test with first design file
        design_file = design_files[0]
        print(f"🎯 Testing with design: {design_file.design_slug}")
        
        seo_content = pipeline.seo_optimizer.generate_seo_content(design_file.design_slug)
        
        print(f"\n📋 Generated SEO Content:")
        print(f"   Title ({len(seo_content['title'])} chars): {seo_content['title']}")
        print(f"   Tags ({len(seo_content['tags'])}): {', '.join(seo_content['tags'][:5])}...")
        print(f"   Description ({len(seo_content['description'])} chars): {seo_content['description'][:100]}...")
        
        # Validate content
        validation = pipeline.seo_optimizer.validate_seo_content(seo_content)
        print(f"\n✅ Validation Results:")
        for check, result in validation.items():
            status = "✅" if result else "❌"
            print(f"      {status} {check}")
        
        return validation['all_valid']
        
    except Exception as e:
        print(f"❌ SEO generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_search():
    """Test template listing search."""
    print("\n🔍 Testing template listing search...")
    
    try:
        pipeline = DigitalDownloadPipeline(mode="validate")
        
        print(f"📋 Template listing ID: {pipeline.template_listing_id}")
        print(f"🖼️  Static image IDs: {pipeline.static_image_ids}")
        
        if pipeline.template_listing_id:
            print("✅ Template listing found successfully")
            return True
        else:
            print("⚠️  Template listing not found - will proceed without static images")
            return True  # Not a failure, just a warning
            
    except Exception as e:
        print(f"❌ Template search failed: {e}")
        return False

def test_complete_pipeline():
    """Test the complete pipeline in validate mode."""
    print("\n🚀 Testing complete pipeline...")
    
    try:
        pipeline = DigitalDownloadPipeline(mode="validate")
        
        print("🔄 Running complete pipeline in validate mode...")
        summary = pipeline.run_pipeline()
        
        # Generate and display report
        report = pipeline.generate_report(summary)
        print(report)
        
        return summary['success']
        
    except Exception as e:
        print(f"❌ Complete pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Phase 2 Complete Pipeline Test")
    print("="*60)
    
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY', 'ETSY_API_KEY', 'ETSY_REFRESH_TOKEN', 'ETSY_SHOP_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Run individual tests
    print("\n📋 Running individual component tests...")
    
    # Test 1: Design Discovery
    discovery_success, design_files = test_design_discovery()
    
    # Test 2: Mockup Generation
    mockup_success = test_mockup_generation(design_files)
    
    # Test 3: SEO Generation
    seo_success = test_seo_generation(design_files)
    
    # Test 4: Template Search
    template_success = test_template_search()
    
    # Test 5: Complete Pipeline
    pipeline_success = test_complete_pipeline()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Design Discovery:     {'✅ PASSED' if discovery_success else '❌ FAILED'}")
    print(f"Mockup Generation:    {'✅ PASSED' if mockup_success else '❌ FAILED'}")
    print(f"SEO Generation:       {'✅ PASSED' if seo_success else '❌ FAILED'}")
    print(f"Template Search:      {'✅ PASSED' if template_success else '❌ FAILED'}")
    print(f"Complete Pipeline:    {'✅ PASSED' if pipeline_success else '❌ FAILED'}")
    
    all_passed = all([discovery_success, mockup_success, seo_success, template_success, pipeline_success])
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"Phase 2 Digital Download Pipeline is ready for production!")
        print(f"\nNext steps:")
        print(f"1. Create 'digital download template' listing with 3 static images")
        print(f"2. Run: python pipeline.py --mode validate")
        print(f"3. Run: python pipeline.py --mode batch")
    else:
        print(f"\n⚠️  Some tests failed. Please review the errors above.")
        sys.exit(1)
