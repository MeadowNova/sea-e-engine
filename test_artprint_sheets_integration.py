#!/usr/bin/env python3
"""
Test Art Print Google Sheets Integration
========================================

Test that art print mockups are successfully uploaded to Google Sheets
and shareable URLs are generated for Airtable integration.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

import logging
from modules.sheets_mockup_uploader import SheetsMockupUploader
from modules.perspective_mockup_generator import PerspectiveMockupGenerator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_artprint_sheets_integration():
    """Test art print mockup upload to Google Sheets."""
    logger.info("🎯 Testing Art Print Google Sheets Integration")
    logger.info("=" * 60)
    
    # Design file for testing
    design_file = "assets/mockups/posters/Designs for Mockups/24x36 TEMPLATE.png"
    
    # Verify design file exists
    if not Path(design_file).exists():
        raise FileNotFoundError(f"Design file not found: {design_file}")
    
    logger.info(f"✅ Using design: {design_file}")
    
    try:
        # Initialize perspective generator
        generator = PerspectiveMockupGenerator(
            assets_dir="assets",
            output_dir="output"
        )
        
        # Initialize sheets uploader
        sheets_uploader = SheetsMockupUploader(
            config_file="config/google_sheets_config.json",
            credentials_path="credentials/google-sa.json"
        )
        
        logger.info("✅ Initialized generators and uploader")
        
        # Test with a few key art print templates (including angled ones)
        test_templates = ['2.jpg', '5.jpg', '1.jpg']  # Mix of angled and rectangular
        
        results = []
        
        for template_name in test_templates:
            logger.info(f"\n🖼️ Testing art print template: {template_name}")
            
            # Generate mockup
            mockup_result = generator.generate_perspective_mockup(design_file, template_name)
            
            if not mockup_result['success']:
                logger.error(f"  ❌ Failed to generate mockup: {mockup_result['error']}")
                continue
            
            mockup_path = mockup_result['mockup_path']
            logger.info(f"  ✅ Generated mockup: {Path(mockup_path).name}")
            
            # Prepare variation info for art prints
            variation_info = {
                'product_type': 'art_prints',
                'template': template_name,
                'size': '24x36',
                'frame_type': 'angled' if template_name in ['2.jpg', '5.jpg', '6.jpg'] else 'rectangular'
            }
            
            # Add upload job
            job_added = sheets_uploader.add_upload_job(
                mockup_path=mockup_path,
                product_name="24x36 Art Print Test",
                variation_info=variation_info,
                airtable_record_id=None,  # No Airtable record for this test
                priority=1
            )
            
            if job_added:
                logger.info(f"  ✅ Added to upload queue")
            else:
                logger.error(f"  ❌ Failed to add to upload queue")
                continue
            
            results.append({
                'template': template_name,
                'mockup_path': mockup_path,
                'job_added': job_added
            })
        
        # Process upload queue
        if results:
            logger.info(f"\n📤 Processing {len(results)} upload jobs...")
            
            batch_result = sheets_uploader.process_upload_queue(max_workers=2)
            
            logger.info(f"\n📊 Upload Results:")
            logger.info(f"  Total jobs: {batch_result.total_jobs}")
            logger.info(f"  Successful uploads: {batch_result.successful_uploads}")
            logger.info(f"  Failed uploads: {batch_result.failed_uploads}")
            logger.info(f"  Execution time: {batch_result.execution_time:.1f}s")
            
            # Display individual results
            if batch_result.upload_results:
                logger.info(f"\n📁 Individual Upload Results:")
                for i, upload_result in enumerate(batch_result.upload_results):
                    template = results[i]['template'] if i < len(results) else 'Unknown'
                    
                    if upload_result.success:
                        logger.info(f"  ✅ {template}: {upload_result.shareable_url}")
                    else:
                        logger.info(f"  ❌ {template}: {upload_result.error_message}")
            
            # Display errors if any
            if batch_result.errors:
                logger.info(f"\n⚠️ Errors:")
                for error in batch_result.errors:
                    logger.error(f"  - {error}")
            
            return batch_result
        
        else:
            logger.error("❌ No mockups generated for upload testing")
            return None
            
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return None


def validate_sheets_integration():
    """Validate the Google Sheets integration results."""
    logger.info(f"\n🔍 Validating Art Print Sheets Integration")
    logger.info("=" * 50)
    
    batch_result = test_artprint_sheets_integration()
    
    if not batch_result:
        logger.error("❌ No batch results to validate")
        return False
    
    # Check success criteria
    success_rate = (batch_result.successful_uploads / batch_result.total_jobs) * 100 if batch_result.total_jobs > 0 else 0
    
    logger.info(f"📊 Upload Success Rate: {success_rate:.1f}%")
    
    # Validate shareable URLs
    successful_uploads = [r for r in batch_result.upload_results if r.success]
    urls_generated = [r for r in successful_uploads if r.shareable_url]
    
    logger.info(f"🔗 Shareable URLs Generated: {len(urls_generated)}/{len(successful_uploads)}")
    
    if urls_generated:
        logger.info(f"\n✅ Generated Shareable URLs:")
        for result in urls_generated:
            logger.info(f"  🔗 {result.shareable_url}")
    
    # Success criteria: 100% upload success and all URLs generated
    integration_success = (
        success_rate == 100.0 and 
        len(urls_generated) == len(successful_uploads) and
        batch_result.total_jobs > 0
    )
    
    return integration_success


def main():
    """Run art print Google Sheets integration testing."""
    logger.info("🎯 Art Print Google Sheets Integration Test")
    logger.info("=" * 60)
    
    # Check dependencies
    try:
        import gspread
        import google.auth
        logger.info(f"✅ Google API libraries available")
    except ImportError as e:
        logger.error(f"❌ Missing Google API libraries: {e}")
        logger.info("Please install: pip install gspread google-auth google-auth-oauthlib google-api-python-client")
        return
    
    # Test integration
    integration_passed = validate_sheets_integration()
    
    # Final summary
    logger.info(f"\n🎉 Art Print Sheets Integration Testing Complete!")
    logger.info(f"🎯 Integration validation: {'✅ PASSED' if integration_passed else '❌ FAILED'}")
    
    if integration_passed:
        logger.info(f"\n🚀 Art Print Sheets Integration Ready!")
        logger.info(f"  ✅ Art print mockups uploading to Google Sheets")
        logger.info(f"  ✅ Shareable URLs generated successfully")
        logger.info(f"  ✅ Ready for Airtable integration")
        logger.info(f"  ✅ Complete workflow validated")
        logger.info(f"  🎯 Ready for commit, tag, and push")
    else:
        logger.info(f"\n⚠️ Integration needs attention")
        logger.info(f"  📝 Review Google Sheets configuration")
        logger.info(f"  📝 Check API credentials and permissions")
        logger.info(f"  📝 Verify upload functionality")
    
    logger.info(f"\n📁 Check Google Sheets for uploaded art print mockups!")


if __name__ == "__main__":
    main()
