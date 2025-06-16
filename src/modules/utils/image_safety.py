#!/usr/bin/env python3
"""
Image Safety Utilities for SEA-E Engine
=======================================

Provides safety checks and validation for generated mockup images,
including blue-grain artifact detection and other quality assurance measures.
"""

import logging
from PIL import Image
from typing import Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


def detect_bluegrain(image: Image.Image, threshold: int = 100) -> bool:
    """
    Detect blue-grain artifacts in generated mockup images.
    
    Blue-grain artifacts appear as spurious blue-tinted noise or texture
    that can contaminate mockups during perspective transformation or compositing.
    
    Args:
        image: PIL Image to analyze
        threshold: Minimum number of blue-grain pixels to trigger detection
        
    Returns:
        True if blue-grain artifacts detected, False otherwise
    """
    try:
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array for efficient processing
        img_array = np.array(image)
        
        # Define blue-grain color range (blue-tinted pixels)
        # These ranges capture the typical blue-grain artifact colors
        blue_grain_ranges = [
            # Light blue grain
            {'r_min': 100, 'r_max': 180, 'g_min': 120, 'g_max': 200, 'b_min': 180, 'b_max': 255},
            # Medium blue grain  
            {'r_min': 80, 'r_max': 150, 'g_min': 100, 'g_max': 180, 'b_min': 160, 'b_max': 240},
            # Dark blue grain
            {'r_min': 60, 'r_max': 120, 'g_min': 80, 'g_max': 140, 'b_min': 140, 'b_max': 200}
        ]
        
        total_blue_grain_pixels = 0
        
        for color_range in blue_grain_ranges:
            # Create mask for pixels in this blue-grain range
            mask = (
                (img_array[:, :, 0] >= color_range['r_min']) & 
                (img_array[:, :, 0] <= color_range['r_max']) &
                (img_array[:, :, 1] >= color_range['g_min']) & 
                (img_array[:, :, 1] <= color_range['g_max']) &
                (img_array[:, :, 2] >= color_range['b_min']) & 
                (img_array[:, :, 2] <= color_range['b_max'])
            )
            
            blue_grain_pixels = np.sum(mask)
            total_blue_grain_pixels += blue_grain_pixels
            
            logger.debug(f"Blue-grain range {color_range}: {blue_grain_pixels} pixels")
        
        logger.debug(f"Total blue-grain pixels detected: {total_blue_grain_pixels}")
        
        # Check if blue-grain pixel count exceeds threshold
        if total_blue_grain_pixels >= threshold:
            logger.warning(f"Blue-grain artifacts detected: {total_blue_grain_pixels} pixels (threshold: {threshold})")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error in blue-grain detection: {e}")
        # Fail safe - assume no blue-grain if detection fails
        return False


def validate_image_quality(image: Image.Image, min_size: Tuple[int, int] = (800, 800)) -> bool:
    """
    Validate overall image quality for mockups.
    
    Args:
        image: PIL Image to validate
        min_size: Minimum required dimensions (width, height)
        
    Returns:
        True if image passes quality checks, False otherwise
    """
    try:
        # Check minimum size
        if image.size[0] < min_size[0] or image.size[1] < min_size[1]:
            logger.warning(f"Image too small: {image.size} < {min_size}")
            return False
        
        # Check for completely transparent images
        if image.mode in ('RGBA', 'LA'):
            # Convert to numpy for alpha channel analysis
            img_array = np.array(image)
            if len(img_array.shape) == 3 and img_array.shape[2] >= 4:
                alpha_channel = img_array[:, :, 3]
                if np.all(alpha_channel == 0):
                    logger.warning("Image is completely transparent")
                    return False
        
        # Check for completely black images
        if image.mode == 'RGB':
            img_array = np.array(image)
            if np.all(img_array == 0):
                logger.warning("Image is completely black")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error in image quality validation: {e}")
        return False


def detect_texture_artifacts(image: Image.Image, threshold: float = 0.1) -> bool:
    """
    Detect unwanted texture artifacts from Image.effect_noise or similar operations.
    
    Args:
        image: PIL Image to analyze
        threshold: Threshold for texture artifact detection (0.0-1.0)
        
    Returns:
        True if texture artifacts detected, False otherwise
    """
    try:
        # Convert to grayscale for texture analysis
        gray_image = image.convert('L')
        img_array = np.array(gray_image)
        
        # Calculate local variance to detect noise patterns
        from scipy import ndimage
        
        # Apply Laplacian filter to detect edges/noise
        laplacian = ndimage.laplace(img_array.astype(float))
        variance = np.var(laplacian)
        
        # Normalize variance by image size
        normalized_variance = variance / (img_array.shape[0] * img_array.shape[1])
        
        logger.debug(f"Texture variance: {normalized_variance:.6f} (threshold: {threshold})")
        
        if normalized_variance > threshold:
            logger.warning(f"Texture artifacts detected: variance {normalized_variance:.6f}")
            return True
        
        return False
        
    except ImportError:
        logger.warning("scipy not available for texture artifact detection")
        return False
    except Exception as e:
        logger.error(f"Error in texture artifact detection: {e}")
        return False


def comprehensive_safety_check(image: Image.Image, 
                             check_bluegrain: bool = True,
                             check_quality: bool = True, 
                             check_texture: bool = True) -> dict:
    """
    Run comprehensive safety checks on a mockup image.
    
    Args:
        image: PIL Image to check
        check_bluegrain: Enable blue-grain detection
        check_quality: Enable quality validation
        check_texture: Enable texture artifact detection
        
    Returns:
        Dictionary with check results and details
    """
    results = {
        'safe': True,
        'issues': [],
        'details': {}
    }
    
    try:
        if check_bluegrain:
            has_bluegrain = detect_bluegrain(image)
            results['details']['bluegrain'] = has_bluegrain
            if has_bluegrain:
                results['safe'] = False
                results['issues'].append('Blue-grain artifacts detected')
        
        if check_quality:
            quality_ok = validate_image_quality(image)
            results['details']['quality'] = quality_ok
            if not quality_ok:
                results['safe'] = False
                results['issues'].append('Image quality validation failed')
        
        if check_texture:
            has_texture_artifacts = detect_texture_artifacts(image)
            results['details']['texture_artifacts'] = has_texture_artifacts
            if has_texture_artifacts:
                results['safe'] = False
                results['issues'].append('Texture artifacts detected')
        
        if results['safe']:
            logger.info("✅ Image passed all safety checks")
        else:
            logger.warning(f"⚠️ Image safety issues: {', '.join(results['issues'])}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in comprehensive safety check: {e}")
        return {
            'safe': False,
            'issues': [f'Safety check error: {e}'],
            'details': {'error': str(e)}
        }
