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
        First tries to load VIA annotation coordinates, then falls back to config file.

        Returns:
            Dictionary of poster template configurations
        """
        # Try to load VIA annotation coordinates first
        via_configs = self._load_via_coordinates()
        if via_configs:
            logger.info(f"Loaded {len(via_configs)} poster configurations from VIA annotations")
            return via_configs

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

    def _load_via_coordinates(self) -> Dict[str, Dict[str, Any]]:
        """
        Load precise coordinates from VIA annotation files.

        Returns:
            Dictionary of poster template configurations with VIA coordinates
        """
        try:
            # Map VIA files to template files
            via_mapping = {
                "1.jpg": "via_project_15Jun2025_9h52m_json.json",
                "2.jpg": "via_project_15Jun2025_9h52m_json (1).json",
                "3.jpg": "via_project_15Jun2025_9h52m_json (2).json",
                "5.jpg": "via_project_15Jun2025_9h52m_json (3).json",
                "6.jpg": "via_project_15Jun2025_9h52m_json (4).json",
                "7.jpg": "via_project_15Jun2025_9h52m_json (5).json",
                "8.jpg": "via_project_15Jun2025_9h52m_json (6).json",
                "9.png": "via_export_json.json"
            }

            # Template names and types
            template_info = {
                "1.jpg": {"name": "Straight Front View Poster", "perspective_type": "straight", "difficulty": "easy"},
                "2.jpg": {"name": "Angled Poster Frame", "perspective_type": "angled", "difficulty": "medium"},
                "3.jpg": {"name": "Side Angle Poster", "perspective_type": "side_angle", "difficulty": "medium"},
                "5.jpg": {"name": "Living Room Poster", "perspective_type": "room_context", "difficulty": "easy"},
                "6.jpg": {"name": "Tilted Frame Poster", "perspective_type": "tilted", "difficulty": "hard"},
                "7.jpg": {"name": "Modern Frame Poster", "perspective_type": "modern", "difficulty": "medium"},
                "8.jpg": {"name": "Artistic Angle Poster", "perspective_type": "artistic", "difficulty": "hard"},
                "9.png": {"name": "New Template Poster", "perspective_type": "straight", "difficulty": "easy"}
            }

            coordinates_data = {}

            for template_file, via_file in via_mapping.items():
                via_path = Path(f"assets/mockups/posters/{via_file}")

                if not via_path.exists():
                    continue

                with open(via_path, 'r') as f:
                    via_data = json.load(f)

                # Extract the first (and only) entry
                file_key = list(via_data.keys())[0]
                file_info = via_data[file_key]

                regions = file_info.get('regions', [])
                if not regions:
                    continue

                region = regions[0]
                shape_attrs = region['shape_attributes']

                # Handle different shape types
                if shape_attrs['name'] == 'rect':
                    # Rectangle coordinates
                    x = shape_attrs['x']
                    y = shape_attrs['y']
                    width = shape_attrs['width']
                    height = shape_attrs['height']

                    # Convert to corner points [top-left, top-right, bottom-right, bottom-left]
                    corners = [
                        (x, y),                    # Top-left
                        (x + width, y),            # Top-right
                        (x + width, y + height),   # Bottom-right
                        (x, y + height)            # Bottom-left
                    ]

                elif shape_attrs['name'] == 'polyline':
                    # Polyline coordinates (for angled/perspective frames)
                    x_points = shape_attrs['all_points_x']
                    y_points = shape_attrs['all_points_y']

                    # Take first 4 points as corners
                    corners = [(x_points[i], y_points[i]) for i in range(min(4, len(x_points)))]

                else:
                    continue

                # Create configuration with VIA coordinates and template info
                config = template_info.get(template_file, {
                    "name": f"Template {template_file}",
                    "perspective_type": "unknown",
                    "difficulty": "medium"
                })
                config['corners'] = corners
                config['via_source'] = via_file

                coordinates_data[template_file] = config

            return coordinates_data

        except Exception as e:
            logger.warning(f"Could not load VIA coordinates: {e}")
            return {}

    def _is_rectangular_frame(self, corners: List[Tuple[int, int]], tolerance: int = 5) -> bool:
        """
        Check if the 4 corners form a rectangular frame (straight view) or angled frame.

        Args:
            corners: List of 4 corner points [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
                     Expected order: [top-left, top-right, bottom-right, bottom-left]
            tolerance: Pixel tolerance for "straight" lines

        Returns:
            True if rectangular (use direct placement), False if angled (use perspective)
        """
        if len(corners) != 4:
            return False

        x1, y1 = corners[0]  # Top-left
        x2, y2 = corners[1]  # Top-right
        x3, y3 = corners[2]  # Bottom-right
        x4, y4 = corners[3]  # Bottom-left

        # Check if top edge is horizontal (y1 ≈ y2)
        top_horizontal = abs(y1 - y2) <= tolerance

        # Check if bottom edge is horizontal (y3 ≈ y4)
        bottom_horizontal = abs(y3 - y4) <= tolerance

        # Check if left edge is vertical (x1 ≈ x4)
        left_vertical = abs(x1 - x4) <= tolerance

        # Check if right edge is vertical (x2 ≈ x3)
        right_vertical = abs(x2 - x3) <= tolerance

        # All edges must be straight for rectangular frame
        is_rect = top_horizontal and bottom_horizontal and left_vertical and right_vertical

        logger.debug(f"Frame analysis: top_h={top_horizontal}, bottom_h={bottom_horizontal}, "
                    f"left_v={left_vertical}, right_v={right_vertical} → {'RECTANGULAR' if is_rect else 'ANGLED'}")

        return is_rect

    def _apply_clean_placement(self, design: Image.Image,
                             corner_points: List[Tuple[int, int]]) -> Tuple[Image.Image, Tuple[int, int]]:
        """
        Apply clean design placement within VIA coordinates (no perspective transformation).
        For rectangular frames only.

        Args:
            design: Design image to place
            corner_points: Four corner points [top-left, top-right, bottom-right, bottom-left]

        Returns:
            Tuple of (resized design, placement position)
        """
        # Calculate target area from VIA coordinates
        x1, y1 = corner_points[0]  # Top-left
        x2, y2 = corner_points[2]  # Bottom-right

        target_width = x2 - x1
        target_height = y2 - y1

        logger.debug(f"Clean placement area: {target_width} x {target_height} at ({x1}, {y1})")

        # Resize design to fit target area exactly
        resized_design = design.resize((target_width, target_height), Image.Resampling.LANCZOS)

        return resized_design, (x1, y1)

    def _apply_perspective_transform(self, design: Image.Image,
                                   corner_points: List[Tuple[int, int]],
                                   template_size: Tuple[int, int]) -> Image.Image:
        """
        Apply perspective transformation to design based on angled corner points.
        For angled frames only.

        Args:
            design: Design image to transform
            corner_points: Four corner points [top-left, top-right, bottom-right, bottom-left]
            template_size: Size of the template image (width, height)

        Returns:
            Transformed design image with template dimensions
        """
        # Convert PIL image to numpy array (keep RGBA format)
        design_array = np.array(design)

        # Define source points (original rectangle)
        src_points = np.float32([
            [0, 0],                           # Top-left
            [design.width, 0],                # Top-right
            [design.width, design.height],    # Bottom-right
            [0, design.height]                # Bottom-left
        ])

        # Define destination points (angled perspective corners)
        dst_points = np.float32(corner_points)

        # Calculate perspective transformation matrix
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)

        # Use template size for output canvas to ensure proper compositing
        template_width, template_height = template_size

        logger.debug(f"Perspective transform: {design.size} → {template_width}x{template_height}")
        logger.debug(f"Corner points: {corner_points}")

        # Apply perspective transformation with template-sized canvas
        # Use BORDER_CONSTANT with transparent value to avoid blue grain artifacts
        transformed = cv2.warpPerspective(
            design_array,
            matrix,
            (template_width, template_height),
            flags=cv2.INTER_LANCZOS4,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0, 0)  # Transparent border
        )

        # Convert back to PIL format (already in RGBA format)
        transformed_pil = Image.fromarray(transformed, 'RGBA')

        return transformed_pil

    def _create_clean_overlay(self, template: Image.Image,
                            resized_design: Image.Image,
                            placement_position: Tuple[int, int]) -> Image.Image:
        """
        Create final mockup by placing design directly at VIA coordinates.

        Args:
            template: Template mockup image
            resized_design: Design resized to fit target area
            placement_position: Exact position to place design (x, y)

        Returns:
            Final mockup image
        """
        # Create a copy of the template
        result = template.copy().convert('RGBA')

        # Paste design directly at VIA coordinates
        result.paste(resized_design, placement_position, resized_design)

        return result

    def _create_perspective_overlay(self, template: Image.Image,
                                  transformed_design: Image.Image,
                                  corner_points: List[Tuple[int, int]]) -> Image.Image:
        """
        Create final mockup by overlaying perspective-transformed design on template.
        For angled frames only.

        Args:
            template: Template mockup image
            transformed_design: Perspective-transformed design (already template-sized)
            corner_points: Corner points for positioning (for reference only)

        Returns:
            Final mockup image
        """
        # Create a copy of the template
        result = template.copy().convert('RGBA')

        # Since transformed_design is already template-sized and positioned correctly,
        # we can directly composite it with the template
        logger.debug(f"Compositing transformed design {transformed_design.size} with template {template.size}")

        # Direct alpha composite - the perspective transform already positioned everything correctly
        result = Image.alpha_composite(result, transformed_design)

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
            # Validate design file before processing
            if not Path(design_path).exists():
                raise FileNotFoundError("Design file missing; aborting.")

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
            
            # Detect frame type and apply appropriate transformation
            if self._is_rectangular_frame(corner_points):
                logger.info(f"RECTANGULAR frame detected - applying clean placement: {corner_points}")

                # Apply clean placement (no perspective transformation needed)
                resized_design, placement_position = self._apply_clean_placement(design, corner_points)

                # Create final mockup with direct placement
                final_mockup = self._create_clean_overlay(template, resized_design, placement_position)

            else:
                logger.info(f"ANGLED frame detected - applying perspective transformation: {corner_points}")

                # Apply perspective transformation for angled frames
                transformed_design = self._apply_perspective_transform(design, corner_points, template.size)

                # Create final mockup with perspective overlay
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
