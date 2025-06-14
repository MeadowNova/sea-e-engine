#!/usr/bin/env python3
"""
Google Sheets Integration Tests for SEA-E Engine
===============================================

Comprehensive tests for Google Sheets mockup upload functionality.
"""

import os
import sys
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from api.google_sheets_client import GoogleSheetsClient, MockupUploadResult
from modules.sheets_mockup_uploader import SheetsMockupUploader, MockupUploadJob
from modules.custom_mockup_generator import CustomMockupGenerator
from api.airtable_client import AirtableClient


class TestGoogleSheetsClient:
    """Test Google Sheets API client functionality."""
    
    @pytest.fixture
    def mock_credentials(self):
        """Mock Google credentials."""
        with patch('api.google_sheets_client.Credentials') as mock_creds:
            yield mock_creds
    
    @pytest.fixture
    def mock_services(self):
        """Mock Google API services."""
        with patch('api.google_sheets_client.gspread') as mock_gspread, \
             patch('api.google_sheets_client.build') as mock_build:
            
            # Mock gspread client
            mock_gc = Mock()
            mock_gspread.authorize.return_value = mock_gc
            
            # Mock Google API services
            mock_sheets = Mock()
            mock_drive = Mock()
            mock_build.side_effect = lambda service, version, credentials: {
                'sheets': mock_sheets,
                'drive': mock_drive
            }[service]
            
            yield {
                'gspread': mock_gspread,
                'gc': mock_gc,
                'sheets': mock_sheets,
                'drive': mock_drive
            }
    
    def test_client_initialization(self, mock_credentials, mock_services):
        """Test Google Sheets client initialization."""
        with patch('pathlib.Path.exists', return_value=True):
            client = GoogleSheetsClient()
            
            assert client.gc is not None
            assert client.sheets_service is not None
            assert client.drive_service is not None
    
    def test_connection_test(self, mock_credentials, mock_services):
        """Test connection validation."""
        with patch('pathlib.Path.exists', return_value=True):
            client = GoogleSheetsClient()
            
            # Mock successful API call
            mock_services['drive'].files().list().execute.return_value = {'files': []}
            
            assert client.test_connection() is True
    
    def test_folder_creation(self, mock_credentials, mock_services):
        """Test folder creation in Google Drive."""
        with patch('pathlib.Path.exists', return_value=True):
            client = GoogleSheetsClient()
            
            # Mock folder creation response
            mock_services['drive'].files().create().execute.return_value = {'id': 'folder123'}
            
            folder_id = client.create_mockup_folder("Test Folder")
            assert folder_id == 'folder123'
    
    def test_image_upload(self, mock_credentials, mock_services):
        """Test image upload to Google Drive."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open_image()):
            
            client = GoogleSheetsClient()
            
            # Mock file upload response
            mock_services['drive'].files().create().execute.return_value = {'id': 'file123'}
            mock_services['drive'].permissions().create().execute.return_value = {}
            
            file_id, url = client.upload_image_to_drive("test.png")
            
            assert file_id == 'file123'
            assert url == "https://drive.google.com/file/d/file123/view"


class TestSheetsMockupUploader:
    """Test the sheets mockup uploader functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        return {
            "upload_settings": {
                "max_file_size_mb": 10,
                "supported_formats": [".png", ".jpg", ".jpeg"]
            },
            "batch_settings": {
                "max_concurrent_uploads": 5,
                "retry_attempts": 3
            },
            "integration_settings": {
                "update_airtable": True,
                "airtable_url_field": "google_sheets_url"
            }
        }
    
    @pytest.fixture
    def mock_uploader(self, mock_config):
        """Create mock uploader with mocked dependencies."""
        with patch('modules.sheets_mockup_uploader.GoogleSheetsClient') as mock_sheets, \
             patch('modules.sheets_mockup_uploader.AirtableClient') as mock_airtable:
            
            uploader = SheetsMockupUploader()
            uploader.config = mock_config
            
            yield uploader
    
    def test_add_upload_job(self, mock_uploader):
        """Test adding upload jobs to queue."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat:
            
            # Mock file size (1MB)
            mock_stat.return_value.st_size = 1024 * 1024
            
            success = mock_uploader.add_upload_job(
                mockup_path="test.png",
                product_name="Test Product",
                variation_info={"color": "black", "size": "M"}
            )
            
            assert success is True
            assert len(mock_uploader.upload_queue) == 1
    
    def test_upload_job_validation(self, mock_uploader):
        """Test upload job validation."""
        # Test non-existent file
        with patch('pathlib.Path.exists', return_value=False):
            success = mock_uploader.add_upload_job(
                mockup_path="nonexistent.png",
                product_name="Test Product"
            )
            assert success is False
        
        # Test unsupported format
        with patch('pathlib.Path.exists', return_value=True):
            success = mock_uploader.add_upload_job(
                mockup_path="test.gif",
                product_name="Test Product"
            )
            assert success is False


class TestCustomMockupGeneratorIntegration:
    """Test integration of Google Sheets upload with mockup generator."""
    
    @pytest.fixture
    def mock_generator(self):
        """Create mock generator with sheets integration."""
        with patch('modules.custom_mockup_generator.SheetsMockupUploader') as mock_uploader:
            generator = CustomMockupGenerator(
                enable_sheets_upload=True
            )
            yield generator
    
    def test_mockup_generation_with_sheets_upload(self, mock_generator):
        """Test mockup generation with Google Sheets upload enabled."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('PIL.Image.open') as mock_image, \
             patch.object(mock_generator, '_load_templates') as mock_templates:
            
            # Mock image and templates
            mock_img = Mock()
            mock_img.size = (2000, 2000)
            mock_image.return_value = mock_img
            
            mock_template = Mock()
            mock_template.name = "test_template"
            mock_template.design_area = (400, 400, 1600, 1600)
            mock_template.opacity = 0.85
            mock_template.blend_mode = "multiply"
            mock_template.load.return_value = mock_img
            
            mock_generator.templates = {'tshirts': [mock_template]}
            
            # Mock sheets uploader
            if mock_generator.sheets_uploader:
                mock_generator.sheets_uploader.add_upload_job.return_value = True
                mock_generator.sheets_uploader.process_upload_queue.return_value = Mock(
                    successful_uploads=1,
                    upload_results=[MockupUploadResult(
                        success=True,
                        shareable_url="https://drive.google.com/file/d/test123/view",
                        file_id="test123"
                    )]
                )
            
            result = mock_generator.generate_mockup(
                product_type="tshirts",
                design_path="test_design.png",
                upload_to_sheets=True,
                variation_info={"color": "black", "product_name": "Test Product"}
            )
            
            assert result['success'] is True
            if mock_generator.enable_sheets_upload:
                assert 'google_sheets_url' in result
                assert result['sheets_upload_status'] == 'success'


