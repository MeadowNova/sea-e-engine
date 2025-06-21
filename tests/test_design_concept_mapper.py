#!/usr/bin/env python3
"""
Test the Design Concept Mapper functionality.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.design_concept_mapper import DesignConceptMapper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_concept_mapper():
    """Test the design concept mapper functionality."""
    print("🧪 Testing Design Concept Mapper")
    print("=" * 60)
    
    try:
        # Initialize mapper
        mapper = DesignConceptMapper()
        
        # Test basic functionality
        print("\n📊 Mapper Statistics:")
        stats = mapper.get_stats()
        print(f"   Total concepts: {stats['total_concepts']}")
        print(f"   Month distribution: {stats['month_distribution']}")
        print(f"   Art movements: {list(stats['art_movement_distribution'].keys())}")
        print(f"   Score range: {stats['score_stats']['min_score']:.1f} - {stats['score_stats']['max_score']:.1f}")
        print(f"   Price range: ${stats['price_range']['min_price']} - ${stats['price_range']['max_price']}")
        
        # Test filename mapping
        print("\n🔍 Testing Filename Mapping:")
        test_files = [
            "september_032.jpg",
            "october_063.png", 
            "december_100.jpg",
            "july_001.jpg",
            "nonexistent_999.jpg"
        ]
        
        for filename in test_files:
            concept = mapper.get_concept_by_filename(filename)
            if concept:
                print(f"   ✅ {filename} → {concept['name']}")
                print(f"      Price: ${concept['optimal_price']}, Score: {concept['predictive_scores']['overall_score']}")
            else:
                print(f"   ❌ {filename} → No concept found")
        
        # Test SEO data extraction
        print("\n🎯 Testing SEO Data Extraction:")
        seo_data = mapper.get_seo_data("september_032.jpg")
        if seo_data:
            print(f"   Concept: {seo_data['concept_name']}")
            print(f"   Title: {seo_data['title']}")
            print(f"   Tags: {seo_data['tags'][:3]}... ({len(seo_data['tags'])} total)")
            print(f"   Price: ${seo_data['price']}")
            print(f"   Demographics: {seo_data['target_demographics']}")
        
        # Test validation with sample files
        print("\n✅ Testing Validation:")
        sample_files = ["september_032.jpg", "october_063.jpg", "december_100.jpg", "missing_file.jpg"]
        validation = mapper.validate_concept_coverage(sample_files)
        print(f"   Files tested: {validation['total_files']}")
        print(f"   Successfully mapped: {validation['mapped_files']}")
        print(f"   Mapping success rate: {validation['mapping_success_rate']:.1f}%")
        print(f"   Unmapped files: {validation['unmapped_files']}")
        
        # Test month filtering
        print("\n📅 Testing Month Filtering:")
        september_concepts = mapper.get_concepts_by_month("september")
        october_concepts = mapper.get_concepts_by_month("october")
        print(f"   September concepts: {len(september_concepts)}")
        print(f"   October concepts: {len(october_concepts)}")
        
        # Test high priority concepts
        print("\n🏆 Testing High Priority Concepts:")
        high_priority = mapper.get_high_priority_concepts(min_score=78.0)
        print(f"   High priority concepts (score ≥ 78): {len(high_priority)}")
        if high_priority:
            top_concept = max(high_priority, key=lambda x: x['predictive_scores']['overall_score'])
            print(f"   Top concept: {top_concept['name']} (Score: {top_concept['predictive_scores']['overall_score']})")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

def test_full_coverage():
    """Test mapping coverage for all 100 concepts."""
    print("\n🔍 Testing Full Coverage (100 Concepts)")
    print("=" * 60)
    
    try:
        mapper = DesignConceptMapper()
        
        # Generate expected filenames for all concepts
        all_concept_ids = list(mapper.id_to_concept.keys())
        expected_files = [f"{concept_id}.jpg" for concept_id in all_concept_ids]
        
        print(f"📊 Expected files for 100% coverage: {len(expected_files)}")
        
        # Test validation
        validation = mapper.validate_concept_coverage(expected_files)
        print(f"   Total concepts: {len(all_concept_ids)}")
        print(f"   Expected files: {len(expected_files)}")
        print(f"   Successfully mapped: {validation['mapped_files']}")
        print(f"   Coverage: {validation['coverage_percentage']:.1f}%")
        print(f"   Mapping success: {validation['mapping_success_rate']:.1f}%")
        
        if validation['coverage_percentage'] == 100.0:
            print("✅ Perfect coverage! All concepts can be mapped.")
        else:
            print(f"⚠️ Missing concepts: {validation['missing_concepts'][:5]}...")
        
        return validation['coverage_percentage'] == 100.0
        
    except Exception as e:
        print(f"❌ Coverage test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Design Concept Mapper Test Suite")
    print("=" * 60)
    
    # Run basic tests
    basic_success = test_concept_mapper()
    
    # Run coverage tests
    coverage_success = test_full_coverage()
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"   Basic functionality: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"   Full coverage: {'✅ PASS' if coverage_success else '❌ FAIL'}")
    
    if basic_success and coverage_success:
        print("\n🎉 All tests passed! Design Concept Mapper is ready for Phase 4.")
    else:
        print("\n⚠️ Some tests failed. Please review and fix issues.")
    
    sys.exit(0 if (basic_success and coverage_success) else 1)
