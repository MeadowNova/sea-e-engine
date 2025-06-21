#!/usr/bin/env python3
"""
Test the Market-Validated SEO Optimizer functionality.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.market_validated_seo_optimizer import MarketValidatedSEOOptimizer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_market_validated_seo():
    """Test the market-validated SEO optimizer."""
    print("🧪 Testing Market-Validated SEO Optimizer")
    print("=" * 60)
    
    try:
        # Initialize optimizer
        optimizer = MarketValidatedSEOOptimizer()
        
        # Test with market-validated concept
        print("\n🎯 Testing Market-Validated Concept:")
        concept_filename = "september_032.jpg"  # Harvest Surreal Cat #32
        
        seo_content = optimizer.generate_seo_content(concept_filename)
        
        print(f"   Source: {seo_content['source']}")
        print(f"   Title: {seo_content['title']}")
        print(f"   Title length: {len(seo_content['title'])} chars")
        print(f"   Tags: {len(seo_content['tags'])} tags")
        print(f"   Tags: {seo_content['tags'][:5]}...")
        print(f"   Price: ${seo_content['price']}")
        
        if 'concept_data' in seo_content:
            concept = seo_content['concept_data']
            print(f"   Concept: {concept['concept_name']}")
            print(f"   Art Movement: {concept['art_movement']}")
            print(f"   Target Month: {concept['target_month']}")
        
        # Validate title requirements
        title = seo_content['title']
        has_digital = any(keyword in title.lower() for keyword in ['digital download', 'digital art print', 'digital print'])
        title_length_ok = 120 <= len(title) <= 140
        
        print(f"   ✅ Has digital keyword: {has_digital}")
        print(f"   ✅ Title length OK (120-140): {title_length_ok}")
        print(f"   ✅ Has 13 tags: {len(seo_content['tags']) == 13}")
        
        # Test with AI naming system
        print("\n🤖 Testing AI Naming System:")
        ai_filename = "A-Surreal-Fall-Zen-Harvest-032.jpg"
        
        ai_seo_content = optimizer.generate_seo_content(ai_filename)
        
        print(f"   Source: {ai_seo_content['source']}")
        print(f"   Title: {ai_seo_content['title']}")
        print(f"   Tags: {ai_seo_content['tags'][:5]}...")
        print(f"   Price: ${ai_seo_content['price']}")
        
        if 'components' in ai_seo_content:
            components = ai_seo_content['components']
            print(f"   Parsed components: {components}")
        
        # Test with fallback (non-matching filename)
        print("\n📝 Testing OpenAI Fallback:")
        fallback_filename = "random_cat_design.jpg"
        
        fallback_seo_content = optimizer.generate_seo_content(fallback_filename)
        
        print(f"   Source: {fallback_seo_content['source']}")
        print(f"   Title: {fallback_seo_content['title']}")
        print(f"   Tags: {len(fallback_seo_content['tags'])} tags")
        
        # Test optimizer stats
        print("\n📊 Testing Optimizer Stats:")
        stats = optimizer.get_optimization_stats()
        
        print(f"   Total concepts available: {stats['total_concepts_available']}")
        print(f"   Art movement mappings: {stats['keyword_mappings']['art_movements']}")
        print(f"   Seasonal mappings: {stats['keyword_mappings']['seasonal']}")
        print(f"   Archetype mappings: {stats['keyword_mappings']['archetypes']}")
        print(f"   Theme mappings: {stats['keyword_mappings']['themes']}")
        print(f"   Fallback optimizer: {stats['fallback_optimizer']}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_processing():
    """Test batch processing with multiple designs."""
    print("\n🔄 Testing Batch Processing")
    print("=" * 60)
    
    try:
        optimizer = MarketValidatedSEOOptimizer()
        
        # Test files representing different scenarios
        test_files = [
            "september_032.jpg",  # Market-validated concept
            "october_063.jpg",    # Market-validated concept
            "A-Pop-Halloween-Trickster-Spooky-045.jpg",  # AI naming system
            "random_design.jpg"   # Fallback
        ]
        
        results = []
        
        for filename in test_files:
            print(f"\n   Processing: {filename}")
            seo_content = optimizer.generate_seo_content(filename)
            
            result = {
                'filename': filename,
                'source': seo_content['source'],
                'title_length': len(seo_content['title']),
                'tag_count': len(seo_content['tags']),
                'price': seo_content.get('price', 'N/A')  # Price may not be available for all sources
            }
            results.append(result)
            
            print(f"     Source: {result['source']}")
            print(f"     Title length: {result['title_length']} chars")
            print(f"     Tags: {result['tag_count']}")
            print(f"     Price: ${result['price']}")
        
        # Summary
        print(f"\n📋 Batch Processing Summary:")
        print(f"   Total files processed: {len(results)}")
        
        source_counts = {}
        for result in results:
            source = result['source']
            source_counts[source] = source_counts.get(source, 0) + 1
        
        for source, count in source_counts.items():
            print(f"   {source}: {count} files")
        
        # Validate all results meet requirements
        all_valid = True
        for result in results:
            if not (120 <= result['title_length'] <= 140):
                print(f"   ⚠️ Title length issue: {result['filename']}")
                all_valid = False
            if result['tag_count'] != 13:
                print(f"   ⚠️ Tag count issue: {result['filename']}")
                all_valid = False
        
        if all_valid:
            print("   ✅ All results meet requirements!")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Batch test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Market-Validated SEO Optimizer Test Suite")
    print("=" * 60)
    
    # Run basic tests
    basic_success = test_market_validated_seo()
    
    # Run batch tests
    batch_success = test_batch_processing()
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"   Basic functionality: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"   Batch processing: {'✅ PASS' if batch_success else '❌ FAIL'}")
    
    if basic_success and batch_success:
        print("\n🎉 All tests passed! Market-Validated SEO Optimizer is ready for Phase 4.")
    else:
        print("\n⚠️ Some tests failed. Please review and fix issues.")
    
    sys.exit(0 if (basic_success and batch_success) else 1)
