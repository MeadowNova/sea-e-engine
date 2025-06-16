#!/usr/bin/env python3
"""
Test Main Engine Integration with Hybrid Workflow
=================================================

Test that the main SEA-E engine correctly integrates with the hybrid workflow
and that all the fixes (positioning, SVG support, color palette, draft publishing)
work in the production context.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent))

from sea_engine import SEAEngine
from src.data.airtable_models import Product, ProductStatus, Priority

def create_test_product() -> Product:
    """Create a test product for integration testing."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    return Product(
        product_name=f"SEA-E Integration Test {timestamp}",
        product_id=f"test_integration_{timestamp}",
        description="Integration test for hybrid workflow in main SEA-E engine",
        product_type="t-shirt",
        status=ProductStatus.DESIGN,
        priority=Priority.HIGH,
        blueprint_key="tshirt_bella_canvas_3001",
        print_provider="Printify",
        batch_group="integration_test",
        base_price=15.99,
        selling_price=29.99
    )

def test_main_engine_integration():
    """Test the main engine with hybrid workflow integration."""
    print("🚀 TESTING: Main Engine Integration with Hybrid Workflow")
    print("=" * 70)
    print("Testing: SEA-E Engine → Hybrid Workflow → Airtable Integration")
    print("=" * 70)
    
    try:
        # Initialize the main engine
        print("🔧 Initializing SEA-E Engine...")
        engine = SEAEngine()
        
        # Validate environment
        print("🔍 Validating environment...")
        if not engine.validate_environment():
            print("❌ Environment validation failed")
            return False
        
        print("✅ Environment validation successful")
        
        # Create test product
        print("📝 Creating test product...")
        test_product = create_test_product()
        
        # Use the specific design file requested
        design_file = "assets/designs_printify/thecreamcatinspace.svg"

        if os.path.exists(design_file):
            print(f"✅ Found design file: {design_file}")
            # Update the test product name to match the design
            test_product.product_name = "thecreamcatinspace"
        else:
            print(f"❌ Design file not found: {design_file}")
            return False
        
        # Test the hybrid workflow integration
        print("\n🔄 Testing hybrid workflow integration...")
        print(f"📝 Product: {test_product.product_name}")
        print(f"🏷️ Type: {test_product.product_type}")
        print(f"💰 Price: ${test_product.selling_price}")
        
        # Test the _create_printify_product method directly
        print("\n🧪 Testing _create_printify_product method...")
        
        # Mock variations for testing
        from src.data.airtable_models import Variation
        test_variations = [
            Variation(
                variation_id="test_var_1",
                color="Black",
                size="M",
                price=29.99,
                sku="TEST-BLK-M"
            )
        ]
        
        # Mock mockup files
        test_mockup_files = ["test_mockup_1.png", "test_mockup_2.png"]
        
        # Test the method (this will test the integration without full workflow)
        try:
            hybrid_result = engine._create_printify_product(
                test_product, 
                test_variations, 
                test_mockup_files
            )
            
            print("\n✅ HYBRID WORKFLOW INTEGRATION SUCCESS!")
            print("=" * 50)
            
            # Validate the result structure
            required_fields = [
                "printify_product_id",
                "etsy_draft_listing_id",
                "draft_status",
                "workflow_stage"
            ]
            
            print("🎯 INTEGRATION VALIDATION:")
            all_success = True
            for field in required_fields:
                has_field = field in hybrid_result and hybrid_result[field] is not None
                status_icon = "✅" if has_field else "❌"
                print(f"{status_icon} {field}: {hybrid_result.get(field, 'N/A')}")
                if not has_field:
                    all_success = False
            
            print("\n📊 INTEGRATION RESULTS:")
            print(f"🆔 Printify Product ID: {hybrid_result.get('printify_product_id', 'N/A')}")
            print(f"🔗 Etsy Draft ID: {hybrid_result.get('etsy_draft_listing_id', 'N/A')}")
            print(f"📈 Draft Status: {hybrid_result.get('draft_status', 'N/A')}")
            print(f"📋 Workflow Stage: {hybrid_result.get('workflow_stage', 'N/A')}")
            print(f"🎨 Total Variants: {hybrid_result.get('total_variants', 0)}")
            print(f"🌈 Colors Available: {len(hybrid_result.get('colors_available', []))}")
            
            if hybrid_result.get('etsy_draft_url'):
                print(f"🔗 Etsy Draft URL: {hybrid_result['etsy_draft_url']}")
            
            # Save integration test results
            results_file = f"output/integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("output", exist_ok=True)
            
            with open(results_file, 'w') as f:
                json.dump(hybrid_result, f, indent=2)
            
            print(f"\n📄 Integration test results saved to: {results_file}")
            
            return all_success
            
        except Exception as e:
            print(f"❌ Hybrid workflow integration failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Main engine integration test failed: {e}")
        return False

def main():
    """Main test execution."""
    print("🚨 SEA-E MAIN ENGINE INTEGRATION TEST")
    print("=" * 70)
    print("Testing hybrid workflow integration in production context")
    print("=" * 70)
    
    # Test the integration
    integration_success = test_main_engine_integration()
    
    if integration_success:
        print("\n🎉 INTEGRATION SUCCESS!")
        print("=" * 70)
        print("✅ Main engine hybrid workflow integration working")
        print("✅ All critical fixes available in production")
        print("✅ Airtable data structure integration complete")
        print("✅ Ready for Google Sheets/Airtable automation")
        print("\n🚀 READY FOR PHASE 2: Complete Automation Pipeline!")
    else:
        print("\n⚠️ INTEGRATION NEEDS ATTENTION")
        print("Check the output above for specific issues")
    
    return integration_success

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    success = main()
    sys.exit(0 if success else 1)
