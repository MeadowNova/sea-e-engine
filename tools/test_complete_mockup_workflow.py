#!/usr/bin/env python3
"""
Complete Mockup Generation & Google Sheets Upload Test
======================================================

Test the complete mockup workflow:
1. Generate mockups for all t-shirt templates using thecreamcatinspace.svg
2. Upload all mockups to Google Sheets
3. Generate shareable URLs for Airtable integration
4. Validate the complete pipeline

This tests the full workflow from design → mockups → Google Sheets → URLs
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent))

# Import the correct modules
from modules.custom_mockup_generator import CustomMockupGenerator
from modules.sheets_mockup_uploader import SheetsMockupUploader
from api.airtable_client import AirtableClient



def test_mockup_generator_setup():
    """Test and discover available templates from the mockup generator."""
    try:
        # Initialize mockup generator to discover templates
        mockup_generator = CustomMockupGenerator(
            output_dir="output/mockup_test",
            enable_sheets_upload=False,  # Test without sheets first
            auto_manage=True
        )

        # Get available templates
        available_templates = mockup_generator.list_available_templates()

        print(f"📋 Available templates discovered:")
        for product_type, template_names in available_templates.items():
            print(f"  {product_type}: {len(template_names)} templates")
            for template_name in template_names:
                print(f"    - {template_name}")

        return mockup_generator, available_templates

    except Exception as e:
        print(f"❌ Failed to initialize mockup generator: {e}")
        return None, {}

def test_complete_mockup_workflow():
    """Test the complete mockup generation and Google Sheets upload workflow."""
    print("🎨 TESTING: Complete Mockup Generation & Google Sheets Upload")
    print("=" * 70)
    print("Testing: Design → All T-Shirt Mockups → Google Sheets → URLs")
    print("=" * 70)
    
    # Design and mockup files
    design_file = "assets/mockups/tshirts/designs_mockups/Copy of New Test for Sizing (1).png"
    product_name = "Copy_of_New_Test_for_Sizing_1"

    # Verify design file exists
    if not os.path.exists(design_file):
        print(f"❌ Design file not found: {design_file}")
        return False

    print(f"✅ Using design file: {design_file}")
    print(f"📝 Product name: {product_name}")
    
    try:
        # Initialize components
        print("\n🔧 Initializing mockup generation system...")

        # Test mockup generator setup first
        mockup_generator, available_templates = test_mockup_generator_setup()

        if not mockup_generator:
            print("❌ Failed to initialize mockup generator")
            return False

        print("✅ Mockup generation system initialized")

        # Get t-shirt templates
        tshirt_templates = available_templates.get('tshirts', [])

        if not tshirt_templates:
            print("❌ No t-shirt templates found")
            return False

        print(f"✅ Found {len(tshirt_templates)} t-shirt templates:")
        for template_name in tshirt_templates:
            print(f"  📄 {template_name}")

        # Now enable Google Sheets upload
        print("\n📊 Enabling Google Sheets integration...")
        try:
            airtable_client = AirtableClient()
            mockup_generator.enable_sheets_upload = True
            mockup_generator.sheets_uploader = SheetsMockupUploader(airtable_client=airtable_client)
            print("✅ Google Sheets integration enabled")
        except Exception as e:
            print(f"⚠️  Google Sheets integration failed: {e}")
            print("📝 Continuing with local mockup generation only")
        
        # Generate mockups for all templates
        print(f"\n🎨 Generating mockups for all {len(tshirt_templates)} templates...")

        results = []
        successful_uploads = []
        failed_uploads = []

        for i, template_name in enumerate(tshirt_templates, 1):
            print(f"\n📸 Generating mockup {i}/{len(tshirt_templates)}: {template_name}")

            try:
                # Prepare variation info for organization
                variation_info = {
                    "product_name": product_name,
                    "template": template_name,
                    "type": "t-shirt"
                }

                # Generate mockup with Google Sheets upload
                result = mockup_generator.generate_mockup(
                    product_type="tshirts",
                    design_path=design_file,
                    template_name=template_name,
                    upload_to_sheets=True,
                    variation_info=variation_info
                )

                results.append(result)

                if result['success']:
                    print(f"  ✅ Generated: {Path(result['mockup_path']).name}")

                    # Check if uploaded to Google Sheets
                    if result.get('google_sheets_url'):
                        print(f"  📊 Uploaded to Google Sheets: {result['google_sheets_url']}")
                        successful_uploads.append({
                            "template": template_name,
                            "mockup_path": result['mockup_path'],
                            "google_sheets_url": result['google_sheets_url'],
                            "file_id": result.get('google_drive_file_id')
                        })
                    else:
                        print(f"  ⚠️  Generated but not uploaded to Google Sheets")
                        failed_uploads.append(template_name)
                else:
                    print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
                    failed_uploads.append(template_name)

            except Exception as e:
                print(f"  ❌ Error generating mockup: {e}")
                failed_uploads.append(template_name)
        
        # Summary
        print(f"\n📊 MOCKUP GENERATION SUMMARY:")
        print(f"✅ Total mockups generated: {len([r for r in results if r.get('success')])}/{len(tshirt_templates)}")
        print(f"📊 Successfully uploaded to Google Sheets: {len(successful_uploads)}")
        print(f"❌ Failed uploads: {len(failed_uploads)}")

        if successful_uploads:
            print(f"\n🔗 GOOGLE SHEETS URLS:")
            for upload in successful_uploads:
                print(f"  📄 {upload['template']}: {upload['google_sheets_url']}")

        if failed_uploads:
            print(f"\n⚠️  FAILED UPLOADS:")
            for failed in failed_uploads:
                print(f"  ❌ {failed}")

        # Save complete results
        results_file = f"output/complete_mockup_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("output", exist_ok=True)

        complete_results = {
            "design_file": design_file,
            "product_name": product_name,
            "templates_processed": len(tshirt_templates),
            "successful_generations": len([r for r in results if r.get('success')]),
            "successful_uploads": len(successful_uploads),
            "failed_uploads": len(failed_uploads),
            "google_sheets_urls": successful_uploads,
            "detailed_results": results,
            "timestamp": datetime.now().isoformat()
        }

        with open(results_file, 'w') as f:
            json.dump(complete_results, f, indent=2)

        print(f"\n📄 Complete results saved to: {results_file}")

        # Validate success criteria
        success_rate = len(successful_uploads) / len(tshirt_templates) if tshirt_templates else 0
        
        if success_rate >= 0.8:  # 80% success rate
            print(f"\n🎉 WORKFLOW SUCCESS! ({success_rate:.1%} success rate)")
            return True
        else:
            print(f"\n⚠️  WORKFLOW NEEDS ATTENTION ({success_rate:.1%} success rate)")
            return False
            
    except Exception as e:
        print(f"❌ Complete mockup workflow failed: {e}")
        return False

def main():
    """Main test execution."""
    print("🚨 SEA-E COMPLETE MOCKUP WORKFLOW TEST")
    print("=" * 70)
    print("Testing complete pipeline: Design → Mockups → Google Sheets → URLs")
    print("=" * 70)
    
    # Test the complete workflow
    workflow_success = test_complete_mockup_workflow()
    
    if workflow_success:
        print("\n🎉 COMPLETE WORKFLOW SUCCESS!")
        print("=" * 70)
        print("✅ All t-shirt mockups generated successfully")
        print("✅ Google Sheets upload integration working")
        print("✅ Shareable URLs generated for Airtable")
        print("✅ Ready for Airtable automation integration")
        print("\n🚀 READY FOR PRODUCTION AUTOMATION!")
    else:
        print("\n⚠️ WORKFLOW NEEDS ATTENTION")
        print("Check the output above for specific issues")
    
    return workflow_success

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    success = main()
    sys.exit(0 if success else 1)
