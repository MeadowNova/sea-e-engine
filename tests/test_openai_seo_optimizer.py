#!/usr/bin/env python3
"""
Test script for OpenAI SEO Optimizer
====================================

Tests the OpenAI SEO optimizer with the existing design file.
"""

import os
import sys
import logging
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, manually load from .env
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.openai_seo_optimizer import OpenAISEOOptimizer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_seo_optimizer():
    """Test the OpenAI SEO optimizer with a real design slug."""
    
    try:
        # Initialize the optimizer
        logger.info("🚀 Initializing OpenAI SEO Optimizer...")
        optimizer = OpenAISEOOptimizer()
        
        # Test with the existing design file
        design_slug = "design3_purrista_barista"
        
        logger.info(f"📝 Generating SEO content for: {design_slug}")
        
        # Generate SEO content
        seo_content = optimizer.generate_seo_content(design_slug)
        
        # Display results
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
            print(f"\n🎉 All validation checks passed! SEO content is ready for Etsy.")
        else:
            print(f"\n⚠️  Some validation checks failed. Review content before using.")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False

def test_batch_processing():
    """Test batch processing with multiple design slugs."""
    
    try:
        logger.info("🔄 Testing batch processing...")
        
        optimizer = OpenAISEOOptimizer()
        
        # Test with multiple design slugs
        design_slugs = [
            "design3_purrista_barista",
            "floral_boho_cat",
            "space_coffee_art"
        ]
        
        # Generate batch SEO content
        batch_results = optimizer.batch_generate_seo(design_slugs)
        
        print(f"\n📦 BATCH PROCESSING RESULTS ({len(batch_results)} designs):")
        print("="*60)
        
        for i, result in enumerate(batch_results, 1):
            print(f"\n{i}. {result['design_slug']}:")
            print(f"   Title: {result['title'][:50]}...")
            print(f"   Tags: {len(result['tags'])} tags")
            print(f"   Description: {len(result['description'])} chars")
            
            if 'error' in result:
                print(f"   ⚠️  Error: {result['error']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Batch test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 OpenAI SEO Optimizer Test Suite")
    print("="*60)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("   Please set your OpenAI API key to run tests.")
        sys.exit(1)
    
    # Run tests
    test1_passed = test_seo_optimizer()
    test2_passed = test_batch_processing()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Single SEO Generation: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Batch Processing:      {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 All tests passed! OpenAI SEO Optimizer is ready for Phase 2.")
    else:
        print(f"\n⚠️  Some tests failed. Check the logs above for details.")
        sys.exit(1)
