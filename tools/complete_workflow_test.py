#!/usr/bin/env python3
"""
Complete Printify-to-Etsy Workflow Test
========================================

This script tests the full workflow:
1. Design → Printify product creation with variations
2. Printify product → Etsy hidden draft listing

IMPORTANT: This creates a HIDDEN draft on Etsy for safe testing.
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
from api.etsy import EtsyAPIClient

class WorkflowTester:
    def __init__(self):
        """Initialize the workflow tester."""
        self.printify = PrintifyAPIClient()
        self.etsy = EtsyAPIClient()
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'design_file': None,
            'printify_product_id': None,
            'etsy_listing_id': None,
            'steps_completed': [],
            'errors': [],
            'success': False
        }
        
    def log_step(self, step: str, success: bool = True, details: str = ""):
        """Log a workflow step."""
        status = "✅" if success else "❌"
        print(f"{status} {step}")
        if details:
            print(f"   {details}")
        
        self.test_results['steps_completed'].append({
            'step': step,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        if not success:
            self.test_results['errors'].append(f"{step}: {details}")
    
    def test_design_file(self, design_path: str) -> bool:
        """Test that the design file exists and is valid."""
        print("\n🎨 STEP 1: Validating Design File")
        print("=" * 50)
        
        if not os.path.exists(design_path):
            self.log_step("Design file validation", False, f"File not found: {design_path}")
            return False
        
        # Check file size and format
        file_size = os.path.getsize(design_path) / (1024 * 1024)  # MB
        file_ext = Path(design_path).suffix.lower()
        
        if file_ext not in ['.png', '.jpg', '.jpeg']:
            self.log_step("Design file validation", False, f"Unsupported format: {file_ext}")
            return False
        
        if file_size > 50:  # 50MB limit
            self.log_step("Design file validation", False, f"File too large: {file_size:.1f}MB")
            return False
        
        self.test_results['design_file'] = design_path
        self.log_step("Design file validation", True, f"Valid {file_ext} file, {file_size:.1f}MB")
        return True
    
    def create_printify_product(self, design_path: str, product_type: str = "tshirts") -> str:
        """Create Printify product with comprehensive variations."""
        print("\n🏭 STEP 2: Creating Printify Product")
        print("=" * 50)
        
        try:
            # Load your exact product blueprint configuration
            with open("config/product_blueprints.json", 'r') as f:
                blueprints = json.load(f)

            # Map product types to blueprint keys
            blueprint_map = {
                'tshirts': 'tshirt_bella_canvas_3001',
                'sweatshirts': 'sweatshirt_gildan_18000',
                'posters': 'poster_matte_sensaria'
            }

            if product_type not in blueprint_map:
                self.log_step("Product type validation", False, f"Unsupported product type: {product_type}")
                return None

            blueprint_key = blueprint_map[product_type]
            blueprint_config = blueprints['products'][blueprint_key]

            # Use YOUR EXACT blueprint configuration
            config = {
                'title': f"MockupDesignTest - {blueprint_config['metadata']['name']} Workflow Test {datetime.now().strftime('%Y%m%d_%H%M')}",
                'description': blueprint_config['product_specifications']['description'],
                'blueprint_id': blueprint_config['printify_config']['blueprint_id'],
                'print_provider_id': blueprint_config['printify_config']['print_provider_id'],
                'colors': list(blueprint_config['automation_settings']['default_colors']),  # Use your default colors
                'sizes': list(blueprint_config['automation_settings']['default_sizes']),    # Use your default sizes
                'product_type': product_type,
                'brand': blueprint_config['metadata']['brand'],
                'model': blueprint_config['metadata']['model']
            }
            
            self.log_step("Product configuration", True, 
                         f"Blueprint: {config['blueprint_id']}, Provider: {config['print_provider_id']}")
            
            # Create the product
            print("🔨 Creating product with variations...")

            # Use the new hybrid workflow method
            tags = ["custom", "t-shirt", "design", "apparel", "clothing", "print-on-demand"]

            result = self.printify.create_product_with_draft_publishing(
                title=config['title'],
                description=config['description'],
                blueprint_id=config['blueprint_id'],
                print_provider_id=config['print_provider_id'],
                design_file_path=design_path,
                tags=tags
            )

            product_id = result.get('printify_product_id')
            etsy_draft_id = result.get('etsy_draft_listing_id')
            
            if not product_id:
                self.log_step("Printify product creation", False, "No product ID returned")
                return None
            
            self.test_results['printify_product_id'] = product_id
            self.log_step("Printify product creation", True, f"Product ID: {product_id}")
            
            # Get product details to verify
            print("🔍 Verifying product details...")
            product_details = self.printify.get_product(product_id)
            
            if product_details:
                variant_count = len(product_details.get('variants', []))
                self.log_step("Product verification", True, f"Created with {variant_count} variants")
                
                # Log some variant details
                variants = product_details.get('variants', [])[:3]  # First 3
                for i, variant in enumerate(variants, 1):
                    title = variant.get('title', 'Unknown')
                    price = variant.get('price', 0) / 100  # Convert from cents
                    print(f"   Variant {i}: {title} - ${price:.2f}")
            
            return product_id
            
        except Exception as e:
            self.log_step("Printify product creation", False, str(e))
            return None

    def create_simple_product(self, title: str, description: str, blueprint_id: int,
                             print_provider_id: int, design_file_path: str) -> str:
        """
        Create a simple Printify product using existing variant structure.
        This approach copies the variant structure from your existing successful products.
        """
        try:
            # Load your existing product analysis to get working variant structure
            with open("config/printify_analysis.json", 'r') as f:
                analysis = json.load(f)

            # Find a working product with the same blueprint and provider
            working_product = None
            for product in analysis['products']:
                if (product['blueprint_id'] == blueprint_id and
                    product['print_provider_id'] == print_provider_id):
                    working_product = product
                    break

            if not working_product:
                raise Exception(f"No working product found for blueprint {blueprint_id} + provider {print_provider_id}")

            self.log_step("Working product template found", True,
                         f"Using structure from: {working_product['title']}")

            # Upload design image
            design_image_id = self.printify.upload_image(design_file_path)
            self.log_step("Design image upload", True, f"Image ID: {design_image_id}")

            # Use the working variant structure but with our new product details
            # Get a subset of variants (first 20 for testing)
            working_variants = working_product['variants'][:20]  # Limit for testing

            # Build product data using proven structure
            product_data = {
                "title": title,
                "description": description,
                "blueprint_id": blueprint_id,
                "print_provider_id": print_provider_id,
                "variants": [
                    {
                        "id": variant["id"],
                        "price": variant["price"],  # Keep existing pricing
                        "is_enabled": True  # Enable for our test
                    }
                    for variant in working_variants
                ],
                "print_areas": [
                    {
                        "variant_ids": [variant["id"] for variant in working_variants],
                        "placeholders": [
                            {
                                "position": "front",
                                "images": [
                                    {
                                        "id": design_image_id,
                                        "x": 0.5,
                                        "y": 0.5,
                                        "scale": 1.0,
                                        "angle": 0
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }

            # Create product
            endpoint = f"/shops/{self.printify.shop_id}/products.json"
            response = self.printify.make_request("POST", endpoint, data=product_data)

            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create product: {response.status_code} - {response.text}")

            product_response = response.json()
            product_id = product_response.get("id")

            self.log_step("Product creation", True, f"Product ID: {product_id}")

            return str(product_id)

        except Exception as e:
            self.log_step("Simple product creation", False, str(e))
            raise
    
    def save_to_airtable(self, product_id: str) -> str:
        """Save Printify product to Airtable for automated Etsy listing creation."""
        print("\n📋 STEP 3: Saving to Airtable for Automated Processing")
        print("=" * 50)
        
        try:
            # Get Printify product details
            print("📋 Getting Printify product details...")
            product_details = self.printify.get_product(product_id)
            
            if not product_details:
                self.log_step("Product details retrieval", False, "Could not get product details")
                return None
            
            self.log_step("Product details retrieval", True, "Retrieved product information")
            
            # Prepare Etsy listing data
            title = product_details.get('title', 'Test Product')
            description = product_details.get('description', 'Test description')
            
            # Get first variant for pricing reference
            variants = product_details.get('variants', [])
            if not variants:
                self.log_step("Variant validation", False, "No variants found")
                return None

            # Calculate retail price from blueprint configuration
            # Get the blueprint config used for this product
            with open("config/product_blueprints.json", 'r') as f:
                blueprints = json.load(f)

            blueprint_map = {'tshirts': 'tshirt_bella_canvas_3001', 'sweatshirts': 'sweatshirt_gildan_18000', 'posters': 'poster_matte_sensaria'}
            blueprint_key = blueprint_map.get('tshirts', 'tshirt_bella_canvas_3001')  # Default to t-shirts
            blueprint_config = blueprints['products'][blueprint_key]

            base_cost = blueprint_config['pricing']['base_cost']
            markup = blueprint_config['pricing']['suggested_retail_markup']
            base_price = base_cost * markup  # Calculate retail price
            
            etsy_data = {
                'title': title,
                'description': description,
                'price': base_price,
                'quantity': 999,  # High quantity for POD
                'tags': ['custom', 'design', 'tshirt', 'unisex', 'cotton', 'comfortable', 
                        'gift', 'art', 'unique', 'printify', 'bella canvas', 'quality', 'casual'],
                'category_id': 69150467,  # T-shirts category
                'who_made': 'i_did',
                'when_made': '2020_2024',
                'is_supply': False,
                'state': 'draft',  # IMPORTANT: Create as draft
                'processing_min': 3,
                'processing_max': 5
            }
            
            self.log_step("Etsy listing preparation", True, f"Price: ${base_price:.2f}, {len(variants)} variants")
            
            # Create the listing (HIDDEN)
            print("🔒 Creating HIDDEN draft listing...")
            listing_id = self.etsy.create_listing(
                title=etsy_data['title'],
                description=etsy_data['description'],
                price=etsy_data['price'],
                tags=etsy_data['tags'],
                image_files=[],  # No images for this test
                printify_product_id=product_id
            )
            
            if not listing_id:
                self.log_step("Etsy listing creation", False, "No listing ID returned")
                return None
            
            self.test_results['etsy_listing_id'] = listing_id
            self.log_step("Etsy listing creation", True, f"Hidden Draft Listing ID: {listing_id}")
            
            # Verify the listing is hidden
            print("🔍 Verifying listing is hidden...")
            listing_details = self.etsy.get_listing(listing_id)
            
            if listing_details:
                state = listing_details.get('state', 'unknown')
                is_hidden = state == 'draft'
                
                if is_hidden:
                    self.log_step("Listing visibility verification", True, "✅ Listing is HIDDEN (draft state)")
                else:
                    self.log_step("Listing visibility verification", False, f"⚠️ Listing state: {state}")
            
            return listing_id
            
        except Exception as e:
            self.log_step("Etsy listing creation", False, str(e))
            return None
    
    def run_complete_test(self, design_path: str) -> bool:
        """Run the complete workflow test."""
        print("🚀 COMPLETE PRINTIFY-TO-ETSY WORKFLOW TEST")
        print("=" * 60)
        print(f"Design: {design_path}")
        print(f"Timestamp: {self.test_results['timestamp']}")
        print("⚠️  IMPORTANT: This creates a HIDDEN draft listing on Etsy")
        print("=" * 60)
        
        # Step 1: Validate design
        if not self.test_design_file(design_path):
            return False
        
        # Step 2: Create Printify product (default to t-shirts for this test)
        product_id = self.create_printify_product(design_path, "tshirts")
        if not product_id:
            return False
        
        # Step 3: Create hidden Etsy listing
        listing_id = self.create_etsy_hidden_listing(product_id)
        if not listing_id:
            return False
        
        # Success!
        self.test_results['success'] = True
        
        print("\n🎉 WORKFLOW TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"✅ Printify Product ID: {product_id}")
        print(f"✅ Etsy Listing ID: {listing_id} (HIDDEN DRAFT)")
        print(f"✅ Total Steps: {len(self.test_results['steps_completed'])}")
        print(f"✅ Errors: {len(self.test_results['errors'])}")
        
        return True

def main():
    """Main test execution."""
    # Use Printify-optimized design file
    design_path = "assets/designs_printify/bold_cat_design.png"

    if not os.path.exists(design_path):
        print(f"❌ Printify design file not found: {design_path}")
        print("Available Printify designs:")
        design_dir = Path("assets/designs_printify")
        if design_dir.exists():
            for file in design_dir.glob("*.png"):
                print(f"  - {file}")
        return False
    
    # Run the test
    tester = WorkflowTester()
    success = tester.run_complete_test(design_path)
    
    # Save results
    results_file = f"output/workflow_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("output", exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(tester.test_results, f, indent=2)
    
    print(f"\n📄 Test results saved to: {results_file}")
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Check the Etsy listing in your drafts (it's hidden)")
        print("2. Verify the Printify product in your dashboard")
        print("3. Test any additional variations or settings")
        print("4. When ready, you can publish the Etsy listing")
    
    return success

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    success = main()
    sys.exit(0 if success else 1)
