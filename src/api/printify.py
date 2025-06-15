
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
        Upload image to Printify with quality preservation and transparency support.

        Args:
            image_path: Path to image file

        Returns:
            str: Uploaded image ID
        """
        try:
            self.logger.info(f"Uploading image: {image_path}")

            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Validate image quality and format
            from PIL import Image
            import io

            # Open and validate the image
            with Image.open(image_path) as img:
                # Log image details for debugging
                self.logger.info(f"Image format: {img.format}, Size: {img.size}, Mode: {img.mode}")

                # Ensure image is high quality (300+ DPI equivalent)
                if hasattr(img, 'info') and 'dpi' in img.info:
                    dpi = img.info['dpi']
                    self.logger.info(f"Image DPI: {dpi}")

                # Optimize image for print quality
                # Ensure minimum resolution for print (300 DPI equivalent)
                min_size = 3000  # Minimum 3000px for high quality print
                if min(img.size) < min_size:
                    # Resize maintaining aspect ratio
                    ratio = min_size / min(img.size)
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    self.logger.info(f"Upscaled image to {new_size} for print quality")

                # Ensure transparency is preserved for PNG
                if img.format == 'PNG' and img.mode in ('RGBA', 'LA'):
                    self.logger.info("PNG with transparency detected - preserving alpha channel")
                elif img.format == 'PNG' and img.mode != 'RGBA':
                    # Convert to RGBA to ensure transparency support
                    img = img.convert('RGBA')
                    self.logger.info("Converted PNG to RGBA for transparency support")

                # Save optimized version while preserving maximum quality
                output_buffer = io.BytesIO()
                if img.format == 'PNG' or img.mode == 'RGBA':
                    # Preserve PNG transparency and quality - NO compression for print
                    img.save(output_buffer, format='PNG', optimize=False, compress_level=0)
                    self.logger.info("Saved as PNG with zero compression for maximum print quality")
                else:
                    # For JPEG, use maximum quality
                    img.save(output_buffer, format='JPEG', quality=100, optimize=False)
                    self.logger.info("Saved as JPEG with 100% quality")

                image_data = output_buffer.getvalue()
                image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Upload image with preserved quality
            endpoint = "/uploads/images.json"
            data = {
                "file_name": Path(image_path).name,
                "contents": image_base64
            }

            response = self.make_request("POST", endpoint, data=data)

            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to upload image: {response.status_code} - {response.text}")

            image_response = response.json()
            image_id = image_response.get("id")

            # Log upload success with quality info
            file_size_mb = len(image_data) / (1024 * 1024)
            self.logger.info(f"Image uploaded with ID: {image_id}, Size: {file_size_mb:.1f}MB")
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

    def get_blueprint_variants(self, blueprint_id: int, print_provider_id: int) -> List[Dict]:
        """Get variants for a specific blueprint and print provider combination."""
        try:
            endpoint = f"/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json"
            response = self.make_request("GET", endpoint)

            if response.status_code == 200:
                variants_data = response.json()
                return variants_data.get("variants", [])
            else:
                raise Exception(f"Failed to get variants: {response.status_code} - {response.text}")

        except Exception as e:
            self.logger.error(f"Failed to get variants for blueprint {blueprint_id}, provider {print_provider_id}: {e}")
            raise
    
    def create_product_with_user_config(self, title: str, description: str,
                                       blueprint_id: int, print_provider_id: int,
                                       design_file_path: str) -> str:
        """
        Create product using user's exact configuration and working product structure.
        This method ensures all 318 variants are created with the correct colors.
        """
        try:
            self.logger.info(f"Creating product with user config: {title}")

            # Upload design image with quality preservation
            design_image_id = self.upload_image(design_file_path)

            # Load user's exact product configuration
            import json
            with open("config/product_blueprints.json", 'r') as f:
                blueprints = json.load(f)

            # Get user's t-shirt configuration (blueprint 12)
            tshirt_config = blueprints['products']['tshirt_bella_canvas_3001']
            user_colors = list(tshirt_config['automation_settings']['default_colors'])

            self.logger.info(f"Target colors: {user_colors}")

            # Get variants from Printify API for this blueprint/provider combination
            blueprint_variants = self.get_blueprint_variants(blueprint_id, print_provider_id)
            self.logger.info(f"Retrieved {len(blueprint_variants)} variants from Printify API")

            if not blueprint_variants:
                # Fallback to working product structure
                with open("config/printify_analysis.json", 'r') as f:
                    analysis = json.load(f)

                working_product = None
                for product in analysis['products']:
                    if (product['blueprint_id'] == blueprint_id and
                        product['print_provider_id'] == print_provider_id):
                        working_product = product
                        break

                if working_product:
                    blueprint_variants = working_product['variants']
                    self.logger.info(f"Using fallback variants from: {working_product['title']}")
                else:
                    raise Exception(f"No variants available for blueprint {blueprint_id}")

            working_variants = blueprint_variants

            # Filter variants to match user's 12 colors using the improved method
            mock_blueprint_details = {"variants": working_variants}
            user_color_variants = self._build_variants(mock_blueprint_details, user_colors)

            self.logger.info(f"Filtered to {len(user_color_variants)} variants matching user colors")

            # Debug: Check if variants have pricing
            if user_color_variants:
                sample_variant = user_color_variants[0]
                self.logger.info(f"Sample variant keys: {list(sample_variant.keys())}")
                self.logger.info(f"Sample variant price: {sample_variant.get('price', 'MISSING')}")

            # If we don't have enough variants, include all working variants
            if len(user_color_variants) < 50:  # Minimum threshold
                self.logger.warning("Not enough color matches, using all working variants")
                user_color_variants = [v.copy() for v in working_variants]
                for variant in user_color_variants:
                    variant['is_enabled'] = True

            # Build product data with working structure and Etsy-specific properties
            product_data = {
                "title": title,
                "description": description,
                "blueprint_id": blueprint_id,
                "print_provider_id": print_provider_id,
                "variants": user_color_variants,
                "print_areas": [
                    {
                        "variant_ids": [variant["id"] for variant in user_color_variants],
                        "placeholders": [
                            {
                                "position": "front",
                                "images": [
                                    {
                                        "id": design_image_id,
                                        "x": 0.5,  # Center placement horizontally
                                        "y": 0.35,  # Higher placement for optimal chest area
                                        "scale": 1.0,  # Standard scale - let design size determine visibility
                                        "angle": 0
                                    }
                                ]
                            }
                        ]
                    }
                ],
                # Add Etsy-specific sales channel properties for free shipping
                "sales_channel_properties": {
                    "free_shipping": True,  # Enable free shipping (USD 0.00)
                    "personalisation": []
                },
                # Keep product as draft initially (not visible)
                "visible": False
            }

            # Create product
            endpoint = f"/shops/{self.shop_id}/products.json"
            response = self.make_request("POST", endpoint, data=product_data)

            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create product: {response.status_code} - {response.text}")

            product_response = response.json()
            product_id = product_response.get("id")

            self.logger.info(f"Product created successfully with ID: {product_id}")
            self.logger.info("Product saved as DRAFT (not published to avoid going live)")

            # DO NOT publish automatically - keep as draft to avoid live listings
            # User can manually publish when ready or use separate publish method

            return str(product_id)

        except Exception as e:
            self.logger.error(f"Failed to create product with user config: {e}")
            raise

    def create_printify_product_only(self, title: str, description: str,
                                    design_file_path: str, blueprint_id: int = 12,
                                    print_provider_id: int = 29) -> Dict:
        """
        Create a Printify product for fulfillment only (no publishing to Etsy).
        This method creates the product with correct pricing, variants, and design placement
        but does NOT use Printify's mockups or publishing features.

        Custom mockups and Etsy listing creation will be handled separately for brand consistency.

        Args:
            title: Product title
            description: Product description
            design_file_path: Path to Printify-optimized design file
            blueprint_id: Printify blueprint ID (default: 12 for t-shirt)
            print_provider_id: Print provider ID (default: 29 for Monster Digital)

        Returns:
            Dict with product_id, variant_count, and product details for external use
        """
        try:
            self.logger.info(f"Creating complete Etsy listing via Printify: {title}")

            # Upload design with maximum quality
            design_image_id = self.upload_image(design_file_path)

            # Get user's configuration
            import json
            with open("config/product_blueprints.json", 'r') as f:
                blueprints = json.load(f)

            tshirt_config = blueprints['products']['tshirt_bella_canvas_3001']
            user_colors = list(tshirt_config['automation_settings']['default_colors'])

            # Get variants with correct pricing
            blueprint_variants = self.get_blueprint_variants(blueprint_id, print_provider_id)
            mock_blueprint_details = {"variants": blueprint_variants}
            user_color_variants = self._build_variants(mock_blueprint_details, user_colors)

            # Build comprehensive product data for Etsy
            product_data = {
                "title": title,
                "description": description,
                "tags": tags[:13],  # Etsy allows max 13 tags
                "blueprint_id": blueprint_id,
                "print_provider_id": print_provider_id,
                "variants": user_color_variants,
                "print_areas": [
                    {
                        "variant_ids": [variant["id"] for variant in user_color_variants],
                        "placeholders": [
                            {
                                "position": "front",
                                "images": [
                                    {
                                        "id": design_image_id,
                                        "x": 0.5,  # Center horizontally
                                        "y": 0.35,  # Optimal chest placement
                                        "scale": 1.0,  # Standard scale
                                        "angle": 0
                                    }
                                ]
                            }
                        ]
                    }
                ],
                # Etsy-specific properties
                "sales_channel_properties": {
                    "free_shipping": True,  # Free shipping as required
                    "personalisation": [],
                    "tags": tags[:13]
                },
                # Safety and compliance information
                "safety_information": {
                    "care_instructions": "Machine wash cold, tumble dry low, do not bleach, do not iron directly on design",
                    "material_composition": "100% Cotton (varies by color)",
                    "country_of_origin": "Printed in USA"
                },
                # Keep as draft initially
                "visible": False
            }

            # Create product
            endpoint = f"/shops/{self.shop_id}/products.json"
            response = self.make_request("POST", endpoint, data=product_data)

            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create product: {response.status_code} - {response.text}")

            product_response = response.json()
            product_id = product_response.get("id")

            # Get product details for external use
            product_details = self.get_product(product_id)

            result = {
                "product_id": product_id,
                "status": "created_for_fulfillment",
                "variant_count": len(user_color_variants),
                "blueprint_id": blueprint_id,
                "print_provider_id": print_provider_id,
                "title": title,
                "description": description,
                "variants": user_color_variants,
                "design_placement": {
                    "x": 0.5,
                    "y": 0.35,
                    "scale": 1.0,
                    "angle": 0
                },
                "note": "Product created for fulfillment only. Use custom mockups and Etsy API for listing creation."
            }

            self.logger.info(f"Printify product created for fulfillment: {product_id}")
            self.logger.info("Ready for custom mockup generation and Etsy listing creation")

            return result

        except Exception as e:
            self.logger.error(f"Failed to create Printify product: {e}")
            raise

    def create_fulfillment_product(self, title: str, description: str,
                                 design_file_path: str, blueprint_id: int = 12,
                                 print_provider_id: int = 29) -> Dict:
        """
        Create a Printify product specifically for fulfillment purposes.

        This method creates a product with:
        - Correct pricing structure ($35.70 S-XL, $38.56 2XL, $40.75 3XL)
        - Free shipping configuration
        - Draft mode (not published)
        - Optimized design placement
        - All user's 12 specified colors

        The product will be used for order fulfillment while custom mockups
        and Etsy listings are handled separately for brand consistency.

        Args:
            title: Product title for internal reference
            description: Product description for internal reference
            design_file_path: Path to Printify-optimized design file
            blueprint_id: Printify blueprint ID (default: 12 for t-shirt)
            print_provider_id: Print provider ID (default: 29 for Monster Digital)

        Returns:
            Dict with product details needed for external listing creation
        """
        try:
            self.logger.info(f"Creating fulfillment product: {title}")

            # Use the fixed product creation method
            product_id = self.create_product_with_user_config(
                title=title,
                description=description,
                blueprint_id=blueprint_id,
                print_provider_id=print_provider_id,
                design_file_path=design_file_path
            )

            if not product_id:
                raise Exception("Failed to create Printify product")

            # Get product details for external use
            product_details = self.get_product(product_id)

            if not product_details:
                raise Exception("Failed to retrieve created product details")

            # Extract key information for external listing creation
            variants = product_details.get('variants', [])

            # Organize variants by color and size for easy reference
            variant_map = {}
            for variant in variants:
                if variant.get('is_enabled', False):
                    title_parts = variant.get('title', '').split(' / ')
                    if len(title_parts) >= 2:
                        color = title_parts[0].strip()
                        size = title_parts[1].strip()

                        if color not in variant_map:
                            variant_map[color] = {}

                        variant_map[color][size] = {
                            'variant_id': variant.get('id'),
                            'price': variant.get('price', 0) / 100,  # Convert to dollars
                            'sku': variant.get('sku', ''),
                            'is_available': variant.get('is_available', True)
                        }

            result = {
                'printify_product_id': product_id,
                'status': 'created_for_fulfillment',
                'title': title,
                'description': description,
                'blueprint_id': blueprint_id,
                'print_provider_id': print_provider_id,
                'total_variants': len([v for v in variants if v.get('is_enabled', False)]),
                'colors_available': list(variant_map.keys()),
                'variant_map': variant_map,
                'design_info': {
                    'placement': {'x': 0.5, 'y': 0.35, 'scale': 1.0, 'angle': 0},
                    'file_path': design_file_path
                },
                'pricing': {
                    'S-XL': 35.70,
                    '2XL': 38.56,
                    '3XL': 40.75
                },
                'shipping': 'free',
                'ready_for_external_listing': True
            }

            self.logger.info(f"Fulfillment product created successfully: {product_id}")
            self.logger.info(f"Available colors: {len(variant_map)} colors")
            self.logger.info(f"Total variants: {result['total_variants']}")
            self.logger.info("Ready for custom mockup generation and Etsy listing creation")

            return result

        except Exception as e:
            self.logger.error(f"Failed to create fulfillment product: {e}")
            raise

    def publish_to_etsy(self, product_id: str, as_draft: bool = True) -> Dict:
        """
        Publish a Printify product to Etsy using the official publishing workflow.
        Based on comprehensive API documentation analysis.

        Args:
            product_id: Printify product ID
            as_draft: Whether to publish as draft (True) or live listing (False)

        Returns:
            Dict with publishing results including Etsy listing ID and mockup images
        """
        try:
            self.logger.info(f"Publishing product {product_id} to Etsy (draft: {as_draft})")

            # Prepare comprehensive publishing data based on API documentation
            publish_data = {
                "title": True,  # Publish Printify title
                "description": True,  # Publish Printify description
                "images": True,  # Publish Printify auto-generated mockup images
                "variants": True,  # Publish all enabled variants
                "tags": True,  # Publish Printify tags
                "keyFeatures": [],  # Additional features
                "shipping_template": True  # Use Etsy shipping template with free shipping
            }

            # Publish to connected Etsy store
            endpoint = f"/shops/{self.shop_id}/products/{product_id}/publish.json"
            response = self.make_request("POST", endpoint, data=publish_data)

            if response.status_code not in [200, 201]:
                # Handle publishing failure
                self._handle_publishing_failure(product_id, f"HTTP {response.status_code}: {response.text}")
                raise Exception(f"Failed to publish to Etsy: {response.status_code} - {response.text}")

            publish_response = response.json()
            self.logger.info("Publishing request sent successfully")

            # The actual Etsy listing creation happens asynchronously
            # We need to wait for the external ID to be available
            external_id = None
            mockup_images = []

            # Check if external ID is immediately available
            if "external" in publish_response:
                external_data = publish_response["external"]
                if isinstance(external_data, list) and len(external_data) > 0:
                    external_id = external_data[0].get("id")
                elif isinstance(external_data, dict):
                    external_id = external_data.get("id")

            # Get mockup images from the product
            product_data = self.get_product(product_id)
            if product_data and "images" in product_data:
                mockup_images = product_data["images"]

            result = {
                "status": "publishing_initiated",
                "product_id": product_id,
                "etsy_listing_id": external_id,
                "is_draft": as_draft,
                "mockup_images": mockup_images,
                "etsy_url": f"https://www.etsy.com/listing/{external_id}" if external_id else None,
                "note": "Etsy listing creation is asynchronous. Check external property later for listing ID."
            }

            # If we got an external ID immediately, confirm success
            if external_id:
                self.logger.info(f"Etsy listing created immediately: {external_id}")
                self._confirm_publishing_success(product_id, external_id)
                result["status"] = "published_successfully"
            else:
                self.logger.info("Etsy listing creation initiated. External ID will be available shortly.")

            return result

        except Exception as e:
            self.logger.error(f"Failed to publish to Etsy: {e}")
            # Report publishing failure to Printify
            self._handle_publishing_failure(product_id, str(e))
            raise

    def _handle_publishing_failure(self, product_id: str, reason: str):
        """Handle publishing failure and unlock product."""
        try:
            endpoint = f"/shops/{self.shop_id}/products/{product_id}/publishing_failed.json"
            data = {"reason": reason}

            response = self.make_request("POST", endpoint, data=data)

            if response.status_code in [200, 201]:
                self.logger.info(f"Publishing failure reported for product {product_id}")
            else:
                self.logger.warning(f"Failed to report publishing failure: {response.status_code}")

        except Exception as e:
            self.logger.warning(f"Failed to report publishing failure: {e}")

    def _confirm_publishing_success(self, product_id: str, external_id: str):
        """Confirm publishing success to Printify."""
        try:
            endpoint = f"/shops/{self.shop_id}/products/{product_id}/publishing_succeeded.json"
            data = {"external": {"id": external_id}}

            response = self.make_request("POST", endpoint, data=data)

            if response.status_code in [200, 201]:
                self.logger.info(f"Publishing success confirmed for product {product_id}")
            else:
                self.logger.warning(f"Failed to confirm publishing success: {response.status_code}")

        except Exception as e:
            self.logger.warning(f"Failed to confirm publishing success: {e}")

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

            # If no precise coordinates provided, use optimized chest placement
            if not printify_coords:
                printify_coords = {"front": {"x": 0.5, "y": 0.4, "scale": 1.2, "angle": 0}}

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
        """
        Build product variants based on user's exact color specifications.
        Uses the user's 12 specified colors from their product configuration.
        """
        try:
            blueprint_variants = blueprint_details.get("variants", [])

            if not blueprint_variants:
                raise Exception("No variants found in blueprint")

            # User's exact 12 colors from their configuration
            user_colors = [
                "Baby Blue", "Black", "Dark Grey Heather", "Deep Heather",
                "Heather Navy", "Natural", "Navy", "Soft Pink",
                "White", "Yellow", "Heather Peach", "Black Heather"
            ]

            # If specific colors provided, use those; otherwise use user's default colors
            target_colors = colors if colors else user_colors

            self.logger.info(f"Filtering variants for colors: {target_colors}")

            # Create color mapping for better matching
            color_variations = {}
            for color in target_colors:
                color_lower = color.lower()
                color_variations[color_lower] = [
                    color_lower,
                    color_lower.replace(" ", ""),
                    color_lower.replace(" ", "_"),
                    color_lower.replace("grey", "gray"),
                    color_lower.replace("gray", "grey")
                ]

            filtered_variants = []

            # Get blueprint options to understand the structure
            blueprint_options = blueprint_details.get("options", [])
            color_option_id = None
            size_option_id = None

            # Find color and size option IDs
            for option in blueprint_options:
                option_type = option.get("type", "").lower()
                if "color" in option_type or option.get("title", "").lower() == "color":
                    color_option_id = option.get("id")
                elif "size" in option_type or option.get("title", "").lower() == "size":
                    size_option_id = option.get("id")

            self.logger.info(f"Color option ID: {color_option_id}, Size option ID: {size_option_id}")

            # Filter variants by matching color names in the title
            for variant in blueprint_variants:
                variant_title = variant.get("title", "").lower()

                # Check if any of our target colors match this variant
                color_match = False
                matched_color = None

                for target_color in target_colors:
                    target_lower = target_color.lower()

                    # Direct match
                    if target_lower in variant_title:
                        color_match = True
                        matched_color = target_color
                        break

                    # Handle specific color mappings
                    color_mappings = {
                        'baby_blue': ['baby blue', 'babyblue'],
                        'dark_grey_heather': ['dark grey heather', 'darkgreyheather', 'dark gray heather'],
                        'deep_heather': ['deep heather', 'deepheather'],
                        'heather_navy': ['heather navy', 'heathernavy'],
                        'soft_pink': ['soft pink', 'softpink'],
                        'heather_peach': ['heather peach', 'heatherpeach'],
                        'black_heather': ['black heather', 'blackheather']
                    }

                    target_key = target_lower.replace(' ', '_')
                    if target_key in color_mappings:
                        for mapping in color_mappings[target_key]:
                            if mapping in variant_title:
                                color_match = True
                                matched_color = target_color
                                break

                    if color_match:
                        break

                if color_match:
                    # Enable the variant and set proper pricing
                    variant_copy = variant.copy()
                    variant_copy["is_enabled"] = True

                    # Calculate pricing based on user's CORRECT configuration
                    # From Issues to Fix.md: $35.70 (S-XL), $38.56 (2XL), $40.75 (3XL)
                    variant_title = variant.get("title", "")

                    if "3XL" in variant_title or "XXXL" in variant_title:
                        price = 4075  # $40.75 for 3XL
                    elif "2XL" in variant_title or "XXL" in variant_title:
                        price = 3856  # $38.56 for 2XL
                    else:
                        price = 3570  # $35.70 for S-XL (default)

                    variant_copy["price"] = price

                    # Log pricing for verification
                    size = "Unknown"
                    if " / " in variant_title:
                        size = variant_title.split(" / ")[1] if len(variant_title.split(" / ")) > 1 else "Unknown"

                    filtered_variants.append(variant_copy)

            # If no matches found, log detailed info and use working product structure
            if not filtered_variants:
                self.logger.warning(f"No variants matched target colors: {target_colors}")
                self.logger.info("Available variant titles:")
                for i, variant in enumerate(blueprint_variants[:10]):
                    self.logger.info(f"  {i+1}: {variant.get('title', 'No title')}")

                # Use working product structure as fallback
                filtered_variants = self._get_working_variants_fallback(blueprint_details)

            self.logger.info(f"Selected {len(filtered_variants)} variants from {len(blueprint_variants)} available")

            # Return all matching variants (user wants all 318 for t-shirts)
            return filtered_variants

        except Exception as e:
            self.logger.error(f"Failed to build variants: {e}")
            # Use working product structure as fallback
            return self._get_working_variants_fallback(blueprint_details)

    def _get_working_variants_fallback(self, blueprint_details: Dict) -> List[Dict]:
        """
        Fallback method using working product variant structure.
        """
        try:
            # Load working product analysis
            import json
            with open("config/printify_analysis.json", 'r') as f:
                analysis = json.load(f)

            # Find working product with same blueprint
            blueprint_id = blueprint_details.get("id")
            working_variants = None

            for product in analysis.get("products", []):
                if product.get("blueprint_id") == blueprint_id:
                    working_variants = product.get("variants", [])
                    self.logger.info(f"Using variant structure from working product: {product.get('title')}")
                    break

            if working_variants:
                # Enable all variants and ensure proper pricing
                enabled_variants = []
                for variant in working_variants:
                    variant_copy = variant.copy()
                    variant_copy["is_enabled"] = True
                    enabled_variants.append(variant_copy)

                return enabled_variants
            else:
                # Last resort: use first 20 blueprint variants
                variants = blueprint_details.get("variants", [])[:20]
                for variant in variants:
                    variant["is_enabled"] = True
                return variants

        except Exception as e:
            self.logger.error(f"Fallback variant selection failed: {e}")
            # Ultimate fallback
            variants = blueprint_details.get("variants", [])[:5]
            for variant in variants:
                variant["is_enabled"] = True
            return variants
    
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
