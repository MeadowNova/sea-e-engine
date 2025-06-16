#!/usr/bin/env python3
"""
SEA-E Phase 2 Digital Download Pipeline
======================================

Entry-point CLI for the digital download automation pipeline.
Turns finished digital-art mockups into fully drafted Etsy listings.

Usage:
    python pipeline.py --mode validate    # Process first file for validation
    python pipeline.py --mode batch       # Process files in batches of 10

Environment Variables Required:
    OPENAI_API_KEY          - OpenAI API key for SEO generation
    ETSY_API_KEY           - Etsy API key
    ETSY_REFRESH_TOKEN     - Etsy refresh token
    ETSY_SHOP_ID           - Etsy shop ID
    REFERENCE_LISTING_ID   - Etsy listing ID to use as template (optional)

Hard Rules:
- Use OAuth 2.0 for Etsy & Drive; refresh tokens automatically
- Respect Etsy write-rate limit (10 calls/sec); throttle with exponential back-off
- Fail fast: if any step errors, log status=error:<message> and halt batch
- Unit-test helpers with pytest; aim 90%+ coverage
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from modules.digital_download_pipeline import DigitalDownloadPipeline

def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('pipeline.log')
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

def validate_environment():
    """Validate required environment variables."""
    required_vars = [
        'OPENAI_API_KEY',
        'ETSY_API_KEY', 
        'ETSY_REFRESH_TOKEN',
        'ETSY_SHOP_ID'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables and try again.")
        return False
    
    # Optional variables
    optional_vars = ['REFERENCE_LISTING_ID']
    for var in optional_vars:
        if not os.getenv(var):
            print(f"⚠️  Optional environment variable not set: {var}")
    
    return True

def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(
        description='SEA-E Phase 2 Digital Download Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--mode',
        choices=['validate', 'batch'],
        required=True,
        help='Processing mode: validate (first file only) or batch (process multiple files)'
    )
    
    parser.add_argument(
        '--mockups-dir',
        type=str,
        help='Path to mockups directory (default: assets/mockups/posters/Designs for Mockups)'
    )
    
    parser.add_argument(
        '--reference-listing',
        type=str,
        help='Etsy listing ID to use as template (overrides REFERENCE_LISTING_ID env var)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform dry run without creating actual Etsy listings'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    print("🚀 SEA-E Phase 2 Digital Download Pipeline")
    print("=" * 50)
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    try:
        # Initialize pipeline
        logger.info(f"Initializing pipeline in {args.mode} mode...")
        
        pipeline = DigitalDownloadPipeline(
            mockups_directory=args.mockups_dir,
            reference_listing_id=args.reference_listing or os.getenv('REFERENCE_LISTING_ID'),
            mode=args.mode
        )
        
        # Override mode for dry run
        if args.dry_run:
            pipeline.mode = "validate"
            logger.info("Dry run mode: will not create actual Etsy listings")
        
        # Run pipeline
        logger.info("Starting pipeline execution...")
        summary = pipeline.run_pipeline()
        
        # Generate and display report
        report = pipeline.generate_report(summary)
        print(report)
        
        # Exit with appropriate code
        if summary['success']:
            logger.info("Pipeline completed successfully")
            
            if args.mode == "validate":
                print("\n🎯 VALIDATION COMPLETE")
                print("Ready to run in batch mode with: python pipeline.py --mode batch")
            else:
                print(f"\n🎉 BATCH PROCESSING COMPLETE")
                print(f"Successfully processed {summary['successful_count']} designs")
            
            sys.exit(0)
        else:
            logger.error("Pipeline completed with errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        print("\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Pipeline failed with unexpected error: {str(e)}")
        print(f"\n❌ Pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
