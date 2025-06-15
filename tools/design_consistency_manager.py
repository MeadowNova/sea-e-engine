#!/usr/bin/env python3
"""
Design Consistency Manager
==========================
Ensures consistent design sizing and placement across all mockups.

This tool standardizes the relationship between your design creation process
and the final mockup appearance, ensuring "what you design is what you get."
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image
from typing import Dict, Tuple, Any

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

class DesignConsistencyManager:
    """Manages design consistency across mockups."""
    
    def __init__(self):
        self.config_path = Path("config/mockup_templates.json")
        self.design_standards = {
            # Your standard design dimensions
            "source_design": {
                "width": 4500,
                "height": 5100,
                "dpi": 300,
                "format": "PNG"
            },
            # Target t-shirt design size (inches at 300 DPI)
            "target_tshirt": {
                "width_inches": 10,      # 10 inch wide design
                "height_inches": 11.33,  # Maintains 4500:5100 ratio
                "dpi": 300,
                "pixels_width": 3000,    # 10 * 300 DPI
                "pixels_height": 3400    # 11.33 * 300 DPI (rounded)
            }
        }
    
    def analyze_current_setup(self) -> Dict[str, Any]:
        """Analyze current template configuration for consistency."""
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        tshirt_templates = config.get('template_categories', {}).get('tshirts', {}).get('templates', {})
        
        analysis = {
            "templates": {},
            "consistency_issues": [],
            "recommendations": []
        }
        
        for template_name, template_config in tshirt_templates.items():
            design_area = template_config.get('design_area', [])
            if design_area:
                width = design_area[2] - design_area[0]
                height = design_area[3] - design_area[1]
                
                analysis["templates"][template_name] = {
                    "design_area": design_area,
                    "width": width,
                    "height": height,
                    "aspect_ratio": round(width / height, 3) if height > 0 else 0
                }
        
        # Check for consistency issues
        areas = [t["width"] * t["height"] for t in analysis["templates"].values()]
        if len(set(areas)) > 1:
            analysis["consistency_issues"].append("Templates have different design area sizes")
        
        ratios = [t["aspect_ratio"] for t in analysis["templates"].values()]
        if len(set(ratios)) > 1:
            analysis["consistency_issues"].append("Templates have different aspect ratios")
        
        return analysis
    
    def calculate_optimal_design_areas(self) -> Dict[str, list]:
        """Calculate optimal design areas for consistent sizing."""
        
        # Target design size in pixels (for mockup templates at ~72-150 DPI)
        # This represents a 10-inch design on a t-shirt
        target_width = 800   # Pixels in mockup template
        target_height = 907  # Maintains 4500:5100 ratio (800 * 5100/4500)
        
        # Standard positioning (centered on chest area)
        # Assuming 2000x2000 mockup templates
        center_x = 1000
        center_y = 950  # Proper chest placement (lower than before)
        
        # Calculate design area bounds
        left = center_x - target_width // 2
        top = center_y - target_height // 2
        right = left + target_width
        bottom = top + target_height
        
        optimal_area = [left, top, right, bottom]
        
        return {
            "standard_design_area": optimal_area,
            "dimensions": {
                "width": target_width,
                "height": target_height,
                "aspect_ratio": round(target_width / target_height, 3)
            },
            "positioning": {
                "center_x": center_x,
                "center_y": center_y,
                "description": "Centered chest placement"
            }
        }
    
    def create_design_export_guide(self) -> Dict[str, Any]:
        """Create a guide for consistent design export."""
        
        return {
            "design_creation": {
                "canvas_size": "4500 x 5100 pixels",
                "dpi": "300 DPI",
                "format": "PNG with transparency",
                "color_mode": "RGB",
                "design_placement": "Centered on canvas with appropriate margins"
            },
            "export_settings": {
                "format": "PNG",
                "quality": "Maximum",
                "transparency": "Preserve",
                "color_profile": "sRGB"
            },
            "mockup_expectations": {
                "design_will_appear": "Approximately 10 inches wide on t-shirt",
                "aspect_ratio": "Maintained (4500:5100 ratio)",
                "placement": "Centered on chest area",
                "sizing": "Consistent across all t-shirt colors/styles"
            }
        }
    
    def standardize_all_templates(self, apply_changes: bool = False) -> Dict[str, Any]:
        """Standardize all t-shirt templates for consistency."""
        
        optimal = self.calculate_optimal_design_areas()
        standard_area = optimal["standard_design_area"]
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        changes = {
            "templates_updated": [],
            "standard_design_area": standard_area,
            "changes_applied": apply_changes
        }
        
        tshirt_templates = config.get('template_categories', {}).get('tshirts', {}).get('templates', {})
        
        for template_name, template_config in tshirt_templates.items():
            old_area = template_config.get('design_area', [])
            
            if apply_changes:
                template_config['design_area'] = standard_area
                changes["templates_updated"].append({
                    "name": template_name,
                    "old_area": old_area,
                    "new_area": standard_area
                })
        
        if apply_changes:
            # Also update default settings
            config['template_categories']['tshirts']['default_settings']['design_area'] = standard_area
            
            # Save the updated configuration
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            changes["config_updated"] = True
        
        return changes

def main():
    parser = argparse.ArgumentParser(description='Design Consistency Manager')
    parser.add_argument('--analyze', action='store_true', help='Analyze current setup')
    parser.add_argument('--standardize', action='store_true', help='Standardize all templates')
    parser.add_argument('--apply', action='store_true', help='Apply changes (use with --standardize)')
    parser.add_argument('--guide', action='store_true', help='Show design export guide')
    
    args = parser.parse_args()
    
    manager = DesignConsistencyManager()
    
    if args.analyze:
        print("🔍 Analyzing Current Template Setup")
        print("=" * 50)
        analysis = manager.analyze_current_setup()
        
        print("📊 Template Analysis:")
        for name, info in analysis["templates"].items():
            print(f"  {name}:")
            print(f"    Design Area: {info['design_area']}")
            print(f"    Size: {info['width']}×{info['height']} pixels")
            print(f"    Aspect Ratio: {info['aspect_ratio']}")
            print()
        
        if analysis["consistency_issues"]:
            print("⚠️  Consistency Issues:")
            for issue in analysis["consistency_issues"]:
                print(f"  • {issue}")
        else:
            print("✅ No consistency issues found")
    
    elif args.guide:
        print("📋 Design Export Guide for Consistency")
        print("=" * 50)
        guide = manager.create_design_export_guide()
        
        print("🎨 Design Creation:")
        for key, value in guide["design_creation"].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print("\n💾 Export Settings:")
        for key, value in guide["export_settings"].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print("\n🎯 Mockup Expectations:")
        for key, value in guide["mockup_expectations"].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    elif args.standardize:
        print("🔧 Standardizing Template Configuration")
        print("=" * 50)
        
        optimal = manager.calculate_optimal_design_areas()
        print("📐 Optimal Design Area:")
        print(f"  Coordinates: {optimal['standard_design_area']}")
        print(f"  Size: {optimal['dimensions']['width']}×{optimal['dimensions']['height']} pixels")
        print(f"  Aspect Ratio: {optimal['dimensions']['aspect_ratio']}")
        print(f"  Positioning: {optimal['positioning']['description']}")
        
        if args.apply:
            print("\n🚀 Applying changes...")
            result = manager.standardize_all_templates(apply_changes=True)
            print(f"✅ Updated {len(result['templates_updated'])} templates")
            print("✅ Configuration saved")
        else:
            print("\n💡 Use --apply to actually make these changes")
            print("   Example: python tools/design_consistency_manager.py --standardize --apply")
    
    else:
        print("🎯 Design Consistency Manager")
        print("=" * 30)
        print("Available commands:")
        print("  --analyze     Analyze current template setup")
        print("  --guide       Show design export guide")
        print("  --standardize Show standardization plan")
        print("  --standardize --apply  Apply standardization")

if __name__ == "__main__":
    main()
