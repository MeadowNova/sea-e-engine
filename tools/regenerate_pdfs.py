#!/usr/bin/env python3
"""
Regenerate PDFs for recent designs with correct Google Drive links.
This script recreates only the PDFs without running the full pipeline.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.pdf_customizer import PDFCustomizer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Regenerate PDFs for recent designs."""
    
    # Design name to Google Drive link mapping from recent pipeline runs
    design_mappings = {
        "van_gogh_starry_night": "https://drive.google.com/drive/folders/1EKfLGM85tgaT4Biz6Jc5XQpe1ikC-w5o",
        "picasso_cat_cubism_art": "https://drive.google.com/drive/folders/17YuLHRGvYy39c6r9wf-LA1ANfdimB0jF",
        "cubist_cat_with_glasses": "https://drive.google.com/drive/folders/1xs9IYwbSXbbpSySf27_LhAzE9qPQsipJ",
        "william_morris_flowers_vintage": "https://drive.google.com/drive/folders/1p9Q179aL045_jr0KGQdrlJTRMMBEFBIy",
        "renoir_cat_picnic_impressionism": "https://drive.google.com/drive/folders/1Sg8H69cxeWZ6GYOR7iMk-D1MPL47XMiy",
        "william_morris_floral_cat": "https://drive.google.com/drive/folders/1NFMeIhROoBUuAHgOtcTH6wExm46CCY2b",
        "andy_warhol_soupcan_cat_art": "https://drive.google.com/drive/folders/1EutQnzxPnZ-cvjShW4h7VIpc-_awPwXu",
        "gustav_klimt_cat_gallery_art": "https://drive.google.com/drive/folders/1C84XUwnhcAol1dz5DLaSL8Rdzadw8fJA",
        "matisse_cat_colorful_print": "https://drive.google.com/drive/folders/1Z_vpI7QepivXYn5Rur8_aGRQmNQbeGhw",
        
        # Add any missing designs with placeholder links (you can update these)
        "black_cat_in_bathrub_japanese_style": "https://drive.google.com/drive/folders/PLACEHOLDER1",
        "black_cat_in_shower_japanese_style": "https://drive.google.com/drive/folders/PLACEHOLDER2",
        "georgia_okeefe_black_cat_flower_print": "https://drive.google.com/drive/folders/PLACEHOLDER3",
    }
    
    logger.info("🔄 Starting PDF regeneration for recent designs")
    logger.info(f"📄 Template: docs/DIGITAL DOWNLOAD TEMPLATE.pdf")
    logger.info(f"📁 Output: output/phase3_custom_pdfs")
    logger.info(f"🎯 Designs to regenerate: {len(design_mappings)}")
    
    # Initialize PDF customizer
    try:
        customizer = PDFCustomizer(
            template_path="docs/DIGITAL DOWNLOAD TEMPLATE.pdf",
            output_dir="output/phase3_custom_pdfs"
        )
        
        # Validate template
        is_valid, error = customizer.validate_template()
        if not is_valid:
            logger.error(f"❌ Template validation failed: {error}")
            return False
            
        logger.info("✅ Template validation successful")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize PDF customizer: {e}")
        return False
    
    # Regenerate PDFs
    success_count = 0
    failed_count = 0
    
    for design_name, google_drive_link in design_mappings.items():
        logger.info(f"\n🎨 Regenerating PDF for: {design_name}")
        
        if "PLACEHOLDER" in google_drive_link:
            logger.warning(f"⚠️  Skipping {design_name} - placeholder link (update manually)")
            continue
            
        try:
            result = customizer.customize_pdf(
                design_name=design_name,
                google_drive_link=google_drive_link
            )
            
            if result.success:
                logger.info(f"✅ PDF regenerated: {result.output_path}")
                success_count += 1
            else:
                logger.error(f"❌ Failed to regenerate PDF: {result.error}")
                failed_count += 1
                
        except Exception as e:
            logger.error(f"❌ Error regenerating PDF for {design_name}: {e}")
            failed_count += 1
    
    # Summary
    logger.info(f"\n🎉 PDF Regeneration Complete!")
    logger.info(f"✅ Successful: {success_count}")
    logger.info(f"❌ Failed: {failed_count}")
    logger.info(f"📁 Check output/phase3_custom_pdfs/ for regenerated PDFs")
    
    if failed_count == 0:
        logger.info("🎯 All PDFs regenerated successfully!")
        return True
    else:
        logger.warning(f"⚠️  {failed_count} PDFs failed to regenerate")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
