#!/usr/bin/env python3
"""
Quick validation script to demonstrate configuration file usage.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def main():
    """Demonstrate configuration file usage."""
    config_dir = project_root / "config"
    
    # Load product blueprints
    with open(config_dir / "product_blueprints.json", 'r') as f:
        product_config = json.load(f)
    
    # Load mockup blueprints  
    with open(config_dir / "mockup_blueprints.json", 'r') as f:
        mockup_config = json.load(f)
    
    print("=== Configuration Summary ===")
    print(f"Product Blueprints Version: {product_config['version']}")
    print(f"Mockup Blueprints Version: {mockup_config['version']}")
    print(f"Last Updated: {product_config['last_updated']}")
    
    print(f"\n=== Available Products ({len(product_config['products'])}) ===")
    for key, product in product_config['products'].items():
        metadata = product['metadata']
        printify = product['printify_config']
        colors = list(product['available_options']['colors'].keys())
        
        print(f"\n{key}:")
        print(f"  Name: {metadata['name']}")
        print(f"  Brand: {metadata['brand']} {metadata['model']}")
        print(f"  Provider: {printify['print_provider_name']} (ID: {printify['print_provider_id']})")
        print(f"  Blueprint ID: {printify['blueprint_id']}")
        print(f"  Colors: {', '.join(colors)}")
        print(f"  Status: {metadata['validation_status']}")
    
    print(f"\n=== Mockup Templates ({len(mockup_config['mockup_templates'])}) ===")
    for key, template in mockup_config['mockup_templates'].items():
        config = template['template_config']
        colors = list(template['color_mappings'].keys())
        
        print(f"\n{key}:")
        print(f"  Template Size: {config['template_size']}")
        print(f"  Design Area: {config['design_area']}")
        print(f"  Category: {config['category']}")
        print(f"  Colors: {', '.join(colors)}")
    
    print(f"\n=== Integration Check ===")
    product_keys = set(product_config['products'].keys())
    mockup_keys = set(mockup_config['mockup_templates'].keys())
    
    if product_keys == mockup_keys:
        print("✅ All blueprint keys match between configurations")
        print(f"✅ Ready for automation engine integration")
        print(f"✅ {len(product_keys)} products configured and validated")
    else:
        print("❌ Blueprint key mismatch detected")
    
    # Test MockupGenerator integration
    try:
        from src.modules.mockup_generator import MockupGenerator
        generator = MockupGenerator()
        generator_keys = set(generator.list_available_blueprints().keys())
        
        if generator_keys == product_keys:
            print("✅ MockupGenerator integration confirmed")
        else:
            print("❌ MockupGenerator integration issue")
            
    except ImportError:
        print("⚠️  MockupGenerator not available for testing")

if __name__ == "__main__":
    main()
