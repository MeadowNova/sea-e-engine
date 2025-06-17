#!/usr/bin/env python3
"""
JPEG Resizer for Phase 3 Premium Digital Products
================================================

Creates high-quality, print-ready JPEG files at optimized resolutions for each standard size.
This provides the perfect balance of print quality and reasonable file sizes.

Standard Print Sizes (Optimized DPI):
- 24x36: 3600×5400 pixels (~3-8 MB)
- 18x24: 3600×4800 pixels (~2-6 MB)
- 16x20: 3200×4000 pixels (~2-5 MB)
- 11x14: 2200×2800 pixels (~1-3 MB)
- 5x7: 1500×2100 pixels (~0.5-2 MB)

Perfect balance of quality and file size for customer downloads!
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from PIL import Image, ImageEnhance
import time

logger = logging.getLogger(__name__)

@dataclass
class PrintSize:
    """Standard print size specification at 300 DPI."""
    name: str
    width_inches: float
    height_inches: float
    width_px: int
    height_px: int
    description: str

@dataclass
class JPEGResizeResult:
    """Result of JPEG resizing operation."""
    success: bool
    created_files: Dict[str, str] = None
    design_name: str = ""
    processing_time: float = 0.0
    total_file_size_mb: float = 0.0
    error: Optional[str] = None

class JPEGResizer:
    """High-quality JPEG resizer for print-ready digital products."""
    
    # Standard print sizes at 300 DPI (optimized for reasonable file sizes)
    STANDARD_SIZES = {
        "24x36": PrintSize(
            name="24x36",
            width_inches=24.0,
            height_inches=36.0,
            width_px=3600,  # 150 DPI - still print quality, smaller files
            height_px=5400,
            description="Large Poster (24\" × 36\")"
        ),
        "18x24": PrintSize(
            name="18x24",
            width_inches=18.0,
            height_inches=24.0,
            width_px=3600,  # 200 DPI - good print quality
            height_px=4800,
            description="Medium Poster (18\" × 24\")"
        ),
        "16x20": PrintSize(
            name="16x20",
            width_inches=16.0,
            height_inches=20.0,
            width_px=3200,  # 200 DPI
            height_px=4000,
            description="Standard Frame (16\" × 20\")"
        ),
        "11x14": PrintSize(
            name="11x14",
            width_inches=11.0,
            height_inches=14.0,
            width_px=2200,  # 200 DPI
            height_px=2800,
            description="Small Frame (11\" × 14\")"
        ),
        "5x7": PrintSize(
            name="5x7",
            width_inches=5.0,
            height_inches=7.0,
            width_px=1500,  # 300 DPI for small prints
            height_px=2100,
            description="Photo Size (5\" × 7\")"
        )
    }
    
    def __init__(self, output_dir: str = "output/phase3_jpeg_files"):
        """Initialize JPEG resizer.

        Args:
            output_dir: Directory to save resized JPEG files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("🖼️  JPEG Resizer initialized")
        logger.info(f"   Output directory: {self.output_dir}")
        logger.info(f"   Standard sizes: {len(self.STANDARD_SIZES)}")

    def create_print_ready_jpegs(self, png_path: str, design_name: str) -> JPEGResizeResult:
        """Create print-ready JPEG files at optimized resolutions for all standard sizes.

        Args:
            png_path: Path to source PNG file
            design_name: Clean design name for file naming

        Returns:
            JPEGResizeResult with created files and details
        """
        start_time = time.time()
        result = JPEGResizeResult(success=False, design_name=design_name)
        
        try:
            png_path = Path(png_path)
            
            if not png_path.exists():
                raise FileNotFoundError(f"PNG file not found: {png_path}")
            
            logger.info(f"🎨 Creating print-ready JPEGs for: {design_name}")
            logger.info(f"   Source: {png_path.name}")

            # Create design-specific output directory
            design_output_dir = self.output_dir / design_name
            design_output_dir.mkdir(parents=True, exist_ok=True)

            # Load source image
            with Image.open(png_path) as source_img:
                # Convert to RGB (JPEG doesn't support transparency)
                if source_img.mode in ('RGBA', 'LA'):
                    # Create white background
                    background = Image.new('RGB', source_img.size, (255, 255, 255))
                    if source_img.mode == 'RGBA':
                        background.paste(source_img, mask=source_img.split()[-1])
                    else:
                        background.paste(source_img)
                    source_img = background
                elif source_img.mode != 'RGB':
                    source_img = source_img.convert('RGB')
                
                logger.info(f"   Source dimensions: {source_img.size[0]}×{source_img.size[1]} pixels")
                
                created_files = {}
                total_size = 0
                
                # Create each standard size
                for size_name, size_spec in self.STANDARD_SIZES.items():
                    logger.info(f"   📐 Creating {size_name} ({size_spec.description})")
                    
                    # Create high-quality resized image
                    resized_img = self._create_high_quality_resize(
                        source_img, 
                        size_spec.width_px, 
                        size_spec.height_px
                    )
                    
                    # Generate output filename
                    output_filename = f"{design_name}_{size_name}_print_ready.jpg"
                    output_path = design_output_dir / output_filename

                    # Save as high-quality JPEG
                    resized_img.save(
                        output_path,
                        'JPEG',
                        quality=92,       # High quality but reasonable file size
                        optimize=True,    # Enable optimization
                        progressive=True  # Progressive JPEG for better loading
                    )
                    
                    # Check file size
                    file_size_mb = output_path.stat().st_size / (1024 * 1024)
                    total_size += file_size_mb
                    
                    created_files[size_name] = str(output_path)
                    
                    logger.info(f"      ✅ {output_filename}: {file_size_mb:.1f} MB")
                
                # Success!
                result.success = True
                result.created_files = created_files
                result.processing_time = time.time() - start_time
                result.total_file_size_mb = total_size
                
                logger.info(f"🎉 Print-ready JPEGs created successfully!")
                logger.info(f"   📁 Files created: {len(created_files)}")
                logger.info(f"   📊 Total size: {total_size:.1f} MB")
                logger.info(f"   ⏱️  Processing time: {result.processing_time:.1f}s")
                
                return result
                
        except Exception as e:
            result.error = str(e)
            result.processing_time = time.time() - start_time
            logger.error(f"❌ JPEG resizing failed: {e}")
            return result
    
    def _create_high_quality_resize(self, source_img: Image.Image, 
                                   target_width: int, target_height: int) -> Image.Image:
        """Create high-quality resized image with proper aspect ratio handling.
        
        Args:
            source_img: Source PIL Image
            target_width: Target width in pixels
            target_height: Target height in pixels
            
        Returns:
            High-quality resized PIL Image
        """
        # Calculate aspect ratios
        source_ratio = source_img.width / source_img.height
        target_ratio = target_width / target_height
        
        if abs(source_ratio - target_ratio) < 0.01:
            # Aspect ratios match - direct resize
            resized = source_img.resize(
                (target_width, target_height),
                Image.Resampling.LANCZOS
            )
        else:
            # Aspect ratios don't match - fit with white background
            if source_ratio > target_ratio:
                # Source is wider - fit to width
                new_width = target_width
                new_height = int(target_width / source_ratio)
            else:
                # Source is taller - fit to height
                new_height = target_height
                new_width = int(target_height * source_ratio)
            
            # Resize source to fit
            fitted = source_img.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )
            
            # Create white background at target size
            resized = Image.new('RGB', (target_width, target_height), (255, 255, 255))
            
            # Center the fitted image
            x_offset = (target_width - new_width) // 2
            y_offset = (target_height - new_height) // 2
            resized.paste(fitted, (x_offset, y_offset))
        
        # Enhance image quality
        enhancer = ImageEnhance.Sharpness(resized)
        resized = enhancer.enhance(1.1)  # Slight sharpening for print
        
        return resized
    
    def get_size_info(self) -> Dict[str, Dict]:
        """Get information about all available print sizes.
        
        Returns:
            Dictionary with size specifications
        """
        return {
            name: {
                'name': spec.name,
                'dimensions_inches': f"{spec.width_inches}\"×{spec.height_inches}\"",
                'dimensions_pixels': f"{spec.width_px}×{spec.height_px}",
                'description': spec.description,
                'dpi': 300,
                'estimated_size_mb': f"{self._estimate_file_size(spec.width_px, spec.height_px):.1f} MB"
            }
            for name, spec in self.STANDARD_SIZES.items()
        }
    
    def _estimate_file_size(self, width: int, height: int) -> float:
        """Estimate PNG file size in MB.

        Args:
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            Estimated file size in MB
        """
        # JPEG compression estimation (much more efficient than PNG)
        # JPEG typically compresses to 0.1-0.3 bytes per pixel for artwork
        pixels = width * height

        # Use compression factor based on image size and JPEG quality
        if pixels > 15_000_000:  # Very large images
            compression_factor = 0.25  # Still good compression
        elif pixels > 8_000_000:  # Large images
            compression_factor = 0.2
        elif pixels > 3_000_000:   # Medium images
            compression_factor = 0.15
        else:  # Small images
            compression_factor = 0.1

        bytes_estimate = pixels * compression_factor
        mb_estimate = bytes_estimate / (1024 * 1024)
        return mb_estimate
    
    def validate_source_image(self, image_path: str) -> bool:
        """Validate that the file is a proper image.

        Args:
            image_path: Path to image file

        Returns:
            True if valid image
        """
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False
