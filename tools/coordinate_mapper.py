#!/usr/bin/env python3
"""
Coordinate Mapper for SEA-E Engine
=================================

Tool for precise design placement mapping using VGG Image Annotator (VIA) JSON exports.
Maps design coordinates from mockup templates to Printify API coordinates.

Features:
- Import VIA JSON annotations
- Convert pixel coordinates to normalized Printify coordinates
- Generate reusable template configurations
- Validate coordinate accuracy
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from PIL import Image
import numpy as np

logger = logging.getLogger("coordinate_mapper")


class CoordinateMapper:
    """
    Maps design coordinates from VIA annotations to Printify API format.
    """
    
    def __init__(self, templates_dir: str = "assets/mockups", 
                 config_dir: str = "config/coordinate_maps"):
        """
        Initialize coordinate mapper.
        
        Args:
            templates_dir: Directory containing mockup template images
            config_dir: Directory to save coordinate mapping configurations
        """
        self.templates_dir = Path(templates_dir)
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"CoordinateMapper initialized: {templates_dir} -> {config_dir}")
    
    def import_via_annotations(self, via_json_path: str) -> Dict[str, Any]:
        """
        Import VIA JSON annotations file.
        
        Args:
            via_json_path: Path to VIA JSON export file
            
        Returns:
            Dict containing parsed VIA annotations
        """
        try:
            with open(via_json_path, 'r') as f:
                via_data = json.load(f)
            
            logger.info(f"Imported VIA annotations: {len(via_data)} images")
            return via_data
            
        except Exception as e:
            logger.error(f"Failed to import VIA annotations: {e}")
            raise
    
    def extract_design_areas(self, via_data: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Extract design areas from VIA annotations.
        
        Args:
            via_data: VIA JSON data
            
        Returns:
            Dict mapping image filenames to design area coordinates
        """
        design_areas = {}
        
        try:
            # VIA format: via_data contains image metadata and regions
            for image_id, image_data in via_data.items():
                if isinstance(image_data, dict) and 'filename' in image_data:
                    filename = image_data['filename']
                    regions = image_data.get('regions', [])
                    
                    areas = []
                    for region in regions:
                        if 'shape_attributes' in region:
                            shape = region['shape_attributes']
                            region_attrs = region.get('region_attributes', {})
                            
                            # Handle different shape types
                            if shape.get('name') == 'polygon':
                                # Polygon coordinates
                                x_coords = shape.get('all_points_x', [])
                                y_coords = shape.get('all_points_y', [])
                                
                                if len(x_coords) >= 4 and len(y_coords) >= 4:
                                    areas.append({
                                        'type': 'polygon',
                                        'coordinates': list(zip(x_coords, y_coords)),
                                        'label': region_attrs.get('label', 'design_area')
                                    })
                            
                            elif shape.get('name') == 'rect':
                                # Rectangle coordinates
                                x = shape.get('x', 0)
                                y = shape.get('y', 0)
                                width = shape.get('width', 0)
                                height = shape.get('height', 0)
                                
                                areas.append({
                                    'type': 'rectangle',
                                    'coordinates': [
                                        (x, y),
                                        (x + width, y),
                                        (x + width, y + height),
                                        (x, y + height)
                                    ],
                                    'label': region_attrs.get('label', 'design_area')
                                })
                    
                    if areas:
                        design_areas[filename] = areas
            
            logger.info(f"Extracted design areas for {len(design_areas)} images")
            return design_areas
            
        except Exception as e:
            logger.error(f"Failed to extract design areas: {e}")
            raise
    
    def normalize_coordinates(self, coordinates: List[Tuple[int, int]], 
                            image_size: Tuple[int, int]) -> List[Tuple[float, float]]:
        """
        Convert pixel coordinates to normalized coordinates (0.0 - 1.0).
        
        Args:
            coordinates: List of (x, y) pixel coordinates
            image_size: (width, height) of the image
            
        Returns:
            List of normalized (x, y) coordinates
        """
        width, height = image_size
        
        normalized = []
        for x, y in coordinates:
            norm_x = x / width
            norm_y = y / height
            normalized.append((norm_x, norm_y))
        
        return normalized
    
    def calculate_printify_coordinates(self, design_area: List[Tuple[float, float]]) -> Dict[str, float]:
        """
        Calculate Printify API coordinates from normalized design area.
        
        Args:
            design_area: Normalized coordinates of design area
            
        Returns:
            Dict with Printify API coordinates (x, y, scale)
        """
        # Calculate center point
        x_coords = [coord[0] for coord in design_area]
        y_coords = [coord[1] for coord in design_area]
        
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        
        # Calculate scale based on area size
        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)
        scale = min(width, height)  # Use smaller dimension for scale
        
        return {
            'x': center_x,
            'y': center_y,
            'scale': scale,
            'angle': 0,
            'width': width,
            'height': height
        }
    
    def generate_template_config(self, template_name: str, design_areas: Dict[str, Any],
                               image_path: str) -> Dict[str, Any]:
        """
        Generate template configuration for mockup generator.
        
        Args:
            template_name: Name of the template
            design_areas: Design area data from VIA
            image_path: Path to template image
            
        Returns:
            Template configuration dictionary
        """
        try:
            # Load image to get dimensions
            with Image.open(image_path) as img:
                image_size = img.size
            
            config = {
                'template_name': template_name,
                'image_path': image_path,
                'image_size': image_size,
                'design_areas': {},
                'printify_coordinates': {}
            }
            
            for area in design_areas:
                label = area.get('label', 'default')
                coordinates = area['coordinates']
                
                # Normalize coordinates
                normalized = self.normalize_coordinates(coordinates, image_size)
                
                # Calculate Printify coordinates
                printify_coords = self.calculate_printify_coordinates(normalized)
                
                config['design_areas'][label] = {
                    'pixel_coordinates': coordinates,
                    'normalized_coordinates': normalized,
                    'type': area['type']
                }
                
                config['printify_coordinates'][label] = printify_coords
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to generate template config: {e}")
            raise
    
    def save_template_config(self, config: Dict[str, Any], output_path: str = None):
        """
        Save template configuration to JSON file.
        
        Args:
            config: Template configuration
            output_path: Output file path (optional)
        """
        try:
            if not output_path:
                template_name = config['template_name']
                output_path = self.config_dir / f"{template_name}_coordinates.json"
            
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved template config: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save template config: {e}")
            raise
    
    def process_via_export(self, via_json_path: str, template_images_dir: str = None):
        """
        Complete workflow: Process VIA export and generate template configs.
        
        Args:
            via_json_path: Path to VIA JSON export
            template_images_dir: Directory containing template images
        """
        try:
            logger.info("Starting VIA export processing...")
            
            # Import VIA annotations
            via_data = self.import_via_annotations(via_json_path)
            
            # Extract design areas
            design_areas = self.extract_design_areas(via_data)
            
            # Process each template
            templates_dir = Path(template_images_dir) if template_images_dir else self.templates_dir
            
            for filename, areas in design_areas.items():
                # Find corresponding image file
                image_path = None
                for ext in ['.png', '.jpg', '.jpeg']:
                    potential_path = templates_dir / filename
                    if potential_path.exists():
                        image_path = potential_path
                        break
                
                if not image_path:
                    logger.warning(f"Image not found for {filename}")
                    continue
                
                # Generate template config
                template_name = Path(filename).stem
                config = self.generate_template_config(template_name, areas, str(image_path))
                
                # Save config
                self.save_template_config(config)
            
            logger.info("VIA export processing completed successfully")
            
        except Exception as e:
            logger.error(f"VIA export processing failed: {e}")
            raise
    
    def validate_coordinates(self, config_path: str) -> bool:
        """
        Validate coordinate mapping configuration.
        
        Args:
            config_path: Path to coordinate config file
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            required_fields = ['template_name', 'image_path', 'design_areas', 'printify_coordinates']
            
            for field in required_fields:
                if field not in config:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate Printify coordinates are in valid range
            for label, coords in config['printify_coordinates'].items():
                if not (0.0 <= coords['x'] <= 1.0 and 0.0 <= coords['y'] <= 1.0):
                    logger.error(f"Invalid Printify coordinates for {label}: {coords}")
                    return False
            
            logger.info(f"Configuration validation passed: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False


def main():
    """CLI interface for coordinate mapping."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SEA-E Coordinate Mapper")
    parser.add_argument("--via-json", required=True, help="Path to VIA JSON export file")
    parser.add_argument("--templates-dir", help="Directory containing template images")
    parser.add_argument("--config-dir", help="Directory to save coordinate configs")
    parser.add_argument("--validate", help="Validate existing config file")
    
    args = parser.parse_args()
    
    # Initialize mapper
    mapper = CoordinateMapper(
        templates_dir=args.templates_dir or "assets/mockups",
        config_dir=args.config_dir or "config/coordinate_maps"
    )
    
    if args.validate:
        # Validate existing config
        is_valid = mapper.validate_coordinates(args.validate)
        print(f"Configuration {'valid' if is_valid else 'invalid'}: {args.validate}")
    else:
        # Process VIA export
        mapper.process_via_export(args.via_json, args.templates_dir)
        print("Coordinate mapping completed successfully!")


if __name__ == "__main__":
    main()
