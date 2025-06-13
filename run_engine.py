
#!/usr/bin/env python3
"""
SEA-E: Scalable E-commerce Automation Engine
Main Entry Point

This is the executable entry point for the SEA-E automation system.
It loads configuration, initializes the engine, and processes product manifests.

Usage:
    python run_engine.py --manifest tshirts_q3_launch
    python run_engine.py --manifest posters_q3_launch --dry-run
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure src directory is in Python path for imports
# This helps resolve imports like 'from core.logger import ...'
# by making the 'src' directory a recognized root for modules.
project_root = Path(__file__).parent.resolve()
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from core.logger import setup_logger

# Load environment variables
load_dotenv()

# Set up logging
logger = setup_logger("sea-engine-main")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SEA-E: Scalable E-commerce Automation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_engine.py --manifest tshirts_q3_launch
  python run_engine.py --manifest posters_q3_launch --dry-run
  python run_engine.py --list-manifests
        """
    )
    
    parser.add_argument(
        "--manifest",
        type=str,
        help="Manifest key to process (from config/manifests.json)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no actual API calls)"
    )
    
    parser.add_argument(
        "--list-manifests",
        action="store_true",
        help="List available manifests and exit"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    return parser.parse_args()


def validate_environment():
    """Validate that required environment variables are set."""
    required_vars = [
        "PRINTIFY_API_KEY",
        "PRINTIFY_SHOP_ID",
        "ETSY_API_KEY",
        "ETSY_ACCESS_TOKEN",
        "ETSY_SHOP_ID",
        "AIRTABLE_API_KEY",
        "AIRTABLE_BASE_ID"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please check your .env file and ensure all credentials are set")
        return False
    
    return True


def check_project_structure():
    """Check that required project directories and files exist."""
    required_dirs = [
        "config",
        "src/core",
        "src/modules",
        "src/services",
        "logs",
        "output"
    ]
    
    required_files = [
        "config/manifests.json",
        "src/core/engine.py"
    ]
    
    missing_dirs = [d for d in required_dirs if not Path(d).exists()]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_dirs:
        logger.warning(f"Missing directories: {missing_dirs}")
        logger.info("Creating missing directories...")
        for d in missing_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {d}")
    
    if missing_files:
        logger.error(f"Missing required files: {missing_files}")
        logger.error("Please ensure the project structure is complete")
        return False
    
    return True


def main():
    """Main function."""
    logger.info("=" * 60)
    logger.info("SEA-E: Scalable E-commerce Automation Engine v2.1")
    logger.info("=" * 60)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Update log level if specified
    if args.log_level != "INFO":
        logger.setLevel(getattr(logging, args.log_level))
        logger.info(f"Log level set to: {args.log_level}")
    
    try:
        # Validate environment
        if not validate_environment():
            logger.error("❌ Environment validation failed")
            return 1
        
        # Check project structure
        if not check_project_structure():
            logger.error("❌ Project structure validation failed")
            return 1
        
        logger.info("✅ Environment and project structure validated")
        
        # Handle list manifests command
        if args.list_manifests:
            logger.info("📋 Available product status filters:")
            logger.info("  - design: Process products in Design status")
            logger.info("  - mockup: Process products in Mockup status")
            logger.info("  - product: Process products in Product status")
            logger.info("  - all: Process all products regardless of status")
            return 0
        
        # Validate manifest argument
        if not args.manifest:
            logger.error("❌ No manifest specified. Use --manifest <name> or --list-manifests")
            return 1
        
        # Initialize and run engine
        logger.info(f"🚀 Starting SEA-E Engine with Airtable integration")
        
        if args.dry_run:
            logger.info("🔍 Running in DRY-RUN mode - no actual API calls will be made")
        
        # Import and initialize the SEA Engine
        from sea_engine import SEAEngine
        from data.airtable_models import ProductStatus
        
        engine = SEAEngine()
        
        # Validate environment (engine does this in __init__)
        if not engine.validate_environment():
            logger.error("❌ Failed to validate environment for SEA Engine")
            return 1
        
        logger.info("✅ SEA Engine initialized successfully")
        
        # Process products based on manifest or default to Design status
        if args.manifest == "design":
            status_filter = ProductStatus.DESIGN
        elif args.manifest == "mockup":
            status_filter = ProductStatus.MOCKUP
        elif args.manifest == "product":
            status_filter = ProductStatus.PRODUCT
        else:
            status_filter = ProductStatus.DESIGN  # Default
        
        logger.info(f"📊 Processing products with status: {status_filter.value}")
        
        # Run batch processing
        results = engine.process_batch(status_filter)
        
        # Report results
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        logger.info(f"✅ Batch processing completed:")
        logger.info(f"   📈 Successful: {successful}")
        logger.info(f"   ❌ Failed: {failed}")
        logger.info(f"   📊 Total: {len(results)}")
        
        return 0 if failed == 0 else 1
        
    except KeyboardInterrupt:
        logger.warning("⚠️ Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        logger.exception("Full error details:")
        return 1
    finally:
        logger.info("=" * 60)


if __name__ == "__main__":
    sys.exit(main())
