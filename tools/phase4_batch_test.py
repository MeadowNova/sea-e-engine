#!/usr/bin/env python3
"""
Phase 4 Batch Test for 100 Market-Validated Designs.

This script tests the Phase 4 Market-Validated SEO Engine with sample filenames
to validate 100% success rate before running the full pipeline.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.design_concept_mapper import DesignConceptMapper
from modules.market_validated_seo_optimizer import MarketValidatedSEOOptimizer
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_expected_filenames():
    """Generate expected filenames for all 100 concepts."""
    mapper = DesignConceptMapper()
    concept_ids = list(mapper.id_to_concept.keys())
    
    # Generate filenames with common extensions
    filenames = []
    for concept_id in concept_ids:
        filenames.append(f"{concept_id}.jpg")
    
    return sorted(filenames)

def test_seo_generation_batch():
    """Test SEO generation for all 100 expected filenames."""
    print("🧪 Phase 4 Batch SEO Generation Test")
    print("=" * 60)
    
    try:
        # Initialize components
        mapper = DesignConceptMapper()
        optimizer = MarketValidatedSEOOptimizer()
        
        # Generate expected filenames
        filenames = generate_expected_filenames()
        
        print(f"📊 Testing SEO generation for {len(filenames)} designs")
        print(f"   Expected 100% market-validated success rate")
        
        # Test each filename
        results = []
        success_count = 0
        failed_count = 0
        
        for i, filename in enumerate(filenames, 1):
            print(f"\n🎨 Testing {i:3d}/100: {filename}")
            
            try:
                # Generate SEO content
                seo_content = optimizer.generate_seo_content(filename)
                
                # Validate requirements
                title_length = len(seo_content['title'])
                tag_count = len(seo_content['tags'])
                has_digital = any(keyword in seo_content['title'].lower() 
                                for keyword in ['digital download', 'digital art print', 'digital print'])
                
                title_ok = 120 <= title_length <= 140
                tags_ok = tag_count == 13
                
                result = {
                    'filename': filename,
                    'source': seo_content.get('source', 'unknown'),
                    'title_length': title_length,
                    'tag_count': tag_count,
                    'title_ok': title_ok,
                    'tags_ok': tags_ok,
                    'has_digital': has_digital,
                    'success': title_ok and tags_ok and has_digital
                }
                
                results.append(result)
                
                if result['success']:
                    success_count += 1
                    print(f"     ✅ SUCCESS - Source: {result['source']}")
                    print(f"        Title: {title_length} chars, Tags: {tag_count}, Digital: {has_digital}")
                else:
                    failed_count += 1
                    print(f"     ❌ FAILED - Issues:")
                    if not title_ok:
                        print(f"        Title length: {title_length} (need 120-140)")
                    if not tags_ok:
                        print(f"        Tag count: {tag_count} (need 13)")
                    if not has_digital:
                        print(f"        Missing digital keyword")
                
            except Exception as e:
                failed_count += 1
                print(f"     ❌ ERROR: {e}")
                results.append({
                    'filename': filename,
                    'error': str(e),
                    'success': False
                })
        
        # Summary
        success_rate = (success_count / len(filenames)) * 100
        
        print(f"\n📋 BATCH TEST SUMMARY")
        print("=" * 60)
        print(f"   Total designs tested: {len(filenames)}")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Success rate: {success_rate:.1f}%")
        
        # Source breakdown
        source_counts = {}
        for result in results:
            if result.get('success'):
                source = result.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
        
        print(f"\n📊 SUCCESS BY SOURCE:")
        for source, count in source_counts.items():
            print(f"   {source}: {count} designs")
        
        # Validation requirements
        print(f"\n✅ VALIDATION RESULTS:")
        title_issues = sum(1 for r in results if not r.get('title_ok', False))
        tag_issues = sum(1 for r in results if not r.get('tags_ok', False))
        digital_issues = sum(1 for r in results if not r.get('has_digital', False))
        
        print(f"   Title length issues: {title_issues}")
        print(f"   Tag count issues: {tag_issues}")
        print(f"   Digital keyword issues: {digital_issues}")
        
        if success_rate == 100.0:
            print(f"\n🎉 PERFECT! 100% success rate achieved!")
            print(f"   Phase 4 is ready for production with your 100 designs!")
        elif success_rate >= 95.0:
            print(f"\n✅ EXCELLENT! {success_rate:.1f}% success rate")
            print(f"   Phase 4 is ready for production")
        else:
            print(f"\n⚠️  Success rate below 95%. Review failed cases.")
        
        return success_rate >= 95.0
        
    except Exception as e:
        print(f"\n❌ Batch test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_concept_coverage():
    """Test that all 100 concepts are properly covered."""
    print("\n🔍 Testing Concept Coverage")
    print("=" * 60)
    
    try:
        mapper = DesignConceptMapper()
        
        # Get all concept IDs
        all_concepts = list(mapper.id_to_concept.keys())
        expected_files = [f"{concept_id}.jpg" for concept_id in all_concepts]
        
        # Test validation
        validation = mapper.validate_concept_coverage(expected_files)
        
        print(f"   Total concepts: {len(all_concepts)}")
        print(f"   Expected files: {len(expected_files)}")
        print(f"   Coverage: {validation['coverage_percentage']:.1f}%")
        print(f"   Mapping success: {validation['mapping_success_rate']:.1f}%")
        
        if validation['coverage_percentage'] == 100.0:
            print("   ✅ Perfect coverage! All concepts mappable.")
        else:
            print(f"   ⚠️ Missing concepts: {validation['missing_concepts'][:5]}...")
        
        return validation['coverage_percentage'] == 100.0
        
    except Exception as e:
        print(f"   ❌ Coverage test failed: {e}")
        return False

def main():
    """Run the complete Phase 4 batch test suite."""
    print("🚀 PHASE 4 BATCH TEST SUITE")
    print("=" * 60)
    print("Testing Market-Validated SEO Engine with 100 designs")
    print("Expected: 100% success rate with market-validated concepts")
    
    # Run tests
    coverage_success = test_concept_coverage()
    batch_success = test_seo_generation_batch()
    
    # Final summary
    print(f"\n📋 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"   Concept coverage: {'✅ PASS' if coverage_success else '❌ FAIL'}")
    print(f"   Batch SEO generation: {'✅ PASS' if batch_success else '❌ FAIL'}")
    
    if coverage_success and batch_success:
        print(f"\n🎉 PHASE 4 READY FOR PRODUCTION!")
        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Rename your 100 design files using concept IDs")
        print(f"   2. Place them in assets/digital_downloads/mockup_files/")
        print(f"   3. Run: python phase3_pipeline.py --mode batch")
        print(f"   4. Enjoy 100% success rate with optimized SEO!")
    else:
        print(f"\n⚠️ PHASE 4 NEEDS ATTENTION")
        print(f"   Please review and fix issues before production use.")
    
    return coverage_success and batch_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
