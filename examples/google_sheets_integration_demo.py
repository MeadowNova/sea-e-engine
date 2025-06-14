#!/usr/bin/env python3
"""
Google Sheets Integration Demo for SEA-E Engine
==============================================

Demonstrates the complete workflow:
Design → Custom Mockup → Google Sheets Upload → Shareable URL → Airtable → Etsy Listing

This script shows how to use the new Google Sheets integration to:
1. Generate high-quality mockups
2. Upload them to Google Sheets
3. Get shareable URLs
4. Update Airtable with the URLs
5. Prepare for Etsy listing creation
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.custom_mockup_generator import CustomMockupGenerator
from modules.sheets_mockup_uploader import SheetsMockupUploader
from api.google_sheets_client import GoogleSheetsClient
from api.airtable_client import AirtableClient
from core.logger import setup_logger

# Set up logging
logger = setup_logger("sheets_demo", level="INFO")


def demo_single_mockup_upload():
    """
    Demo: Generate a single mockup and upload to Google Sheets.
    """
    logger.info("🎨 Demo: Single Mockup Upload to Google Sheets")
    logger.info("=" * 60)
    
    try:
        # Initialize the custom mockup generator with Google Sheets integration
        generator = CustomMockupGenerator(
            assets_dir="assets",
            output_dir="output",
            enable_sheets_upload=True,  # 🔥 Enable Google Sheets integration
            auto_manage=True
        )
        
        # Check if we have templates available
        templates = generator.list_available_templates()
        logger.info(f"Available templates: {templates}")
        
        if not any(templates.values()):
            logger.error("❌ No mockup templates found. Please ensure templates are in assets/mockups/")
            return False
        
        # Generate a mockup with Google Sheets upload
        # Note: Replace with actual design file path
        design_path = "assets/designs/sample_design.png"  # Update this path
        
        if not Path(design_path).exists():
            logger.warning(f"⚠️ Design file not found: {design_path}")
            logger.info("Creating a sample design file for demo...")
            
            # Create a simple sample design for demo
            from PIL import Image, ImageDraw, ImageFont
            
            # Create sample design
            img = Image.new('RGBA', (1200, 1200), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Add sample text
            try:
                # Try to use a system font
                font = ImageFont.truetype("arial.ttf", 100)
            except:
                font = ImageFont.load_default()
            
            draw.text((600, 600), "SEA-E\nDemo", fill=(0, 0, 0, 255), 
                     anchor="mm", align="center", font=font)
            
            # Save sample design
            Path(design_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(design_path, "PNG")
            logger.info(f"✅ Created sample design: {design_path}")
        
        # Generate mockup with Google Sheets upload
        result = generator.generate_mockup(
            product_type="tshirts",
            design_path=design_path,
            template_name=None,  # Use first available template
            upload_to_sheets=True,  # 🔥 Upload to Google Sheets
            variation_info={
                "color": "black",
                "size": "M",
                "product_name": "SEA-E Demo Product"
            }
        )
        
        if result['success']:
            logger.info("✅ Mockup generated successfully!")
            logger.info(f"📁 Local file: {result['mockup_path']}")
            
            if 'google_sheets_url' in result:
                logger.info(f"🔗 Google Sheets URL: {result['google_sheets_url']}")
                logger.info(f"📊 Upload status: {result['sheets_upload_status']}")
                logger.info("🎉 Mockup is now available as a shareable URL!")
            else:
                logger.warning("⚠️ Google Sheets upload not completed")
        else:
            logger.error(f"❌ Mockup generation failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        return False


def demo_batch_upload():
    """
    Demo: Batch upload multiple mockups to Google Sheets.
    """
    logger.info("📦 Demo: Batch Upload to Google Sheets")
    logger.info("=" * 60)
    
    try:
        # Initialize the sheets uploader
        uploader = SheetsMockupUploader()
        
        # Create sample mockup files for demo
        sample_mockups = []
        for i, (color, size) in enumerate([("black", "M"), ("white", "L"), ("navy", "S")]):
            # Create sample mockup file
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', (2000, 2000), (200, 200, 200))
            draw = ImageDraw.Draw(img)
            draw.text((1000, 1000), f"Demo {color} {size}", fill=(0, 0, 0), anchor="mm")
            
            mockup_path = f"output/demo_mockup_{color}_{size}.png"
            Path(mockup_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(mockup_path)
            
            sample_mockups.append({
                'path': mockup_path,
                'color': color,
                'size': size
            })
        
        # Add upload jobs to queue
        for mockup in sample_mockups:
            success = uploader.add_upload_job(
                mockup_path=mockup['path'],
                product_name="SEA-E Batch Demo",
                variation_info={
                    "color": mockup['color'],
                    "size": mockup['size'],
                    "product_name": "SEA-E Batch Demo"
                }
            )
            
            if success:
                logger.info(f"✅ Added to queue: {mockup['color']} {mockup['size']}")
            else:
                logger.error(f"❌ Failed to add: {mockup['color']} {mockup['size']}")
        
        # Process the upload queue
        logger.info("🚀 Processing upload queue...")
        batch_result = uploader.process_upload_queue()
        
        # Display results
        logger.info(f"📊 Batch Upload Results:")
        logger.info(f"   Total jobs: {batch_result.total_jobs}")
        logger.info(f"   Successful: {batch_result.successful_uploads}")
        logger.info(f"   Failed: {batch_result.failed_uploads}")
        logger.info(f"   Execution time: {batch_result.execution_time:.2f}s")
        
        # Show successful uploads
        for i, result in enumerate(batch_result.upload_results):
            if result.success:
                logger.info(f"✅ Upload {i+1}: {result.shareable_url}")
            else:
                logger.error(f"❌ Upload {i+1}: {result.error_message}")
        
        # Cleanup demo files
        for mockup in sample_mockups:
            try:
                Path(mockup['path']).unlink()
            except:
                pass
        
        return batch_result.successful_uploads > 0
        
    except Exception as e:
        logger.error(f"❌ Batch demo failed: {e}")
        return False


def demo_airtable_integration():
    """
    Demo: Show how Google Sheets URLs are stored in Airtable.
    """
    logger.info("🗃️ Demo: Airtable Integration")
    logger.info("=" * 60)
    
    try:
        # Initialize Airtable client
        airtable_client = AirtableClient()
        
        # Test connection
        if not airtable_client.test_connection():
            logger.error("❌ Airtable connection failed")
            return False
        
        logger.info("✅ Airtable connection successful")
        
        # Show the new fields available for Google Sheets URLs
        mockup_fields = airtable_client.FIELD_MAPPINGS['mockups']
        sheets_fields = {k: v for k, v in mockup_fields.items() 
                        if 'google' in k.lower() or 'sheets' in k.lower()}
        
        logger.info("📋 New Airtable fields for Google Sheets integration:")
        for field_key, field_name in sheets_fields.items():
            logger.info(f"   {field_key}: {field_name}")
        
        # Example of how URLs would be stored
        logger.info("\n💡 Example: How Google Sheets URLs are stored in Airtable:")
        logger.info("   When a mockup is uploaded to Google Sheets, the following fields are updated:")
        logger.info("   - Google Sheets URL: https://drive.google.com/file/d/FILE_ID/view")
        logger.info("   - Sheets Upload Status: Uploaded")
        logger.info("   - Sheets Upload Date: 2024-01-15T10:30:00")
        logger.info("   - Google Drive File ID: FILE_ID")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Airtable demo failed: {e}")
        return False


def main():
    """
    Run all Google Sheets integration demos.
    """
    logger.info("🚀 SEA-E Google Sheets Integration Demo")
    logger.info("=" * 80)
    
    demos = [
        ("Single Mockup Upload", demo_single_mockup_upload),
        ("Batch Upload", demo_batch_upload),
        ("Airtable Integration", demo_airtable_integration)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        logger.info(f"\n🎯 Running: {demo_name}")
        try:
            success = demo_func()
            results.append((demo_name, success))
            
            if success:
                logger.info(f"✅ {demo_name} completed successfully")
            else:
                logger.error(f"❌ {demo_name} failed")
                
        except Exception as e:
            logger.error(f"❌ {demo_name} crashed: {e}")
            results.append((demo_name, False))
        
        logger.info("-" * 60)
    
    # Summary
    logger.info("\n📊 Demo Summary:")
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for demo_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"   {demo_name}: {status}")
    
    logger.info(f"\n🎉 Overall: {successful}/{total} demos successful")
    
    if successful == total:
        logger.info("🎊 All demos passed! Google Sheets integration is working correctly.")
        logger.info("\n🔗 Next Steps:")
        logger.info("   1. Generate mockups with enable_sheets_upload=True")
        logger.info("   2. Use the shareable URLs in your Etsy listings")
        logger.info("   3. Monitor uploads in your Google Sheets")
        logger.info("   4. Check Airtable for URL storage")
    else:
        logger.warning("⚠️ Some demos failed. Check the logs above for details.")


if __name__ == "__main__":
    main()
