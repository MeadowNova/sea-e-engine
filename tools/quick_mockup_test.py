#!/usr/bin/env python3
"""
Quick Mockup Test Tool
======================
Quickly test design sizing and placement adjustments.

Usage:
    python tools/quick_mockup_test.py
    python tools/quick_mockup_test.py --template "3- Black"
    python tools/quick_mockup_test.py --design "assets/designs/your_design.png"
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from modules.custom_mockup_generator import CustomMockupGenerator

# Try to import QA, but make it optional
try:
    from modules.quality_assurance import QualityAssurance
    HAS_QA = True
except ImportError:
    HAS_QA = False

def quick_test(template_name="3- Black", design_path="assets/designs/Copy of Cat with Pearl Earring.png"):
    """Run a quick mockup test with the specified template and design."""
    
    print(f"🧪 Quick Test: {template_name}")
    print("=" * 50)
    
    # Initialize generator
    generator = CustomMockupGenerator()
    qa = QualityAssurance() if HAS_QA else None
    
    # Generate mockup
    print(f"📁 Design: {design_path}")
    print(f"👕 Template: {template_name}")
    print("🔄 Generating mockup...")
    
    result = generator.generate_mockup(
        product_type='tshirts',
        design_path=design_path,
        template_name=template_name
    )
    
    if result['success']:
        print(f"✅ Mockup generated: {result['mockup_path']}")
        print(f"📍 Design position: {result['design_position']}")
        
        # Quick quality check (if available)
        if qa:
            print("🔍 Quality assessment...")
            qa_result = qa.assess_mockup_quality(result['mockup_path'])
            print(f"📊 Quality Score: {qa_result['overall_score']:.1f}/10")
            print(f"📐 Resolution: {qa_result['resolution']}")
            print(f"🎯 Status: {'✅ PASSED' if qa_result['passes_quality_check'] else '❌ FAILED'}")
        else:
            print("🔍 Quality assessment: Not available")
        
        # Show current design area from config
        try:
            import json
            with open('config/mockup_templates.json', 'r') as f:
                config = json.load(f)

            template_config = config.get('product_types', {}).get('tshirts', {}).get('templates', {}).get(template_name, {})
            design_area = template_config.get('design_area', [])
            if design_area:
                width = design_area[2] - design_area[0]
                height = design_area[3] - design_area[1]
                print(f"📏 Current design area: {design_area} ({width}×{height} pixels)")
        except Exception as e:
            print(f"📏 Could not read design area: {e}")
        
        print(f"\n🖼️  Open mockup: {result['mockup_path']}")
        
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 50)

def main():
    parser = argparse.ArgumentParser(description='Quick mockup test tool')
    parser.add_argument('--template', '-t', default='3- Black', 
                       help='Template name (default: "3- Black")')
    parser.add_argument('--design', '-d', default='assets/designs/Copy of Cat with Pearl Earring.png',
                       help='Design file path')
    
    args = parser.parse_args()
    
    # Check if design file exists
    if not os.path.exists(args.design):
        print(f"❌ Design file not found: {args.design}")
        print("Available designs:")
        design_dir = Path("assets/designs")
        if design_dir.exists():
            for design_file in design_dir.glob("*.png"):
                print(f"   - {design_file}")
        return
    
    quick_test(args.template, args.design)

if __name__ == "__main__":
    main()
