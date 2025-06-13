
#!/usr/bin/env python3
"""
SEA-E Mockup Generator Module
============================

Generates high-quality product mockups for T-Shirts, Sweatshirts, and Poster Prints.

This module creates realistic mockups by overlaying designs onto product templates,
supporting multiple colors, variations, and viewing angles. It integrates with the
Printify specifications from Phase 1 research and provides both programmatic API
and command-line interface.

Features:
---------
- Support for 3 product types: T-Shirts, Sweatshirts, and Poster Prints
- Multiple color variations per product
- Different product variations (crew neck, v-neck, hoodie, etc.)
- Automatic static asset generation (thumbnails, previews, social media formats)
- Integration with Printify API specifications
- Comprehensive error handling and logging
- Progress indicators for batch operations
- Professional CLI interface

Supported Products:
------------------
1. T-Shirts (Bella+Canvas 3001 via Monster Digital)
   - Colors: white, black, navy, heather_gray, red
   - Variations: crew_neck, v_neck
   - Blueprint ID: 12, Provider ID: 29

2. Sweatshirts (Gildan 18000 via Monster Digital)
   - Colors: white, black, navy, heather_gray
   - Variations: crewneck, hoodie
   - Blueprint ID: 49, Provider ID: 29

3. Poster Prints (Matte Posters via Ideju Druka)
   - Colors: white, cream
   - Variations: standard, premium
   - Blueprint ID: 983, Provider ID: 95

Command Line Usage:
------------------
Basic usage:
    python mockup_generator.py <blueprint_key> <design_file>

Examples:
    # Generate single mockup with defaults
    python mockup_generator.py tshirt_bella_canvas_3001 design.png
    
    # Generate with specific color and variation
    python mockup_generator.py sweatshirt_gildan_18000 artwork.jpg --color black --variation hoodie
    
    # Generate all color/variation combinations
    python mockup_generator.py tshirt_bella_canvas_3001 logo.png --all-variations
    
    # List available blueprints
    python mockup_generator.py --list-blueprints
    
    # Create sample design for testing
    python mockup_generator.py --create-sample
    
    # Use custom output directory
    python mockup_generator.py tshirt_bella_canvas_3001 design.png --output-dir /custom/path

Programmatic Usage:
------------------
    from modules.mockup_generator import MockupGenerator
    
    # Initialize generator
    generator = MockupGenerator("/output/directory")
    
    # Generate single mockup
    result = generator.generate_mockup(
        'tshirt_bella_canvas_3001', 
        'design.png', 
        color='black', 
        variation='v_neck'
    )
    
    # Generate all variations
    results = generator.generate_all_variations(
        'tshirt_bella_canvas_3001', 
        'design.png'
    )
    
    # List available blueprints
    blueprints = generator.list_available_blueprints()

Output Structure:
----------------
For each mockup, the following files are generated:
- Main mockup: {design}_{blueprint}_{color}_{variation}.png
- Thumbnail: {design}_{blueprint}_{color}_{variation}_thumbnail.png (300x300)
- Preview: {design}_{blueprint}_{color}_{variation}_preview.png (600x600)
- Square: {design}_{blueprint}_{color}_{variation}_square.png (1080x1080)

Integration:
-----------
This module integrates with:
- Phase 1 Printify API research (/phase1/printify_specs.json)
- SEA-E logging system (/src/core/logger.py)
- Project output directory structure

Dependencies:
------------
- PIL (Pillow): Image processing and manipulation
- tqdm: Progress bars for batch operations
- colorlog: Colored logging output

Author: SEA-E Development Team
Version: 1.0.0
License: MIT
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from tqdm import tqdm

# Import project logger
sys.path.append(str(Path(__file__).parent.parent))
from core.logger import setup_logger

# Initialize logger
logger = setup_logger("mockup_generator", "INFO")

class MockupGenerator:
    """
    Advanced mockup generation system for SEA-E project.
    
    Creates high-quality product mockups using Printify specifications
    and supports multiple product types, colors, and variations.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the mockup generator.
        
        Args:
            output_dir: Directory to save generated mockups
        """
        if output_dir is None:
            # Default to project output directory
            project_root = Path(__file__).parent.parent.parent
            output_dir = project_root / "output"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load Printify specifications
        self.specs_path = Path(__file__).parent.parent.parent / "phase1" / "printify_specs.json"
        self.printify_specs = self._load_printify_specs()
        
        # Define product configurations based on Printify research
        self.product_configs = self._initialize_product_configs()
        
        # Create templates directory
        self.templates_dir = self.output_dir / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        logger.info(f"MockupGenerator initialized with output directory: {self.output_dir}")
    
    def _load_printify_specs(self) -> Dict[str, Any]:
        """Load Printify specifications from Phase 1 research."""
        try:
            if self.specs_path.exists():
                with open(self.specs_path, 'r') as f:
                    specs = json.load(f)
                logger.info("Loaded Printify specifications from Phase 1 research")
                return specs
            else:
                logger.warning(f"Printify specs not found at {self.specs_path}, using defaults")
                return {}
        except Exception as e:
            logger.error(f"Error loading Printify specs: {e}")
            return {}
    
    def _initialize_product_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize product configurations based on Printify specifications."""
        configs = {
            # T-Shirt configuration from Printify specs
            'tshirt_bella_canvas_3001': {
                'name': 'Unisex Jersey Short Sleeve Tee',
                'brand': 'Bella+Canvas',
                'model': '3001',
                'blueprint_id': 12,
                'print_provider_id': 29,
                'print_provider_name': 'Monster Digital',
                'template_size': (1000, 1200),
                'design_area': (300, 250, 700, 650),  # x1, y1, x2, y2
                'colors': ['white', 'black', 'navy', 'heather_gray', 'red'],
                'variations': ['crew_neck', 'v_neck'],
                'category': 'apparel'
            },
            
            # Sweatshirt configuration from Printify specs  
            'sweatshirt_gildan_18000': {
                'name': 'Unisex Heavy Blend™ Crewneck Sweatshirt',
                'brand': 'Gildan',
                'model': '18000',
                'blueprint_id': 49,
                'print_provider_id': 29,
                'print_provider_name': 'Monster Digital',
                'template_size': (1000, 1200),
                'design_area': (300, 250, 700, 650),
                'colors': ['white', 'black', 'navy', 'heather_gray'],
                'variations': ['crewneck', 'hoodie'],
                'category': 'apparel'
            },
            
            # Poster configuration (using alternative from research)
            'poster_matte_ideju': {
                'name': 'Matte Posters',
                'brand': 'Generic brand',
                'model': 'Standard',
                'blueprint_id': 983,
                'print_provider_id': 95,
                'print_provider_name': 'Ideju Druka',
                'template_size': (800, 1200),
                'design_area': (50, 50, 750, 1150),
                'colors': ['white', 'cream'],
                'variations': ['standard', 'premium'],
                'category': 'print'
            }
        }
        
        logger.info(f"Initialized {len(configs)} product configurations")
        return configs
    
    def _create_template(self, config: Dict[str, Any]) -> Image.Image:
        """
        Create a product template based on configuration.
        
        Args:
            config: Product configuration dictionary
            
        Returns:
            PIL Image template
        """
        width, height = config['template_size']
        template = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(template)
        
        category = config['category']
        
        if category == 'apparel':
            # Create apparel template (t-shirt/sweatshirt)
            if 'sweatshirt' in config['name'].lower():
                # Sweatshirt shape - more boxy
                draw.rectangle([(200, 200), (800, 900)], fill=(240, 240, 240, 255), outline=(0, 0, 0, 255), width=2)
                # Neckline
                draw.rectangle([(450, 200), (550, 250)], fill=(255, 255, 255, 0), outline=(0, 0, 0, 255), width=2)
                # Sleeves
                draw.rectangle([(200, 250), (300, 600)], fill=(240, 240, 240, 255), outline=(0, 0, 0, 255), width=2)
                draw.rectangle([(700, 250), (800, 600)], fill=(240, 240, 240, 255), outline=(0, 0, 0, 255), width=2)
            else:
                # T-shirt shape
                draw.rectangle([(250, 200), (750, 800)], fill=(240, 240, 240, 255), outline=(0, 0, 0, 255), width=2)
                # Neckline
                draw.rectangle([(450, 200), (550, 250)], fill=(255, 255, 255, 0), outline=(0, 0, 0, 255), width=2)
                # Sleeves
                draw.rectangle([(250, 250), (350, 500)], fill=(240, 240, 240, 255), outline=(0, 0, 0, 255), width=2)
                draw.rectangle([(650, 250), (750, 500)], fill=(240, 240, 240, 255), outline=(0, 0, 0, 255), width=2)
                
        elif category == 'print':
            # Create poster template
            draw.rectangle([(50, 50), (750, 1150)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=3)
            # Add subtle frame effect
            draw.rectangle([(60, 60), (740, 1140)], fill=None, outline=(200, 200, 200, 255), width=1)
        
        # Add product info
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        brand_text = f"{config['brand']} {config['model']}"
        provider_text = f"by {config['print_provider_name']}"
        
        draw.text((width//2, height-80), brand_text, fill=(0, 0, 0, 255), font=font, anchor="mm")
        draw.text((width//2, height-60), provider_text, fill=(100, 100, 100, 255), font=font, anchor="mm")
        
        return template
    
    def _apply_color_to_template(self, template: Image.Image, color: str, config: Dict[str, Any]) -> Image.Image:
        """
        Apply color to product template.
        
        Args:
            template: Base template image
            color: Color name to apply
            config: Product configuration
            
        Returns:
            Colored template image
        """
        if color == 'white':
            return template.copy()
        
        # Color mapping
        color_map = {
            'black': (30, 30, 30),
            'navy': (25, 25, 112),
            'heather_gray': (150, 150, 150),
            'red': (220, 20, 60),
            'cream': (255, 253, 208)
        }
        
        rgb_color = color_map.get(color, (255, 255, 255))
        colored_template = template.copy()
        
        # Create color overlay
        overlay = Image.new('RGBA', template.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        category = config['category']
        
        if category == 'apparel':
            # Color the main garment area
            if 'sweatshirt' in config['name'].lower():
                draw.rectangle([(200, 200), (800, 900)], fill=rgb_color + (255,))
                draw.rectangle([(200, 250), (300, 600)], fill=rgb_color + (255,))
                draw.rectangle([(700, 250), (800, 600)], fill=rgb_color + (255,))
            else:
                draw.rectangle([(250, 200), (750, 800)], fill=rgb_color + (255,))
                draw.rectangle([(250, 250), (350, 500)], fill=rgb_color + (255,))
                draw.rectangle([(650, 250), (750, 500)], fill=rgb_color + (255,))
        elif category == 'print':
            # Color the poster background
            draw.rectangle([(50, 50), (750, 1150)], fill=rgb_color + (255,))
        
        # Blend with original template
        colored_template = Image.alpha_composite(colored_template, overlay)
        
        return colored_template
    
    def _apply_variation(self, template: Image.Image, variation: str, config: Dict[str, Any]) -> Image.Image:
        """
        Apply product variation to template.
        
        Args:
            template: Base template image
            variation: Variation name
            config: Product configuration
            
        Returns:
            Modified template with variation
        """
        modified_template = template.copy()
        draw = ImageDraw.Draw(modified_template)
        
        if variation == 'v_neck' and config['category'] == 'apparel':
            # Modify neckline for V-neck
            draw.polygon([(450, 250), (500, 300), (550, 250)], fill=(255, 255, 255, 0))
            
        elif variation == 'hoodie' and 'sweatshirt' in config['name'].lower():
            # Add hood for hoodie
            draw.rectangle([(400, 150), (600, 200)], fill=(200, 200, 200, 255), outline=(0, 0, 0, 255), width=2)
            draw.text((500, 175), "HOOD", fill=(0, 0, 0, 255), anchor="mm")
            
        elif variation == 'premium' and config['category'] == 'print':
            # Add premium frame for poster
            draw.rectangle([(40, 40), (760, 1160)], fill=None, outline=(184, 134, 11, 255), width=8)
        
        return modified_template
    
    def _resize_design_to_fit(self, design: Image.Image, design_area: Tuple[int, int, int, int]) -> Image.Image:
        """
        Resize design to fit within the design area while maintaining aspect ratio.
        
        Args:
            design: Design image to resize
            design_area: Tuple of (x1, y1, x2, y2) coordinates
            
        Returns:
            Resized design image
        """
        area_width = design_area[2] - design_area[0]
        area_height = design_area[3] - design_area[1]
        
        # Calculate scaling factor to fit design in area
        scale_x = area_width / design.width
        scale_y = area_height / design.height
        scale = min(scale_x, scale_y) * 0.8  # Leave some padding
        
        new_width = int(design.width * scale)
        new_height = int(design.height * scale)
        
        return design.resize((new_width, new_height), Image.LANCZOS)
    
    def _create_static_assets(self, mockup_path: str, config: Dict[str, Any]) -> List[str]:
        """
        Create additional static assets (thumbnails, previews, etc.).
        
        Args:
            mockup_path: Path to the main mockup
            config: Product configuration
            
        Returns:
            List of paths to created assets
        """
        assets = []
        
        try:
            mockup = Image.open(mockup_path)
            base_name = Path(mockup_path).stem
            
            # Create thumbnail (300x300)
            thumbnail = mockup.copy()
            thumbnail.thumbnail((300, 300), Image.LANCZOS)
            thumbnail_path = self.output_dir / f"{base_name}_thumbnail.png"
            thumbnail.save(thumbnail_path)
            assets.append(str(thumbnail_path))
            
            # Create preview (600x600)
            preview = mockup.copy()
            preview.thumbnail((600, 600), Image.LANCZOS)
            preview_path = self.output_dir / f"{base_name}_preview.png"
            preview.save(preview_path)
            assets.append(str(preview_path))
            
            # Create square crop for social media
            size = min(mockup.width, mockup.height)
            left = (mockup.width - size) // 2
            top = (mockup.height - size) // 2
            square = mockup.crop((left, top, left + size, top + size))
            square = square.resize((1080, 1080), Image.LANCZOS)
            square_path = self.output_dir / f"{base_name}_square.png"
            square.save(square_path)
            assets.append(str(square_path))
            
            logger.info(f"Created {len(assets)} static assets for {base_name}")
            
        except Exception as e:
            logger.error(f"Error creating static assets: {e}")
        
        return assets
    
    def generate_mockup(self, mockup_blueprint_key: str, design_file: str, 
                       color: str = None, variation: str = None) -> Dict[str, Any]:
        """
        Generate a single mockup for the given blueprint and design.
        
        Args:
            mockup_blueprint_key: Product blueprint key (e.g., 'tshirt_bella_canvas_3001')
            design_file: Path to design file
            color: Product color (optional, uses first available if not specified)
            variation: Product variation (optional, uses first available if not specified)
            
        Returns:
            Dictionary with mockup generation results
        """
        logger.info(f"Generating mockup for {mockup_blueprint_key} with design {design_file}")
        
        try:
            # Validate inputs
            if mockup_blueprint_key not in self.product_configs:
                raise ValueError(f"Unknown blueprint key: {mockup_blueprint_key}")
            
            if not os.path.exists(design_file):
                raise FileNotFoundError(f"Design file not found: {design_file}")
            
            config = self.product_configs[mockup_blueprint_key]
            
            # Set defaults if not specified
            if color is None:
                color = config['colors'][0]
            if variation is None:
                variation = config['variations'][0]
            
            # Validate color and variation
            if color not in config['colors']:
                logger.warning(f"Color '{color}' not available, using '{config['colors'][0]}'")
                color = config['colors'][0]
            
            if variation not in config['variations']:
                logger.warning(f"Variation '{variation}' not available, using '{config['variations'][0]}'")
                variation = config['variations'][0]
            
            # Load and process design
            design = Image.open(design_file).convert("RGBA")
            design = self._resize_design_to_fit(design, config['design_area'])
            
            # Create template
            template = self._create_template(config)
            
            # Apply color
            colored_template = self._apply_color_to_template(template, color, config)
            
            # Apply variation
            final_template = self._apply_variation(colored_template, variation, config)
            
            # Position design on template
            design_area = config['design_area']
            x_pos = design_area[0] + (design_area[2] - design_area[0] - design.width) // 2
            y_pos = design_area[1] + (design_area[3] - design_area[1] - design.height) // 2
            
            # Create final mockup
            mockup = final_template.copy()
            mockup.paste(design, (x_pos, y_pos), design)
            
            # Generate output filename
            design_name = Path(design_file).stem
            output_filename = f"{design_name}_{mockup_blueprint_key}_{color}_{variation}.png"
            output_path = self.output_dir / output_filename
            
            # Save mockup
            mockup.save(output_path)
            
            # Create static assets
            static_assets = self._create_static_assets(str(output_path), config)
            
            result = {
                'success': True,
                'mockup_path': str(output_path),
                'static_assets': static_assets,
                'config': config,
                'color': color,
                'variation': variation,
                'design_file': design_file
            }
            
            logger.info(f"Successfully generated mockup: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating mockup: {e}")
            return {
                'success': False,
                'error': str(e),
                'mockup_blueprint_key': mockup_blueprint_key,
                'design_file': design_file
            }
    
    def generate_all_variations(self, mockup_blueprint_key: str, design_file: str) -> List[Dict[str, Any]]:
        """
        Generate mockups for all color and variation combinations.
        
        Args:
            mockup_blueprint_key: Product blueprint key
            design_file: Path to design file
            
        Returns:
            List of mockup generation results
        """
        logger.info(f"Generating all variations for {mockup_blueprint_key}")
        
        if mockup_blueprint_key not in self.product_configs:
            logger.error(f"Unknown blueprint key: {mockup_blueprint_key}")
            return []
        
        config = self.product_configs[mockup_blueprint_key]
        results = []
        
        total_combinations = len(config['colors']) * len(config['variations'])
        
        with tqdm(total=total_combinations, desc="Generating mockups") as pbar:
            for color in config['colors']:
                for variation in config['variations']:
                    result = self.generate_mockup(mockup_blueprint_key, design_file, color, variation)
                    results.append(result)
                    pbar.update(1)
        
        successful = sum(1 for r in results if r['success'])
        logger.info(f"Generated {successful}/{len(results)} mockups successfully")
        
        return results
    
    def list_available_blueprints(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available blueprint configurations.
        
        Returns:
            Dictionary of available blueprints
        """
        return self.product_configs.copy()


def create_sample_design(output_path: str) -> str:
    """
    Create a sample design for testing purposes.
    
    Args:
        output_path: Path to save the sample design
        
    Returns:
        Path to created sample design
    """
    # Create a simple sample design
    design = Image.new('RGBA', (400, 400), (255, 255, 255, 0))
    draw = ImageDraw.Draw(design)
    
    # Draw a colorful geometric design
    draw.rectangle([(50, 50), (350, 350)], fill=(70, 130, 180, 255), outline=(0, 0, 0, 255), width=3)
    draw.ellipse([(100, 100), (300, 300)], fill=(255, 165, 0, 255), outline=(0, 0, 0, 255), width=3)
    draw.polygon([(200, 120), (280, 280), (120, 280)], fill=(255, 69, 0, 255), outline=(0, 0, 0, 255), width=3)
    
    # Add text
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((200, 200), "SEA-E", fill=(255, 255, 255, 255), font=font, anchor="mm")
    draw.text((200, 230), "SAMPLE", fill=(255, 255, 255, 255), font=font, anchor="mm")
    
    design.save(output_path)
    return output_path


def main():
    """Main CLI interface for the mockup generator."""
    parser = argparse.ArgumentParser(
        description="SEA-E Mockup Generator - Create high-quality product mockups",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s tshirt_bella_canvas_3001 design.png
  %(prog)s sweatshirt_gildan_18000 artwork.jpg --color black --variation hoodie
  %(prog)s poster_matte_ideju logo.svg --all-variations
  %(prog)s --list-blueprints

Available Blueprint Keys:
  tshirt_bella_canvas_3001    - Bella+Canvas 3001 T-Shirt via Monster Digital
  sweatshirt_gildan_18000     - Gildan 18000 Sweatshirt via Monster Digital  
  poster_matte_ideju          - Matte Poster via Ideju Druka

For more information, visit: https://github.com/your-org/sea-engine
        """
    )
    
    parser.add_argument('mockup_blueprint_key', nargs='?',
                       help='Product blueprint key (e.g., tshirt_bella_canvas_3001)')
    parser.add_argument('design_file', nargs='?',
                       help='Path to design file (PNG, JPG, SVG)')
    parser.add_argument('--color', '-c',
                       help='Product color (optional, uses default if not specified)')
    parser.add_argument('--variation', '-v', 
                       help='Product variation (optional, uses default if not specified)')
    parser.add_argument('--all-variations', '-a', action='store_true',
                       help='Generate mockups for all color and variation combinations')
    parser.add_argument('--output-dir', '-o', default=None,
                       help='Output directory for generated mockups (default: project/output)')
    parser.add_argument('--list-blueprints', '-l', action='store_true',
                       help='List all available blueprint configurations')
    parser.add_argument('--create-sample', action='store_true',
                       help='Create a sample design file for testing')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger("mockup_generator").setLevel(logging.DEBUG)
    
    # Initialize generator
    generator = MockupGenerator(args.output_dir)
    
    # Handle list blueprints
    if args.list_blueprints:
        blueprints = generator.list_available_blueprints()
        print("\n=== Available Blueprint Configurations ===\n")
        for key, config in blueprints.items():
            print(f"Key: {key}")
            print(f"  Name: {config['name']}")
            print(f"  Brand: {config['brand']} {config['model']}")
            print(f"  Provider: {config['print_provider_name']} (ID: {config['print_provider_id']})")
            print(f"  Blueprint ID: {config['blueprint_id']}")
            print(f"  Colors: {', '.join(config['colors'])}")
            print(f"  Variations: {', '.join(config['variations'])}")
            print()
        return
    
    # Handle create sample
    if args.create_sample:
        # Initialize generator to get the correct output directory
        generator = MockupGenerator(args.output_dir)
        sample_path = generator.output_dir / "sample_design.png"
        create_sample_design(str(sample_path))
        print(f"Sample design created: {sample_path}")
        return
    
    # Validate required arguments
    if not args.mockup_blueprint_key or not args.design_file:
        parser.error("Both mockup_blueprint_key and design_file are required")
    
    # Generate mockups
    if args.all_variations:
        results = generator.generate_all_variations(args.mockup_blueprint_key, args.design_file)
        successful = sum(1 for r in results if r['success'])
        print(f"\nGenerated {successful}/{len(results)} mockups successfully")
        
        if successful > 0:
            print(f"Mockups saved to: {args.output_dir}")
            for result in results:
                if result['success']:
                    print(f"  - {Path(result['mockup_path']).name}")
    else:
        result = generator.generate_mockup(
            args.mockup_blueprint_key, 
            args.design_file,
            args.color,
            args.variation
        )
        
        if result['success']:
            print(f"Mockup generated successfully: {result['mockup_path']}")
            print(f"Static assets: {len(result['static_assets'])} files")
        else:
            print(f"Error generating mockup: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
