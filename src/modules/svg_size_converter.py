#!/usr/bin/env python3
"""
SVG Size Converter for Phase 3 Premium Digital Products
======================================================

Converts SVG files to multiple standard print sizes for customer delivery.
Creates 5 different sizes: 24x36", 18x24", 16x20", 11x14", 5x7" at 300 DPI.

Features:
- Maintains aspect ratio and quality
- Generates PNG files at 300 DPI for printing
- Preserves original SVG for infinite scalability
- Optimized file sizes for customer download
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import tempfile
import subprocess
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

class SVGSizeConverter:
    """Converts SVG files to multiple standard print sizes."""
    
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
    
    def __init__(self, output_dir: str = "output/svg_conversions"):
        """Initialize the SVG size converter.
        
        Args:
            output_dir: Directory to save converted files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check for required tools
        self._check_dependencies()
        
        logger.info(f"SVG Size Converter initialized")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Available sizes: {list(self.STANDARD_SIZES.keys())}")
    
    def _check_dependencies(self):
        """Check for required system dependencies."""
        try:
            # Check for Inkscape (preferred for SVG conversion)
            result = subprocess.run(['inkscape', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.converter = 'inkscape'
                logger.info("Using Inkscape for SVG conversion")
                return
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        try:
            # Check for ImageMagick as fallback
            result = subprocess.run(['convert', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.converter = 'imagemagick'
                logger.info("Using ImageMagick for SVG conversion")
                return
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check for cairosvg (Python library)
        try:
            import cairosvg
            self.converter = 'cairosvg'
            logger.info("Using cairosvg for SVG conversion")
            return
        except ImportError:
            pass
        
        raise RuntimeError(
            "No SVG converter found. Please install one of:\n"
            "- Inkscape: sudo apt install inkscape\n"
            "- ImageMagick: sudo apt install imagemagick\n"
            "- cairosvg: pip install cairosvg"
        )
    
    def convert_svg_to_sizes(self, svg_path: str, design_name: str) -> Dict[str, str]:
        """Convert SVG/PNG to all standard sizes.

        Phase 3 Enhancement: Handles both SVG and PNG files (some .svg files are actually PNG)

        Args:
            svg_path: Path to source SVG/PNG file
            design_name: Name for the design (used in output filenames)

        Returns:
            Dictionary mapping size names to output file paths
        """
        source_path = Path(svg_path)

        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Detect actual file type
        import subprocess
        try:
            result = subprocess.run(['file', str(source_path)],
                                  capture_output=True, text=True, timeout=10)
            file_info = result.stdout.lower()

            if 'png' in file_info:
                actual_format = 'PNG'
                logger.info(f"Detected PNG file (despite .svg extension): {source_path.name}")
            elif 'svg' in file_info:
                actual_format = 'SVG'
                logger.info(f"Detected true SVG file: {source_path.name}")
            else:
                actual_format = 'UNKNOWN'
                logger.warning(f"Unknown file format: {source_path.name}")
        except:
            # Fallback to extension-based detection
            actual_format = 'SVG' if source_path.suffix.lower() == '.svg' else 'PNG'

        logger.info(f"Converting {actual_format} to 5 standard sizes: {design_name}")
        logger.info(f"Source: {source_path}")

        # Create output directory for this design
        design_output_dir = self.output_dir / design_name
        design_output_dir.mkdir(exist_ok=True)

        converted_files = {}

        # Convert to each standard size
        for size_name, size_spec in self.STANDARD_SIZES.items():
            try:
                output_filename = f"{design_name}_{size_name}.png"
                output_path = design_output_dir / output_filename

                logger.info(f"Converting to {size_spec.description}...")

                if actual_format == 'PNG':
                    # Use PIL for PNG resizing (more reliable)
                    success = self._convert_png_with_pil(
                        source_path=source_path,
                        output_path=output_path,
                        width_px=size_spec.width_px,
                        height_px=size_spec.height_px
                    )
                else:
                    # Use SVG converters for true SVG files
                    success = self._convert_single_size(
                        svg_path=source_path,
                        output_path=output_path,
                        width_px=size_spec.width_px,
                        height_px=size_spec.height_px
                    )

                if success:
                    converted_files[size_name] = str(output_path)
                    logger.info(f"✅ Created: {output_filename}")
                else:
                    logger.error(f"❌ Failed to create: {output_filename}")

            except Exception as e:
                logger.error(f"Error converting to {size_name}: {e}")
                continue

        # Copy the original file with appropriate extension
        if actual_format == 'PNG':
            original_file_path = design_output_dir / f"{design_name}_original.png"
        else:
            original_file_path = design_output_dir / f"{design_name}_original.svg"

        try:
            import shutil
            shutil.copy2(source_path, original_file_path)
            converted_files['original'] = str(original_file_path)
            logger.info(f"✅ Copied original file: {original_file_path.name}")
        except Exception as e:
            logger.error(f"Failed to copy original file: {e}")

        logger.info(f"🎉 Conversion complete: {len(converted_files)} files created")
        return converted_files
    
    def _convert_single_size(self, svg_path: Path, output_path: Path, 
                           width_px: int, height_px: int) -> bool:
        """Convert SVG to a single size using available converter.
        
        Args:
            svg_path: Source SVG file
            output_path: Output PNG file path
            width_px: Target width in pixels
            height_px: Target height in pixels
            
        Returns:
            True if conversion successful
        """
        try:
            if self.converter == 'inkscape':
                return self._convert_with_inkscape(svg_path, output_path, width_px, height_px)
            elif self.converter == 'imagemagick':
                return self._convert_with_imagemagick(svg_path, output_path, width_px, height_px)
            elif self.converter == 'cairosvg':
                return self._convert_with_cairosvg(svg_path, output_path, width_px, height_px)
            else:
                logger.error(f"Unknown converter: {self.converter}")
                return False
                
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return False
    
    def _convert_with_inkscape(self, svg_path: Path, output_path: Path, 
                             width_px: int, height_px: int) -> bool:
        """Convert using Inkscape."""
        cmd = [
            'inkscape',
            str(svg_path),
            '--export-type=png',
            f'--export-filename={output_path}',
            f'--export-width={width_px}',
            f'--export-height={height_px}',
            '--export-dpi=300'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    
    def _convert_with_imagemagick(self, svg_path: Path, output_path: Path, 
                                width_px: int, height_px: int) -> bool:
        """Convert using ImageMagick."""
        cmd = [
            'convert',
            '-density', '300',
            str(svg_path),
            '-resize', f'{width_px}x{height_px}',
            '-quality', '95',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    
    def _convert_with_cairosvg(self, svg_path: Path, output_path: Path, 
                             width_px: int, height_px: int) -> bool:
        """Convert using cairosvg."""
        try:
            import cairosvg
            
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(output_path),
                output_width=width_px,
                output_height=height_px,
                dpi=300
            )
            return True
            
        except Exception as e:
            logger.error(f"cairosvg conversion failed: {e}")
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
