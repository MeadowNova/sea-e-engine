#!/usr/bin/env python3
"""
Etsy OAuth 2.0 Authentication Test Script

This script tests the Etsy API authentication using OAuth 2.0 and performs
a basic authenticated action (fetch shop information).

Requirements:
- ETSY_API_KEY, ETSY_API_SECRET, ETSY_ACCESS_TOKEN, ETSY_REFRESH_TOKEN, ETSY_SHOP_ID in .env file
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
logger = setup_logger("etsy_auth_test")


class EtsyAuthTest:
    """Test class for Etsy API authentication with token refresh capability."""
    
    def __init__(self):
        """Initialize with credentials from environment."""
        self.api_key = os.getenv("ETSY_API_KEY")
        self.api_secret = os.getenv("ETSY_API_SECRET")
        self.access_token = os.getenv("ETSY_ACCESS_TOKEN")
        self.refresh_token = os.getenv("ETSY_REFRESH_TOKEN")
        self.shop_id = os.getenv("ETSY_SHOP_ID")
        
        self.base_url = "https://openapi.etsy.com/v3"
        self.token_expiry = 0  # Will be set when token is refreshed
        
        # Validate required credentials
        required_vars = ["ETSY_API_KEY", "ETSY_REFRESH_TOKEN", "ETSY_SHOP_ID"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    def get_headers(self):
        """Get authentication headers for API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def refresh_access_token(self):
        """Refresh access token using refresh token."""
        logger.info("Refreshing Etsy access token...")
        
        if not self.refresh_token:
            logger.error("No refresh token available. Cannot refresh access token.")
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

                # Update refresh token if a new one was provided
                if new_refresh_token:
                    self.refresh_token = new_refresh_token

                logger.info("✅ Access token refreshed successfully.")
                logger.info(f"New token expires in {token_data.get('expires_in', 3600)} seconds")
                return True
            else:
                logger.error(f"❌ Failed to refresh access token: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Exception refreshing access token: {str(e)}")
            return False
    
    def make_authenticated_request(self, method, endpoint, params=None, data=None, retry_count=0):
        """Make an authenticated request to the Etsy API with automatic token refresh."""
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
            
            # Handle token expiration
            if response.status_code == 401 and retry_count < 1:
                logger.warning("Unauthorized response. Attempting to refresh token...")
                if self.refresh_access_token():
                    return self.make_authenticated_request(method, endpoint, params, data, retry_count + 1)
            
            # Handle rate limiting
            if response.status_code == 429 and retry_count < 3:
                retry_after = int(response.headers.get("Retry-After", 5))
                logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                return self.make_authenticated_request(method, endpoint, params, data, retry_count + 1)
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error during API request: {e}")
            if retry_count < 2:
                logger.info(f"Retrying request ({retry_count + 1}/3)...")
                time.sleep(2 ** retry_count)  # Exponential backoff
                return self.make_authenticated_request(method, endpoint, params, data, retry_count + 1)
            raise
    
    def test_authentication(self):
        """Test authentication by fetching shop information."""
        logger.info("Testing Etsy API authentication...")
        
        try:
            # Test endpoint: Get shop information
            endpoint = f"/application/shops/{self.shop_id}"
            
            logger.info(f"Making request to: {self.base_url}{endpoint}")
            response = self.make_authenticated_request("GET", endpoint)
            
            if response.status_code == 200:
                shop_data = response.json()
                shop_name = shop_data.get("shop_name", "Unknown")
                shop_title = shop_data.get("title", "No title")
                
                logger.info("✅ Etsy authentication successful!")
                logger.info(f"Shop Name: {shop_name}")
                logger.info(f"Shop Title: {shop_title}")
                logger.info(f"Shop ID: {self.shop_id}")
                
                return True
                
            else:
                logger.error(f"❌ Authentication failed with status {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during authentication test: {e}")
            return False
    
    def test_token_refresh(self):
        """Test token refresh functionality."""
        logger.info("Testing Etsy token refresh functionality...")
        
        try:
            # Store original token for comparison
            original_token = self.access_token
            
            # Attempt to refresh token
            refresh_success = self.refresh_access_token()
            
            if refresh_success:
                if self.access_token != original_token:
                    logger.info("✅ Token refresh successful - new token received!")
                else:
                    logger.info("✅ Token refresh successful - same token returned (still valid)")
                return True
            else:
                logger.warning("⚠️ Token refresh failed - tokens may be expired")
                logger.info("This is expected if tokens haven't been refreshed recently")
                logger.info("Manual re-authentication may be required")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during token refresh test: {e}")
            return False
    
    def test_basic_api_call(self):
        """Test a basic API call to verify full functionality."""
        logger.info("Testing basic Etsy API functionality...")
        
        try:
            # Test endpoint: Get shop sections (categories)
            endpoint = f"/application/shops/{self.shop_id}/sections"
            
            response = self.make_authenticated_request("GET", endpoint)
            
            if response.status_code == 200:
                sections_data = response.json()
                sections_count = len(sections_data.get("results", []))
                
                logger.info("✅ Basic API call successful!")
                logger.info(f"Shop has {sections_count} sections/categories")
                
                return True
            else:
                logger.warning(f"⚠️ Basic API call returned status {response.status_code}")
                logger.warning(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during basic API test: {e}")
            return False
    
    def test_user_info(self):
        """Test fetching authenticated user information."""
        logger.info("Testing user information retrieval...")
        
        try:
            # Test endpoint: Get authenticated user info
            endpoint = "/application/users/me"
            
            response = self.make_authenticated_request("GET", endpoint)
            
            if response.status_code == 200:
                user_data = response.json()
                user_id = user_data.get("user_id", "Unknown")
                login_name = user_data.get("login_name", "Unknown")
                
                logger.info("✅ User information retrieval successful!")
                logger.info(f"User ID: {user_id}")
                logger.info(f"Login Name: {login_name}")
                
                return True
            else:
                logger.warning(f"⚠️ User info call returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during user info test: {e}")
            return False


def main():
    """Main function to run all authentication tests."""
    logger.info("=" * 60)
    logger.info("ETSY API AUTHENTICATION TEST")
    logger.info("=" * 60)
    
    try:
        # Initialize test class
        etsy_test = EtsyAuthTest()
        
        # Run token refresh test first
        refresh_success = etsy_test.test_token_refresh()
        
        if refresh_success:
            # Run authentication test
            auth_success = etsy_test.test_authentication()
            
            if auth_success:
                # Run user info test
                user_success = etsy_test.test_user_info()
                
                # Run basic API functionality test
                api_success = etsy_test.test_basic_api_call()
                
                if user_success and api_success:
                    logger.info("🎉 All Etsy API tests passed successfully!")
                    logger.info("✅ Token refresh working")
                    logger.info("✅ Authentication working")
                    logger.info("✅ User info retrieval working")
                    logger.info("✅ Basic API calls working")
                    return True
                else:
                    logger.warning("⚠️ Authentication works but some API calls failed")
                    return False
            else:
                logger.error("❌ Etsy authentication failed")
                return False
        else:
            logger.warning("⚠️ Etsy token refresh failed - this indicates tokens need manual renewal")
            logger.info("📋 ETSY AUTHENTICATION STATUS:")
            logger.info("   - API credentials are configured")
            logger.info("   - Token refresh mechanism is implemented")
            logger.info("   - Manual re-authentication required to get fresh tokens")
            logger.info("   - Once fresh tokens are obtained, the system will work correctly")
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
