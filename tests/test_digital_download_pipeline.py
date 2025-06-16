#!/usr/bin/env python3
"""
Test Digital Download Pipeline
=============================

Comprehensive tests for the Phase 2 digital download pipeline.
"""

import os
import sys
import pytest
import tempfile
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.digital_download_pipeline import DigitalDownloadPipeline, DesignFile, PipelineResult

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDigitalDownloadPipeline:
    """Test suite for Digital Download Pipeline."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test design files
        self.create_test_files()
        
    def create_test_files(self):
        """Create test design files."""
        test_files = [
            "design3_purrista_barista__w=2000__h=2000.png",
            "floral_boho_cat__w=1500__h=1500.jpg",
            "space_coffee_art.png"  # Simple format
        ]
        
        for filename in test_files:
            filepath = self.temp_path / filename
            filepath.write_bytes(b"fake_image_data")
    
    def test_discover_design_files(self):
        """Test design file discovery and parsing."""
        pipeline = DigitalDownloadPipeline(mockups_directory=str(self.temp_path))
        
        design_files = pipeline.discover_design_files()
        
        assert len(design_files) == 3
        
        # Check parsed design file
        purrista_file = next(f for f in design_files if f.design_slug == "design3_purrista_barista")
        assert purrista_file.width == 2000
        assert purrista_file.height == 2000
        assert purrista_file.filename == "design3_purrista_barista__w=2000__h=2000.png"
        
        # Check simple format file
        simple_file = next(f for f in design_files if f.design_slug == "space_coffee_art")
        assert simple_file.width == 2000  # Default
        assert simple_file.height == 2000  # Default
    
    @patch('modules.digital_download_pipeline.GoogleSheetsClient')
    @patch('modules.digital_download_pipeline.EtsyClient')
    @patch('modules.digital_download_pipeline.OpenAISEOOptimizer')
    def test_process_single_design_validate_mode(self, mock_seo, mock_etsy, mock_sheets):
        """Test processing a single design in validate mode."""
        # Mock the clients
        mock_sheets_instance = Mock()
        mock_sheets_instance.upload_image_to_drive.return_value = ("file123", "https://drive.google.com/file/d/file123/view")
        mock_sheets.return_value = mock_sheets_instance
        
        mock_seo_instance = Mock()
        mock_seo_instance.generate_seo_content.return_value = {
            'title': 'Purrista Barista Cat Art Print | Coffee Lover Gift | Digital Download',
            'tags': ['cat art', 'coffee art', 'digital print', 'wall art', 'gift'],
            'description': 'Adorable cat barista art perfect for coffee lovers and cat enthusiasts.'
        }
        mock_seo.return_value = mock_seo_instance
        
        mock_etsy_instance = Mock()
        mock_etsy.return_value = mock_etsy_instance
        
        # Create pipeline in validate mode
        pipeline = DigitalDownloadPipeline(
            mockups_directory=str(self.temp_path),
            mode="validate"
        )
        
        # Create test design file
        design_file = DesignFile(
            filepath=self.temp_path / "test.png",
            design_slug="test_design",
            width=2000,
            height=2000,
            filename="test.png"
        )
        
        # Process the design
        result = pipeline.process_single_design(design_file)
        
        # Verify result
        assert result.success is True
        assert result.google_drive_url == "https://drive.google.com/file/d/file123/view"
        assert result.seo_content is not None
        assert result.etsy_listing_id == "draft_preview_only"  # Validate mode
        
        # Verify client calls
        mock_sheets_instance.upload_image_to_drive.assert_called_once()
        mock_seo_instance.generate_seo_content.assert_called_once_with("test_design")
    
    @patch('modules.digital_download_pipeline.GoogleSheetsClient')
    @patch('modules.digital_download_pipeline.EtsyClient')
    @patch('modules.digital_download_pipeline.OpenAISEOOptimizer')
    def test_process_single_design_batch_mode(self, mock_seo, mock_etsy, mock_sheets):
        """Test processing a single design in batch mode."""
        # Mock the clients
        mock_sheets_instance = Mock()
        mock_sheets_instance.upload_image_to_drive.return_value = ("file123", "https://drive.google.com/file/d/file123/view")
        mock_sheets.return_value = mock_sheets_instance
        
        mock_seo_instance = Mock()
        mock_seo_instance.generate_seo_content.return_value = {
            'title': 'Test Art Print',
            'tags': ['art', 'print'],
            'description': 'Test description'
        }
        mock_seo.return_value = mock_seo_instance
        
        mock_etsy_instance = Mock()
        mock_etsy_instance.create_listing.return_value = "listing_123"
        mock_etsy.return_value = mock_etsy_instance
        
        # Create pipeline in batch mode
        pipeline = DigitalDownloadPipeline(
            mockups_directory=str(self.temp_path),
            mode="batch"
        )
        
        # Create test design file
        design_file = DesignFile(
            filepath=self.temp_path / "test.png",
            design_slug="test_design",
            width=2000,
            height=2000,
            filename="test.png"
        )
        
        # Process the design
        result = pipeline.process_single_design(design_file)
        
        # Verify result
        assert result.success is True
        assert result.etsy_listing_id == "listing_123"  # Actual listing created
        
        # Verify Etsy listing creation was called
        mock_etsy_instance.create_listing.assert_called_once()
    
    def test_prepare_listing_data(self):
        """Test listing data preparation."""
        pipeline = DigitalDownloadPipeline(mockups_directory=str(self.temp_path))
        
        design_file = DesignFile(
            filepath=self.temp_path / "test.png",
            design_slug="test_design",
            width=2000,
            height=2000,
            filename="test.png"
        )
        
        seo_content = {
            'title': 'Test Art Print',
            'tags': ['art', 'print', 'digital'],
            'description': 'Beautiful test art print'
        }
        
        listing_data = pipeline._prepare_listing_data(
            design_file, seo_content, "https://example.com/image.png"
        )
        
        assert listing_data['title'] == 'Test Art Print'
        assert listing_data['tags'] == ['art', 'print', 'digital']
        assert listing_data['description'] == 'Beautiful test art print'
        assert listing_data['type'] == 'download'
        assert listing_data['price'] == 4.99
        assert listing_data['images'] == ["https://example.com/image.png"]
    
    @patch('modules.digital_download_pipeline.GoogleSheetsClient')
    @patch('modules.digital_download_pipeline.EtsyClient')
    @patch('modules.digital_download_pipeline.OpenAISEOOptimizer')
    def test_run_pipeline_validate_mode(self, mock_seo, mock_etsy, mock_sheets):
        """Test running the complete pipeline in validate mode."""
        # Mock successful processing
        mock_sheets_instance = Mock()
        mock_sheets_instance.upload_image_to_drive.return_value = ("file123", "https://drive.google.com/file/d/file123/view")
        mock_sheets.return_value = mock_sheets_instance
        
        mock_seo_instance = Mock()
        mock_seo_instance.generate_seo_content.return_value = {
            'title': 'Test Art Print',
            'tags': ['art'],
            'description': 'Test'
        }
        mock_seo.return_value = mock_seo_instance
        
        mock_etsy.return_value = Mock()
        
        # Create pipeline
        pipeline = DigitalDownloadPipeline(
            mockups_directory=str(self.temp_path),
            mode="validate"
        )
        
        # Run pipeline
        summary = pipeline.run_pipeline()
        
        # Verify summary
        assert summary['success'] is True
        assert summary['mode'] == 'validate'
        assert summary['processed_count'] == 1  # Only first file in validate mode
        assert summary['successful_count'] == 1
        assert summary['failed_count'] == 0
        assert len(summary['results']) == 1
    
    def test_generate_report(self):
        """Test report generation."""
        pipeline = DigitalDownloadPipeline(mockups_directory=str(self.temp_path))
        
        # Create mock summary
        design_file = DesignFile(
            filepath=self.temp_path / "test.png",
            design_slug="test_design",
            width=2000,
            height=2000,
            filename="test.png"
        )
        
        result = PipelineResult(
            design_file=design_file,
            success=True,
            google_drive_url="https://drive.google.com/test",
            etsy_listing_id="listing_123",
            processing_time=1.5
        )
        
        summary = {
            'success': True,
            'mode': 'validate',
            'total_files_found': 3,
            'processed_count': 1,
            'successful_count': 1,
            'failed_count': 0,
            'total_time': 5.2,
            'results': [result]
        }
        
        report = pipeline.generate_report(summary)
        
        assert "DIGITAL DOWNLOAD PIPELINE REPORT" in report
        assert "✅ Status: SUCCESS" in report
        assert "📊 Mode: VALIDATE" in report
        assert "⏱️  Total Time: 5.20 seconds" in report
        assert "test_design" in report

def test_environment_validation():
    """Test environment variable validation."""
    # This would be in the main CLI module
    required_vars = ['OPENAI_API_KEY', 'ETSY_API_KEY', 'ETSY_REFRESH_TOKEN', 'ETSY_SHOP_ID']
    
    # Check if any required vars are missing
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"Missing environment variables for full testing: {missing_vars}")
    else:
        logger.info("All required environment variables are set")

if __name__ == "__main__":
    # Run basic tests
    test_suite = TestDigitalDownloadPipeline()
    test_suite.setup_method()
    
    print("🧪 Running Digital Download Pipeline Tests")
    print("=" * 50)
    
    try:
        test_suite.test_discover_design_files()
        print("✅ Design file discovery test passed")
        
        test_suite.test_prepare_listing_data()
        print("✅ Listing data preparation test passed")
        
        test_suite.test_generate_report()
        print("✅ Report generation test passed")
        
        test_environment_validation()
        print("✅ Environment validation test passed")
        
        print("\n🎉 All basic tests passed!")
        print("Run with pytest for complete test suite including mocked API calls.")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)
