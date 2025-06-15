#!/usr/bin/env python3
"""
Check Blueprint Structure
========================

Quick script to understand what the Printify blueprint API returns.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from api.printify import PrintifyAPIClient

def main():
    """Check blueprint structure."""
    printify = PrintifyAPIClient()
    
    print("🔍 Checking Blueprint 12 (T-shirt) Structure")
    print("=" * 50)
    
    try:
        # Get blueprint details
        blueprint_details = printify.get_blueprint_details(12)
        
        print("📋 Blueprint Details Structure:")
        print(json.dumps(blueprint_details, indent=2)[:2000] + "..." if len(json.dumps(blueprint_details, indent=2)) > 2000 else json.dumps(blueprint_details, indent=2))
        
        # Check for variants
        if "variants" in blueprint_details:
            variants = blueprint_details["variants"]
            print(f"\n✅ Found {len(variants)} variants in blueprint")
            if variants:
                print("📊 First variant structure:")
                print(json.dumps(variants[0], indent=2))
        else:
            print("\n❌ No 'variants' key in blueprint")
            print("Available keys:", list(blueprint_details.keys()))
        
        # Check variants from API
        print("\n🔍 Checking variants from API...")
        try:
            api_variants = printify.get_blueprint_variants(12, 29)
            print(f"📊 API returned {len(api_variants)} variants")
            if api_variants:
                print("📋 First API variant structure:")
                print(json.dumps(api_variants[0], indent=2))
                print("\n📋 Second API variant structure:")
                print(json.dumps(api_variants[1], indent=2))
        except Exception as e:
            print(f"❌ Error getting API variants: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    main()
