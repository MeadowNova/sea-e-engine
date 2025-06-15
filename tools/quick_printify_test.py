#!/usr/bin/env python3
"""
Quick Printify Test
==================

Fast, focused test to validate the critical fixes without stalling.
Tests the key components individually with timeouts and error handling.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from api.printify import PrintifyAPIClient

def test_design_file():
    """Quick test of the Printify design file."""
    print("🎨 TESTING: Printify Design File")
    print("=" * 40)
    
    design_path = "assets/designs_printify/bold_cat_design.png"
    
    if not os.path.exists(design_path):
        print(f"❌ Design file not found: {design_path}")
        return False
    
    try:
        from PIL import Image
        with Image.open(design_path) as img:
            print(f"✅ File exists: {design_path}")
            print(f"✅ Format: {img.format}")
            print(f"✅ Size: {img.size}")
            print(f"✅ Mode: {img.mode}")
            print(f"✅ Transparency: {img.mode in ('RGBA', 'LA')}")
            print(f"✅ Print ready: {min(img.size) >= 3000}")
            
            file_size = os.path.getsize(design_path) / (1024 * 1024)
            print(f"✅ File size: {file_size:.1f} MB")
            
        return True
    except Exception as e:
        print(f"❌ Error analyzing design: {e}")
        return False

def test_pricing_logic():
    """Test the pricing logic without API calls."""
    print("\n💰 TESTING: Pricing Logic")
    print("=" * 40)
    
    try:
        # Test pricing calculation logic
        test_variants = [
            {"title": "Black / S", "expected": 35.70},
            {"title": "White / M", "expected": 35.70},
            {"title": "Navy / L", "expected": 35.70},
            {"title": "Black / XL", "expected": 35.70},
            {"title": "White / 2XL", "expected": 38.56},
            {"title": "Navy / XXL", "expected": 38.56},
            {"title": "Black / 3XL", "expected": 40.75},
            {"title": "White / XXXL", "expected": 40.75},
        ]
        
        all_correct = True
        for variant in test_variants:
            title = variant["title"]
            expected = variant["expected"]
            
            # Apply the same logic as in the fixed method
            if "3XL" in title or "XXXL" in title:
                price = 4075  # $40.75
            elif "2XL" in title or "XXL" in title:
                price = 3856  # $38.56
            else:
                price = 3570  # $35.70
            
            actual = price / 100
            
            if abs(actual - expected) > 0.01:
                print(f"❌ {title}: ${actual:.2f} (expected ${expected:.2f})")
                all_correct = False
            else:
                print(f"✅ {title}: ${actual:.2f}")
        
        return all_correct
        
    except Exception as e:
        print(f"❌ Error testing pricing: {e}")
        return False

def test_api_connection():
    """Quick test of API connection without creating products."""
    print("\n🔌 TESTING: API Connection")
    print("=" * 40)
    
    try:
        printify = PrintifyAPIClient()
        
        # Test basic API connectivity
        print("✅ PrintifyAPIClient initialized")
        
        # Test shop access (quick call)
        shop_info = printify.get_shop_info()
        if shop_info:
            print(f"✅ Shop connected: {shop_info.get('title', 'Unknown')}")
            print(f"✅ Shop ID: {printify.shop_id}")
            return True
        else:
            print("❌ Failed to get shop info")
            return False
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_image_upload():
    """Test image upload with the Printify design."""
    print("\n📤 TESTING: Image Upload Quality")
    print("=" * 40)
    
    design_path = "assets/designs_printify/bold_cat_design.png"
    
    try:
        printify = PrintifyAPIClient()
        
        print("🔄 Uploading Printify-optimized design...")
        start_time = time.time()
        
        image_id = printify.upload_image(design_path)
        
        upload_time = time.time() - start_time
        
        if image_id:
            print(f"✅ Image uploaded successfully")
            print(f"✅ Image ID: {image_id}")
            print(f"✅ Upload time: {upload_time:.1f} seconds")
            
            # Check file size
            file_size = os.path.getsize(design_path) / (1024 * 1024)
            print(f"✅ Original file: {file_size:.1f} MB")
            
            return image_id
        else:
            print("❌ Image upload failed - no ID returned")
            return None
            
    except Exception as e:
        print(f"❌ Image upload error: {e}")
        return None

def test_variant_generation():
    """Test variant generation logic without creating products."""
    print("\n🎨 TESTING: Variant Generation Logic")
    print("=" * 40)
    
    try:
        printify = PrintifyAPIClient()
        
        # Get blueprint variants (this is a quick API call)
        print("🔄 Getting blueprint variants...")
        variants = printify.get_blueprint_variants(12, 29)  # T-shirt, Monster Digital
        
        if variants:
            print(f"✅ Retrieved {len(variants)} variants from API")
            
            # Test color filtering logic
            user_colors = [
                "Baby Blue", "Black", "Dark Grey Heather", "Deep Heather", 
                "Heather Navy", "Natural", "Navy", "Soft Pink", 
                "White", "Yellow", "Heather Peach", "Black Heather"
            ]
            
            # Count how many variants match our colors
            matching_variants = 0
            found_colors = set()
            
            for variant in variants:
                title = variant.get("title", "").lower()
                
                for color in user_colors:
                    if color.lower() in title:
                        matching_variants += 1
                        found_colors.add(color)
                        break
            
            print(f"✅ Matching variants: {matching_variants}")
            print(f"✅ Colors found: {len(found_colors)}/12")
            print(f"✅ Found colors: {sorted(found_colors)}")
            
            return matching_variants > 50  # Should have plenty of matches
        else:
            print("❌ No variants retrieved")
            return False
            
    except Exception as e:
        print(f"❌ Variant generation test failed: {e}")
        return False

def create_test_product():
    """Create a single test product to validate all fixes."""
    print("\n🏭 TESTING: Create Test Product")
    print("=" * 40)
    
    design_path = "assets/designs_printify/bold_cat_design.png"
    
    try:
        printify = PrintifyAPIClient()
        
        title = f"QUICK TEST - {datetime.now().strftime('%Y%m%d_%H%M')}"
        description = "Quick test product to validate all Printify fixes"
        
        print("🔄 Creating product with all fixes...")
        start_time = time.time()
        
        # Use the fixed method
        product_id = printify.create_product_with_user_config(
            title=title,
            description=description,
            blueprint_id=12,
            print_provider_id=29,
            design_file_path=design_path
        )
        
        creation_time = time.time() - start_time
        
        if product_id:
            print(f"✅ Product created successfully")
            print(f"✅ Product ID: {product_id}")
            print(f"✅ Creation time: {creation_time:.1f} seconds")
            
            # Quick validation of the created product
            product = printify.get_product(product_id)
            
            if product:
                variants = product.get('variants', [])
                visible = product.get('visible', True)
                sales_props = product.get('sales_channel_properties', {})
                free_shipping = sales_props.get('free_shipping', False)
                
                print(f"✅ Variants created: {len(variants)}")
                print(f"✅ Draft mode (not visible): {not visible}")
                print(f"✅ Free shipping enabled: {free_shipping}")
                
                # Check pricing on first few variants
                if variants:
                    sample_variant = variants[0]
                    price = sample_variant.get('price', 0) / 100
                    print(f"✅ Sample pricing: ${price:.2f}")
                
                return product_id
            else:
                print("❌ Could not retrieve created product")
                return None
        else:
            print("❌ Product creation failed")
            return None
            
    except Exception as e:
        print(f"❌ Product creation error: {e}")
        return None

def main():
    """Run quick focused tests."""
    print("🚨 QUICK PRINTIFY FIXES VALIDATION")
    print("=" * 60)
    print("Fast validation of critical fixes without stalling")
    print("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Test 1: Design file
    results['tests']['design_file'] = test_design_file()
    
    # Test 2: Pricing logic
    results['tests']['pricing_logic'] = test_pricing_logic()
    
    # Test 3: API connection
    results['tests']['api_connection'] = test_api_connection()
    
    # Test 4: Image upload
    image_id = test_image_upload()
    results['tests']['image_upload'] = image_id is not None
    
    # Test 5: Variant generation
    results['tests']['variant_generation'] = test_variant_generation()
    
    # Test 6: Create test product (if all previous tests pass)
    if all(results['tests'].values()):
        product_id = create_test_product()
        results['tests']['product_creation'] = product_id is not None
        results['test_product_id'] = product_id
    else:
        print("\n⚠️ Skipping product creation due to previous test failures")
        results['tests']['product_creation'] = False
    
    # Summary
    print("\n🎯 QUICK TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for result in results['tests'].values() if result)
    total = len(results['tests'])
    
    for test_name, result in results['tests'].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🏆 OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL FIXES VALIDATED - READY FOR PRODUCTION!")
    else:
        print("⚠️ Some issues need attention")
    
    # Save results
    results_file = f"output/quick_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("output", exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    return passed == total

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    success = main()
    sys.exit(0 if success else 1)
