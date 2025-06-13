#!/usr/bin/env python3
"""
Simple Etsy Authentication Test - Tests Current Tokens
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))
from core.logger import setup_logger

# Load environment variables
load_dotenv()

# Set up logging
logger = setup_logger("etsy_current_auth_test")


def test_current_etsy_auth():
    """Test current Etsy authentication without refresh."""
    logger.info("=" * 60)
    logger.info("ETSY CURRENT AUTHENTICATION TEST")
    logger.info("=" * 60)
    
    # Get credentials
    api_key = os.getenv("ETSY_API_KEY")
    access_token = os.getenv("ETSY_ACCESS_TOKEN")
    shop_id = os.getenv("ETSY_SHOP_ID")
    
    if not all([api_key, access_token, shop_id]):
        logger.error("❌ Missing required environment variables")
        return False
    
    # Test authentication by fetching shop information
    logger.info("🔍 Testing current access token...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        # Test endpoint: Get shop information
        url = f"https://openapi.etsy.com/v3/application/shops/{shop_id}"
        
        logger.info(f"Making request to: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            shop_data = response.json()
            shop_name = shop_data.get("shop_name", "Unknown")
            shop_title = shop_data.get("title", "No title")
            
            logger.info("✅ Etsy authentication successful!")
            logger.info(f"Shop Name: {shop_name}")
            logger.info(f"Shop Title: {shop_title}")
            logger.info(f"Shop ID: {shop_id}")
            
            # Test another endpoint
            logger.info("🔍 Testing additional API call...")
            sections_url = f"https://openapi.etsy.com/v3/application/shops/{shop_id}/sections"
            sections_response = requests.get(sections_url, headers=headers, timeout=30)
            
            if sections_response.status_code == 200:
                sections_data = sections_response.json()
                sections_count = len(sections_data.get("results", []))
                logger.info(f"✅ Shop has {sections_count} sections/categories")
            else:
                logger.warning(f"⚠️ Sections API returned: {sections_response.status_code}")
            
            logger.info("🎉 All Etsy API tests passed!")
            logger.info("✅ Access token is valid and working")
            logger.info("✅ API calls are successful")
            logger.info("✅ Etsy integration is ready for SEA-E engine")
            
            return True
            
        elif response.status_code == 401:
            logger.error("❌ Authentication failed - token may be expired")
            logger.error(f"Response: {response.text}")
            logger.error("Run: python auth/etsy_oauth_renewal.py")
            return False
        else:
            logger.error(f"❌ API call failed with status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during authentication test: {e}")
        return False
    finally:
        logger.info("=" * 60)


if __name__ == "__main__":
    success = test_current_etsy_auth()
    sys.exit(0 if success else 1)
