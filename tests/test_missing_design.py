#!/usr/bin/env python3
"""
Test Missing Design File Handling
=================================

Tests that both CustomMockupGenerator and PerspectiveMockupGenerator
properly handle missing design files with appropriate error handling.
"""

import sys
import pytest
from pathlib import Path
import tempfile
import os

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.custom_mockup_generator import CustomMockupGenerator
from modules.perspective_mockup_generator import PerspectiveMockupGenerator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestMissingDesignFiles:
    """Test missing design file handling for both mockup generators."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.missing_design_path = os.path.join(self.temp_dir, "nonexistent_design.png")
        
        # Ensure the file doesn't exist
        if os.path.exists(self.missing_design_path):
            os.unlink(self.missing_design_path)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_custom_mockup_generator_missing_design(self):
        """Test CustomMockupGenerator handles missing design files."""
        generator = CustomMockupGenerator(output_dir=self.temp_dir)
        
        # Attempt to generate mockup with missing design file
        result = generator.generate_mockup(
            product_type="tshirts",
            design_path=self.missing_design_path,
            template_name="1.png"  # Assuming template exists
        )
        
        # Should fail gracefully
        assert not result['success'], "Should fail with missing design file"
        assert 'error' in result, "Should include error message"
        
        # Error should mention missing file
        error_msg = result['error'].lower()
        assert any(keyword in error_msg for keyword in ['not found', 'missing', 'exist']), \
            f"Error message should mention missing file: {result['error']}"
    
    def test_perspective_mockup_generator_missing_design(self):
        """Test PerspectiveMockupGenerator handles missing design files."""
        generator = PerspectiveMockupGenerator(output_dir=self.temp_dir)
        
        # Get available templates
        templates = generator.list_available_templates()
        if not templates:
            pytest.skip("No poster templates available for testing")
        
        template = templates[0]
        
        # Attempt to generate mockup with missing design file
        result = generator.generate_perspective_mockup(
            design_path=self.missing_design_path,
            template_name=template
        )
        
        # Should fail gracefully with FileNotFoundError
        assert not result['success'], "Should fail with missing design file"
        assert 'error' in result, "Should include error message"
        
        # Error should mention missing file or be FileNotFoundError
        error_msg = result['error']
        assert "Design file missing; aborting." in error_msg or \
               "not found" in error_msg.lower() or \
               "missing" in error_msg.lower(), \
            f"Error message should mention missing design file: {error_msg}"
    
    def test_perspective_mockup_early_exit_behavior(self):
        """Test that PerspectiveMockupGenerator exits early with missing design."""
        generator = PerspectiveMockupGenerator(output_dir=self.temp_dir)
        
        templates = generator.list_available_templates()
        if not templates:
            pytest.skip("No poster templates available for testing")
        
        template = templates[0]
        
        # Test that the generator fails fast without creating partial files
        initial_files = set(os.listdir(self.temp_dir))
        
        result = generator.generate_perspective_mockup(
            design_path=self.missing_design_path,
            template_name=template
        )
        
        final_files = set(os.listdir(self.temp_dir))
        
        # Should not create any new files
        assert initial_files == final_files, "Should not create files when design is missing"
        assert not result['success'], "Should fail immediately"
    
    def test_missing_design_with_custom_corners(self):
        """Test missing design handling with custom corner specification."""
        generator = PerspectiveMockupGenerator(output_dir=self.temp_dir)
        
        templates = generator.list_available_templates()
        if not templates:
            pytest.skip("No poster templates available for testing")
        
        template = templates[0]
        custom_corners = [(100, 100), (500, 100), (500, 400), (100, 400)]
        
        # Should still fail even with valid custom corners
        result = generator.generate_perspective_mockup(
            design_path=self.missing_design_path,
            template_name=template,
            custom_corners=custom_corners
        )
        
        assert not result['success'], "Should fail even with custom corners"
        assert "Design file missing; aborting." in result.get('error', ''), \
            "Should have specific missing design error message"
    
    def test_missing_design_error_propagation(self):
        """Test that missing design errors propagate correctly through the system."""
        generator = PerspectiveMockupGenerator(output_dir=self.temp_dir)
        
        templates = generator.list_available_templates()
        if not templates:
            pytest.skip("No poster templates available for testing")
        
        # Test with completely invalid path
        invalid_paths = [
            "/nonexistent/path/design.png",
            "definitely_not_a_file.png",
            "",  # Empty path
            None  # None path (should be handled gracefully)
        ]
        
        for invalid_path in invalid_paths:
            if invalid_path is None:
                continue  # Skip None test as it would cause different error
                
            result = generator.generate_perspective_mockup(
                design_path=invalid_path,
                template_name=templates[0]
            )
            
            assert not result['success'], f"Should fail with invalid path: {invalid_path}"
            assert 'error' in result, f"Should include error for path: {invalid_path}"


class TestDesignFileValidation:
    """Test design file validation and error handling."""
    
    def test_empty_design_file(self):
        """Test handling of empty design files."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            empty_file_path = f.name
            # File exists but is empty
        
        try:
            generator = PerspectiveMockupGenerator()
            templates = generator.list_available_templates()
            
            if templates:
                result = generator.generate_perspective_mockup(
                    design_path=empty_file_path,
                    template_name=templates[0]
                )
                
                # Should fail due to invalid image file
                assert not result['success'], "Should fail with empty/invalid image file"
        
        finally:
            os.unlink(empty_file_path)
    
    def test_non_image_file_as_design(self):
        """Test handling of non-image files as design input."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"This is not an image file")
            text_file_path = f.name
        
        try:
            generator = PerspectiveMockupGenerator()
            templates = generator.list_available_templates()
            
            if templates:
                result = generator.generate_perspective_mockup(
                    design_path=text_file_path,
                    template_name=templates[0]
                )
                
                # Should fail due to invalid image format
                assert not result['success'], "Should fail with non-image file"
        
        finally:
            os.unlink(text_file_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
