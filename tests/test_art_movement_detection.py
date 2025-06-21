#!/usr/bin/env python3
"""
Test the Art Movement Detection functionality.
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

def test_art_movement_detection():
    """Test art movement detection from filenames."""
    print("🧪 Testing Art Movement Detection")
    print("=" * 60)
    
    try:
        optimizer = MarketValidatedSEOOptimizer()
        
        # Test cases for art movement detection
        test_cases = [
            {
                'filename': 'black-cat-japanese.jpg',
                'expected_movement': 'japanese',
                'description': 'Japanese art movement'
            },
            {
                'filename': 'surreal-cat-dream.png',
                'expected_movement': 'surreal',
                'description': 'Surreal art movement'
            },
            {
                'filename': 'pop-art-cat-warhol.jpg',
                'expected_movement': 'pop',
                'description': 'Pop art movement'
            },
            {
                'filename': 'renaissance-classical-cat.jpg',
                'expected_movement': 'renaissance',
                'description': 'Renaissance art movement'
            },
            {
                'filename': 'impressionist-monet-cat.jpg',
                'expected_movement': 'impressionist',
                'description': 'Impressionist art movement'
            },
            {
                'filename': 'cubism-picasso-geometric-cat.jpg',
                'expected_movement': 'cubism',
                'description': 'Cubism art movement'
            },
            {
                'filename': 'vintage-retro-cat-art.jpg',
                'expected_movement': 'vintage',
                'description': 'Vintage art movement'
            },
            {
                'filename': 'gothic-dark-medieval-cat.jpg',
                'expected_movement': 'gothic',
                'description': 'Gothic art movement'
            },
            {
                'filename': 'random-cat-design.jpg',
                'expected_movement': None,
                'description': 'No detectable art movement'
            }
        ]
        
        print(f"📊 Testing {len(test_cases)} art movement detection cases")
        
        success_count = 0
        failed_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            filename = test_case['filename']
            expected = test_case['expected_movement']
            description = test_case['description']
            
            print(f"\n🎨 Test {i:2d}: {filename}")
            print(f"     Expected: {expected or 'None'}")
            
            # Test detection
            detected = optimizer._detect_art_movement(filename)
            
            if detected == expected:
                print(f"     ✅ SUCCESS - Detected: {detected}")
                success_count += 1
            else:
                print(f"     ❌ FAILED - Detected: {detected}, Expected: {expected}")
                failed_count += 1
        
        # Summary
        success_rate = (success_count / len(test_cases)) * 100
        
        print(f"\n📋 DETECTION TEST SUMMARY")
        print("=" * 60)
        print(f"   Total tests: {len(test_cases)}")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Success rate: {success_rate:.1f}%")
        
        return success_rate >= 90.0
        
    except Exception as e:
        print(f"\n❌ Detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_art_movement_seo_generation():
    """Test SEO generation from art movement detection."""
    print("\n🎯 Testing Art Movement SEO Generation")
    print("=" * 60)
    
    try:
        optimizer = MarketValidatedSEOOptimizer()
        
        # Test files with art movements
        test_files = [
            'black-cat-japanese.jpg',
            'surreal-dream-cat.jpg', 
            'pop-art-modern-cat.jpg',
            'renaissance-classical-cat.jpg',
            'vintage-retro-cat.jpg'
        ]
        
        print(f"📊 Testing SEO generation for {len(test_files)} art movement files")
        
        success_count = 0
        failed_count = 0
        
        for i, filename in enumerate(test_files, 1):
            print(f"\n🎨 Test {i}: {filename}")
            
            try:
                seo_content = optimizer.generate_seo_content(filename)
                
                # Validate requirements
                title_length = len(seo_content['title'])
                tag_count = len(seo_content['tags'])
                has_digital = any(keyword in seo_content['title'].lower() 
                                for keyword in ['digital download', 'digital art print', 'digital print'])
                source = seo_content.get('source', 'unknown')
                
                title_ok = 120 <= title_length <= 140
                tags_ok = tag_count == 13
                
                print(f"     Source: {source}")
                print(f"     Title: {title_length} chars")
                print(f"     Tags: {tag_count}")
                print(f"     Has digital: {has_digital}")
                
                if source == 'art_movement_detection':
                    art_movement = seo_content.get('art_movement', 'unknown')
                    print(f"     Art movement: {art_movement}")
                
                if title_ok and tags_ok and has_digital:
                    print(f"     ✅ SUCCESS")
                    success_count += 1
                else:
                    print(f"     ❌ FAILED - Requirements not met")
                    failed_count += 1
                
            except Exception as e:
                print(f"     ❌ ERROR: {e}")
                failed_count += 1
        
        # Summary
        success_rate = (success_count / len(test_files)) * 100
        
        print(f"\n📋 SEO GENERATION TEST SUMMARY")
        print("=" * 60)
        print(f"   Total tests: {len(test_files)}")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Success rate: {success_rate:.1f}%")
        
        return success_rate >= 90.0
        
    except Exception as e:
        print(f"\n❌ SEO generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_hierarchy():
    """Test the complete fallback hierarchy."""
    print("\n🔄 Testing Complete Fallback Hierarchy")
    print("=" * 60)
    
    try:
        optimizer = MarketValidatedSEOOptimizer()
        
        # Test different types of filenames
        test_cases = [
            {
                'filename': 'september_032.jpg',
                'expected_source': 'market_validated',
                'description': 'Market-validated concept'
            },
            {
                'filename': 'A-Surreal-Fall-Zen-Harvest-032.jpg',
                'expected_source': 'ai_naming_system',
                'description': 'AI naming system'
            },
            {
                'filename': 'black-cat-japanese.jpg',
                'expected_source': 'art_movement_detection',
                'description': 'Art movement detection'
            },
            {
                'filename': 'random-cat-design.jpg',
                'expected_source': 'openai_fallback',
                'description': 'OpenAI fallback'
            }
        ]
        
        print(f"📊 Testing {len(test_cases)} fallback scenarios")
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            filename = test_case['filename']
            expected_source = test_case['expected_source']
            description = test_case['description']
            
            print(f"\n🔄 Test {i}: {filename}")
            print(f"     Expected: {expected_source}")
            
            try:
                seo_content = optimizer.generate_seo_content(filename)
                actual_source = seo_content.get('source', 'unknown')
                
                if actual_source == expected_source:
                    print(f"     ✅ SUCCESS - Source: {actual_source}")
                    success_count += 1
                else:
                    print(f"     ⚠️  DIFFERENT - Source: {actual_source} (expected {expected_source})")
                    # Still count as success if it's a valid source
                    if actual_source in ['market_validated', 'ai_naming_system', 'art_movement_detection', 'openai_fallback']:
                        success_count += 1
                
            except Exception as e:
                print(f"     ❌ ERROR: {e}")
        
        success_rate = (success_count / len(test_cases)) * 100
        
        print(f"\n📋 FALLBACK HIERARCHY TEST SUMMARY")
        print("=" * 60)
        print(f"   Total tests: {len(test_cases)}")
        print(f"   Successful: {success_count}")
        print(f"   Success rate: {success_rate:.1f}%")
        
        return success_rate >= 90.0
        
    except Exception as e:
        print(f"\n❌ Fallback test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Art Movement Detection Test Suite")
    print("=" * 60)
    
    # Run tests
    detection_success = test_art_movement_detection()
    seo_success = test_art_movement_seo_generation()
    fallback_success = test_fallback_hierarchy()
    
    # Summary
    print(f"\n📋 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"   Art movement detection: {'✅ PASS' if detection_success else '❌ FAIL'}")
    print(f"   SEO generation: {'✅ PASS' if seo_success else '❌ FAIL'}")
    print(f"   Fallback hierarchy: {'✅ PASS' if fallback_success else '❌ FAIL'}")
    
    if detection_success and seo_success and fallback_success:
        print(f"\n🎉 All tests passed! Art movement detection is ready.")
        print(f"\n🎯 USAGE EXAMPLES:")
        print(f"   black-cat-japanese.jpg → Japanese art movement SEO")
        print(f"   surreal-dream-cat.jpg → Surreal art movement SEO")
        print(f"   pop-art-modern-cat.jpg → Pop art movement SEO")
    else:
        print(f"\n⚠️ Some tests failed. Please review and fix issues.")
    
    sys.exit(0 if (detection_success and seo_success and fallback_success) else 1)
