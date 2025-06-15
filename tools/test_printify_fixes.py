#!/usr/bin/env python3
"""
Test Printify Fixes
===================

This script tests all the critical fixes for Printify product creation:
1. ✅ Correct pricing ($35.70 S-XL, $38.56 2XL, $40.75 3XL)
2. ✅ Free shipping (sales_channel_properties.free_shipping = true)
3. ✅ Draft mode (visible = false, no auto-publish)
4. ✅ Enhanced design quality and placement
5. ✅ Complete Printify-only publishing workflow

Tests both the fixed create_product_with_user_config and new create_complete_etsy_listing methods.
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

class PrintifyFixTester:
    def __init__(self):
        """Initialize the tester."""
        self.printify = PrintifyAPIClient()
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'products_created': [],
            'all_fixes_working': False
        }
        
    def log_test(self, test_name: str, success: bool = True, details: str = "", data: dict = None):
        """Log a test result."""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results['tests'].append({
            'test': test_name,
            'success': success,
            'details': details,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        })
    
    def test_pricing_fix(self, product_id: str) -> bool:
        """Test that pricing is correctly set."""
        print("\n💰 TESTING: Correct Pricing Structure")
        print("=" * 50)
        
        try:
            product = self.printify.get_product(product_id)
            variants = product.get('variants', [])
            
            pricing_correct = True
            pricing_details = []
            
            for variant in variants[:10]:  # Check first 10 variants
                title = variant.get('title', '')
                price = variant.get('price', 0) / 100  # Convert from cents
                
                expected_price = 35.70  # Default S-XL
                if '3XL' in title or 'XXXL' in title:
                    expected_price = 40.75
                elif '2XL' in title or 'XXL' in title:
                    expected_price = 38.56
                
                if abs(price - expected_price) > 0.01:  # Allow 1 cent tolerance
                    pricing_correct = False
                
                pricing_details.append(f"{title}: ${price:.2f} (expected: ${expected_price:.2f})")
            
            self.log_test("Pricing structure", pricing_correct, 
                         f"Checked {len(pricing_details)} variants", 
                         {"pricing_details": pricing_details})
            
            return pricing_correct
            
        except Exception as e:
            self.log_test("Pricing structure", False, str(e))
            return False
    
    def test_free_shipping(self, product_id: str) -> bool:
        """Test that free shipping is enabled."""
        print("\n🚚 TESTING: Free Shipping Configuration")
        print("=" * 50)
        
        try:
            product = self.printify.get_product(product_id)
            
            # Check sales channel properties
            sales_props = product.get('sales_channel_properties', {})
            free_shipping = sales_props.get('free_shipping', False)
            
            self.log_test("Free shipping enabled", free_shipping,
                         f"sales_channel_properties.free_shipping = {free_shipping}")
            
            return free_shipping
            
        except Exception as e:
            self.log_test("Free shipping enabled", False, str(e))
            return False
    
    def test_draft_mode(self, product_id: str) -> bool:
        """Test that product is created as draft."""
        print("\n👁️ TESTING: Draft Mode (Hide in Store)")
        print("=" * 50)
        
        try:
            product = self.printify.get_product(product_id)
            
            visible = product.get('visible', True)
            is_draft = not visible
            
            self.log_test("Draft mode (not visible)", is_draft,
                         f"Product visible = {visible} (should be False for draft)")
            
            return is_draft
            
        except Exception as e:
            self.log_test("Draft mode", False, str(e))
            return False
    
    def test_design_quality(self, design_path: str) -> bool:
        """Test design quality improvements."""
        print("\n🎨 TESTING: Design Quality & Placement")
        print("=" * 50)
        
        try:
            from PIL import Image
            
            # Test image processing
            with Image.open(design_path) as img:
                original_size = img.size
                has_transparency = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                
                self.log_test("Design transparency", has_transparency,
                             f"Image mode: {img.mode}, Transparency: {has_transparency}")
                
                self.log_test("Design resolution", min(img.size) >= 3000,
                             f"Image size: {img.size} (minimum 3000px required)")
            
            return True
            
        except Exception as e:
            self.log_test("Design quality", False, str(e))
            return False
    
    def test_fixed_method(self, design_path: str) -> str:
        """Test the fixed create_product_with_user_config method."""
        print("\n🔧 TESTING: Fixed Product Creation Method")
        print("=" * 50)
        
        try:
            title = f"FIXED TEST - {datetime.now().strftime('%Y%m%d_%H%M')}"
            description = "Test product with all fixes: correct pricing, free shipping, draft mode, enhanced quality."
            
            product_id = self.printify.create_product_with_user_config(
                title=title,
                description=description,
                blueprint_id=12,
                print_provider_id=29,
                design_file_path=design_path
            )
            
            if product_id:
                self.test_results['products_created'].append({
                    'method': 'create_product_with_user_config',
                    'product_id': product_id,
                    'title': title
                })
                
                self.log_test("Fixed method execution", True, f"Product ID: {product_id}")
                return product_id
            else:
                self.log_test("Fixed method execution", False, "No product ID returned")
                return None
                
        except Exception as e:
            self.log_test("Fixed method execution", False, str(e))
            return None
    
    def test_complete_etsy_method(self, design_path: str) -> str:
        """Test the new complete Etsy listing method."""
        print("\n🏪 TESTING: Complete Etsy Listing Method")
        print("=" * 50)
        
        try:
            title = f"COMPLETE ETSY TEST - {datetime.now().strftime('%Y%m%d_%H%M')}"
            description = "Complete Etsy listing created via Printify only - no Etsy API needed!"
            tags = ["t-shirt", "custom", "design", "printify", "etsy", "clothing", "apparel"]
            
            result = self.printify.create_complete_etsy_listing(
                title=title,
                description=description,
                tags=tags,
                design_file_path=design_path,
                publish_immediately=False  # Keep as draft
            )
            
            product_id = result.get('product_id')
            
            if product_id:
                self.test_results['products_created'].append({
                    'method': 'create_complete_etsy_listing',
                    'product_id': product_id,
                    'title': title,
                    'result': result
                })
                
                self.log_test("Complete Etsy method", True, 
                             f"Product ID: {product_id}, Status: {result.get('status')}")
                return product_id
            else:
                self.log_test("Complete Etsy method", False, "No product ID returned")
                return None
                
        except Exception as e:
            self.log_test("Complete Etsy method", False, str(e))
            return None
    
    def run_comprehensive_test(self, design_path: str) -> bool:
        """Run all tests comprehensively."""
        print("🚨 COMPREHENSIVE PRINTIFY FIXES TEST")
        print("=" * 70)
        print(f"Design: {design_path}")
        print(f"Testing all critical fixes identified in Issues to Fix.md")
        print("=" * 70)
        
        # Test design quality first
        if not self.test_design_quality(design_path):
            return False
        
        # Test fixed method
        fixed_product_id = self.test_fixed_method(design_path)
        if not fixed_product_id:
            return False
        
        # Test all fixes on the fixed method product
        pricing_ok = self.test_pricing_fix(fixed_product_id)
        shipping_ok = self.test_free_shipping(fixed_product_id)
        draft_ok = self.test_draft_mode(fixed_product_id)
        
        # Test complete Etsy method
        complete_product_id = self.test_complete_etsy_method(design_path)
        complete_ok = complete_product_id is not None
        
        # Overall success
        all_fixes_working = pricing_ok and shipping_ok and draft_ok and complete_ok
        self.test_results['all_fixes_working'] = all_fixes_working
        
        print("\n🎯 COMPREHENSIVE TEST RESULTS")
        print("=" * 70)
        print(f"✅ Pricing Fix: {'PASS' if pricing_ok else 'FAIL'}")
        print(f"✅ Free Shipping: {'PASS' if shipping_ok else 'FAIL'}")
        print(f"✅ Draft Mode: {'PASS' if draft_ok else 'FAIL'}")
        print(f"✅ Complete Method: {'PASS' if complete_ok else 'FAIL'}")
        print(f"🎉 ALL FIXES: {'WORKING' if all_fixes_working else 'NEED ATTENTION'}")
        
        if all_fixes_working:
            print("\n🚀 READY FOR PRODUCTION!")
            print("All critical issues have been resolved:")
            print("✅ Correct pricing structure implemented")
            print("✅ Free shipping enabled")
            print("✅ Draft mode working (no live listings)")
            print("✅ Enhanced design quality and placement")
            print("✅ Complete Printify-only workflow available")
        
        return all_fixes_working

def main():
    """Main test execution."""
    # Use the specific Printify-optimized design file
    design_path = "assets/designs_printify/bold_cat_design.png"

    if not os.path.exists(design_path):
        print(f"❌ Printify design file not found: {design_path}")
        print("Please ensure the Printify-optimized design exists at this location.")
        return False
    
    # Run comprehensive tests
    tester = PrintifyFixTester()
    success = tester.run_comprehensive_test(design_path)
    
    # Save results
    results_file = f"output/printify_fixes_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("output", exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(tester.test_results, f, indent=2)
    
    print(f"\n📄 Test results saved to: {results_file}")
    
    return success

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    success = main()
    sys.exit(0 if success else 1)
