#!/usr/bin/env python3
"""
Test script for Custom Mockup Generator
=======================================

Tests the custom mockup generation system with your actual assets.
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


def create_test_design(output_path: str, text: str = "SEA-E TEST") -> str:
    """
    Create a test design for mockup generation.
    
    Args:
        output_path: Path to save test design
        text: Text to include in design
        
    Returns:
        Path to created design
    """
    # Create a test design
    design = Image.new('RGBA', (800, 800), (255, 255, 255, 0))
    draw = ImageDraw.Draw(design)
    
    # Draw background circle
    draw.ellipse([(50, 50), (750, 750)], fill=(70, 130, 180, 255), outline=(0, 0, 0, 255), width=8)
    
    # Draw inner design
    draw.rectangle([(200, 200), (600, 600)], fill=(255, 165, 0, 255), outline=(0, 0, 0, 255), width=6)
    draw.polygon([(400, 250), (550, 550), (250, 550)], fill=(255, 69, 0, 255), outline=(0, 0, 0, 255), width=4)
    
    # Add text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except:
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    if font:
        draw.text((400, 400), text, fill=(255, 255, 255, 255), font=font, anchor="mm")
    
    design.save(output_path)
    logger.info(f"Created test design: {output_path}")
    return output_path


def test_mockup_generation():
    """Test the custom mockup generation system."""
    logger.info("🎨 Testing Custom Mockup Generator")
    logger.info("=" * 50)
    
    # Initialize generator
    generator = CustomMockupGenerator()
    
    # List available templates
    templates = generator.list_available_templates()
    logger.info("📁 Available Templates:")
    for product_type, template_names in templates.items():
        logger.info(f"  {product_type}: {len(template_names)} templates")
        for name in template_names[:3]:  # Show first 3
            logger.info(f"    - {name}")
        if len(template_names) > 3:
            logger.info(f"    ... and {len(template_names) - 3} more")
    
    # Create test design
    test_design_path = "test_design.png"
    create_test_design(test_design_path, "MEADOW\nNOVA")
    
    # Test mockup generation for each product type
    test_results = []
    
    for product_type in ['tshirts', 'sweatshirts', 'posters']:
        if templates[product_type]:
            logger.info(f"\n🧪 Testing {product_type} mockup generation...")
            
            # Get template info
            template_name = templates[product_type][0]
            template_info = generator.get_template_info(product_type, template_name)
            logger.info(f"Template: {template_name}")
            logger.info(f"Size: {template_info['size']}")
            logger.info(f"Design Area: {template_info['design_area']}")
            
            # Generate mockup
            result = generator.generate_mockup(product_type, test_design_path)
            
            if result['success']:
                logger.info(f"✅ Success: {result['mockup_path']}")
                logger.info(f"Position: {result['design_position']}")
                logger.info(f"Output Size: {result['output_size']}")
                test_results.append(result)
            else:
                logger.error(f"❌ Failed: {result['error']}")
        else:
            logger.warning(f"⚠️ No templates found for {product_type}")
    
    # Summary
    logger.info(f"\n🎉 Test Summary:")
    logger.info(f"Generated {len(test_results)} mockups successfully")
    
    if test_results:
        logger.info("📁 Generated Files:")
        for result in test_results:
            logger.info(f"  - {Path(result['mockup_path']).name}")
    
    # Clean up test design
    try:
        Path(test_design_path).unlink()
        logger.info(f"Cleaned up test design: {test_design_path}")
    except:
        pass
    
    return test_results


def test_coordinate_precision():
    """Test precise coordinate positioning."""
    logger.info("\n🎯 Testing Coordinate Precision")
    logger.info("=" * 40)
    
    generator = CustomMockupGenerator()
    templates = generator.list_available_templates()
    
    if not templates['tshirts']:
        logger.warning("No t-shirt templates available for coordinate testing")
        return
    
    # Create small test design for positioning
    test_design = "position_test.png"
    design = Image.new('RGBA', (200, 200), (255, 0, 0, 255))  # Red square
    draw = ImageDraw.Draw(design)
    draw.text((100, 100), "X", fill=(255, 255, 255, 255), anchor="mm")
    design.save(test_design)
    
    # Test different positions
    positions = [
        (500, 400),   # Upper chest
        (700, 600),   # Center chest
        (900, 800),   # Lower chest
    ]
    
    template_name = templates['tshirts'][0]
    
    for i, position in enumerate(positions):
        result = generator.generate_mockup(
            'tshirts', 
            test_design, 
            template_name, 
            custom_position=position
        )
        
        if result['success']:
            output_name = f"position_test_{i+1}_{position[0]}_{position[1]}.png"
            Path(result['mockup_path']).rename(Path("output") / output_name)
            logger.info(f"✅ Position {position}: {output_name}")
        else:
            logger.error(f"❌ Position {position}: {result['error']}")
    
    # Clean up
    try:
        Path(test_design).unlink()
    except:
        pass


if __name__ == "__main__":
    # Run tests
    test_mockup_generation()
    test_coordinate_precision()
    
    logger.info("\n🚀 Custom Mockup Generator Testing Complete!")
    logger.info("Check the 'output' directory for generated mockups.")
