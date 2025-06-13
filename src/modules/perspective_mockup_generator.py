#!/usr/bin/env python3
"""
Perspective Mockup Generator for Art Prints
==========================================

Advanced mockup generation with perspective transformation for art prints
and posters shown at angles in mockup templates.

Features:
- Perspective transformation to match angled frames
- Corner point mapping for precise alignment
- Automatic perspective detection (future enhancement)
- Manual corner specification for perfect alignment
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from PIL import Image, ImageDraw, ImageFilter
import cv2

# Set up logging
logger = logging.getLogger("perspective_mockup_generator")


class PerspectiveMockupGenerator:
    """
    Advanced mockup generator with perspective transformation for art prints.
    """
    
    def __init__(self, assets_dir: str = "assets", output_dir: str = "output"):
        """
        Initialize the perspective mockup generator.
        
        Args:
            assets_dir: Directory containing mockup assets
            output_dir: Directory for generated mockups
        """
        self.assets_dir = Path(assets_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load poster configurations with perspective data
        self.poster_configs = self._load_poster_configs()
        
        logger.info(f"Initialized PerspectiveMockupGenerator")
    
    def _load_poster_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Load poster mockup configurations with perspective corner points.

        Returns:
            Dictionary of poster template configurations
        """
        # Try to load from configuration file
        config_path = Path("config/poster_perspective_config.json")

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    templates = config_data.get('templates', {})

                    # Convert corner arrays to tuples
                    for template_name, template_config in templates.items():
                        if 'corners' in template_config:
                            template_config['corners'] = [tuple(corner) for corner in template_config['corners']]

                    logger.info(f"Loaded {len(templates)} poster configurations from config file")
                    return templates

            except Exception as e:
                logger.warning(f"Could not load poster config file: {e}")

        # Fallback to default configurations
        logger.info("Using default poster configurations")
        configs = {
            "1.jpg": {
                "name": "Straight Poster Frame",
                "corners": [(350, 250), (1650, 250), (1650, 1750), (350, 1750)],
                "perspective_type": "straight"
            },
            "2.jpg": {
                "name": "Angled Poster Frame",
                "corners": [(400, 300), (1600, 250), (1650, 1750), (350, 1800)],
                "perspective_type": "angled"
            }
        }

        return configs
    
    def _apply_perspective_transform(self, design: Image.Image, 
                                   corner_points: List[Tuple[int, int]]) -> Image.Image:
        """
        Apply perspective transformation to design based on corner points.
        
        Args:
            design: Design image to transform
            corner_points: Four corner points [top-left, top-right, bottom-right, bottom-left]
            
        Returns:
            Transformed design image
        """
        # Convert PIL image to OpenCV format
        design_cv = cv2.cvtColor(np.array(design), cv2.COLOR_RGBA2BGRA)
        
        # Define source points (original rectangle)
        src_points = np.float32([
            [0, 0],                           # Top-left
            [design.width, 0],                # Top-right
            [design.width, design.height],    # Bottom-right
            [0, design.height]                # Bottom-left
        ])
        
        # Define destination points (perspective corners)
        dst_points = np.float32(corner_points)
        
        # Calculate perspective transformation matrix
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        # Calculate output size based on corner points
        x_coords = [p[0] for p in corner_points]
        y_coords = [p[1] for p in corner_points]
        output_width = int(max(x_coords) - min(x_coords)) + 100
        output_height = int(max(y_coords) - min(y_coords)) + 100
        
        # Apply perspective transformation
        transformed = cv2.warpPerspective(
            design_cv, 
            matrix, 
            (output_width, output_height),
            flags=cv2.INTER_LANCZOS4,
            borderMode=cv2.BORDER_TRANSPARENT
        )
        
        # Convert back to PIL format
        transformed_pil = Image.fromarray(cv2.cvtColor(transformed, cv2.COLOR_BGRA2RGBA))
        
        return transformed_pil
    
    def _create_perspective_overlay(self, template: Image.Image, 
                                  transformed_design: Image.Image,
                                  corner_points: List[Tuple[int, int]]) -> Image.Image:
        """
        Create final mockup by overlaying transformed design on template.
        
        Args:
            template: Template mockup image
            transformed_design: Perspective-transformed design
            corner_points: Corner points for positioning
            
        Returns:
            Final mockup image
        """
        # Create a copy of the template
        result = template.copy()
        
        # Calculate position to place transformed design
        min_x = min(p[0] for p in corner_points)
        min_y = min(p[1] for p in corner_points)
        
        # Create overlay with same size as template
        overlay = Image.new('RGBA', template.size, (0, 0, 0, 0))
        
        # Paste transformed design at calculated position
        overlay.paste(transformed_design, (int(min_x), int(min_y)), transformed_design)
        
        # Composite with template
        result = Image.alpha_composite(result.convert('RGBA'), overlay)
        
        return result
    
    def generate_perspective_mockup(self, design_path: str, template_name: str,
                                  custom_corners: List[Tuple[int, int]] = None) -> Dict[str, Any]:
        """
        Generate a perspective-corrected mockup for art prints.
        
        Args:
            design_path: Path to design file
            template_name: Name of template file (e.g., "2.jpg")
            custom_corners: Custom corner points (optional)
            
        Returns:
            Dictionary with generation results
        """
        try:
            # Load template
            template_path = self.assets_dir / "mockups" / "posters" / template_name
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path}")
            
            template = Image.open(template_path).convert("RGBA")
            
            # Load design
            design = Image.open(design_path).convert("RGBA")
            
            # Get corner points
            if custom_corners:
                corner_points = custom_corners
            else:
                config = self.poster_configs.get(template_name)
                if not config:
                    raise ValueError(f"No configuration found for template: {template_name}")
                corner_points = config['corners']
            
            logger.info(f"Applying perspective transformation with corners: {corner_points}")
            
            # Apply perspective transformation
            transformed_design = self._apply_perspective_transform(design, corner_points)
            
            # Create final mockup
            final_mockup = self._create_perspective_overlay(template, transformed_design, corner_points)
            
            # Generate output filename
            design_name = Path(design_path).stem
            template_stem = Path(template_name).stem
            output_filename = f"{design_name}_poster_perspective_{template_stem}.png"
            output_path = self.output_dir / output_filename
            
            # Save mockup
            final_mockup.save(output_path, "PNG", quality=95)
            
            logger.info(f"Generated perspective mockup: {output_path}")
            
            return {
                'success': True,
                'mockup_path': str(output_path),
                'template_used': template_name,
                'corner_points': corner_points,
                'output_size': final_mockup.size
            }
            
        except Exception as e:
            logger.error(f"Error generating perspective mockup: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def calibrate_corners(self, template_name: str, design_path: str = None) -> Dict[str, Any]:
        """
        Helper method to calibrate corner points for a template.
        Creates a test image with corner markers for manual adjustment.
        
        Args:
            template_name: Name of template file
            design_path: Optional test design (creates default if not provided)
            
        Returns:
            Dictionary with calibration info
        """
        try:
            # Load template
            template_path = self.assets_dir / "mockups" / "posters" / template_name
            template = Image.open(template_path).convert("RGBA")
            
            # Create test design if not provided
            if not design_path:
                test_design = Image.new('RGBA', (800, 600), (255, 100, 100, 255))
                draw = ImageDraw.Draw(test_design)
                
                # Draw corner markers
                draw.ellipse([(10, 10), (50, 50)], fill=(255, 255, 255, 255))  # Top-left
                draw.ellipse([(750, 10), (790, 50)], fill=(255, 255, 255, 255))  # Top-right
                draw.ellipse([(750, 550), (790, 590)], fill=(255, 255, 255, 255))  # Bottom-right
                draw.ellipse([(10, 550), (50, 590)], fill=(255, 255, 255, 255))  # Bottom-left
                
                # Add center text
                draw.text((400, 300), "CALIBRATION", fill=(255, 255, 255, 255), anchor="mm")
                
                design_path = "calibration_design.png"
                test_design.save(design_path)
            
            # Get current corner configuration
            config = self.poster_configs.get(template_name, {})
            corners = config.get('corners', [(300, 200), (1700, 200), (1700, 1800), (300, 1800)])
            
            # Generate test mockup
            result = self.generate_perspective_mockup(design_path, template_name, corners)
            
            if result['success']:
                logger.info(f"Calibration mockup generated: {result['mockup_path']}")
                logger.info(f"Current corners: {corners}")
                logger.info("Adjust corner points in poster_configs and regenerate for fine-tuning")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in calibration: {e}")
            return {'success': False, 'error': str(e)}
    
    def list_available_templates(self) -> List[str]:
        """List available poster templates."""
        poster_dir = self.assets_dir / "mockups" / "posters"
        if poster_dir.exists():
            return [f.name for f in poster_dir.glob("*") if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        return []
    
    def get_template_config(self, template_name: str) -> Dict[str, Any]:
        """Get configuration for a specific template."""
        return self.poster_configs.get(template_name, {})
    
    def update_template_corners(self, template_name: str, 
                              corners: List[Tuple[int, int]]) -> None:
        """
        Update corner points for a template.
        
        Args:
            template_name: Template file name
            corners: New corner points [top-left, top-right, bottom-right, bottom-left]
        """
        if template_name not in self.poster_configs:
            self.poster_configs[template_name] = {}
        
        self.poster_configs[template_name]['corners'] = corners
        logger.info(f"Updated corners for {template_name}: {corners}")


def create_test_art_design(output_path: str) -> str:
    """Create a test art design for perspective testing."""
    # Create an art-style design
    design = Image.new('RGBA', (1200, 900), (255, 255, 255, 255))
    draw = ImageDraw.Draw(design)
    
    # Draw frame border
    draw.rectangle([(50, 50), (1150, 850)], fill=None, outline=(0, 0, 0, 255), width=8)
    
    # Draw abstract art
    draw.ellipse([(200, 150), (600, 550)], fill=(70, 130, 180, 255))
    draw.rectangle([(400, 200), (1000, 600)], fill=(255, 165, 0, 200))
    draw.polygon([(600, 100), (900, 400), (300, 700)], fill=(255, 69, 0, 180))
    
    # Add title
    draw.text((600, 750), "ABSTRACT ART", fill=(0, 0, 0, 255), anchor="mm")
    draw.text((600, 800), "Limited Edition Print", fill=(100, 100, 100, 255), anchor="mm")
    
    design.save(output_path)
    return output_path
