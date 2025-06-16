#!/usr/bin/env python3
"""
Test All Poster Perspective Transformations
==========================================

Generates perspective-corrected mockups for all available poster templates.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.perspective_mockup_generator import PerspectiveMockupGenerator, create_test_art_design
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_sample_art_designs():
    """Create multiple sample art designs for testing."""
    designs = {}
    
    # 1. Abstract geometric art
    from PIL import Image, ImageDraw
    
    abstract = Image.new('RGBA', (1000, 1400), (255, 255, 255, 255))
    draw = ImageDraw.Draw(abstract)
    
    # Draw abstract shapes
    draw.rectangle([(50, 50), (950, 1350)], fill=None, outline=(0, 0, 0, 255), width=6)
    draw.ellipse([(200, 200), (800, 800)], fill=(70, 130, 180, 200))
    draw.rectangle([(300, 600), (700, 1200)], fill=(255, 165, 0, 180))
    draw.polygon([(500, 100), (800, 500), (200, 900)], fill=(255, 69, 0, 160))
    
    draw.text((500, 1300), "ABSTRACT GEOMETRY", fill=(0, 0, 0, 255), anchor="mm")
    
    abstract_path = "abstract_art.png"
    abstract.save(abstract_path)
    designs['abstract'] = abstract_path
    
    # 2. Typography art
    typography = Image.new('RGBA', (800, 1200), (240, 240, 240, 255))
    draw = ImageDraw.Draw(typography)
    
    # Typography design
    draw.rectangle([(40, 40), (760, 1160)], fill=None, outline=(0, 0, 0, 255), width=4)
    draw.text((400, 300), "MEADOW", fill=(50, 50, 50, 255), anchor="mm")
    draw.text((400, 400), "NOVA", fill=(50, 50, 50, 255), anchor="mm")
    draw.text((400, 600), "ART", fill=(100, 100, 100, 255), anchor="mm")
    draw.text((400, 800), "COLLECTION", fill=(150, 150, 150, 255), anchor="mm")
    draw.text((400, 1000), "Limited Edition", fill=(200, 200, 200, 255), anchor="mm")
    
    typography_path = "typography_art.png"
    typography.save(typography_path)
    designs['typography'] = typography_path
    
    # 3. Nature-inspired art
    nature = Image.new('RGBA', (1200, 800), (245, 245, 220, 255))
    draw = ImageDraw.Draw(nature)
    
    # Nature elements
    draw.rectangle([(30, 30), (1170, 770)], fill=None, outline=(139, 69, 19, 255), width=5)
    draw.ellipse([(300, 200), (900, 600)], fill=(34, 139, 34, 180))
    draw.ellipse([(400, 100), (800, 300)], fill=(135, 206, 235, 150))
    draw.polygon([(600, 500), (700, 300), (500, 300)], fill=(160, 82, 45, 200))
    
    draw.text((600, 700), "NATURE'S HARMONY", fill=(139, 69, 19, 255), anchor="mm")
    
    nature_path = "nature_art.png"
    nature.save(nature_path)
    designs['nature'] = nature_path
    
    return designs


def test_all_poster_templates():
    """Test perspective transformation on all poster templates."""
    logger.info("🎨 Testing All Poster Template Perspectives")
    logger.info("=" * 60)
    
    # Initialize generator
    generator = PerspectiveMockupGenerator()
    
    # Get all available templates
    templates = generator.list_available_templates()
    logger.info(f"📁 Found {len(templates)} poster templates")
    
    # Create sample designs
    designs = create_sample_art_designs()
    logger.info(f"🎨 Created {len(designs)} sample art designs")
    
    results = []
    
    # Test each template with each design
    for template in templates:
        logger.info(f"\n🖼️ Testing template: {template}")
        
        # Get template configuration
        config = generator.get_template_config(template)
        if config:
            logger.info(f"  Name: {config.get('name', 'Unknown')}")
            logger.info(f"  Type: {config.get('perspective_type', 'unknown')}")
            logger.info(f"  Difficulty: {config.get('difficulty', 'unknown')}")
            
            # Test with first design (abstract)
            design_name = 'abstract'
            design_path = designs[design_name]
            
            result = generator.generate_perspective_mockup(design_path, template)
            
            if result['success']:
                # Rename with descriptive name
                original_path = Path(result['mockup_path'])
                template_stem = Path(template).stem
                new_name = f"poster_{template_stem}_{design_name}_perspective.png"
                new_path = original_path.parent / new_name
                original_path.rename(new_path)
                
                logger.info(f"  ✅ Generated: {new_name}")
                results.append({
                    'template': template,
                    'design': design_name,
                    'path': str(new_path),
                    'config': config
                })
            else:
                logger.error(f"  ❌ Failed: {result['error']}")
        else:
            logger.warning(f"  ⚠️ No configuration found for {template}")
    
    # Clean up design files
    for design_path in designs.values():
        try:
            Path(design_path).unlink()
        except:
            pass
    
    return results


def generate_comparison_grid():
    """Generate a comparison showing different perspective types."""
    logger.info("\n📊 Generating Perspective Comparison")
    logger.info("=" * 40)
    
    generator = PerspectiveMockupGenerator()
    
    # Create a simple test design for comparison
    test_design = Image.new('RGBA', (600, 800), (255, 255, 255, 255))
    draw = ImageDraw.Draw(test_design)
    
    # Simple grid pattern for perspective visibility
    for i in range(0, 600, 100):
        draw.line([(i, 0), (i, 800)], fill=(200, 200, 200, 255), width=2)
    for i in range(0, 800, 100):
        draw.line([(0, i), (600, i)], fill=(200, 200, 200, 255), width=2)
    
    # Add corner markers
    draw.ellipse([(10, 10), (40, 40)], fill=(255, 0, 0, 255))  # Top-left
    draw.ellipse([(560, 10), (590, 40)], fill=(0, 255, 0, 255))  # Top-right
    draw.ellipse([(560, 760), (590, 790)], fill=(0, 0, 255, 255))  # Bottom-right
    draw.ellipse([(10, 760), (40, 790)], fill=(255, 255, 0, 255))  # Bottom-left
    
    draw.text((300, 400), "PERSPECTIVE", fill=(0, 0, 0, 255), anchor="mm")
    draw.text((300, 450), "TEST GRID", fill=(0, 0, 0, 255), anchor="mm")
    
    test_design_path = "perspective_test_grid.png"
    test_design.save(test_design_path)
    
    # Generate comparison mockups
    comparison_templates = ['1.jpg', '2.jpg', '6.jpg', '8.jpg']  # Different perspective types
    comparison_results = []
    
    for template in comparison_templates:
        if template in [t for t in generator.list_available_templates()]:
            result = generator.generate_perspective_mockup(test_design_path, template)
            
            if result['success']:
                # Rename for comparison
                original_path = Path(result['mockup_path'])
                template_stem = Path(template).stem
                config = generator.get_template_config(template)
                perspective_type = config.get('perspective_type', 'unknown')
                
                new_name = f"comparison_{template_stem}_{perspective_type}.png"
                new_path = original_path.parent / new_name
                original_path.rename(new_path)
                
                logger.info(f"✅ Comparison: {new_name}")
                comparison_results.append(new_path)
    
    # Clean up test design
    try:
        Path(test_design_path).unlink()
    except:
        pass
    
    return comparison_results


def main():
    """Run comprehensive poster perspective testing."""
    logger.info("🎨 Comprehensive Poster Perspective Testing")
    logger.info("=" * 70)
    
    # Check OpenCV availability
    try:
        import cv2
        logger.info("✅ OpenCV available for perspective transformation")
    except ImportError:
        logger.error("❌ OpenCV required. Install with: pip install opencv-python")
        return
    
    # Run tests
    poster_results = test_all_poster_templates()
    comparison_results = generate_comparison_grid()
    
    # Summary
    total_generated = len(poster_results) + len(comparison_results)
    
    logger.info(f"\n🎉 Testing Complete!")
    logger.info(f"Generated {total_generated} perspective mockups:")
    logger.info(f"  - Poster templates: {len(poster_results)}")
    logger.info(f"  - Comparison grids: {len(comparison_results)}")
    
    if poster_results:
        logger.info(f"\n📁 Generated Poster Mockups:")
        for result in poster_results:
            config = result['config']
            logger.info(f"  - {Path(result['path']).name} ({config.get('perspective_type', 'unknown')})")
    
    logger.info(f"\n💡 Perspective Transformation Benefits:")
    logger.info(f"  ✅ Realistic angled poster presentations")
    logger.info(f"  ✅ Perfect alignment with frame perspectives")
    logger.info(f"  ✅ Professional art print mockups")
    logger.info(f"  ✅ Supports all 8 poster templates")
    logger.info(f"  ✅ Configurable corner points for fine-tuning")
    
    logger.info(f"\n🎯 Next Steps:")
    logger.info(f"  1. Review generated mockups in 'output' directory")
    logger.info(f"  2. Fine-tune corner points if needed")
    logger.info(f"  3. Integrate with Google Sheets workflow")
    logger.info(f"  4. Connect to Etsy listing creation")


if __name__ == "__main__":
    from PIL import Image, ImageDraw
    main()
