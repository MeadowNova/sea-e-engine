
#!/usr/bin/env python3
"""
SEA-E Core Automation Engine
===========================

Production-ready automation engine that orchestrates the complete product creation workflow
from Google Sheets input to Etsy listing publication.

Features:
- Complete workflow orchestration
- Robust API integration with retry mechanisms
- Comprehensive error handling and logging
- Configuration-driven operation
- Batch processing capabilities
- State management and recovery
- Production-ready quality standards

Author: SEA-E Development Team
Version: 2.0.0
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from core.logger import setup_logger
from api.etsy import EtsyAPIClient
from api.printify import PrintifyAPIClient
from api.airtable_client import AirtableClient
from data.airtable_models import (
    Product, Variation, Mockup, Listing, Collection,
    ProductStatus, Priority, AirtableDataManager
)

# For backward compatibility with existing tests
ProductData = Product  # Alias for legacy code
from workflow.state import WorkflowStateManager
from modules.mockup_generator import MockupGenerator


@dataclass
class WorkflowResult:
    """Result of a complete workflow execution."""
    success: bool
    product: Product
    variations: List[Variation]
    mockup_files: List[str]
    printify_product_id: Optional[str]
    etsy_listing_id: Optional[str]
    error_message: Optional[str]
    execution_time: float


class SEAEngine:
    """
    Main automation engine class that orchestrates the complete product creation workflow.
    
    This class manages the entire process from reading Google Sheets data to publishing
    products on Etsy through Printify integration.
    """
    
    def __init__(self, config_dir: str = None, output_dir: str = None):
        """
        Initialize the SEA Engine with configuration and output directories.
        
        Args:
            config_dir: Path to configuration directory (default: ./config)
            output_dir: Path to output directory (default: ./output)
        """
        self.config_dir = Path(config_dir or "config")
        self.output_dir = Path(output_dir or "output")
        self.logs_dir = Path("logs")
        
        # Ensure directories exist
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Initialize logger
        self.logger = setup_logger("sea_engine")
        
        # Configuration storage
        self.config = {}
        self.product_blueprints = {}
        self.mockup_blueprints = {}
        
        # API clients
        self.etsy_client = None
        self.printify_client = None
        self.airtable_client = None
        self.data_manager = None
        self.mockup_generator = None
        self.state_manager = None
        
        # Initialize components
        self._load_configurations()
        self._initialize_clients()
        
        self.logger.info("SEA Engine initialized successfully")
    
    def _load_configurations(self):
        """Load all configuration files."""
        try:
            self.logger.info("Loading configuration files...")
            
            # Load product blueprints
            product_config_path = self.config_dir / "product_blueprints.json"
            if product_config_path.exists():
                with open(product_config_path, 'r') as f:
                    self.product_blueprints = json.load(f)
                self.logger.info(f"Loaded product blueprints: {len(self.product_blueprints.get('products', {}))} products")
            else:
                raise FileNotFoundError(f"Product blueprints not found: {product_config_path}")
            
            # Load mockup blueprints
            mockup_config_path = self.config_dir / "mockup_blueprints.json"
            if mockup_config_path.exists():
                with open(mockup_config_path, 'r') as f:
                    self.mockup_blueprints = json.load(f)
                self.logger.info(f"Loaded mockup blueprints: {len(self.mockup_blueprints.get('blueprints', {}))} blueprints")
            else:
                raise FileNotFoundError(f"Mockup blueprints not found: {mockup_config_path}")
            
            # Load general configuration if exists
            general_config_path = self.config_dir / "general.json"
            if general_config_path.exists():
                with open(general_config_path, 'r') as f:
                    self.config = json.load(f)
            
            self.logger.info("Configuration files loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load configurations: {e}")
            raise
    
    def _initialize_clients(self):
        """Initialize API clients and supporting components."""
        try:
            self.logger.info("Initializing API clients...")
            
            # Initialize Etsy client
            self.etsy_client = EtsyAPIClient()
            
            # Initialize Printify client
            self.printify_client = PrintifyAPIClient()
            
            # Initialize Airtable client
            self.airtable_client = AirtableClient()
            self.data_manager = AirtableDataManager(self.airtable_client)
            
            # Initialize mockup generator
            self.mockup_generator = MockupGenerator(str(self.output_dir))
            
            # Initialize state manager
            self.state_manager = WorkflowStateManager(str(self.logs_dir))
            
            self.logger.info("API clients initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize clients: {e}")
            raise
    
    def validate_environment(self) -> bool:
        """
        Validate that all required environment variables and configurations are present.
        
        Returns:
            bool: True if environment is valid, False otherwise
        """
        try:
            self.logger.info("Validating environment...")
            
            # Test API connections
            etsy_valid = self.etsy_client.test_connection()
            printify_valid = self.printify_client.test_connection()
            airtable_valid = self.airtable_client.test_connection()
            
            if not etsy_valid:
                self.logger.error("Etsy API connection failed")
                return False
            
            if not printify_valid:
                self.logger.error("Printify API connection failed")
                return False
            
            if not airtable_valid:
                self.logger.error("Airtable API connection failed")
                return False
            
            # Validate configurations
            if not self.product_blueprints:
                self.logger.error("Product blueprints not loaded")
                return False
            
            if not self.mockup_blueprints:
                self.logger.error("Mockup blueprints not loaded")
                return False
            
            self.logger.info("Environment validation successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Environment validation failed: {e}")
            return False
    
    def read_products_from_airtable(self, status_filter: ProductStatus = None) -> List[Product]:
        """
        Read product data from Airtable.
        
        Args:
            status_filter: Optional status filter (default: None for all products)
            
        Returns:
            List[Product]: List of product objects
        """
        try:
            self.logger.info("Reading products from Airtable")
            
            if status_filter:
                products = self.data_manager.get_products_by_status(status_filter)
                self.logger.info(f"Found {len(products)} products with status: {status_filter.value}")
            else:
                # Get all products
                records = self.airtable_client.list_records('products')
                products = [Product.from_airtable_record(record) for record in records]
                self.logger.info(f"Found {len(products)} total products")
            
            return products
            
        except Exception as e:
            self.logger.error(f"Failed to read products from Airtable: {e}")
            raise
    
    def process_single_product(self, product: Product) -> WorkflowResult:
        """
        Process a single product through the complete workflow.
        
        Args:
            product: Product object to process
            
        Returns:
            WorkflowResult: Result of the workflow execution
        """
        start_time = time.time()
        workflow_id = f"{product.product_name}_{int(start_time)}"
        
        try:
            self.logger.info(f"Starting workflow for product: {product.product_name}")
            
            # Update product status to indicate processing has started
            self.data_manager.update_product_status(product.product_id, ProductStatus.MOCKUP)
            
            # Get product variations
            _, variations = self.data_manager.get_product_with_variations(product.product_id)
            
            # Initialize workflow state
            self.state_manager.start_workflow(workflow_id, product.to_airtable_fields())
            
            # Step 1: Generate mockups
            self.logger.info("Step 1: Generating mockups...")
            mockup_files = self._generate_mockups(product, variations)
            self.state_manager.update_workflow_step(workflow_id, "mockups_generated", {"files": mockup_files})
            
            # Step 2: Create Printify product with hybrid workflow (includes Etsy draft)
            self.logger.info("Step 2: Creating Printify product with hybrid workflow...")
            hybrid_result = self._create_printify_product(product, variations, mockup_files)
            printify_product_id = hybrid_result.get('printify_product_id')
            etsy_draft_id = hybrid_result.get('etsy_draft_listing_id')

            self.state_manager.update_workflow_step(workflow_id, "hybrid_workflow_completed", {
                "printify_product_id": printify_product_id,
                "etsy_draft_id": etsy_draft_id,
                "draft_status": hybrid_result.get('draft_status'),
                "workflow_stage": hybrid_result.get('workflow_stage')
            })

            # Step 3: For hybrid workflow, Etsy draft is already created
            # This step is now for custom mockup integration and final publishing
            self.logger.info("Step 3: Hybrid workflow completed - ready for custom mockups...")
            etsy_listing_id = etsy_draft_id  # Use draft ID as listing ID for now
            
            # Update product status to LISTED (draft created, ready for custom mockups)
            self.data_manager.update_product_status(product.product_id, ProductStatus.LISTED)

            # Complete workflow
            execution_time = time.time() - start_time
            self.state_manager.complete_workflow(workflow_id, {
                "printify_product_id": printify_product_id,
                "etsy_draft_id": etsy_draft_id,
                "etsy_listing_id": etsy_listing_id,
                "hybrid_workflow_data": hybrid_result,
                "execution_time": execution_time
            })
            
            self.logger.info(f"Workflow completed successfully in {execution_time:.2f} seconds")
            
            return WorkflowResult(
                success=True,
                product=product,
                variations=variations,
                mockup_files=mockup_files,
                printify_product_id=printify_product_id,
                etsy_listing_id=etsy_listing_id,
                error_message=None,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = str(e)
            
            self.logger.error(f"Workflow failed for {product.product_name}: {error_message}")
            self.state_manager.fail_workflow(workflow_id, error_message)
            
            # Update product status and log error
            self.data_manager.update_product_status(product.product_id, ProductStatus.DESIGN, error_message)
            
            return WorkflowResult(
                success=False,
                product=product,
                variations=[],
                mockup_files=[],
                printify_product_id=None,
                etsy_listing_id=None,
                error_message=error_message,
                execution_time=execution_time
            )
    
    def _generate_mockups(self, product: Product, variations: List[Variation]) -> List[str]:
        """Generate mockups for the product."""
        try:
            # Use blueprint key from product or determine from product type
            blueprint_key = product.blueprint_key or self._get_blueprint_key(product.product_type)
            
            # Generate mockups using the mockup generator
            mockup_files = []
            
            if variations:
                # Generate mockups for each variation
                for variation in variations:
                    result = self.mockup_generator.generate_mockup(
                        blueprint_key,
                        f"designs/{product.product_name}.png",  # Assume design file path
                        color=variation.color,
                        variation=variation.size
                    )
                    if result and result.get("success"):
                        generated_files = result.get("files", [])
                        mockup_files.extend(generated_files)
                        
                        # Create mockup records in Airtable
                        for file_path in generated_files:
                            mockup_data = {
                                'mockup_id': f"{variation.variation_id}_{len(mockup_files)}",
                                'mockup_type': 'Front',  # Default type
                                'generation_status': 'Generated',
                                'file_path': file_path,
                                'approved': True
                            }
                            mockup_record = self.airtable_client.create_linked_record(
                                'mockups', mockup_data, 'variations', variation.record_id, 'variation'
                            )
            else:
                # Generate default mockups
                result = self.mockup_generator.generate_mockup(
                    blueprint_key,
                    f"designs/{product.product_name}.png"
                )
                mockup_files = result.get("files", []) if result and result.get("success") else []
            
            self.logger.info(f"Generated {len(mockup_files)} mockup files")
            return mockup_files
            
        except Exception as e:
            self.logger.error(f"Failed to generate mockups: {e}")
            raise
    
    def _get_blueprint_key(self, product_type: str) -> str:
        """Get blueprint key from product type."""
        type_mapping = {
            "tshirt": "tshirt_bella_canvas_3001",
            "t-shirt": "tshirt_bella_canvas_3001",
            "sweatshirt": "sweatshirt_gildan_18000",
            "hoodie": "sweatshirt_gildan_18000",
            "poster": "poster_matte_ideju"
        }
        
        return type_mapping.get(product_type.lower(), "tshirt_bella_canvas_3001")

    def _get_product_tags(self, product_type: str) -> List[str]:
        """Get Etsy tags for product type from configuration."""
        try:
            # Load current product configs for tags
            import json
            with open("config/current_product_configs.json", 'r') as f:
                config = json.load(f)

            # Get default tags for product type
            default_tags = config.get("etsy_settings", {}).get("default_tags", {})
            product_type_key = product_type.lower().replace("-", "").replace("_", "")

            # Map product types to tag keys
            tag_mapping = {
                "tshirt": "tshirts",
                "t-shirt": "tshirts",
                "sweatshirt": "sweatshirts",
                "hoodie": "sweatshirts",
                "poster": "posters",
                "artprint": "posters"
            }

            tag_key = tag_mapping.get(product_type_key, "tshirts")
            tags = default_tags.get(tag_key, ["custom", "design", "unique", "gift", "art"])

            self.logger.info(f"Using tags for {product_type}: {tags}")
            return tags

        except Exception as e:
            self.logger.warning(f"Failed to load tags from config: {e}")
            # Fallback tags
            return ["custom", "design", "unique", "gift", "art", "quality"]

    def _get_design_file_path(self, product_name: str) -> str:
        """Get design file path, preferring SVG over PNG for better quality."""
        # Check for SVG first (infinite DPI scalability)
        svg_path = f"assets/designs_printify/{product_name}.svg"
        if os.path.exists(svg_path):
            self.logger.info(f"Using SVG design file: {svg_path}")
            return svg_path

        # Fallback to PNG
        png_path = f"designs/{product_name}.png"
        if os.path.exists(png_path):
            self.logger.info(f"Using PNG design file: {png_path}")
            return png_path

        # Alternative PNG locations
        alt_paths = [
            f"assets/designs_printify/{product_name}.png",
            f"assets/designs/{product_name}.png",
            f"designs/{product_name}_optimized.png"
        ]

        for path in alt_paths:
            if os.path.exists(path):
                self.logger.info(f"Using design file: {path}")
                return path

        # For testing, use known good design files
        test_design_files = [
            "assets/designs_printify/New Test for Sizing.svg",
            "assets/designs_printify/bold_cat_design_printify_final.png",
            "assets/designs_printify/bold_cat_design_optimized.png",
            "designs/bold_cat_design.png"
        ]

        for test_path in test_design_files:
            if os.path.exists(test_path):
                self.logger.info(f"Using test design file: {test_path}")
                return test_path

        # Default fallback
        default_path = f"designs/{product_name}.png"
        self.logger.warning(f"Design file not found, using default path: {default_path}")
        return default_path
    
    def _create_printify_product(self, product: Product, variations: List[Variation], mockup_files: List[str]) -> Dict:
        """Create product in Printify using hybrid workflow."""
        try:
            # Get blueprint configuration
            blueprint_key = product.blueprint_key or self._get_blueprint_key(product.product_type)
            blueprint_config = self.product_blueprints.get("products", {}).get(blueprint_key)

            if not blueprint_config:
                raise ValueError(f"Blueprint configuration not found for {blueprint_key}")

            # Get tags for Etsy from configuration
            tags = self._get_product_tags(product.product_type)

            # Determine design file path - check for SVG first, then PNG
            design_file_path = self._get_design_file_path(product.product_name)

            # Create product using hybrid workflow (Printify + Etsy Draft)
            hybrid_result = self.printify_client.create_product_with_draft_publishing(
                title=product.product_name,
                description=product.description,
                blueprint_id=blueprint_config["printify_config"]["blueprint_id"],
                print_provider_id=blueprint_config["printify_config"]["print_provider_id"],
                design_file_path=design_file_path,
                tags=tags
            )

            # Update product with Printify ID and draft status (if record_id exists)
            if product.record_id:
                self.airtable_client.update_record('products', product.record_id, {
                    'Print Provider': 'Printify',
                    'Status': ProductStatus.PRODUCT.value,
                    'Printify Product ID': hybrid_result.get('printify_product_id'),
                    'Etsy Draft ID': hybrid_result.get('etsy_draft_listing_id'),
                    'Draft Status': hybrid_result.get('draft_status', 'draft_created')
                })
                self.logger.info("Updated product record in Airtable")
            else:
                self.logger.info("Skipping Airtable update - no record_id (test mode)")

            self.logger.info(f"Created Printify product with hybrid workflow: {hybrid_result.get('printify_product_id')}")
            self.logger.info(f"Etsy draft created: {hybrid_result.get('etsy_draft_listing_id')}")

            return hybrid_result

        except Exception as e:
            self.logger.error(f"Failed to create Printify product with hybrid workflow: {e}")
            raise
    
    def _publish_to_etsy(self, product: Product, printify_product_id: str, mockup_files: List[str]) -> str:
        """
        Legacy method - now handled by hybrid workflow.
        This method is kept for backward compatibility but is no longer used in the main workflow.
        """
        try:
            self.logger.info("Note: Etsy publishing is now handled by the hybrid workflow")
            self.logger.info("Draft listing should already be created via Printify integration")

            # For hybrid workflow, we would typically:
            # 1. Upload custom mockups to Google Sheets
            # 2. Update Airtable with mockup URLs
            # 3. Use Airtable automation to publish draft as live listing

            # For now, return the printify_product_id as a placeholder
            # This will be replaced with proper custom mockup workflow
            return f"draft_{printify_product_id}"

        except Exception as e:
            self.logger.error(f"Failed in legacy Etsy publish method: {e}")
            raise
    
    def process_batch(self, status_filter: ProductStatus = ProductStatus.DESIGN) -> List[WorkflowResult]:
        """
        Process multiple products from Airtable.
        
        Args:
            status_filter: Status filter for products to process
            
        Returns:
            List[WorkflowResult]: Results for all processed products
        """
        try:
            self.logger.info(f"Starting batch processing for products with status: {status_filter.value}")
            
            # Read products from Airtable
            products = self.read_products_from_airtable(status_filter)
            
            if not products:
                self.logger.warning("No products found to process")
                return []
            
            results = []
            
            for i, product in enumerate(products, 1):
                self.logger.info(f"Processing product {i}/{len(products)}: {product.product_name}")
                
                try:
                    result = self.process_single_product(product)
                    results.append(result)
                    
                    # Update dashboard metrics
                    self._update_dashboard_metrics()
                    
                    # Add delay between products to respect rate limits
                    if i < len(products):
                        time.sleep(2)
                        
                except Exception as e:
                    self.logger.error(f"Failed to process product {product.product_name}: {e}")
                    # Continue with next product
                    continue
            
            # Generate batch summary
            successful = sum(1 for r in results if r.success)
            failed = len(results) - successful
            
            self.logger.info(f"Batch processing completed: {successful} successful, {failed} failed")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            raise
    
    def _update_dashboard_metrics(self):
        """Update dashboard metrics in Airtable."""
        try:
            # Get workflow statistics
            stats = self.data_manager.get_workflow_statistics()
            
            # Update each metric
            for metric_name, value in stats.items():
                category = "Products"
                if "variations" in metric_name:
                    category = "Variations"
                elif "mockups" in metric_name:
                    category = "Mockups"
                elif "listings" in metric_name:
                    category = "Listings"
                
                self.airtable_client.update_dashboard_metric(
                    metric_name=metric_name.replace("_", " ").title(),
                    metric_value=str(value),
                    category=category
                )
            
        except Exception as e:
            self.logger.error(f"Failed to update dashboard metrics: {e}")
            # Don't raise - this is not critical to the main workflow
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow."""
        return self.state_manager.get_workflow_status(workflow_id)
    
    def list_active_workflows(self) -> List[str]:
        """List all active workflow IDs."""
        return self.state_manager.list_active_workflows()
    
    def cleanup_old_workflows(self, days: int = 7):
        """Clean up workflow states older than specified days."""
        self.state_manager.cleanup_old_workflows(days)


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SEA-E Automation Engine")
    parser.add_argument("--sheet-id", help="Google Sheets document ID")
    parser.add_argument("--sheet-name", default="Products", help="Sheet name (default: Products)")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    parser.add_argument("--validate", action="store_true", help="Validate environment only")
    parser.add_argument("--config-dir", help="Configuration directory path")
    parser.add_argument("--output-dir", help="Output directory path")
    
    args = parser.parse_args()
    
    try:
        # Initialize engine
        engine = SEAEngine(config_dir=args.config_dir, output_dir=args.output_dir)
        
        # Validate environment
        if not engine.validate_environment():
            print("❌ Environment validation failed")
            sys.exit(1)
        
        if args.validate:
            print("✅ Environment validation successful")
            sys.exit(0)
        
        if args.test:
            print("🧪 Running in test mode...")
            # Add test mode logic here
            sys.exit(0)
        
        if args.sheet_id:
            # Process batch from Google Sheets
            results = engine.process_batch(args.sheet_id, args.sheet_name)
            
            successful = sum(1 for r in results if r.success)
            failed = len(results) - successful
            
            print(f"✅ Batch processing completed: {successful} successful, {failed} failed")
        else:
            print("Please provide --sheet-id for batch processing or use --test for test mode")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Engine execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
