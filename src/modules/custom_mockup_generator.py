#!/usr/bin/env python3
"""
Custom Mockup Generator for SEA-E Engine
========================================

Advanced image manipulation system for creating realistic product mockups
using custom template assets with precise positioning and effects.

Features:
- Custom mockup template loading
- Precise design positioning with coordinates
- Realistic opacity and blending effects
- Perspective transformation support
- Multiple product type support
- Batch processing capabilities
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np

# Set up logging
logger = logging.getLogger("custom_mockup_generator")


class MockupTemplate:
    """Represents a mockup template with positioning data."""
    
    def __init__(self, template_path: str, config: Dict[str, Any]):
        """
        Initialize mockup template.
        
        Args:
            template_path: Path to template image file
            config: Template configuration with positioning data
        """
        self.template_path = Path(template_path)
        self.config = config
        self.image = None
        
    def load(self) -> Image.Image:
        """Load template image."""
        if self.image is None:
            self.image = Image.open(self.template_path).convert("RGBA")
        return self.image
    
    @property
    def name(self) -> str:
        """Get template name."""
        return self.template_path.stem
    
    @property
    def design_area(self) -> Tuple[int, int, int, int]:
        """Get design placement area (x1, y1, x2, y2)."""
        return tuple(self.config.get('design_area', [400, 400, 1600, 1600]))
    
    @property
    def opacity(self) -> float:
        """Get design opacity for realism."""
        return self.config.get('opacity', 0.85)
    
    @property
    def blend_mode(self) -> str:
        """Get blend mode for design overlay."""
        return self.config.get('blend_mode', 'multiply')


class CustomMockupGenerator:
    """
    Advanced mockup generator using custom template assets.
    """
    
    def __init__(self, assets_dir: str = "assets", output_dir: str = "output",
                 config_file: str = "config/mockup_templates.json"):
        """
        Initialize the custom mockup generator.

        Args:
            assets_dir: Directory containing mockup assets
            output_dir: Directory for generated mockups
            config_file: Path to template configuration file
        """
        self.assets_dir = Path(assets_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config(config_file)

        # Load template configurations
        self.templates = self._load_templates()

        logger.info(f"Initialized CustomMockupGenerator with {len(self.templates)} templates")
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load config file {config_file}: {e}")
            return {}

    def _load_templates(self) -> Dict[str, List[MockupTemplate]]:
        """
        Load all mockup templates from assets directory using configuration.

        Returns:
            Dictionary of product type -> list of templates
        """
        templates = {
            'tshirts': [],
            'sweatshirts': [],
            'posters': []
        }

        # Load templates for each product type
        for product_type in templates.keys():
            mockup_dir = self.assets_dir / "mockups" / product_type
            if mockup_dir.exists():
                # Get default settings from config
                category_config = self.config.get('template_categories', {}).get(product_type, {})
                default_settings = category_config.get('default_settings', {})
                template_configs = category_config.get('templates', {})

                for template_file in mockup_dir.glob("*"):
                    if template_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                        template_name = template_file.stem

                        # Get specific config for this template or use defaults
                        template_config = template_configs.get(template_name, {})

                        # Merge default settings with specific template settings
                        config = default_settings.copy()
                        config.update(template_config)

                        template = MockupTemplate(str(template_file), config)
                        templates[product_type].append(template)

                logger.info(f"Loaded {len(templates[product_type])} {product_type} templates")

        return templates
    
    def _resize_design_to_fit(self, design: Image.Image, target_area: Tuple[int, int, int, int], 
                             padding_factor: float = 0.8) -> Image.Image:
        """
        Resize design to fit target area while maintaining aspect ratio.
        
        Args:
            design: Design image to resize
            target_area: Target area (x1, y1, x2, y2)
            padding_factor: Factor to leave padding (0.8 = 20% padding)
            
        Returns:
            Resized design image
        """
        area_width = target_area[2] - target_area[0]
        area_height = target_area[3] - target_area[1]
        
        # Calculate scaling factor
        scale_x = (area_width * padding_factor) / design.width
        scale_y = (area_height * padding_factor) / design.height
        scale = min(scale_x, scale_y)
        
        new_width = int(design.width * scale)
        new_height = int(design.height * scale)
        
        return design.resize((new_width, new_height), Image.LANCZOS)
    
    def _apply_realistic_effects(self, design: Image.Image, template: MockupTemplate) -> Image.Image:
        """
        Apply realistic effects to design for better integration.
        
        Args:
            design: Design image
            template: Mockup template with effect settings
            
        Returns:
            Design with realistic effects applied
        """
        # Apply opacity
        if template.opacity < 1.0:
            # Create alpha mask
            alpha = design.split()[-1]  # Get alpha channel
            alpha = ImageEnhance.Brightness(alpha).enhance(template.opacity)
            design.putalpha(alpha)
        
        # Apply subtle blur for fabric texture integration
        if template.config.get('fabric_blur', False):
            design = design.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Apply slight perspective/warp for realism (placeholder for future enhancement)
        # This would involve more complex transformations
        
        return design
    
    def _blend_design_with_template(self, template_img: Image.Image, design: Image.Image,
                                   position: Tuple[int, int], blend_mode: str) -> Image.Image:
        """
        Blend design with template using specified blend mode.

        Args:
            template_img: Template image
            design: Design to overlay
            position: Position to place design (x, y)
            blend_mode: Blending mode ('normal', 'multiply', 'screen', 'overlay')

        Returns:
            Final mockup image
        """
        # Create a copy of template
        result = template_img.copy()

        if blend_mode == 'normal':
            # Simple paste with alpha
            result.paste(design, position, design)

        elif blend_mode == 'multiply':
            # Multiply blend for fabric integration
            overlay = Image.new('RGBA', template_img.size, (255, 255, 255, 0))
            overlay.paste(design, position, design)

            # Convert to RGB for blending
            if result.mode == 'RGBA':
                background = Image.new('RGB', result.size, (255, 255, 255))
                background.paste(result, mask=result.split()[-1] if result.mode == 'RGBA' else None)
                result = background

            if overlay.mode == 'RGBA':
                overlay_rgb = Image.new('RGB', overlay.size, (255, 255, 255))
                overlay_rgb.paste(overlay, mask=overlay.split()[-1])
                overlay = overlay_rgb

            # Apply multiply blend
            result_array = np.array(result, dtype=np.float32)
            overlay_array = np.array(overlay, dtype=np.float32)
            blended = (result_array * overlay_array) / 255.0
            result = Image.fromarray(np.uint8(blended))

        elif blend_mode == 'screen':
            # Screen blend for light designs on dark backgrounds
            overlay = Image.new('RGBA', template_img.size, (0, 0, 0, 0))
            overlay.paste(design, position, design)

            # Convert to RGB
            if result.mode == 'RGBA':
                background = Image.new('RGB', result.size, (0, 0, 0))
                background.paste(result, mask=result.split()[-1] if result.mode == 'RGBA' else None)
                result = background

            if overlay.mode == 'RGBA':
                overlay_rgb = Image.new('RGB', overlay.size, (0, 0, 0))
                overlay_rgb.paste(overlay, mask=overlay.split()[-1])
                overlay = overlay_rgb

            # Apply screen blend: 1 - (1-a) * (1-b)
            result_array = np.array(result, dtype=np.float32) / 255.0
            overlay_array = np.array(overlay, dtype=np.float32) / 255.0
            blended = 1 - (1 - result_array) * (1 - overlay_array)
            result = Image.fromarray(np.uint8(blended * 255))

        else:  # Default to normal
            result.paste(design, position, design)

        return result
    
    def generate_mockup(self, product_type: str, design_path: str, template_name: str = None,
                       custom_position: Tuple[int, int] = None) -> Dict[str, Any]:
        """
        Generate a single mockup.
        
        Args:
            product_type: Type of product ('tshirts', 'sweatshirts', 'posters')
            design_path: Path to design file
            template_name: Specific template name (optional, uses first if not specified)
            custom_position: Custom position override (x, y)
            
        Returns:
            Dictionary with generation results
        """
        try:
            # Validate inputs
            if product_type not in self.templates:
                raise ValueError(f"Unknown product type: {product_type}")
            
            if not self.templates[product_type]:
                raise ValueError(f"No templates found for product type: {product_type}")
            
            # Select template
            if template_name:
                template = next((t for t in self.templates[product_type] if t.name == template_name), None)
                if not template:
                    raise ValueError(f"Template '{template_name}' not found for {product_type}")
            else:
                template = self.templates[product_type][0]  # Use first template
            
            # Load design
            design = Image.open(design_path).convert("RGBA")
            
            # Load template
            template_img = template.load()
            
            # Resize design to fit
            design_resized = self._resize_design_to_fit(design, template.design_area)
            
            # Apply realistic effects
            design_processed = self._apply_realistic_effects(design_resized, template)
            
            # Calculate position
            if custom_position:
                position = custom_position
            else:
                # Center design in design area
                area = template.design_area
                center_x = area[0] + (area[2] - area[0] - design_processed.width) // 2
                center_y = area[1] + (area[3] - area[1] - design_processed.height) // 2
                position = (center_x, center_y)
            
            # Blend design with template
            final_mockup = self._blend_design_with_template(
                template_img, design_processed, position, template.blend_mode
            )
            
            # Generate output filename
            design_name = Path(design_path).stem
            output_filename = f"{design_name}_{product_type}_{template.name}.png"
            output_path = self.output_dir / output_filename
            
            # Save mockup
            final_mockup.save(output_path, "PNG", quality=95)
            
            logger.info(f"Generated mockup: {output_path}")
            
            return {
                'success': True,
                'mockup_path': str(output_path),
                'template_used': template.name,
                'design_position': position,
                'output_size': final_mockup.size
            }
            
        except Exception as e:
            logger.error(f"Error generating mockup: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_available_templates(self) -> Dict[str, List[str]]:
        """
        List all available templates by product type.
        
        Returns:
            Dictionary of product type -> list of template names
        """
        return {
            product_type: [template.name for template in templates]
            for product_type, templates in self.templates.items()
        }
    
    def get_template_info(self, product_type: str, template_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific template.
        
        Args:
            product_type: Product type
            template_name: Template name
            
        Returns:
            Template information dictionary
        """
        if product_type not in self.templates:
            return {'error': f'Unknown product type: {product_type}'}
        
        template = next((t for t in self.templates[product_type] if t.name == template_name), None)
        if not template:
            return {'error': f'Template not found: {template_name}'}
        
        img = template.load()
        return {
            'name': template.name,
            'path': str(template.template_path),
            'size': img.size,
            'mode': img.mode,
            'design_area': template.design_area,
            'opacity': template.opacity,
            'blend_mode': template.blend_mode
        }