def mock_open_image():
    """Mock file opening for image files."""
    mock_file = Mock()
    mock_file.read.return_value = b"fake_image_data"
    return mock_file


class TestEndToEndIntegration:
    """Test complete end-to-end Google Sheets integration."""
    
    def test_complete_workflow(self):
        """Test the complete workflow from mockup generation to Google Sheets."""
        with patch('api.google_sheets_client.Credentials'), \
             patch('api.google_sheets_client.gspread'), \
             patch('api.google_sheets_client.build'), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('PIL.Image.open') as mock_image:
            
            # Mock image
            mock_img = Mock()
            mock_img.size = (2000, 2000)
            mock_img.convert.return_value = mock_img
            mock_img.resize.return_value = mock_img
            mock_img.save = Mock()
            mock_image.return_value = mock_img
            
            # Create temporary test image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            try:
                # Initialize components
                sheets_client = GoogleSheetsClient()
                uploader = SheetsMockupUploader()
                
                # Mock successful upload
                with patch.object(sheets_client, 'upload_mockup_to_sheets') as mock_upload:
                    mock_upload.return_value = MockupUploadResult(
                        success=True,
                        file_id="test123",
                        shareable_url="https://drive.google.com/file/d/test123/view"
                    )
                    
                    # Test upload
                    result = sheets_client.upload_mockup_to_sheets(
                        image_path=tmp_path,
                        product_name="Test Product",
                        variation_info={"color": "black", "size": "M"}
                    )
                    
                    assert result.success is True
                    assert result.shareable_url is not None
                    
            finally:
                # Cleanup
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
