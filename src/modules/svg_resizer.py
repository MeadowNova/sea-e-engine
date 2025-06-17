#!/usr/bin/env python3
"""
SVG Resizer for Phase 3 Premium Digital Products
===============================================

Creates multiple sized SVG files from a source SVG.
Maintains vector format for infinite scalability while providing
standard print sizes: 24x36", 18x24", 16x20", 11x14", 5x7".

Features:
- Creates resized SVG files (not PNG)
- Maintains vector scalability
- Small file sizes for customer download
- Standard print dimensions
"""

import os
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SizeSpec:
    """Specification for a print size."""
    name: str
    width_inches: float
    height_inches: float
    width_px: int
    height_px: int
    description: str

class SVGResizer:
    """Creates multiple sized SVG files from source SVG."""
    
    # Standard print sizes at 300 DPI
    STANDARD_SIZES = {
        "24x36": SizeSpec(
            name="24x36",
            width_inches=24.0,
            height_inches=36.0,
            width_px=7200,
            height_px=10800,
            description="Large Poster (24x36 inches)"
        ),
        "18x24": SizeSpec(
            name="18x24", 
            width_inches=18.0,
            height_inches=24.0,
            width_px=5400,
            height_px=7200,
            description="Medium Poster (18x24 inches)"
        ),
        "16x20": SizeSpec(
            name="16x20",
            width_inches=16.0,
            height_inches=20.0,
            width_px=4800,
            height_px=6000,
            description="Standard Frame (16x20 inches)"
        ),
        "11x14": SizeSpec(
            name="11x14",
            width_inches=11.0,
            height_inches=14.0,
            width_px=3300,
            height_px=4200,
            description="Popular Frame (11x14 inches)"
        ),
        "5x7": SizeSpec(
            name="5x7",
            width_inches=5.0,
            height_inches=7.0,
            width_px=1500,
            height_px=2100,
            description="Small Print/Card (5x7 inches)"
        )
    }
    
    def __init__(self, output_dir: str = "output/svg_resized"):
        """Initialize the SVG resizer.
        
        Args:
            output_dir: Directory to save resized SVG files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SVG Resizer initialized")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Available sizes: {list(self.STANDARD_SIZES.keys())}")
    
    def create_sized_svgs(self, svg_path: str, design_name: str) -> Dict[str, str]:
        """Create 5 different sized SVG files from source SVG.
        
        Args:
            svg_path: Path to source SVG file
            design_name: Name for the design (used in output filenames)
            
        Returns:
            Dictionary mapping size names to output file paths
        """
        svg_path = Path(svg_path)
        
        if not svg_path.exists():
            raise FileNotFoundError(f"SVG file not found: {svg_path}")
        
        logger.info(f"Creating 5 sized SVG files: {design_name}")
        logger.info(f"Source: {svg_path}")
        
        # Create output directory for this design
        design_output_dir = self.output_dir / design_name
        design_output_dir.mkdir(exist_ok=True)
        
        created_files = {}
        
        # Create resized SVG for each standard size
        for size_name, size_spec in self.STANDARD_SIZES.items():
            try:
                output_filename = f"{design_name}_{size_name}.svg"
                output_path = design_output_dir / output_filename
                
                logger.info(f"Creating {size_spec.description} SVG...")
                
                success = self._create_resized_svg(
                    source_svg_path=svg_path,
                    output_path=output_path,
                    target_width=size_spec.width_px,
                    target_height=size_spec.height_px,
                    size_name=size_name
                )
                
                if success:
                    created_files[size_name] = str(output_path)
                    file_size = output_path.stat().st_size / 1024  # KB
                    logger.info(f"✅ Created: {output_filename} ({file_size:.1f} KB)")
                else:
                    logger.error(f"❌ Failed to create: {output_filename}")
                    
            except Exception as e:
                logger.error(f"Error creating {size_name} SVG: {e}")
                continue
        
        # Note: Original SVG file not included in customer package
        # Customers get exactly 5 sized files for their needs

        logger.info(f"🎉 SVG resizing complete: {len(created_files)} files created")
        return created_files
    
    def _create_resized_svg(self, source_svg_path: Path, output_path: Path, 
                           target_width: int, target_height: int, size_name: str) -> bool:
        """Create a resized SVG file by modifying the viewBox and dimensions.
        
        Args:
            source_svg_path: Source SVG file
            output_path: Output SVG file path
            target_width: Target width in pixels
            target_height: Target height in pixels
            size_name: Size name for metadata
            
        Returns:
            True if successful
        """
        try:
            # Read the source SVG
            with open(source_svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # Parse the SVG
            # Register SVG namespace to avoid namespace prefixes in output
            ET.register_namespace('', 'http://www.w3.org/2000/svg')
            root = ET.fromstring(svg_content)
            
            # Update width and height attributes
            root.set('width', str(target_width))
            root.set('height', str(target_height))
            
            # Update viewBox if it exists, or create one
            viewbox = root.get('viewBox')
            if viewbox:
                # Parse existing viewBox: "x y width height"
                parts = viewbox.split()
                if len(parts) == 4:
                    # Keep the same aspect ratio but update dimensions
                    x, y = parts[0], parts[1]
                    root.set('viewBox', f"{x} {y} {target_width} {target_height}")
            else:
                # Create a new viewBox
                root.set('viewBox', f"0 0 {target_width} {target_height}")
            
            # Add metadata about the size
            size_spec = self.STANDARD_SIZES[size_name]
            title_elem = root.find('.//{http://www.w3.org/2000/svg}title')
            if title_elem is None:
                title_elem = ET.SubElement(root, 'title')
            title_elem.text = f"{size_spec.description} - {target_width}x{target_height}px"
            
            # Write the modified SVG
            tree = ET.ElementTree(root)
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create resized SVG: {e}")
            return False
    
    def get_size_info(self) -> Dict[str, Dict]:
        """Get information about all available sizes.
        
        Returns:
            Dictionary with size specifications
        """
        return {
            name: {
                'name': spec.name,
                'dimensions_inches': f"{spec.width_inches}x{spec.height_inches}",
                'dimensions_pixels': f"{spec.width_px}x{spec.height_px}",
                'description': spec.description,
                'dpi': 300
            }
            for name, spec in self.STANDARD_SIZES.items()
        }
    
    def validate_svg(self, svg_path: str) -> bool:
        """Validate that the file is a proper SVG.

        Args:
            svg_path: Path to SVG file

        Returns:
            True if valid SVG
        """
        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic validation
            if not content.strip().startswith('<?xml') and not content.strip().startswith('<svg'):
                return False

            # Try to parse as XML
            ET.fromstring(content)

            # Check if it's a PNG-wrapped SVG (not true vector)
            if 'data:image/png;base64' in content:
                logger.warning(f"SVG file contains embedded PNG image - not true vector graphics")
                return False

            return True

        except Exception as e:
            logger.error(f"SVG validation failed: {e}")
            return False

    def is_png_wrapped_svg(self, svg_path: str) -> bool:
        """Check if SVG file contains embedded PNG data.

        Args:
            svg_path: Path to SVG file

        Returns:
            True if SVG contains PNG data
        """
        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return 'data:image/png;base64' in content

        except Exception as e:
            logger.error(f"Error checking SVG content: {e}")
            return False
