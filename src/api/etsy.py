
#!/usr/bin/env python3
"""
Etsy API Client for SEA-E Engine
===============================

Production-ready Etsy API client with comprehensive error handling,
retry mechanisms, and authentication management.
"""

import os
import time
import requests
from typing import Dict, List, Optional, Any
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import logging
from pathlib import Path


class EtsyAPIClient:
    """
    Production-ready Etsy API client with automatic token refresh and retry mechanisms.
    """
    
    def __init__(self):
        """Initialize Etsy API client with credentials from environment."""
        self.api_key = os.getenv("ETSY_API_KEY")
        self.api_secret = os.getenv("ETSY_API_SECRET")
        self.access_token = os.getenv("ETSY_ACCESS_TOKEN")
        self.refresh_token = os.getenv("ETSY_REFRESH_TOKEN")
        self.shop_id = os.getenv("ETSY_SHOP_ID")
        
        self.base_url = "https://openapi.etsy.com/v3"
        self.token_expiry = 0
        self.rate_limit_delay = 0.1  # 10 calls/sec rate limit

        # Validate required credentials
        required_vars = ["ETSY_API_KEY", "ETSY_REFRESH_TOKEN", "ETSY_SHOP_ID"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")

        # Set up logging
        self.logger = logging.getLogger("etsy_api")

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
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "SEA-Engine/2.0"
        }
    
    def refresh_access_token(self) -> bool:
        """
        Refresh access token using refresh token.
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        self.logger.info("Refreshing Etsy access token...")
        
        if not self.refresh_token:
            self.logger.error("No refresh token available")
            return False
        
        url = "https://api.etsy.com/v3/public/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.api_key,
            "refresh_token": self.refresh_token
        }
        
        try:
            response = requests.post(url, data=data, timeout=30)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                new_refresh_token = token_data.get("refresh_token")
                self.token_expiry = time.time() + token_data.get("expires_in", 3600)
                
                if new_refresh_token:
                    self.refresh_token = new_refresh_token
                
                self.logger.info("Access token refreshed successfully")
                return True
            else:
                self.logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception refreshing token: {e}")
            return False
    
    def make_request(self, method: str, endpoint: str, params: Dict = None, 
                    data: Dict = None, files: Dict = None, retry_count: int = 0) -> requests.Response:
        """
        Make authenticated request to Etsy API with automatic retry and token refresh.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            files: Files to upload
            retry_count: Current retry attempt
            
        Returns:
            requests.Response: API response
        """
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers()
        
        # Remove Content-Type for file uploads
        if files:
            headers.pop("Content-Type", None)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data if not files else None,
                files=files,
                timeout=60
            )
            
            # Handle token expiration
            if response.status_code == 401 and retry_count < 1:
                self.logger.warning("Unauthorized response, attempting token refresh...")
                if self.refresh_access_token():
                    return self.make_request(method, endpoint, params, data, files, retry_count + 1)
            
            # Handle rate limiting with custom backoff
            if response.status_code == 429 and retry_count < 3:
                retry_after = int(response.headers.get("Retry-After", 5))
                self.logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                time.sleep(retry_after)
                return self.make_request(method, endpoint, params, data, files, retry_count + 1)
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error: {e}")
            if retry_count < 2:
                wait_time = 2 ** retry_count
                self.logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                return self.make_request(method, endpoint, params, data, files, retry_count + 1)
            raise
    
    def test_connection(self) -> bool:
        """
        Test API connection and authentication.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info("Testing Etsy API connection...")
            
            endpoint = f"/application/shops/{self.shop_id}"
            response = self.make_request("GET", endpoint)
            
            if response.status_code == 200:
                shop_data = response.json()
                shop_name = shop_data.get("shop_name", "Unknown")
                self.logger.info(f"Connection successful - Shop: {shop_name}")
                return True
            else:
                self.logger.error(f"Connection failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def create_listing(self, title: str, description: str, price: float, 
                      tags: List[str], image_files: List[str], 
                      printify_product_id: str = None) -> str:
        """
        Create a new Etsy listing.
        
        Args:
            title: Listing title
            description: Listing description
            price: Price in shop currency
            tags: List of tags (max 13)
            image_files: List of image file paths
            printify_product_id: Associated Printify product ID
            
        Returns:
            str: Created listing ID
        """
        try:
            self.logger.info(f"Creating Etsy listing: {title}")
            
            # Prepare listing data
            listing_data = {
                "quantity": 999,  # High quantity for print-on-demand
                "title": title[:140],  # Etsy title limit
                "description": description,
                "price": price,
                "who_made": "i_did",
                "when_made": "2020_2024",
                "taxonomy_id": 1063,  # Clothing category
                "shipping_template_id": None,  # Will use shop default
                "materials": ["cotton", "polyester"],
                "tags": tags[:13],  # Etsy allows max 13 tags
                "should_auto_renew": True,
                "is_supply": False,
                "state": "draft"  # Create as draft first
            }
            
            # Create listing
            endpoint = f"/application/shops/{self.shop_id}/listings"
            response = self.make_request("POST", endpoint, data=listing_data)
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create listing: {response.status_code} - {response.text}")
            
            listing_data = response.json()
            listing_id = listing_data.get("listing_id")
            
            self.logger.info(f"Listing created with ID: {listing_id}")
            
            # Upload images if provided
            if image_files and listing_id:
                self._upload_listing_images(listing_id, image_files)
            
            # Activate listing
            self._activate_listing(listing_id)
            
            return str(listing_id)
            
        except Exception as e:
            self.logger.error(f"Failed to create listing: {e}")
            raise
    
    def _upload_listing_images(self, listing_id: str, image_files: List[str]):
        """Upload images to a listing."""
        try:
            self.logger.info(f"Uploading {len(image_files)} images to listing {listing_id}")
            
            for i, image_path in enumerate(image_files[:10]):  # Max 10 images
                if not Path(image_path).exists():
                    self.logger.warning(f"Image file not found: {image_path}")
                    continue
                
                endpoint = f"/application/shops/{self.shop_id}/listings/{listing_id}/images"
                
                with open(image_path, 'rb') as f:
                    files = {
                        'image': (Path(image_path).name, f, 'image/png'),
                        'rank': (None, str(i + 1))
                    }
                    
                    response = self.make_request("POST", endpoint, files=files)
                    
                    if response.status_code not in [200, 201]:
                        self.logger.error(f"Failed to upload image {image_path}: {response.text}")
                    else:
                        self.logger.info(f"Uploaded image {i + 1}/{len(image_files)}")
                
                # Small delay between uploads
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Failed to upload images: {e}")
            # Don't raise - listing can exist without images
    
    def _activate_listing(self, listing_id: str):
        """Activate a draft listing."""
        try:
            endpoint = f"/application/shops/{self.shop_id}/listings/{listing_id}"
            data = {"state": "active"}
            
            response = self.make_request("PUT", endpoint, data=data)
            
            if response.status_code == 200:
                self.logger.info(f"Listing {listing_id} activated successfully")
            else:
                self.logger.error(f"Failed to activate listing: {response.text}")
                
        except Exception as e:
            self.logger.error(f"Failed to activate listing: {e}")
            # Don't raise - listing exists even if not activated
    
    def get_listing(self, listing_id: str) -> Dict[str, Any]:
        """Get listing details."""
        try:
            endpoint = f"/application/listings/{listing_id}"
            response = self.make_request("GET", endpoint)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get listing: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.logger.error(f"Failed to get listing {listing_id}: {e}")
            raise
    
    def update_listing(self, listing_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing listing."""
        try:
            endpoint = f"/application/shops/{self.shop_id}/listings/{listing_id}"
            response = self.make_request("PUT", endpoint, data=updates)
            
            if response.status_code == 200:
                self.logger.info(f"Listing {listing_id} updated successfully")
                return True
            else:
                self.logger.error(f"Failed to update listing: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update listing {listing_id}: {e}")
            return False

    def create_digital_download_listing(self, title: str, description: str, price: float,
                                      tags: List[str], mockup_files: List[str],
                                      static_image_ids: List[str] = None) -> str:
        """
        Create a digital download listing with mockups and static images.

        Args:
            title: Listing title
            description: Listing description
            price: Price in shop currency
            tags: List of tags (max 13)
            mockup_files: List of mockup image file paths (up to 7)
            static_image_ids: List of static image IDs to copy from template

        Returns:
            str: Created listing ID
        """
        try:
            self.logger.info(f"Creating digital download listing: {title}")

            # Prepare listing data for digital download
            listing_data = {
                "quantity": 999,  # High quantity for digital downloads
                "title": title[:140],  # Etsy title limit
                "description": description,
                "price": 13.32,  # Fixed price for digital downloads
                "who_made": "i_did",
                "when_made": "2020_2025",
                "taxonomy_id": 66,  # Art & Collectibles category (confirmed working)
                "shipping_template_id": None,  # Not needed for digital downloads
                "materials": ["digital"],
                "tags": tags[:13],  # Etsy allows max 13 tags
                "should_auto_renew": True,
                "is_supply": False,
                "type": "download",  # Digital download type
                "state": "draft"  # Create as draft first
            }

            # Create listing
            endpoint = f"/application/shops/{self.shop_id}/listings"
            response = self.make_request("POST", endpoint, data=listing_data)

            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create listing: {response.status_code} - {response.text}")

            listing_response = response.json()
            listing_id = listing_response.get("listing_id")

            self.logger.info(f"Digital download listing created with ID: {listing_id}")

            # Upload mockup images (up to 7)
            if mockup_files and listing_id:
                self._upload_mockup_images(listing_id, mockup_files[:7])

            # Copy static images from template (if provided)
            if static_image_ids and listing_id:
                self._copy_static_images(listing_id, static_image_ids)

            return str(listing_id)

        except Exception as e:
            self.logger.error(f"Failed to create digital download listing: {e}")
            raise

    def upload_digital_file(self, listing_id: str, file_path: str, file_name: str = None) -> bool:
        """
        Upload a digital file to an Etsy listing.

        Args:
            listing_id: Etsy listing ID
            file_path: Path to the digital file to upload
            file_name: Custom filename (optional)

        Returns:
            bool: True if upload successful
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                self.logger.error(f"Digital file not found: {file_path}")
                return False

            # Use custom filename or original filename
            upload_filename = file_name or file_path.name

            self.logger.info(f"Uploading digital file to listing {listing_id}: {upload_filename}")

            # Etsy digital file upload endpoint
            endpoint = f"/application/shops/{self.shop_id}/listings/{listing_id}/files"

            with open(file_path, 'rb') as f:
                files = {
                    'file': (upload_filename, f, 'application/pdf'),
                    'name': (None, upload_filename),
                    'rank': (None, '1')  # Primary digital file
                }

                response = self.make_request("POST", endpoint, files=files)

                if response.status_code in [200, 201]:
                    self.logger.info(f"✅ Digital file uploaded successfully: {upload_filename}")
                    return True
                else:
                    self.logger.error(f"❌ Failed to upload digital file: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            self.logger.error(f"Error uploading digital file: {e}")
            return False

    def _upload_mockup_images(self, listing_id: str, mockup_files: List[str]):
        """Upload mockup images to a listing."""
        try:
            self.logger.info(f"Uploading {len(mockup_files)} mockup images to listing {listing_id}")

            for i, image_path in enumerate(mockup_files):
                if not Path(image_path).exists():
                    self.logger.warning(f"Mockup file not found: {image_path}")
                    continue

                endpoint = f"/application/shops/{self.shop_id}/listings/{listing_id}/images"

                with open(image_path, 'rb') as f:
                    files = {
                        'image': (Path(image_path).name, f, 'image/png'),
                        'rank': (None, str(i + 1))  # Mockups get ranks 1-7
                    }

                    response = self.make_request("POST", endpoint, files=files)

                    if response.status_code not in [200, 201]:
                        self.logger.error(f"Failed to upload mockup {image_path}: {response.text}")
                    else:
                        self.logger.info(f"Uploaded mockup {i + 1}/{len(mockup_files)}: {Path(image_path).name}")

                # Rate limiting delay
                time.sleep(self.rate_limit_delay)

        except Exception as e:
            self.logger.error(f"Failed to upload mockup images: {e}")
            # Don't raise - listing can exist without images

    def _copy_static_images(self, listing_id: str, static_image_ids: List[str]):
        """Copy static images from template listing to new listing."""
        try:
            self.logger.info(f"Copying {len(static_image_ids)} static images to listing {listing_id}")

            if not static_image_ids:
                self.logger.warning("No static image IDs provided")
                return

            # Get template listing with images
            template_listing = self._get_template_listing_with_images()
            if not template_listing:
                self.logger.error("Could not fetch template listing for image copying")
                return

            # Find the static images in template listing
            template_images = template_listing.get('images', [])
            static_images_to_copy = []

            for image in template_images:
                image_id = str(image.get('listing_image_id', ''))
                if image_id in static_image_ids:
                    static_images_to_copy.append(image)

            self.logger.info(f"Found {len(static_images_to_copy)} static images to copy")

            # Download and re-upload each static image
            for i, image in enumerate(static_images_to_copy):
                try:
                    image_url = image.get('url_fullxfull') or image.get('url_570xN')
                    if not image_url:
                        self.logger.warning(f"No URL found for static image {image.get('listing_image_id')}")
                        continue

                    # Download image
                    import requests
                    import tempfile
                    from pathlib import Path

                    response = requests.get(image_url, timeout=30)
                    if response.status_code == 200:
                        # Save to temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                            temp_file.write(response.content)
                            temp_path = temp_file.name

                        # Upload to new listing with rank after mockups (8, 9, 10)
                        rank = i + 8  # Start after 7 mockups (ranks 8, 9, 10)

                        endpoint = f"/application/shops/{self.shop_id}/listings/{listing_id}/images"

                        with open(temp_path, 'rb') as f:
                            files = {
                                'image': (f'static_image_{i+1}.jpg', f, 'image/jpeg'),
                                'rank': (None, str(rank))
                            }

                            upload_response = self.make_request("POST", endpoint, files=files)

                            if upload_response.status_code in [200, 201]:
                                self.logger.info(f"✅ Uploaded static image {i+1}/{len(static_images_to_copy)}")
                            else:
                                self.logger.error(f"❌ Failed to upload static image {i+1}: {upload_response.text}")

                        # Clean up temp file
                        Path(temp_path).unlink(missing_ok=True)

                        # Rate limiting
                        time.sleep(self.rate_limit_delay)

                    else:
                        self.logger.error(f"Failed to download static image from {image_url}")

                except Exception as e:
                    self.logger.error(f"Error processing static image {i+1}: {e}")
                    continue

            self.logger.info(f"Completed static image copying for listing {listing_id}")

        except Exception as e:
            self.logger.error(f"Failed to copy static images: {e}")
            # Don't raise - listing can exist without static images

    def _get_template_listing_with_images(self) -> Optional[Dict[str, Any]]:
        """Get template listing with images."""
        try:
            # Search for template listing
            endpoint = f"/application/shops/{self.shop_id}/listings"
            params = {
                'state': 'draft',
                'limit': 100,
                'includes': ['Images']
            }

            response = self.make_request("GET", endpoint, params=params)

            if response.status_code != 200:
                return None

            listings_data = response.json()
            listings = listings_data.get('results', [])

            # Find template listing
            for listing in listings:
                title = listing.get('title', '').lower()
                if 'digital download template' in title:
                    return listing

            return None

        except Exception as e:
            self.logger.error(f"Error fetching template listing: {e}")
            return None
    
    def delete_listing(self, listing_id: str) -> bool:
        """Delete a listing."""
        try:
            endpoint = f"/application/shops/{self.shop_id}/listings/{listing_id}"
            response = self.make_request("DELETE", endpoint)
            
            if response.status_code == 200:
                self.logger.info(f"Listing {listing_id} deleted successfully")
                return True
            else:
                self.logger.error(f"Failed to delete listing: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete listing {listing_id}: {e}")
            return False
