#!/usr/bin/env python3
"""
Quick test for OpenAI SEO Optimizer
===================================

Simple test to verify OpenAI integration is working.
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
else:
    print("❌ .env file not found")

# Check for OpenAI API key
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    print(f"✅ OpenAI API key found: {openai_key[:10]}...")
else:
    print("❌ OpenAI API key not found in environment")
    sys.exit(1)

# Add src to path for imports
sys.path.append(str(Path("src")))

try:
    from modules.openai_seo_optimizer import OpenAISEOOptimizer
    print("✅ Successfully imported OpenAISEOOptimizer")
except ImportError as e:
    print(f"❌ Failed to import OpenAISEOOptimizer: {e}")
    sys.exit(1)

def test_seo_generation():
    """Test SEO content generation."""
    print("\n🚀 Testing OpenAI SEO Optimizer...")
    
    try:
        # Initialize the optimizer
        optimizer = OpenAISEOOptimizer()
        print("✅ OpenAI SEO Optimizer initialized successfully")
        
        # Test with the existing design
        design_slug = "design3_purrista_barista"
        print(f"📝 Generating SEO content for: {design_slug}")
        
        # Generate SEO content
        seo_content = optimizer.generate_seo_content(design_slug)
        
        print("\n" + "="*60)
        print("🎯 SEO CONTENT GENERATED")
        print("="*60)
        
        print(f"\n📋 TITLE ({len(seo_content['title'])} chars):")
        print(f"   {seo_content['title']}")
        
        print(f"\n🏷️  TAGS ({len(seo_content['tags'])} tags):")
        for i, tag in enumerate(seo_content['tags'], 1):
            print(f"   {i:2d}. {tag} ({len(tag)} chars)")
        
        print(f"\n📄 DESCRIPTION ({len(seo_content['description'])} chars):")
        print(f"   {seo_content['description']}")
        
        # Validate content
        validation = optimizer.validate_seo_content(seo_content)
        
        print(f"\n✅ VALIDATION RESULTS:")
        for check, result in validation.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}: {result}")
        
        if validation['all_valid']:
            print(f"\n🎉 SUCCESS! SEO content is ready for Etsy listings.")
            return True
        else:
            print(f"\n⚠️  Some validation checks failed. Review content.")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Quick OpenAI SEO Test")
    print("="*40)
    
    success = test_seo_generation()
    
    if success:
        print(f"\n🎉 OpenAI SEO Optimizer is working perfectly!")
        print(f"Ready to proceed with Phase 2 pipeline testing.")
    else:
        print(f"\n❌ OpenAI SEO Optimizer test failed.")
        print(f"Please check the error messages above.")
        sys.exit(1)
