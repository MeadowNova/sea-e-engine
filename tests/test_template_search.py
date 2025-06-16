#!/usr/bin/env python3
"""
Test Template Listing Search
============================

Test script to find the "digital download template" listing and extract static images.
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
env_path = Path(".env")
if env_path.exists():
    print("📁 Loading environment variables from .env file...")
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    print("✅ Environment variables loaded")

# Add src to path for imports
sys.path.append(str(Path("src")))

try:
    from api.etsy import EtsyAPIClient
    print("✅ Successfully imported EtsyAPIClient")
except ImportError as e:
    print(f"❌ Failed to import EtsyAPIClient: {e}")
    sys.exit(1)

def test_template_search():
    """Test searching for the digital download template listing."""
    
    try:
        # Initialize Etsy client
        etsy_client = EtsyAPIClient()
        print("✅ Etsy client initialized")
        
        # Search for draft listings
        print("\n🔍 Searching for draft listings...")
        endpoint = f"/application/shops/{etsy_client.shop_id}/listings"
        params = {
            'state': 'draft',
            'limit': 100,
            'includes': ['Images']
        }
        
        response = etsy_client.make_request("GET", endpoint, params=params)
        
        if response.status_code != 200:
            print(f"❌ Failed to search listings: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        listings_data = response.json()
        listings = listings_data.get('results', [])
        
        print(f"📋 Found {len(listings)} draft listings")
        
        # List all draft listings
        print("\n📝 Draft listings:")
        for i, listing in enumerate(listings, 1):
            title = listing.get('title', 'No title')
            listing_id = listing.get('listing_id')
            images = listing.get('images', [])
            print(f"   {i:2d}. {title} (ID: {listing_id}, Images: {len(images)})")
        
        # Find template listing
        template_listing = None
        for listing in listings:
            title = listing.get('title', '').lower()
            if 'digital download template' in title:
                template_listing = listing
                break
        
        if template_listing:
            print(f"\n✅ Found template listing!")
            print(f"   Title: {template_listing.get('title')}")
            print(f"   ID: {template_listing.get('listing_id')}")
            
            # Extract image information
            images = template_listing.get('images', [])
            print(f"   Images: {len(images)}")
            
            if images:
                print(f"\n🖼️  Image details:")
                for i, image in enumerate(images, 1):
                    image_id = image.get('listing_image_id')
                    url = image.get('url_570xN', 'No URL')
                    rank = image.get('rank', 'No rank')
                    print(f"      {i}. ID: {image_id}, Rank: {rank}")
                    print(f"         URL: {url}")
                
                # Identify static images (last 3)
                if len(images) >= 3:
                    static_images = images[-3:]
                    print(f"\n📌 Static images (last 3):")
                    for i, image in enumerate(static_images, 1):
                        image_id = image.get('listing_image_id')
                        print(f"      {i}. Static Image ID: {image_id}")
            
            return True
        else:
            print(f"\n❌ No listing found with 'digital download template' in title")
            print(f"   Please create a draft listing with this title containing your 3 static images")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Template Listing Search Test")
    print("="*50)
    
    # Check for required environment variables
    required_vars = ['ETSY_API_KEY', 'ETSY_REFRESH_TOKEN', 'ETSY_SHOP_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    success = test_template_search()
    
    if success:
        print(f"\n🎉 Template listing found successfully!")
        print(f"Ready to proceed with Phase 2 pipeline testing.")
    else:
        print(f"\n⚠️  Template listing not found.")
        print(f"Please create a draft listing titled 'digital download template' with your 3 static images.")
        sys.exit(1)
