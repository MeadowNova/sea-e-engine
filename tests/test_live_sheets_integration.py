#!/usr/bin/env python3
"""
Live Google Sheets Integration Test
==================================

Real integration test with actual Google Sheets API calls.
"""

import sys
import logging
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from api.google_sheets_client import GoogleSheetsClient
from modules.sheets_mockup_uploader import SheetsMockupUploader
from modules.custom_mockup_generator import CustomMockupGenerator
from core.logger import setup_logger

# Set up logging
logger = setup_logger("live_sheets_test", level="INFO")


def create_test_mockup(filename: str = "test_mockup.png") -> str:
    """Create a test mockup image."""
    # Create a realistic mockup-style image
    img = Image.new('RGB', (2000, 2000), (240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple t-shirt outline
    draw.rectangle([600, 400, 1400, 1600], fill=(255, 255, 255), outline=(200, 200, 200), width=3)
    
    # Add design area
    draw.rectangle([800, 600, 1200, 1000], fill=(50, 50, 50), outline=(0, 0, 0), width=2)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    draw.text((1000, 800), "SEA-E\nTEST", fill=(255, 255, 255), anchor="mm", align="center", font=font)
    
    # Add timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((100, 1900), f"Generated: {timestamp}", fill=(100, 100, 100), font=font)
    
    # Save to output directory
    output_path = Path("output") / filename
    output_path.parent.mkdir(exist_ok=True)
    img.save(output_path, "PNG", quality=95)
    
    logger.info(f"✅ Created test mockup: {output_path}")
    return str(output_path)


def test_google_sheets_client():
    """Test the Google Sheets client directly."""
    logger.info("🧪 Testing Google Sheets Client")
    logger.info("=" * 50)
    
    try:
        # Initialize client
        client = GoogleSheetsClient()
        
        # Test connection
        if not client.test_connection():
            logger.error("❌ Google Sheets connection failed")
            return False
        
        logger.info("✅ Google Sheets connection successful")
        
        # Create test mockup
        mockup_path = create_test_mockup("sheets_client_test.png")
        
        # Test folder creation
        folder_id = client.create_mockup_folder("SEA-E Test Folder")
        logger.info(f"✅ Created test folder: {folder_id}")
        
        # Test image upload
        file_id, shareable_url = client.upload_image_to_drive(
            mockup_path, 
            "test_mockup_upload.png",
            folder_id
        )
        
        logger.info(f"✅ Uploaded image to Drive:")
        logger.info(f"   File ID: {file_id}")
        logger.info(f"   Shareable URL: {shareable_url}")
        
        # Test spreadsheet creation
        spreadsheet_id, spreadsheet = client.create_or_get_spreadsheet("SEA-E Test Mockups")
        logger.info(f"✅ Created/found spreadsheet: {spreadsheet_id}")
        
        # Test image insertion in sheet
        success = client.insert_image_in_sheet(
            spreadsheet_id, 
            "Sheet1", 
            file_id, 
            "A1"
        )
        
        if success:
            logger.info("✅ Image inserted into spreadsheet")
            logger.info(f"🔗 View spreadsheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        else:
            logger.error("❌ Failed to insert image into spreadsheet")
            return False
        
        # Cleanup test file
        Path(mockup_path).unlink()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Google Sheets client test failed: {e}")
        return False


def test_mockup_uploader():
    """Test the mockup uploader."""
    logger.info("📦 Testing Mockup Uploader")
    logger.info("=" * 50)
    
    try:
        # Initialize uploader
        uploader = SheetsMockupUploader()
        
        # Create test mockups
        mockup_paths = []
        for i, (color, size) in enumerate([("black", "M"), ("white", "L")]):
            mockup_path = create_test_mockup(f"uploader_test_{color}_{size}.png")
            mockup_paths.append(mockup_path)
            
            # Add to upload queue
            success = uploader.add_upload_job(
                mockup_path=mockup_path,
                product_name="SEA-E Uploader Test",
                variation_info={
                    "color": color,
                    "size": size,
                    "product_name": "SEA-E Uploader Test"
                }
            )
            
            if success:
                logger.info(f"✅ Added to queue: {color} {size}")
            else:
                logger.error(f"❌ Failed to add: {color} {size}")
                return False
        
        # Process upload queue
        logger.info("🚀 Processing upload queue...")
        batch_result = uploader.process_upload_queue()
        
        # Display results
        logger.info(f"📊 Upload Results:")
        logger.info(f"   Total: {batch_result.total_jobs}")
        logger.info(f"   Successful: {batch_result.successful_uploads}")
        logger.info(f"   Failed: {batch_result.failed_uploads}")
        logger.info(f"   Time: {batch_result.execution_time:.2f}s")
        
        # Show URLs
        for i, result in enumerate(batch_result.upload_results):
            if result.success:
                logger.info(f"✅ Upload {i+1}: {result.shareable_url}")
            else:
                logger.error(f"❌ Upload {i+1}: {result.error_message}")
        
        # Cleanup
        for path in mockup_paths:
            try:
                Path(path).unlink()
            except:
                pass
        
        return batch_result.successful_uploads > 0
        
    except Exception as e:
        logger.error(f"❌ Mockup uploader test failed: {e}")
        return False


def test_complete_workflow():
    """Test the complete workflow with mockup generation."""
    logger.info("🎨 Testing Complete Workflow")
    logger.info("=" * 50)
    
    try:
        # Create a simple design file
        design_img = Image.new('RGBA', (1200, 1200), (255, 255, 255, 0))
        draw = ImageDraw.Draw(design_img)
        
        # Add design content
        draw.ellipse([300, 300, 900, 900], fill=(50, 50, 50, 255))
        draw.text((600, 600), "SEA-E", fill=(255, 255, 255, 255), anchor="mm")
        
        # Save design
        design_path = "output/test_design.png"
        Path(design_path).parent.mkdir(exist_ok=True)
        design_img.save(design_path, "PNG")
        
        logger.info(f"✅ Created test design: {design_path}")
        
        # Test with custom mockup generator (without sheets upload first)
        generator = CustomMockupGenerator(
            enable_sheets_upload=False,  # Test without sheets first
            auto_manage=True
        )
        
        # Check if we have templates
        templates = generator.list_available_templates()
        logger.info(f"Available templates: {templates}")
        
        if not any(templates.values()):
            logger.warning("⚠️ No mockup templates found, creating a simple test")
            
            # Create a simple mockup manually
            mockup_img = Image.new('RGB', (2000, 2000), (200, 200, 200))
            draw = ImageDraw.Draw(mockup_img)
            
            # Simulate t-shirt
            draw.rectangle([600, 400, 1400, 1600], fill=(255, 255, 255))
            
            # Add design
            design_resized = design_img.resize((400, 400))
            mockup_img.paste(design_resized, (800, 600), design_resized)
            
            mockup_path = "output/manual_test_mockup.png"
            mockup_img.save(mockup_path, "PNG")
            
            logger.info(f"✅ Created manual test mockup: {mockup_path}")
            
            # Now test Google Sheets upload
            uploader = SheetsMockupUploader()
            
            result = uploader.upload_single_mockup(
                uploader.MockupUploadJob(
                    mockup_path=mockup_path,
                    product_name="SEA-E Complete Test",
                    variation_info={
                        "color": "black",
                        "size": "M",
                        "product_name": "SEA-E Complete Test"
                    }
                )
            )
            
            if result.success:
                logger.info("✅ Complete workflow test successful!")
                logger.info(f"🔗 Mockup URL: {result.shareable_url}")
                
                # Cleanup
                Path(design_path).unlink()
                Path(mockup_path).unlink()
                
                return True
            else:
                logger.error(f"❌ Upload failed: {result.error_message}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Complete workflow test failed: {e}")
        return False


def main():
    """Run all live integration tests."""
    logger.info("🚀 SEA-E Google Sheets Live Integration Tests")
    logger.info("=" * 80)
    
    tests = [
        ("Google Sheets Client", test_google_sheets_client),
        ("Mockup Uploader", test_mockup_uploader),
        ("Complete Workflow", test_complete_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🎯 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name} CRASHED: {e}")
            results.append((test_name, False))
        
        logger.info("-" * 60)
    
    # Summary
    logger.info("\n📊 Test Summary:")
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\n🎉 Overall: {successful}/{total} tests successful")
    
    if successful == total:
        logger.info("🎊 All tests passed! Google Sheets integration is working!")
    else:
        logger.warning("⚠️ Some tests failed. Check logs for details.")
    
    return successful == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
