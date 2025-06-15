#!/usr/bin/env python3
"""
Test script to understand the actual Printify blueprint structure
and fix the variant building issue.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from api.printify import PrintifyAPIClient
import json

def test_blueprint_structure():
    """Test the actual blueprint structure from Printify API."""
    print("🔍 Testing Blueprint 12 Structure...")
    
    try:
        client = PrintifyAPIClient()
        
        # Get blueprint details
        blueprint = client.get_blueprint_details(12)
        
        print(f"Blueprint: {blueprint.get('title', 'Unknown')}")
        print(f"Provider 29 available: {any(p.get('id') == 29 for p in blueprint.get('print_providers', []))}")
        
        # Check variants structure
        variants = blueprint.get('variants', [])
        print(f"Total variants: {len(variants)}")
        
        if variants:
            print("\nFirst variant structure:")
            first_variant = variants[0]
            print(f"  ID: {first_variant.get('id')}")
            print(f"  Title: {first_variant.get('title', 'N/A')}")
            print(f"  Price: ${first_variant.get('price', 0)/100:.2f}")
            print(f"  Available: {first_variant.get('is_enabled', False)}")
            
            options = first_variant.get('options', [])
            print(f"  Options ({len(options)}):")
            for option in options:
                print(f"    - {option.get('name', 'N/A')}: {option.get('value', 'N/A')}")
        
        # Test simple variant filtering for white color
        print("\n🔧 Testing variant filtering...")
        white_variants = [v for v in variants if any(
            'white' in opt.get('value', '').lower() 
            for opt in v.get('options', [])
        )]
        print(f"White variants found: {len(white_variants)}")
        
        if white_variants:
            print(f"Sample white variant: {white_variants[0].get('title', 'N/A')}")
        
        # Test filtering for specific colors from our blueprint config
        test_colors = ['white', 'black', 'navy', 'ash']
        print(f"\n🎨 Testing filtering for colors: {test_colors}")
        
        for color in test_colors:
            color_variants = [v for v in variants if any(
                color.lower() in opt.get('value', '').lower() 
                for opt in v.get('options', [])
            )]
            print(f"  {color}: {len(color_variants)} variants")
            
            if color_variants:
                # Show first variant for this color
                sample = color_variants[0]
                print(f"    Sample: {sample.get('title', 'N/A')} (ID: {sample.get('id')})")
        
        # Test size filtering
        test_sizes = ['S', 'M', 'L', 'XL']
        print(f"\n📏 Testing filtering for sizes: {test_sizes}")
        
        for size in test_sizes:
            size_variants = [v for v in variants if any(
                size.upper() == opt.get('value', '').upper() 
                for opt in v.get('options', [])
            )]
            print(f"  {size}: {len(size_variants)} variants")
        
        # Test combined filtering (white + medium)
        print("\n🔄 Testing combined filtering (White + Medium)...")
        combined_variants = [v for v in variants if 
            any('white' in opt.get('value', '').lower() for opt in v.get('options', [])) and
            any('M' == opt.get('value', '').upper() for opt in v.get('options', []))
        ]
        print(f"White + Medium variants: {len(combined_variants)}")
        
        if combined_variants:
            sample = combined_variants[0]
            print(f"Sample: {sample.get('title', 'N/A')} (ID: {sample.get('id')})")
            print(f"Price: ${sample.get('price', 0)/100:.2f}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    success = test_blueprint_structure()
    print(f"\n{'✅ Test completed successfully' if success else '❌ Test failed'}")
