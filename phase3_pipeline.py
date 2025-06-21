#!/usr/bin/env python3
"""
Phase 3 Premium Digital Products Pipeline - Main Script
======================================================

The ULTIMATE automation system for premium digital product creation!

This script orchestrates the complete Phase 3 workflow:
1. 📁 Detects PNG+SVG design file pairs
2. 📐 Creates 5 sized SVG files (24x36, 18x24, 16x20, 11x14, 5x7)
3. ☁️  Uploads to Google Drive with shareable links
4. 📄 Customizes PDF template with Google Drive link
5. 🖼️  Generates 7 high-quality mockups
6. 🔍 Creates AI-optimized SEO content
7. 🛒 Creates Etsy listing with mockups + digital PDF

SCALE TO 50-100 LISTINGS PER DAY WITH THIS SYSTEM!
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modules.phase3_premium_pipeline import Phase3PremiumPipeline

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "phase3_pipeline.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)

def validate_environment():
    """Validate that all required environment variables and files are present."""
    print("🔍 Validating environment...")
    
    # Check required environment variables
    required_env_vars = [
        "ETSY_API_KEY",
        "ETSY_REFRESH_TOKEN", 
        "ETSY_SHOP_ID",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    # Check required files
    required_files = [
        "credentials/google-sa.json",
        "docs/DIGITAL DOWNLOAD TEMPLATE.pdf"
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    # Check mockups directory
    mockups_dir = Path("assets/mockups/posters/Designs for Mockups")
    if not mockups_dir.exists():
        print(f"❌ Mockups directory not found: {mockups_dir}")
        return False
    
    # Check for design files
    png_files = list(mockups_dir.glob("*.png"))
    svg_files = list(mockups_dir.glob("*.svg"))
    
    if not png_files:
        print(f"❌ No PNG files found in {mockups_dir}")
        return False
    
    if not svg_files:
        print(f"❌ No SVG files found in {mockups_dir}")
        print(f"   Phase 3 requires SVG files for premium digital products")
        return False
    
    print("✅ Environment validation passed")
    print(f"   Found {len(png_files)} PNG files")
    print(f"   Found {len(svg_files)} SVG files")
    
    return True

def run_validate_mode(pipeline: Phase3PremiumPipeline):
    """Run pipeline in validate mode."""
    print("\n🧪 Running Phase 3 Pipeline - VALIDATE MODE")
    print("=" * 60)
    print("This will process the first design pair to validate the complete workflow")
    print()
    
    # Discover designs
    premium_designs = pipeline.discover_design_pairs()
    
    if not premium_designs:
        print("❌ No premium design pairs found for validation")
        return False
    
    # Process first design
    test_design = premium_designs[0]
    print(f"🎨 Testing with design: {test_design['design_name']}")
    print(f"   Folder: {test_design['folder_number']}")
    print(f"   Mockup file: {test_design['mockup_file'].name}")
    print(f"   Production files: {len(test_design['production_files'])}")
    print()
    
    result = pipeline.process_premium_design(test_design)
    
    if result.success:
        print(f"\n🎉 VALIDATION SUCCESS!")
        print(f"   ✅ JPEG files created: {result.jpeg_files_created}")
        print(f"   ✅ Google Drive folder: {result.google_drive_link}")
        print(f"   ✅ Custom PDF: {Path(result.customized_pdf).name}")
        print(f"   ✅ Mockups generated: {len(result.mockup_files)}")
        print(f"   ✅ SEO content: {len(result.seo_content['tags'])} tags")
        print(f"   ✅ Processing time: {result.processing_time:.1f}s")
        print()
        print("🚀 Phase 3 Premium Pipeline is READY FOR PRODUCTION!")
        return True
    else:
        print(f"\n❌ VALIDATION FAILED: {result.error}")
        return False

def run_batch_mode(pipeline: Phase3PremiumPipeline):
    """Run pipeline in batch mode."""
    print("\n🚀 Running Phase 3 Pipeline - BATCH MODE")
    print("=" * 60)
    print("This will process ALL premium design pairs for production")
    print()
    
    # Confirm batch processing
    response = input("⚠️  This will create real Etsy listings. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Batch processing cancelled")
        return False
    
    # Run batch processing
    results = pipeline.run_batch_processing()
    
    if results['success']:
        print(f"\n🎉 BATCH PROCESSING SUCCESS!")
        print(f"   ✅ Processed: {results['processed_count']}/{results['total_designs']}")
        print(f"   ⏱️  Total time: {results['total_time']:.1f}s")
        print(f"   📈 Average per design: {results['total_time']/results['total_designs']:.1f}s")
        print()
        print("🏆 PHASE 3 PREMIUM DIGITAL PRODUCTS PIPELINE COMPLETE!")
        return True
    else:
        print(f"\n❌ BATCH PROCESSING FAILED: {results['message']}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Phase 3 Premium Digital Products Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python phase3_pipeline.py --mode validate --verbose
  python phase3_pipeline.py --mode batch
  
This pipeline creates premium digital product listings with:
- 5 sized SVG files uploaded to Google Drive
- Custom PDF with embedded Google Drive links
- 7 high-quality mockups
- AI-optimized SEO content
- Complete Etsy listings ready for customers
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["validate", "batch"],
        default="validate",
        help="Processing mode (default: validate)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--mockups-dir",
        type=str,
        help="Custom mockups directory path"
    )
    
    parser.add_argument(
        "--pdf-template",
        type=str,
        help="Custom PDF template path"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    print("🚀 Phase 3 Premium Digital Products Pipeline")
    print("=" * 70)
    print("The ULTIMATE automation system for premium digital product creation!")
    print()
    
    # Validate environment
    if not validate_environment():
        print("\n❌ Environment validation failed. Please fix the issues above.")
        sys.exit(1)
    
    try:
        # Initialize pipeline
        print("\n⚙️  Initializing Phase 3 Premium Pipeline...")
        pipeline = Phase3PremiumPipeline(
            mockups_directory=args.mockups_dir,
            pdf_template_path=args.pdf_template,
            mode=args.mode
        )
        print("✅ Pipeline initialized successfully")
        
        # Run based on mode
        if args.mode == "validate":
            success = run_validate_mode(pipeline)
        else:
            success = run_batch_mode(pipeline)
        
        if success:
            print(f"\n🎯 Phase 3 Pipeline completed successfully!")
            if args.mode == "batch":
                print(f"🎉 Ready to scale to 50-100 listings per day!")
            sys.exit(0)
        else:
            print(f"\n❌ Phase 3 Pipeline failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
