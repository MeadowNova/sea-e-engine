#!/usr/bin/env python3
"""
Test Blue-Grain Detection for Poster Mockups
===========================================

Tests the blue-grain artifact detection system for perspective mockup generation.
Ensures that clean mockups pass detection and contaminated mockups are rejected.
"""

import sys
import pytest
from pathlib import Path
from PIL import Image, ImageDraw
import tempfile
import os

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.perspective_mockup_generator import PerspectiveMockupGenerator
from modules.utils.image_safety import detect_bluegrain
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestBlueGrainDetection:
    """Test blue-grain artifact detection for poster mockups."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = PerspectiveMockupGenerator(output_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_clean_test_design(self) -> str:
        """Create a clean test design without blue-grain artifacts."""
        design = Image.new('RGBA', (800, 1200), (255, 255, 255, 255))
        draw = ImageDraw.Draw(design)
        
        # Draw clean, non-blue content
        draw.rectangle([(50, 50), (750, 1150)], fill=None, outline=(0, 0, 0, 255), width=4)
        draw.ellipse([(200, 200), (600, 600)], fill=(255, 100, 100, 255))  # Red circle
        draw.rectangle([(150, 700), (650, 1000)], fill=(100, 200, 100, 255))  # Green rectangle
        draw.text((400, 1100), "CLEAN DESIGN", fill=(0, 0, 0, 255), anchor="mm")
        
        design_path = os.path.join(self.temp_dir, "clean_test_design.png")
        design.save(design_path)
        return design_path
    
    def create_bluegrain_contaminated_design(self) -> str:
        """Create a design with blue-grain artifacts for testing detection."""
        design = Image.new('RGBA', (800, 1200), (255, 255, 255, 255))
        draw = ImageDraw.Draw(design)
        
        # Draw normal content
        draw.rectangle([(50, 50), (750, 1150)], fill=None, outline=(0, 0, 0, 255), width=4)
        draw.ellipse([(200, 200), (600, 600)], fill=(255, 100, 100, 255))
        
        # Add blue-grain artifacts (simulate contamination)
        for i in range(0, 800, 10):
            for j in range(0, 1200, 10):
                if (i + j) % 30 == 0:  # Scattered blue-grain pattern
                    draw.point((i, j), fill=(120, 150, 200, 255))  # Blue-grain color
                    draw.point((i+1, j), fill=(100, 140, 190, 255))
                    draw.point((i, j+1), fill=(110, 145, 195, 255))
        
        design_path = os.path.join(self.temp_dir, "bluegrain_test_design.png")
        design.save(design_path)
        return design_path
    
    def test_clean_design_passes_detection(self):
        """Test that clean designs pass blue-grain detection."""
        clean_design_path = self.create_clean_test_design()
        clean_image = Image.open(clean_design_path)
        
        # Clean image should NOT trigger blue-grain detection
        has_bluegrain = detect_bluegrain(clean_image)
        assert not has_bluegrain, "Clean design incorrectly flagged as having blue-grain artifacts"
    
    def test_contaminated_design_fails_detection(self):
        """Test that contaminated designs fail blue-grain detection."""
        contaminated_design_path = self.create_bluegrain_contaminated_design()
        contaminated_image = Image.open(contaminated_design_path)
        
        # Contaminated image SHOULD trigger blue-grain detection
        has_bluegrain = detect_bluegrain(contaminated_image)
        assert has_bluegrain, "Contaminated design not detected by blue-grain detection"
    
    def test_perspective_mockup_with_clean_design(self):
        """Test perspective mockup generation with clean design passes."""
        # Skip if no poster templates available
        templates = self.generator.list_available_templates()
        if not templates:
            pytest.skip("No poster templates available for testing")
        
        clean_design_path = self.create_clean_test_design()
        template = templates[0]  # Use first available template
        
        # Generate mockup - should succeed with clean design
        result = self.generator.generate_perspective_mockup(clean_design_path, template)
        
        assert result['success'], f"Clean design mockup generation failed: {result.get('error')}"
        assert 'mockup_path' in result
        assert os.path.exists(result['mockup_path'])
        
        # Verify generated mockup doesn't have blue-grain artifacts
        generated_mockup = Image.open(result['mockup_path'])
        has_bluegrain = detect_bluegrain(generated_mockup)
        assert not has_bluegrain, "Generated mockup contains blue-grain artifacts"
    
    def test_perspective_mockup_rejects_contaminated_result(self):
        """Test that perspective mockup generation rejects contaminated results."""
        # This test verifies the blue-grain protection is working
        # We'll create a clean design but simulate contamination during processing
        
        templates = self.generator.list_available_templates()
        if not templates:
            pytest.skip("No poster templates available for testing")
        
        clean_design_path = self.create_clean_test_design()
        template = templates[0]
        
        # Mock the blue-grain detection to simulate contamination
        original_detect = detect_bluegrain
        
        def mock_detect_bluegrain(image):
            # Simulate contamination detected
            return True
        
        # Temporarily replace detection function
        import modules.utils.image_safety
        modules.utils.image_safety.detect_bluegrain = mock_detect_bluegrain
        
        try:
            # Generate mockup - should fail due to simulated contamination
            result = self.generator.generate_perspective_mockup(clean_design_path, template)
            
            assert not result['success'], "Mockup generation should have failed due to blue-grain detection"
            assert "Blue-grain artefacts detected" in result.get('error', ''), "Expected blue-grain error message"
            
        finally:
            # Restore original detection function
            modules.utils.image_safety.detect_bluegrain = original_detect
    
    def test_bluegrain_detection_threshold(self):
        """Test blue-grain detection with different thresholds."""
        # Create image with minimal blue-grain
        design = Image.new('RGBA', (100, 100), (255, 255, 255, 255))
        draw = ImageDraw.Draw(design)
        
        # Add exactly 50 blue-grain pixels
        for i in range(50):
            x = i % 10
            y = i // 10
            draw.point((x, y), fill=(120, 150, 200, 255))
        
        # Test with high threshold (should pass)
        assert not detect_bluegrain(design, threshold=100), "Should pass with high threshold"
        
        # Test with low threshold (should fail)
        assert detect_bluegrain(design, threshold=25), "Should fail with low threshold"


def test_known_good_cat_poster():
    """Test perspective mockup generation for a known-good cat poster design."""
    # Create a cat-themed poster design
    design = Image.new('RGBA', (600, 900), (240, 240, 240, 255))
    draw = ImageDraw.Draw(design)
    
    # Draw cat poster elements
    draw.rectangle([(30, 30), (570, 870)], fill=None, outline=(0, 0, 0, 255), width=3)
    draw.ellipse([(200, 150), (400, 350)], fill=(255, 165, 0, 255))  # Cat face
    draw.ellipse([(230, 200), (250, 220)], fill=(0, 0, 0, 255))      # Left eye
    draw.ellipse([(350, 200), (370, 220)], fill=(0, 0, 0, 255))      # Right eye
    draw.polygon([(300, 250), (280, 280), (320, 280)], fill=(255, 192, 203, 255))  # Nose
    draw.text((300, 400), "CUTE CAT", fill=(0, 0, 0, 255), anchor="mm")
    draw.text((300, 450), "Limited Edition", fill=(100, 100, 100, 255), anchor="mm")
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        design.save(f.name)
        cat_design_path = f.name
    
    try:
        generator = PerspectiveMockupGenerator()
        templates = generator.list_available_templates()
        
        if templates:
            # Generate mockup with first available template
            result = generator.generate_perspective_mockup(cat_design_path, templates[0])
            
            if result['success']:
                # Verify no blue-grain artifacts
                generated_mockup = Image.open(result['mockup_path'])
                has_bluegrain = detect_bluegrain(generated_mockup)
                assert not has_bluegrain, "Cat poster mockup contains blue-grain artifacts"
                
                # Clean up generated file
                os.unlink(result['mockup_path'])
        
    finally:
        # Clean up test design
        os.unlink(cat_design_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
