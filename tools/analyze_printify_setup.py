#!/usr/bin/env python3
"""
Analyze current Printify setup to understand recent product configurations,
variations, pricing, and shipping profiles for the workflow test.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from api.printify import PrintifyAPIClient

def analyze_current_setup():
    """Analyze current Printify setup and recent products."""
    print("🔍 Analyzing Current Printify Setup")
    print("=" * 60)
    
    try:
        # Initialize client
        client = PrintifyAPIClient()
        print("✅ Printify client initialized")
        
        # Test connection
        if not client.test_connection():
            print("❌ Connection failed")
            return None
            
        print("✅ Connection successful")
        
        # Use shop ID from client (already configured)
        shop_id = client.shop_id
        print(f"\n🎯 Using configured shop ID: {shop_id}")
        
        # Get recent products
        print("\n📋 Analyzing recent products...")
        products = client.list_products(limit=5)
        
        if not products:
            print("No products found")
            return {
                'shop_id': shop_id,
                'shops': shops,
                'products': [],
                'analysis': 'No existing products to analyze'
            }
        
        print(f"Found {len(products)} recent products:")
        
        analysis_data = {
            'shop_id': shop_id,
            'products': [],
            'common_patterns': {
                'blueprints': {},
                'providers': {},
                'pricing_ranges': {},
                'variant_counts': []
            }
        }
        
        for i, product in enumerate(products, 1):
            print(f"\n📋 Product {i}: {product.get('title', 'Untitled')}")
            print(f"   ID: {product.get('id')}")
            print(f"   Blueprint: {product.get('blueprint_id')}")
            print(f"   Provider: {product.get('print_provider_id')}")
            print(f"   Status: {product.get('status', 'unknown')}")
            
            # Get detailed product info
            try:
                details = client.get_product(product.get('id'))
                if details:
                    variants = details.get('variants', [])
                    print(f"   Variants: {len(variants)}")
                    
                    # Analyze pricing
                    if variants:
                        prices = [v.get('price', 0) for v in variants if v.get('price')]
                        if prices:
                            min_price = min(prices) / 100  # Convert from cents
                            max_price = max(prices) / 100
                            print(f"   Price range: ${min_price:.2f} - ${max_price:.2f}")
                            
                            # Store for analysis
                            analysis_data['common_patterns']['pricing_ranges'][product.get('id')] = {
                                'min': min_price,
                                'max': max_price,
                                'count': len(variants)
                            }
                    
                    # Store product details
                    analysis_data['products'].append({
                        'id': product.get('id'),
                        'title': product.get('title'),
                        'blueprint_id': product.get('blueprint_id'),
                        'print_provider_id': product.get('print_provider_id'),
                        'status': product.get('status'),
                        'variant_count': len(variants),
                        'variants': variants[:3] if variants else []  # Store first 3 for analysis
                    })
                    
                    # Track common patterns
                    blueprint_id = product.get('blueprint_id')
                    provider_id = product.get('print_provider_id')
                    
                    if blueprint_id:
                        analysis_data['common_patterns']['blueprints'][blueprint_id] = \
                            analysis_data['common_patterns']['blueprints'].get(blueprint_id, 0) + 1
                    
                    if provider_id:
                        analysis_data['common_patterns']['providers'][provider_id] = \
                            analysis_data['common_patterns']['providers'].get(provider_id, 0) + 1
                    
                    analysis_data['common_patterns']['variant_counts'].append(len(variants))
                    
            except Exception as e:
                print(f"   ⚠️ Could not get details: {e}")
        
        # Generate recommendations
        print("\n📊 ANALYSIS SUMMARY")
        print("=" * 40)
        
        if analysis_data['common_patterns']['blueprints']:
            most_used_blueprint = max(analysis_data['common_patterns']['blueprints'].items(), 
                                    key=lambda x: x[1])
            print(f"Most used blueprint: {most_used_blueprint[0]} ({most_used_blueprint[1]} products)")
        
        if analysis_data['common_patterns']['providers']:
            most_used_provider = max(analysis_data['common_patterns']['providers'].items(), 
                                   key=lambda x: x[1])
            print(f"Most used provider: {most_used_provider[0]} ({most_used_provider[1]} products)")
        
        if analysis_data['common_patterns']['variant_counts']:
            avg_variants = sum(analysis_data['common_patterns']['variant_counts']) / len(analysis_data['common_patterns']['variant_counts'])
            print(f"Average variants per product: {avg_variants:.1f}")
        
        # Save analysis
        output_file = "config/printify_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        print(f"\n💾 Analysis saved to: {output_file}")
        
        return analysis_data
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return None

def get_recommended_config(analysis_data):
    """Generate recommended configuration based on analysis."""
    if not analysis_data or not analysis_data['products']:
        # Default configuration for t-shirts
        return {
            'blueprint_id': 6,  # Unisex Heavy Cotton Tee (Gildan 5000)
            'print_provider_id': 1,  # Printify default
            'base_price_markup': 1.5,  # 50% markup
            'recommended_variants': ['S', 'M', 'L', 'XL'],
            'recommended_colors': ['White', 'Black', 'Navy', 'Heather Grey']
        }
    
    # Use most common patterns from existing products
    blueprints = analysis_data['common_patterns']['blueprints']
    providers = analysis_data['common_patterns']['providers']
    
    recommended_blueprint = max(blueprints.items(), key=lambda x: x[1])[0] if blueprints else 6
    recommended_provider = max(providers.items(), key=lambda x: x[1])[0] if providers else 1
    
    return {
        'blueprint_id': recommended_blueprint,
        'print_provider_id': recommended_provider,
        'base_price_markup': 1.5,
        'recommended_variants': ['S', 'M', 'L', 'XL'],
        'recommended_colors': ['White', 'Black', 'Navy', 'Heather Grey']
    }

if __name__ == "__main__":
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    
    # Run analysis
    analysis = analyze_current_setup()
    
    if analysis:
        # Generate recommendations
        config = get_recommended_config(analysis)
        
        print("\n🎯 RECOMMENDED CONFIGURATION")
        print("=" * 40)
        print(f"Blueprint ID: {config['blueprint_id']}")
        print(f"Print Provider ID: {config['print_provider_id']}")
        print(f"Base Price Markup: {config['base_price_markup']}x")
        print(f"Recommended Variants: {', '.join(config['recommended_variants'])}")
        print(f"Recommended Colors: {', '.join(config['recommended_colors'])}")
        
        # Save recommended config
        with open("config/recommended_product_config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n✅ Analysis complete! Ready for workflow test.")
    else:
        print("\n❌ Analysis failed. Please check credentials and connection.")
