
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
from api.google_sheets_client import GoogleSheetsClient
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

            # Initialize Google Sheets client
            self.sheets_client = GoogleSheetsClient()

            # Initialize mockup generator with Google Sheets integration
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
            sheets_valid = self.sheets_client.test_connection()

            if not etsy_valid:
                self.logger.error("Etsy API connection failed")
                return False

            if not printify_valid:
                self.logger.error("Printify API connection failed")
                return False

            if not airtable_valid:
                self.logger.error("Airtable API connection failed")
                return False

            if not sheets_valid:
                self.logger.error("Google Sheets API connection failed")
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
            
            # Step 2: Create Printify product
            self.logger.info("Step 2: Creating Printify product...")
            printify_product_id = self._create_printify_product(product, variations, mockup_files)
            self.state_manager.update_workflow_step(workflow_id, "printify_created", {"product_id": printify_product_id})
            
            # Step 3: Publish to Etsy
            self.logger.info("Step 3: Publishing to Etsy...")
            etsy_listing_id = self._publish_to_etsy(product, printify_product_id, mockup_files)
            self.state_manager.update_workflow_step(workflow_id, "etsy_published", {"listing_id": etsy_listing_id})
            
            # Update product status to Published
            self.data_manager.update_product_status(product.product_id, ProductStatus.PUBLISHED)
            
            # Complete workflow
            execution_time = time.time() - start_time
            self.state_manager.complete_workflow(workflow_id, {
                "printify_product_id": printify_product_id,
                "etsy_listing_id": etsy_listing_id,
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
    
    def _create_printify_product(self, product: Product, variations: List[Variation], mockup_files: List[str]) -> str:
        """Create product in Printify."""
        try:
            # Get blueprint configuration
            blueprint_key = product.blueprint_key or self._get_blueprint_key(product.product_type)
            blueprint_config = self.product_blueprints.get("products", {}).get(blueprint_key)
            
            if not blueprint_config:
                raise ValueError(f"Blueprint configuration not found for {blueprint_key}")
            
            # Create product using Printify client
            product_id = self.printify_client.create_product(
                title=product.product_name,
                description=product.description,
                blueprint_id=blueprint_config["printify_config"]["blueprint_id"],
                print_provider_id=blueprint_config["printify_config"]["print_provider_id"],
                design_file_path=f"designs/{product.product_name}.png",
                mockup_files=mockup_files,
                colors=[var.color for var in variations],
                variations=[f"{var.color}-{var.size}" for var in variations]
            )
            
            # Update product with Printify ID
            self.airtable_client.update_record('products', product.record_id, {
                'Print Provider': 'Printify',
                'Status': ProductStatus.PRODUCT.value
            })
            
            self.logger.info(f"Created Printify product: {product_id}")
            return product_id
            
        except Exception as e:
            self.logger.error(f"Failed to create Printify product: {e}")
            raise
    
    def _publish_to_etsy(self, product: Product, printify_product_id: str, mockup_files: List[str]) -> str:
        """Publish product to Etsy."""
        try:
            # Create Etsy listing
            listing_id = self.etsy_client.create_listing(
                title=product.product_name,
                description=product.description,
                price=product.selling_price,
                tags=[],  # Tags would come from a separate field or be generated
                image_files=mockup_files[:10],  # Etsy allows max 10 images
                printify_product_id=printify_product_id
            )
            
            # Create listing record in Airtable
            listing_data = {
                'listing_id': f"listing_{int(time.time())}",
                'etsy_listing_id': listing_id,
                'publication_status': 'Active',
                'product': [product.record_id]
            }
            self.airtable_client.create_record('listings', listing_data)
            
            self.logger.info(f"Created Etsy listing: {listing_id}")
            return listing_id
            
        except Exception as e:
            self.logger.error(f"Failed to publish to Etsy: {e}")
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
