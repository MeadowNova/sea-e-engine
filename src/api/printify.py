
#!/usr/bin/env python3
"""
Printify API Client for SEA-E Engine
===================================

Production-ready Printify API client with comprehensive error handling,
retry mechanisms, and product management.
"""

import os
import time
import requests
from typing import Dict, List, Optional, Any
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import logging
from pathlib import Path
import base64


class PrintifyAPIClient:
    """
    Production-ready Printify API client with retry mechanisms and error handling.
    """
    
    def __init__(self):
        """Initialize Printify API client with credentials from environment."""
        self.api_key = os.getenv("PRINTIFY_API_KEY")
        self.shop_id = os.getenv("PRINTIFY_SHOP_ID")
        
        self.base_url = "https://api.printify.com/v1"
        
        # Validate required credentials
        required_vars = ["PRINTIFY_API_KEY", "PRINTIFY_SHOP_ID"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        # Set up logging
        self.logger = logging.getLogger("printify_api")
        
        # Initialize session with retry strategy
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "SEA-Engine/2.0"
        }
    
    def make_request(self, method: str, endpoint: str, params: Dict = None, 
                    data: Dict = None, retry_count: int = 0) -> requests.Response:
        """
        Make authenticated request to Printify API with retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            retry_count: Current retry attempt
            
        Returns:
            requests.Response: API response
        """
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=60
            )
            
            # Handle rate limiting
            if response.status_code == 429 and retry_count < 3:
                retry_after = int(response.headers.get("Retry-After", 5))
                self.logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                time.sleep(retry_after)
                return self.make_request(method, endpoint, params, data, retry_count + 1)
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error: {e}")
            if retry_count < 2:
                wait_time = 2 ** retry_count
                self.logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                return self.make_request(method, endpoint, params, data, retry_count + 1)
            raise
    
    def test_connection(self) -> bool:
        """
        Test API connection and authentication.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info("Testing Printify API connection...")
            
            endpoint = "/shops.json"
            response = self.make_request("GET", endpoint)
            
            if response.status_code == 200:
                shops_data = response.json()
                shops = shops_data if isinstance(shops_data, list) else shops_data.get("data", [])
                
                # Verify shop exists
                shop_found = any(str(shop.get("id")) == str(self.shop_id) for shop in shops)
                
                if shop_found:
                    self.logger.info(f"Connection successful - Shop ID {self.shop_id} found")
                    return True
                else:
                    self.logger.error(f"Shop ID {self.shop_id} not found in account")
                    return False
            else:
                self.logger.error(f"Connection failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def upload_image(self, image_path: str) -> str:
        """
        Upload image to Printify and return image ID.
        
        Args:
            image_path: Path to image file
            
        Returns:
            str: Uploaded image ID
        """
        try:
            self.logger.info(f"Uploading image: {image_path}")
            
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Upload image
            endpoint = "/uploads/images.json"
            data = {
                "file_name": Path(image_path).name,
                "contents": image_base64
            }
            
            response = self.make_request("POST", endpoint, data=data)
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to upload image: {response.status_code} - {response.text}")
            
            image_data = response.json()
            image_id = image_data.get("id")
            
            self.logger.info(f"Image uploaded with ID: {image_id}")
            return str(image_id)
            
        except Exception as e:
            self.logger.error(f"Failed to upload image: {e}")
            raise
    
    def get_blueprint_details(self, blueprint_id: int) -> Dict[str, Any]:
        """Get detailed blueprint information."""
        try:
            endpoint = f"/catalog/blueprints/{blueprint_id}.json"
            response = self.make_request("GET", endpoint)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get blueprint: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.logger.error(f"Failed to get blueprint {blueprint_id}: {e}")
            raise
    
    def create_product(self, title: str, description: str, blueprint_id: int,
                      print_provider_id: int, design_file_path: str,
                      mockup_files: List[str] = None, colors: List[str] = None,
                      variations: List[str] = None) -> str:
        """
        Create a new product in Printify.
        
        Args:
            title: Product title
            description: Product description
            blueprint_id: Printify blueprint ID
            print_provider_id: Print provider ID
            design_file_path: Path to design file
            mockup_files: List of mockup file paths
            colors: List of color names
            variations: List of variation names
            
        Returns:
            str: Created product ID
        """
        try:
            self.logger.info(f"Creating Printify product: {title}")
            
            # Upload design image
            design_image_id = self.upload_image(design_file_path)
            
            # Get blueprint details to understand variants
            blueprint_details = self.get_blueprint_details(blueprint_id)
            
            # Build product data
            product_data = {
                "title": title,
                "description": description,
                "blueprint_id": blueprint_id,
                "print_provider_id": print_provider_id,
                "variants": self._build_variants(blueprint_details, colors, variations),
                "print_areas": [
                    {
                        "variant_ids": [],  # Will be populated with all variant IDs
                        "placeholders": [
                            {
                                "position": "front",
                                "images": [
                                    {
                                        "id": design_image_id,
                                        "x": 0.5,
                                        "y": 0.5,
                                        "scale": 1.0,
                                        "angle": 0
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            # Set variant IDs for print areas
            variant_ids = [variant["id"] for variant in product_data["variants"]]
            product_data["print_areas"][0]["variant_ids"] = variant_ids
            
            # Create product
            endpoint = f"/shops/{self.shop_id}/products.json"
            response = self.make_request("POST", endpoint, data=product_data)
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create product: {response.status_code} - {response.text}")
            
            product_response = response.json()
            product_id = product_response.get("id")
            
            self.logger.info(f"Product created with ID: {product_id}")
            
            # Publish product
            if product_id:
                self._publish_product(product_id)
            
            return str(product_id)

        except Exception as e:
            self.logger.error(f"Failed to create product: {e}")
            raise

    def create_product_with_precise_placement(self, title: str, description: str,
                                            blueprint_id: int, print_provider_id: int,
                                            design_file_path: str, coordinate_config: dict,
                                            colors: List[str] = None, variations: List[str] = None) -> str:
        """
        Create a product with precise design placement using coordinate mapping.

        Args:
            title: Product title
            description: Product description
            blueprint_id: Printify blueprint ID
            print_provider_id: Print provider ID
            design_file_path: Path to design file
            coordinate_config: Precise coordinate configuration from coordinate mapper
            colors: List of color names
            variations: List of variation names

        Returns:
            str: Created product ID
        """
        try:
            self.logger.info(f"Creating Printify product with precise placement: {title}")

            # Upload design image
            design_image_id = self.upload_image(design_file_path)

            # Get blueprint details to understand variants
            blueprint_details = self.get_blueprint_details(blueprint_id)

            # Build variants
            variants = self._build_variants(blueprint_details, colors, variations)
            variant_ids = [variant["id"] for variant in variants]

            # Build print areas with precise coordinates
            print_areas = []
            printify_coords = coordinate_config.get("printify_coordinates", {})

            # If no precise coordinates provided, use default center placement
            if not printify_coords:
                printify_coords = {"front": {"x": 0.5, "y": 0.5, "scale": 1.0, "angle": 0}}

            for position, coords in printify_coords.items():
                print_area = {
                    "variant_ids": variant_ids,
                    "placeholders": [
                        {
                            "position": position,
                            "images": [
                                {
                                    "id": design_image_id,
                                    "x": coords["x"],
                                    "y": coords["y"],
                                    "scale": coords["scale"],
                                    "angle": coords.get("angle", 0)
                                }
                            ]
                        }
                    ]
                }
                print_areas.append(print_area)

            # Build product data with precise placement
            product_data = {
                "title": title,
                "description": description,
                "blueprint_id": blueprint_id,
                "print_provider_id": print_provider_id,
                "variants": variants,
                "print_areas": print_areas
            }

            # Create product
            endpoint = f"/shops/{self.shop_id}/products.json"
            response = self.make_request("POST", endpoint, data=product_data)

            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create product: {response.status_code} - {response.text}")

            product_response = response.json()
            product_id = product_response.get("id")

            self.logger.info(f"Product created with precise placement, ID: {product_id}")

            # Publish product
            if product_id:
                self._publish_product(product_id)

            return str(product_id)

        except Exception as e:
            self.logger.error(f"Failed to create product with precise placement: {e}")
            raise
    
    def _build_variants(self, blueprint_details: Dict, colors: List[str] = None,
                       variations: List[str] = None) -> List[Dict]:
        """Build product variants based on blueprint and requirements."""
        try:
            blueprint_variants = blueprint_details.get("variants", [])
            
            if not blueprint_variants:
                raise Exception("No variants found in blueprint")
            
            # If no specific colors/variations requested, use first few variants
            if not colors and not variations:
                return blueprint_variants[:5]  # Limit to first 5 variants
            
            # Filter variants based on colors and variations
            filtered_variants = []
            
            for variant in blueprint_variants:
                variant_options = variant.get("options", [])
                
                # Check if variant matches requested colors/variations
                matches = True
                
                if colors:
                    color_match = any(
                        color.lower() in option.get("value", "").lower()
                        for option in variant_options
                        for color in colors
                    )
                    if not color_match:
                        matches = False
                
                if variations and matches:
                    variation_match = any(
                        variation.lower() in option.get("value", "").lower()
                        for option in variant_options
                        for variation in variations
                    )
                    if not variation_match:
                        matches = False
                
                if matches:
                    filtered_variants.append(variant)
            
            # If no matches found, use default variants
            if not filtered_variants:
                self.logger.warning("No variants matched criteria, using defaults")
                filtered_variants = blueprint_variants[:5]
            
            return filtered_variants[:20]  # Limit to 20 variants max
            
        except Exception as e:
            self.logger.error(f"Failed to build variants: {e}")
            # Return first few variants as fallback
            return blueprint_details.get("variants", [])[:5]
    
    def _publish_product(self, product_id: str):
        """Publish a product to make it available."""
        try:
            endpoint = f"/shops/{self.shop_id}/products/{product_id}/publish.json"
            data = {"title": True, "description": True, "images": True, "variants": True, "tags": True}
            
            response = self.make_request("POST", endpoint, data=data)
            
            if response.status_code == 200:
                self.logger.info(f"Product {product_id} published successfully")
            else:
                self.logger.error(f"Failed to publish product: {response.text}")
                
        except Exception as e:
            self.logger.error(f"Failed to publish product: {e}")
            # Don't raise - product exists even if not published
    
    def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get product details."""
        try:
            endpoint = f"/shops/{self.shop_id}/products/{product_id}.json"
            response = self.make_request("GET", endpoint)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get product: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.logger.error(f"Failed to get product {product_id}: {e}")
            raise
    
    def update_product(self, product_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing product."""
        try:
            endpoint = f"/shops/{self.shop_id}/products/{product_id}.json"
            response = self.make_request("PUT", endpoint, data=updates)
            
            if response.status_code == 200:
                self.logger.info(f"Product {product_id} updated successfully")
                return True
            else:
                self.logger.error(f"Failed to update product: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update product {product_id}: {e}")
            return False
    
    def delete_product(self, product_id: str) -> bool:
        """Delete a product."""
        try:
            endpoint = f"/shops/{self.shop_id}/products/{product_id}.json"
            response = self.make_request("DELETE", endpoint)
            
            if response.status_code == 200:
                self.logger.info(f"Product {product_id} deleted successfully")
                return True
            else:
                self.logger.error(f"Failed to delete product: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete product {product_id}: {e}")
            return False
    
    def list_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List products in the shop."""
        try:
            endpoint = f"/shops/{self.shop_id}/products.json"
            params = {"limit": limit}
            
            response = self.make_request("GET", endpoint, params=params)
            
            if response.status_code == 200:
                products_data = response.json()
                return products_data.get("data", [])
            else:
                raise Exception(f"Failed to list products: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.logger.error(f"Failed to list products: {e}")
            raise
