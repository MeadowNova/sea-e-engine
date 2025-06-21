#!/usr/bin/env python3
"""
Quick test for Art Movement Detection (no API calls).
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.market_validated_seo_optimizer import MarketValidatedSEOOptimizer
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduce log noise
logger = logging.getLogger(__name__)

def test_art_movement_detection_only():
    """Test just the art movement detection logic."""
    print("🧪 Quick Art Movement Detection Test")
    print("=" * 50)
    
    try:
        optimizer = MarketValidatedSEOOptimizer()
        
        # Test cases for art movement detection
        test_cases = [
            ('black-cat-japanese.jpg', 'japanese'),
            ('surreal-cat-dream.png', 'surreal'),
            ('pop-art-cat-warhol.jpg', 'pop'),
            ('renaissance-classical-cat.jpg', 'renaissance'),
            ('impressionist-monet-cat.jpg', 'impressionist'),
            ('cubism-picasso-geometric-cat.jpg', 'cubism'),
            ('vintage-retro-cat-art.jpg', 'vintage'),
            ('gothic-dark-medieval-cat.jpg', 'gothic'),
            ('random-cat-design.jpg', None),
        ]
        
        print(f"Testing {len(test_cases)} detection cases...")
        
        success_count = 0
        
        for filename, expected in test_cases:
            detected = optimizer._detect_art_movement(filename)
            
            if detected == expected:
                print(f"✅ {filename} → {detected}")
                success_count += 1
            else:
                print(f"❌ {filename} → {detected} (expected {expected})")
        
        success_rate = (success_count / len(test_cases)) * 100
        
        print(f"\n📋 Results: {success_count}/{len(test_cases)} ({success_rate:.1f}%)")
        
        return success_rate == 100.0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_design_element_extraction():
    """Test design element extraction."""
    print("\n🎨 Testing Design Element Extraction")
    print("=" * 50)
    
    try:
        optimizer = MarketValidatedSEOOptimizer()
        
        test_cases = [
            ('black-cat-japanese.jpg', {'colors': ['black'], 'subject': 'cat'}),
            ('red-vintage-kitten.jpg', {'colors': ['red'], 'subject': 'kitten'}),
            ('blue-modern-feline-art.jpg', {'colors': ['blue'], 'subject': 'feline'}),
        ]
        
        success_count = 0
        
        for filename, expected_partial in test_cases:
            clean_name = Path(filename).stem.lower()
            elements = optimizer._extract_design_elements(clean_name)
            
            # Check if expected elements are present
            colors_match = all(color in elements['colors'] for color in expected_partial.get('colors', []))
            subject_match = elements['subject'] == expected_partial.get('subject', elements['subject'])
            
            if colors_match and subject_match:
                print(f"✅ {filename} → colors: {elements['colors']}, subject: {elements['subject']}")
                success_count += 1
            else:
                print(f"❌ {filename} → {elements}")
        
        success_rate = (success_count / len(test_cases)) * 100
        print(f"\n📋 Results: {success_count}/{len(test_cases)} ({success_rate:.1f}%)")
        
        return success_rate >= 80.0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_art_movement_seo_structure():
    """Test the structure of art movement SEO generation (without API calls)."""
    print("\n🎯 Testing Art Movement SEO Structure")
    print("=" * 50)
    
    try:
        optimizer = MarketValidatedSEOOptimizer()
        
        # Test the _generate_from_art_movement method directly
        test_cases = [
            ('black-cat-japanese.jpg', 'japanese'),
            ('surreal-dream-cat.jpg', 'surreal'),
            ('pop-art-modern-cat.jpg', 'pop'),
        ]
        
        success_count = 0
        
        for filename, art_movement in test_cases:
            try:
                seo_content = optimizer._generate_from_art_movement(filename, art_movement)
                
                # Validate structure
                has_title = 'title' in seo_content and len(seo_content['title']) >= 120
                has_tags = 'tags' in seo_content and len(seo_content['tags']) == 13
                has_description = 'description' in seo_content and len(seo_content['description']) > 100
                has_source = seo_content.get('source') == 'art_movement_detection'
                has_movement = seo_content.get('art_movement') == art_movement
                
                if has_title and has_tags and has_description and has_source and has_movement:
                    print(f"✅ {filename} → {art_movement}")
                    print(f"   Title: {len(seo_content['title'])} chars")
                    print(f"   Tags: {len(seo_content['tags'])}")
                    print(f"   Movement: {seo_content['art_movement']}")
                    success_count += 1
                else:
                    print(f"❌ {filename} → Structure issues")
                    print(f"   Title OK: {has_title}")
                    print(f"   Tags OK: {has_tags}")
                    print(f"   Description OK: {has_description}")
                    print(f"   Source OK: {has_source}")
                    print(f"   Movement OK: {has_movement}")
                
            except Exception as e:
                print(f"❌ {filename} → Error: {e}")
        
        success_rate = (success_count / len(test_cases)) * 100
        print(f"\n📋 Results: {success_count}/{len(test_cases)} ({success_rate:.1f}%)")
        
        return success_rate >= 80.0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_fallback_priority():
    """Test that the fallback priority works correctly."""
    print("\n🔄 Testing Fallback Priority")
    print("=" * 50)
    
    try:
        optimizer = MarketValidatedSEOOptimizer()
        
        # Test different filename types and their expected processing paths
        test_cases = [
            ('september_032.jpg', 'market_validated'),  # Should find concept
            ('A-Surreal-Fall-Zen-Harvest-032.jpg', 'ai_naming_system'),  # Should parse AI naming
            ('black-cat-japanese.jpg', 'art_movement_detection'),  # Should detect art movement
            ('random-filename.jpg', 'openai_fallback'),  # Should fall back to OpenAI
        ]
        
        success_count = 0
        
        for filename, expected_path in test_cases:
            # Test the logic without making API calls
            concept_data = optimizer.concept_mapper.get_seo_data(filename)
            parsed_components = optimizer._parse_ai_naming(filename)
            art_movement = optimizer._detect_art_movement(filename)
            
            if concept_data:
                actual_path = 'market_validated'
            elif parsed_components:
                actual_path = 'ai_naming_system'
            elif art_movement:
                actual_path = 'art_movement_detection'
            else:
                actual_path = 'openai_fallback'
            
            if actual_path == expected_path:
                print(f"✅ {filename} → {actual_path}")
                success_count += 1
            else:
                print(f"❌ {filename} → {actual_path} (expected {expected_path})")
        
        success_rate = (success_count / len(test_cases)) * 100
        print(f"\n📋 Results: {success_count}/{len(test_cases)} ({success_rate:.1f}%)")
        
        return success_rate >= 75.0  # Allow some flexibility
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Art Movement Detection Test Suite")
    print("=" * 60)
    
    # Run quick tests (no API calls)
    detection_success = test_art_movement_detection_only()
    elements_success = test_design_element_extraction()
    structure_success = test_art_movement_seo_structure()
    fallback_success = test_fallback_priority()
    
    # Summary
    print(f"\n📋 FINAL RESULTS")
    print("=" * 60)
    print(f"   Art movement detection: {'✅ PASS' if detection_success else '❌ FAIL'}")
    print(f"   Design element extraction: {'✅ PASS' if elements_success else '❌ FAIL'}")
    print(f"   SEO structure generation: {'✅ PASS' if structure_success else '❌ FAIL'}")
    print(f"   Fallback priority: {'✅ PASS' if fallback_success else '❌ FAIL'}")
    
    all_passed = detection_success and elements_success and structure_success and fallback_success
    
    if all_passed:
        print(f"\n🎉 All tests passed! Art movement detection is working.")
        print(f"\n🎯 READY FOR USE:")
        print(f"   black-cat-japanese.jpg → Japanese art movement SEO")
        print(f"   surreal-dream-cat.jpg → Surreal art movement SEO")
        print(f"   pop-art-modern-cat.jpg → Pop art movement SEO")
        print(f"   vintage-retro-cat.jpg → Vintage art movement SEO")
    else:
        print(f"\n⚠️ Some tests failed. Please review.")
    
    sys.exit(0 if all_passed else 1)
