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
import sys
from copy import deepcopy
import cv2

# Add utils to path for output manager
sys.path.append(str(Path(__file__).parent.parent))
from utils.output_manager import OutputManager

# Set up logging
logger = logging.getLogger("custom_mockup_generator")

# Optional Google Sheets integration
try:
    from modules.sheets_mockup_uploader import SheetsMockupUploader
    SHEETS_AVAILABLE = True
except ImportError:
    logger.warning("Google Sheets integration not available - continuing without it")
    SheetsMockupUploader = None
    SHEETS_AVAILABLE = False


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
                 config_file: str = "config/mockup_templates.json", auto_manage: bool = True,
                 enable_sheets_upload: bool = False, airtable_client=None):
        """
        Initialize the custom mockup generator.

        Args:
            assets_dir: Directory containing mockup assets
            output_dir: Directory for generated mockups
            config_file: Path to template configuration file
            auto_manage: Enable automatic file management and cleanup
            enable_sheets_upload: Enable Google Sheets upload integration
            airtable_client: Existing Airtable client for integration
        """
        self.assets_dir = Path(assets_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize output manager
        self.auto_manage = auto_manage
        if auto_manage:
            self.output_manager = OutputManager(output_dir)
            # Clean up on startup
            self.output_manager.cleanup_old_files()

        # Load configuration
        self.config = self._load_config(config_file)

        # Load template configurations
        self.templates = self._load_templates()

        # Load VIA coordinates for poster perspective transformation
        self.poster_via_configs = self._load_via_coordinates()

        # Initialize Google Sheets uploader if enabled
        self.enable_sheets_upload = enable_sheets_upload
        self.sheets_uploader = None
        if enable_sheets_upload:
            try:
                self.sheets_uploader = SheetsMockupUploader(airtable_client=airtable_client)
                logger.info("Google Sheets upload integration enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Sheets uploader: {e}")
                self.enable_sheets_upload = False

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

                        # Merge default settings with specific template settings using deep copy
                        # This prevents shared references that could cause coordinate drift
                        config = deepcopy(default_settings)
                        config.update(template_config)

                        template = MockupTemplate(str(template_file), config)
                        templates[product_type].append(template)

                logger.info(f"Loaded {len(templates[product_type])} {product_type} templates")

        return templates

    def _load_via_coordinates(self) -> Dict[str, Dict[str, Any]]:
        """
        Load precise coordinates from VIA annotation files for poster perspective transformation.

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

            logger.info(f"Loaded VIA coordinates for {len(coordinates_data)} poster templates")
            return coordinates_data

        except Exception as e:
            logger.warning(f"Could not load VIA coordinates: {e}")
            return {}

    def _resize_design_to_fit(self, design: Image.Image, target_area: Tuple[int, int, int, int],
                             template: MockupTemplate) -> Image.Image:
        """
        Resize design to fit target area while maintaining aspect ratio.

        Args:
            design: Design image to resize
            target_area: Target area (x1, y1, x2, y2)
            template: Template with padding_factor configuration

        Returns:
            Resized design image
        """
        area_width = target_area[2] - target_area[0]
        area_height = target_area[3] - target_area[1]

        # Get padding factor from template config (default 0.95 for slight padding)
        padding_factor = template.config.get("padding_factor", 0.95)

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
            # Enhanced screen blend for better visibility on dark backgrounds
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

            # Apply enhanced screen blend with brightness boost
            result_array = np.array(result, dtype=np.float32) / 255.0
            overlay_array = np.array(overlay, dtype=np.float32) / 255.0

            # Boost overlay brightness for better visibility on dark fabrics
            # Use higher boost factor for better contrast
            overlay_array = np.clip(overlay_array * 1.6, 0, 1)

            # Apply screen blend: 1 - (1-a) * (1-b)
            blended = 1 - (1 - result_array) * (1 - overlay_array)
            result = Image.fromarray(np.uint8(blended * 255))

        else:  # Default to normal
            result.paste(design, position, design)

        return result
    
    def generate_mockup(self, product_type: str, design_path: str, template_name: str = None,
                       custom_position: Tuple[int, int] = None, upload_to_sheets: bool = None,
                       variation_info: Dict[str, str] = None, airtable_record_id: str = None) -> Dict[str, Any]:
        """
        Generate a single mockup with optional Google Sheets upload.

        Args:
            product_type: Type of product ('tshirts', 'sweatshirts', 'posters')
            design_path: Path to design file
            template_name: Specific template name (optional, uses first if not specified)
            custom_position: Custom position override (x, y)
            upload_to_sheets: Override sheets upload setting for this mockup
            variation_info: Variation details for organization (color, size, etc.)
            airtable_record_id: Associated Airtable record ID for URL updates

        Returns:
            Dictionary with generation results including Google Sheets URL if uploaded
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

            # Handle poster perspective transformation if VIA coordinates are available
            if product_type == 'posters' and f"{template.name}.jpg" in self.poster_via_configs:
                # Use perspective transformation for posters with VIA coordinates
                via_config = self.poster_via_configs[f"{template.name}.jpg"]
                corner_points = via_config['corners']

                logger.info(f"Using VIA coordinates for poster {template.name}: {corner_points}")

                # Detect frame type and apply appropriate transformation
                if self._is_rectangular_frame(corner_points):
                    logger.info(f"RECTANGULAR frame detected - applying clean placement")

                    # Apply clean placement (no perspective transformation needed)
                    design_processed, position = self._apply_clean_placement(design, corner_points)

                    # Create final mockup with direct placement
                    final_mockup = self._create_clean_overlay(template_img, design_processed, position)

                else:
                    logger.info(f"ANGLED frame detected - applying perspective transformation")

                    # Apply perspective transformation for angled frames
                    design_processed = self._apply_perspective_transform(design, corner_points, template_img.size)

                    # Create final mockup with perspective overlay
                    final_mockup = self._create_perspective_overlay(template_img, design_processed, corner_points)

                # Set position for result reporting
                position = corner_points[0] if corner_points else (0, 0)

            elif product_type == 'posters' and f"{template.name}.png" in self.poster_via_configs:
                # Handle PNG templates (like 9.png)
                via_config = self.poster_via_configs[f"{template.name}.png"]
                corner_points = via_config['corners']

                logger.info(f"Using VIA coordinates for poster {template.name}: {corner_points}")

                # Detect frame type and apply appropriate transformation
                if self._is_rectangular_frame(corner_points):
                    logger.info(f"RECTANGULAR frame detected - applying clean placement")

                    # Apply clean placement (no perspective transformation needed)
                    design_processed, position = self._apply_clean_placement(design, corner_points)

                    # Create final mockup with direct placement
                    final_mockup = self._create_clean_overlay(template_img, design_processed, position)

                else:
                    logger.info(f"ANGLED frame detected - applying perspective transformation")

                    # Apply perspective transformation for angled frames
                    design_processed = self._apply_perspective_transform(design, corner_points, template_img.size)

                    # Create final mockup with perspective overlay
                    final_mockup = self._create_perspective_overlay(template_img, design_processed, corner_points)

                # Set position for result reporting
                position = corner_points[0] if corner_points else (0, 0)

            else:
                # Standard processing for t-shirts, sweatshirts, and posters without VIA coordinates
                # Resize design to fit with template-specific padding factor
                design_resized = self._resize_design_to_fit(design, template.design_area, template)

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

            # Auto-organize file if enabled
            if self.auto_manage:
                organized_path = self.output_manager.organize_file(output_path)
                output_path = organized_path

            logger.info(f"Generated mockup: {output_path}")

            # Upload to Google Sheets if enabled
            sheets_result = None
            if (upload_to_sheets is True or
                (upload_to_sheets is None and self.enable_sheets_upload)) and self.sheets_uploader:

                try:
                    # Prepare product name from design path if not in variation_info
                    product_name = variation_info.get('product_name') if variation_info else Path(design_path).stem

                    # Add upload job to queue
                    self.sheets_uploader.add_upload_job(
                        mockup_path=str(output_path),
                        product_name=product_name,
                        variation_info=variation_info,
                        airtable_record_id=airtable_record_id
                    )

                    # Process the upload immediately for single mockup
                    batch_result = self.sheets_uploader.process_upload_queue(max_workers=1)

                    if batch_result.successful_uploads > 0:
                        sheets_result = batch_result.upload_results[0]
                        logger.info(f"✅ Uploaded mockup to Google Sheets: {sheets_result.shareable_url}")
                    else:
                        logger.error(f"❌ Failed to upload mockup to Google Sheets: {batch_result.errors}")

                except Exception as e:
                    logger.error(f"Error during Google Sheets upload: {e}")

            result = {
                'success': True,
                'mockup_path': str(output_path),
                'template_used': template.name,
                'design_position': position,
                'output_size': final_mockup.size
            }

            # Add Google Sheets information if uploaded
            if sheets_result and sheets_result.success:
                result.update({
                    'google_sheets_url': sheets_result.shareable_url,
                    'google_drive_file_id': sheets_result.file_id,
                    'sheets_upload_status': 'success'
                })
            elif upload_to_sheets or self.enable_sheets_upload:
                result['sheets_upload_status'] = 'failed'

            return result
            
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
