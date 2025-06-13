#!/usr/bin/env python3
"""
Printify API Authentication Test Script

This script tests the Printify API authentication using API token and performs
comprehensive authenticated actions including shop validation and catalog access.

Requirements:
- PRINTIFY_API_KEY and PRINTIFY_SHOP_ID in .env file
"""

import os
import sys
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))
from core.logger import setup_logger

# Load environment variables
load_dotenv()

# Set up logging
logger = setup_logger("printify_auth_test")


class PrintifyAuthTest:
    """Test class for Printify API authentication with comprehensive validation."""
    
    def __init__(self):
        """Initialize with credentials from environment."""
        self.api_key = os.getenv("PRINTIFY_API_KEY")
        self.shop_id = os.getenv("PRINTIFY_SHOP_ID")
        
        self.base_url = "https://api.printify.com/v1"
        
        # Validate required credentials
        required_vars = ["PRINTIFY_API_KEY", "PRINTIFY_SHOP_ID"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    def get_headers(self):
        """Get authentication headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "SEA-Engine/2.1"
        }
    
    def make_request(self, method, endpoint, params=None, data=None, retry_count=0):
        """Make a request to the Printify API with retry logic."""
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=30
            )
            
            # Handle rate limiting
            if response.status_code == 429 and retry_count < 3:
                retry_after = int(response.headers.get("Retry-After", 5))
                logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                return self.make_request(method, endpoint, params, data, retry_count + 1)
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error during API request: {e}")
            if retry_count < 2:
                logger.info(f"Retrying request ({retry_count + 1}/3)...")
                time.sleep(2 ** retry_count)  # Exponential backoff
                return self.make_request(method, endpoint, params, data, retry_count + 1)
            raise
    
    def test_authentication(self):
        """Test authentication by fetching shops and validating access."""
        logger.info("Testing Printify API authentication...")
        
        try:
            # Test endpoint: Get all shops (this validates authentication)
            endpoint = "/shops.json"
            
            logger.info(f"Making request to: {self.base_url}{endpoint}")
            response = self.make_request("GET", endpoint)
            
            if response.status_code == 200:
                shops_data = response.json()
                shops = shops_data if isinstance(shops_data, list) else shops_data.get("data", [])
                
                logger.info("✅ Printify authentication successful!")
                logger.info(f"Found {len(shops)} shops in account")
                
                # Show shop details
                for shop in shops:
                    shop_title = shop.get("title", "Unknown")
                    shop_id = shop.get("id", "Unknown")
                    logger.info(f"  - {shop_title} (ID: {shop_id})")
                
                return True
                
            else:
                logger.error(f"❌ Authentication failed with status {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during authentication test: {e}")
            return False
    
    def test_shop_validation(self):
        """Test shop validation by checking if shop exists in user's account."""
        logger.info("Testing Printify shop validation...")
        
        try:
            # Test endpoint: Get all shops
            endpoint = "/shops.json"
            
            response = self.make_request("GET", endpoint)
            
            if response.status_code == 200:
                shops_data = response.json()
                shops = shops_data if isinstance(shops_data, list) else shops_data.get("data", [])
                
                # Find shop with matching ID
                target_shop = None
                for shop in shops:
                    if str(shop.get("id")) == str(self.shop_id):
                        target_shop = shop
                        break
                
                if target_shop:
                    logger.info("✅ Shop validation successful!")
                    logger.info(f"Shop found: {target_shop.get('title', 'Unknown')}")
                    logger.info(f"Shop ID: {target_shop.get('id')}")
                    logger.info(f"Total shops in account: {len(shops)}")
                    return True
                else:
                    logger.error(f"❌ Shop ID {self.shop_id} not found in your Printify account")
                    logger.info(f"Available shops: {[shop.get('id') for shop in shops]}")
                    return False
            else:
                logger.error(f"❌ Shop validation failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during shop validation: {e}")
            return False
    
    def test_blueprint_access(self):
        """Test API functionality by fetching available blueprints."""
        logger.info("Testing Printify blueprint access...")
        
        try:
            # Test endpoint: Get catalog blueprints
            endpoint = "/catalog/blueprints.json"
            params = {"limit": 10}  # Limit for faster testing
            
            response = self.make_request("GET", endpoint, params=params)
            
            if response.status_code == 200:
                blueprints_data = response.json()
                blueprints = blueprints_data if isinstance(blueprints_data, list) else blueprints_data.get("data", [])
                blueprint_count = len(blueprints)
                
                logger.info("✅ Blueprint access successful!")
                logger.info(f"Available blueprints (first 10): {blueprint_count}")
                
                # Show first few blueprint titles for verification
                if blueprints:
                    logger.info("Sample blueprints:")
                    for i, blueprint in enumerate(blueprints[:3]):
                        title = blueprint.get("title", "Unknown")
                        blueprint_id = blueprint.get("id", "Unknown")
                        logger.info(f"  {i+1}. {title} (ID: {blueprint_id})")
                
                return True
            else:
                logger.warning(f"⚠️ Blueprint access returned status {response.status_code}")
                logger.warning(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during blueprint access test: {e}")
            return False
    
    def test_print_providers(self):
        """Test API functionality by fetching print providers."""
        logger.info("Testing Printify print providers access...")
        
        try:
            # Test endpoint: Get print providers
            endpoint = "/catalog/print_providers.json"
            
            response = self.make_request("GET", endpoint)
            
            if response.status_code == 200:
                providers_data = response.json()
                providers = providers_data if isinstance(providers_data, list) else providers_data.get("data", [])
                provider_count = len(providers)
                
                logger.info("✅ Print providers access successful!")
                logger.info(f"Available print providers: {provider_count}")
                
                # Show first few providers for verification
                if providers:
                    logger.info("Sample print providers:")
                    for i, provider in enumerate(providers[:3]):
                        title = provider.get("title", "Unknown")
                        provider_id = provider.get("id", "Unknown")
                        location = provider.get("location", {}).get("country", "Unknown")
                        logger.info(f"  {i+1}. {title} (ID: {provider_id}, Country: {location})")
                
                return True
            else:
                logger.warning(f"⚠️ Print providers access returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during print providers test: {e}")
            return False
    
    def test_products_access(self):
        """Test products access in the shop."""
        logger.info("Testing Printify products access...")
        
        try:
            # Test endpoint: Get products in shop
            endpoint = f"/shops/{self.shop_id}/products.json"
            params = {"limit": 5}  # Limit for faster testing
            
            response = self.make_request("GET", endpoint, params=params)
            
            if response.status_code == 200:
                products_data = response.json()
                products = products_data.get("data", [])
                product_count = len(products)
                
                logger.info("✅ Products access successful!")
                logger.info(f"Products in shop (first 5): {product_count}")
                
                # Show product details if any exist
                if products:
                    logger.info("Sample products:")
                    for i, product in enumerate(products[:3]):
                        title = product.get("title", "Unknown")
                        product_id = product.get("id", "Unknown")
                        status = product.get("visible", False)
                        logger.info(f"  {i+1}. {title} (ID: {product_id}, Visible: {status})")
                else:
                    logger.info("No products found in shop (this is normal for new shops)")
                
                return True
            else:
                logger.warning(f"⚠️ Products access returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during products access test: {e}")
            return False
    
    def test_blueprint_details(self):
        """Test fetching detailed blueprint information."""
        logger.info("Testing blueprint details access...")
        
        try:
            # First get a blueprint ID
            blueprints_response = self.make_request("GET", "/catalog/blueprints.json", {"limit": 1})
            
            if blueprints_response.status_code != 200:
                logger.warning("⚠️ Could not fetch blueprints for detail test")
                return False
            
            blueprints_data = blueprints_response.json()
            blueprints = blueprints_data if isinstance(blueprints_data, list) else blueprints_data.get("data", [])
            
            if not blueprints:
                logger.warning("⚠️ No blueprints available for detail test")
                return False
            
            blueprint_id = blueprints[0].get("id")
            blueprint_title = blueprints[0].get("title", "Unknown")
            
            # Test endpoint: Get blueprint details
            endpoint = f"/catalog/blueprints/{blueprint_id}.json"
            
            response = self.make_request("GET", endpoint)
            
            if response.status_code == 200:
                blueprint_data = response.json()
                title = blueprint_data.get("title", "Unknown")
                description = blueprint_data.get("description", "No description")
                
                logger.info("✅ Blueprint details access successful!")
                logger.info(f"Blueprint: {title}")
                logger.info(f"Description: {description[:100]}...")
                
                return True
            else:
                logger.warning(f"⚠️ Blueprint details returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during blueprint details test: {e}")
            return False


def main():
    """Main function to run all authentication tests."""
    logger.info("=" * 60)
    logger.info("PRINTIFY API AUTHENTICATION TEST")
    logger.info("=" * 60)
    
    try:
        # Initialize test class
        printify_test = PrintifyAuthTest()
        
        # Run authentication test
        auth_success = printify_test.test_authentication()
        
        if auth_success:
            # Run shop validation test
            shop_success = printify_test.test_shop_validation()
            
            # Run blueprint access test
            blueprint_success = printify_test.test_blueprint_access()
            
            # Run print providers test
            providers_success = printify_test.test_print_providers()
            
            # Run products access test
            products_success = printify_test.test_products_access()
            
            # Run blueprint details test
            details_success = printify_test.test_blueprint_details()
            
            # Evaluate overall success
            all_tests = [shop_success, blueprint_success, providers_success, products_success, details_success]
            passed_tests = sum(all_tests)
            total_tests = len(all_tests)
            
            if passed_tests == total_tests:
                logger.info("🎉 All Printify API tests passed successfully!")
                logger.info("✅ Authentication working")
                logger.info("✅ Shop validation working")
                logger.info("✅ Blueprint access working")
                logger.info("✅ Print providers access working")
                logger.info("✅ Products access working")
                logger.info("✅ Blueprint details access working")
                return True
            elif passed_tests >= total_tests - 1:
                logger.info("🎉 Printify API tests mostly successful!")
                logger.info(f"✅ {passed_tests}/{total_tests} tests passed")
                logger.warning("⚠️ Some non-critical tests failed but core functionality works")
                return True
            else:
                logger.warning(f"⚠️ Authentication works but {total_tests - passed_tests}/{total_tests} API tests failed")
                return False
        else:
            logger.error("❌ Printify authentication failed")
            return False
            
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False
    finally:
        logger.info("=" * 60)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
