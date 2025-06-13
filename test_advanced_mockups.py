#!/usr/bin/env python3
"""
Advanced Mockup Testing Script
=============================

Tests advanced features of the custom mockup generator including:
- Configuration-based template settings
- Different blend modes
- Precise positioning
- Multiple template variations
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from modules.custom_mockup_generator import CustomMockupGenerator
from PIL import Image, ImageDraw, ImageFont
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_design_samples():
    """Create different design samples for testing."""
    designs = {}
    
    # 1. Colorful logo design
    logo = Image.new('RGBA', (600, 600), (255, 255, 255, 0))
    draw = ImageDraw.Draw(logo)
    
    # Draw colorful logo
    draw.ellipse([(50, 50), (550, 550)], fill=(255, 100, 100, 255), outline=(0, 0, 0, 255), width=8)
    draw.rectangle([(200, 200), (400, 400)], fill=(100, 255, 100, 255), outline=(0, 0, 0, 255), width=6)
    draw.polygon([(300, 150), (450, 450), (150, 450)], fill=(100, 100, 255, 255), outline=(0, 0, 0, 255), width=4)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    draw.text((300, 300), "LOGO", fill=(255, 255, 255, 255), font=font, anchor="mm")
    
    logo_path = "test_logo.png"
    logo.save(logo_path)
    designs['logo'] = logo_path
    
    # 2. Text-based design
    text_design = Image.new('RGBA', (800, 200), (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_design)
    
    # Background
    draw.rectangle([(0, 0), (800, 200)], fill=(50, 50, 50, 255))
    
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except:
        font_large = ImageFont.load_default()
    
    draw.text((400, 100), "MEADOW NOVA", fill=(255, 255, 255, 255), font=font_large, anchor="mm")
    
    text_path = "test_text.png"
    text_design.save(text_path)
    designs['text'] = text_path
    
    # 3. Light design for dark shirts
    light_design = Image.new('RGBA', (500, 500), (255, 255, 255, 0))
    draw = ImageDraw.Draw(light_design)
    
    # Light colored design
    draw.ellipse([(50, 50), (450, 450)], fill=(255, 255, 255, 255), outline=(200, 200, 200, 255), width=4)
    draw.text((250, 250), "LIGHT", fill=(100, 100, 100, 255), font=font, anchor="mm")
    
    light_path = "test_light.png"
    light_design.save(light_path)
    designs['light'] = light_path
    
    return designs


def test_blend_modes():
    """Test different blend modes on various shirt colors."""
    logger.info("🎨 Testing Blend Modes")
    logger.info("=" * 40)
    
    generator = CustomMockupGenerator()
    designs = create_design_samples()
    
    # Test blend modes on different colored shirts
    test_cases = [
        ('tshirts', '1', 'logo', 'multiply'),           # White shirt with colorful logo
        ('tshirts', '3- Black', 'light', 'screen'),    # Black shirt with light design
        ('tshirts', '7 - Soft Pink', 'text', 'multiply'), # Pink shirt with text
        ('tshirts', '5 - Athletic Heather', 'logo', 'multiply'), # Gray shirt with logo
    ]
    
    results = []
    
    for product_type, template_name, design_key, expected_blend in test_cases:
        if design_key in designs:
            logger.info(f"Testing {template_name} with {design_key} design")
            
            result = generator.generate_mockup(
                product_type, 
                designs[design_key], 
                template_name
            )
            
            if result['success']:
                # Rename file to include blend mode info
                original_path = Path(result['mockup_path'])
                new_name = f"blend_test_{template_name.replace(' ', '_').replace('-', '')}_{design_key}_{expected_blend}.png"
                new_path = original_path.parent / new_name
                original_path.rename(new_path)
                
                logger.info(f"✅ Generated: {new_name}")
                results.append(new_path)
            else:
                logger.error(f"❌ Failed: {result['error']}")
    
    return results


def test_positioning_precision():
    """Test precise positioning with different coordinates."""
    logger.info("\n🎯 Testing Positioning Precision")
    logger.info("=" * 40)
    
    generator = CustomMockupGenerator()
    
    # Create small positioning marker
    marker = Image.new('RGBA', (100, 100), (255, 0, 0, 255))
    draw = ImageDraw.Draw(marker)
    draw.text((50, 50), "X", fill=(255, 255, 255, 255), anchor="mm")
    marker_path = "position_marker.png"
    marker.save(marker_path)
    
    # Test different positions on white t-shirt
    positions = [
        (500, 400, "upper_left"),
        (700, 600, "center"),
        (900, 800, "lower_right"),
        (550, 550, "left_chest"),
        (850, 550, "right_chest"),
    ]
    
    results = []
    
    for x, y, label in positions:
        result = generator.generate_mockup(
            'tshirts', 
            marker_path, 
            '1',  # White shirt
            custom_position=(x, y)
        )
        
        if result['success']:
            # Rename with position info
            original_path = Path(result['mockup_path'])
            new_name = f"position_{label}_{x}_{y}.png"
            new_path = original_path.parent / new_name
            original_path.rename(new_path)
            
            logger.info(f"✅ Position {label} ({x}, {y}): {new_name}")
            results.append(new_path)
        else:
            logger.error(f"❌ Position {label}: {result['error']}")
    
    # Clean up marker
    Path(marker_path).unlink()
    
    return results


def test_template_configurations():
    """Test template-specific configurations."""
    logger.info("\n⚙️ Testing Template Configurations")
    logger.info("=" * 40)
    
    generator = CustomMockupGenerator()
    
    # Test different templates with same design
    designs = create_design_samples()
    logo_design = designs['logo']
    
    # Get available t-shirt templates
    templates = generator.list_available_templates()
    
    results = []
    
    for template_name in templates['tshirts'][:4]:  # Test first 4 templates
        # Get template info
        info = generator.get_template_info('tshirts', template_name)
        
        logger.info(f"Testing template: {template_name}")
        logger.info(f"  Design area: {info['design_area']}")
        logger.info(f"  Opacity: {info['opacity']}")
        logger.info(f"  Blend mode: {info['blend_mode']}")
        
        result = generator.generate_mockup('tshirts', logo_design, template_name)
        
        if result['success']:
            # Rename with template info
            original_path = Path(result['mockup_path'])
            clean_name = template_name.replace(' ', '_').replace('-', '').replace('.', '')
            new_name = f"template_test_{clean_name}.png"
            new_path = original_path.parent / new_name
            original_path.rename(new_path)
            
            logger.info(f"✅ Generated: {new_name}")
            results.append(new_path)
        else:
            logger.error(f"❌ Failed: {result['error']}")
    
    return results


def cleanup_test_files(designs):
    """Clean up test design files."""
    for design_path in designs.values():
        try:
            Path(design_path).unlink()
        except:
            pass


def main():
    """Run all advanced mockup tests."""
    logger.info("🚀 Advanced Mockup Generator Testing")
    logger.info("=" * 50)
    
    # Create test designs
    designs = create_design_samples()
    logger.info(f"Created {len(designs)} test designs")
    
    try:
        # Run tests
        blend_results = test_blend_modes()
        position_results = test_positioning_precision()
        template_results = test_template_configurations()
        
        # Summary
        total_generated = len(blend_results) + len(position_results) + len(template_results)
        
        logger.info(f"\n🎉 Testing Complete!")
        logger.info(f"Generated {total_generated} test mockups:")
        logger.info(f"  - Blend mode tests: {len(blend_results)}")
        logger.info(f"  - Position tests: {len(position_results)}")
        logger.info(f"  - Template tests: {len(template_results)}")
        logger.info(f"\nCheck the 'output' directory for all generated mockups.")
        
        # Show configuration recommendations
        logger.info(f"\n💡 Configuration Recommendations:")
        logger.info(f"  - White/light shirts: Use 'multiply' blend mode")
        logger.info(f"  - Dark shirts: Use 'screen' blend mode for light designs")
        logger.info(f"  - Center chest position: ~(700, 600) for t-shirts")
        logger.info(f"  - Left chest logo: ~(550, 550) for small designs")
        
    finally:
        # Clean up test files
        cleanup_test_files(designs)
        logger.info("Cleaned up test design files")


if __name__ == "__main__":
    main()
