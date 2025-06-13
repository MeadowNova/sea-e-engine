
#!/usr/bin/env python3
"""
Unit tests for API clients.
"""

import pytest
import os
import sys
import requests
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from api.etsy import EtsyAPIClient
from api.printify import PrintifyAPIClient
from api.airtable_client import AirtableClient


class TestEtsyAPIClient:
    """Test cases for Etsy API client."""
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for Etsy."""
        env_vars = {
            "ETSY_API_KEY": "test_api_key",
            "ETSY_API_SECRET": "test_api_secret",
            "ETSY_ACCESS_TOKEN": "test_access_token",
            "ETSY_REFRESH_TOKEN": "test_refresh_token",
            "ETSY_SHOP_ID": "test_shop_id"
        }
        
        with patch.dict(os.environ, env_vars):
            yield env_vars
    
    def test_client_initialization_success(self, mock_env_vars):
        """Test successful client initialization."""
        client = EtsyAPIClient()
        
        assert client.api_key == "test_api_key"
        assert client.shop_id == "test_shop_id"
        assert client.base_url == "https://openapi.etsy.com/v3"
    
    def test_client_initialization_missing_vars(self):
        """Test client initialization with missing environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                EtsyAPIClient()
            
            assert "Missing required environment variables" in str(exc_info.value)
    
    def test_get_headers(self, mock_env_vars):
        """Test header generation."""
        client = EtsyAPIClient()
        headers = client.get_headers()
        
        assert "Authorization" in headers
        assert "Bearer test_access_token" in headers["Authorization"]
        assert headers["x-api-key"] == "test_api_key"
        assert headers["Content-Type"] == "application/json"
    
    @patch('api.etsy.requests.post')
    def test_refresh_access_token_success(self, mock_post, mock_env_vars):
        """Test successful token refresh."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response
        
        client = EtsyAPIClient()
        result = client.refresh_access_token()
        
        assert result is True
        assert client.access_token == "new_access_token"
        assert client.refresh_token == "new_refresh_token"
    
    @patch('api.etsy.requests.post')
    def test_refresh_access_token_failure(self, mock_post, mock_env_vars):
        """Test failed token refresh."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid refresh token"
        mock_post.return_value = mock_response
        
        client = EtsyAPIClient()
        result = client.refresh_access_token()
        
        assert result is False
    
    @patch('api.etsy.EtsyAPIClient.make_request')
    def test_test_connection_success(self, mock_make_request, mock_env_vars):
        """Test successful connection test."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "shop_name": "test_shop",
            "title": "Test Shop"
        }
        mock_make_request.return_value = mock_response
        
        client = EtsyAPIClient()
        result = client.test_connection()
        
        assert result is True
    
    @patch('api.etsy.EtsyAPIClient.make_request')
    def test_test_connection_failure(self, mock_make_request, mock_env_vars):
        """Test failed connection test."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_make_request.return_value = mock_response
        
        client = EtsyAPIClient()
        result = client.test_connection()
        
        assert result is False
    
    @patch('api.etsy.EtsyAPIClient.make_request')
    @patch('api.etsy.EtsyAPIClient._upload_listing_images')
    @patch('api.etsy.EtsyAPIClient._activate_listing')
    def test_create_listing_success(self, mock_activate, mock_upload, mock_make_request, mock_env_vars):
        """Test successful listing creation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"listing_id": 12345}
        mock_make_request.return_value = mock_response
        
        client = EtsyAPIClient()
        listing_id = client.create_listing(
            title="Test Product",
            description="Test Description",
            price=19.99,
            tags=["tag1", "tag2"],
            image_files=["image1.png", "image2.png"]
        )
        
        assert listing_id == "12345"
        mock_upload.assert_called_once()
        mock_activate.assert_called_once()


class TestPrintifyAPIClient:
    """Test cases for Printify API client."""
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for Printify."""
        env_vars = {
            "PRINTIFY_API_KEY": "test_api_key",
            "PRINTIFY_SHOP_ID": "test_shop_id"
        }
        
        with patch.dict(os.environ, env_vars):
            yield env_vars
    
    def test_client_initialization_success(self, mock_env_vars):
        """Test successful client initialization."""
        client = PrintifyAPIClient()
        
        assert client.api_key == "test_api_key"
        assert client.shop_id == "test_shop_id"
        assert client.base_url == "https://api.printify.com/v1"
    
    def test_client_initialization_missing_vars(self):
        """Test client initialization with missing environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                PrintifyAPIClient()
            
            assert "Missing required environment variables" in str(exc_info.value)
    
    def test_get_headers(self, mock_env_vars):
        """Test header generation."""
        client = PrintifyAPIClient()
        headers = client.get_headers()
        
        assert "Authorization" in headers
        assert "Bearer test_api_key" in headers["Authorization"]
        assert headers["Content-Type"] == "application/json"
    
    @patch('api.printify.PrintifyAPIClient.make_request')
    def test_test_connection_success(self, mock_make_request, mock_env_vars):
        """Test successful connection test."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "test_shop_id", "title": "Test Shop"}
        ]
        mock_make_request.return_value = mock_response
        
        client = PrintifyAPIClient()
        result = client.test_connection()
        
        assert result is True
    
    @patch('api.printify.PrintifyAPIClient.make_request')
    def test_test_connection_shop_not_found(self, mock_make_request, mock_env_vars):
        """Test connection test when shop not found."""
        # Mock response without matching shop
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "other_shop_id", "title": "Other Shop"}
        ]
        mock_make_request.return_value = mock_response
        
        client = PrintifyAPIClient()
        result = client.test_connection()
        
        assert result is False
    
    @patch('api.printify.PrintifyAPIClient.upload_image')
    @patch('api.printify.PrintifyAPIClient.get_blueprint_details')
    @patch('api.printify.PrintifyAPIClient.make_request')
    @patch('api.printify.PrintifyAPIClient._publish_product')
    def test_create_product_success(self, mock_publish, mock_make_request, 
                                   mock_get_blueprint, mock_upload, mock_env_vars):
        """Test successful product creation."""
        # Mock image upload
        mock_upload.return_value = "image_123"
        
        # Mock blueprint details
        mock_get_blueprint.return_value = {
            "variants": [
                {"id": 1, "options": [{"value": "Black"}]},
                {"id": 2, "options": [{"value": "White"}]}
            ]
        }
        
        # Mock product creation response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "product_123"}
        mock_make_request.return_value = mock_response
        
        client = PrintifyAPIClient()
        product_id = client.create_product(
            title="Test Product",
            description="Test Description",
            blueprint_id=12,
            print_provider_id=29,
            design_file_path="/path/to/design.png"
        )
        
        assert product_id == "product_123"
        mock_upload.assert_called_once()
        mock_publish.assert_called_once()


class TestAirtableClient:
    """Test cases for Google Sheets API client."""
    
    @pytest.fixture
    def mock_credentials_file(self, tmp_path):
        """Create mock credentials file."""
        creds_file = tmp_path / "test_creds.json"
        creds_data = {
            "type": "service_account",
            "project_id": "test_project",
            "private_key_id": "test_key_id",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest_key\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test.iam.gserviceaccount.com",
            "client_id": "test_client_id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        
        with open(creds_file, 'w') as f:
            import json
            json.dump(creds_data, f)
        
        return str(creds_file)
    
    @patch('api.sheets.gspread.authorize')
    @patch('api.sheets.Credentials.from_service_account_file')
    def test_client_initialization_success(self, mock_creds, mock_authorize, mock_credentials_file):
        """Test successful client initialization."""
        mock_creds.return_value = Mock()
        mock_authorize.return_value = Mock()
        
        client = AirtableClient(credentials_path=mock_credentials_file)
        
        assert client.client is not None
        mock_creds.assert_called_once()
        mock_authorize.assert_called_once()
    
    def test_client_initialization_missing_file(self):
        """Test client initialization with missing credentials file."""
        with pytest.raises(FileNotFoundError):
            AirtableClient(credentials_path="/nonexistent/path.json")
    
    @patch('api.sheets.AirtableClient.open_spreadsheet')
    def test_read_sheet_data_success(self, mock_open_spreadsheet):
        """Test successful sheet data reading."""
        # Mock spreadsheet and worksheet
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ["Header1", "Header2"],
            ["Value1", "Value2"],
            ["Value3", "Value4"]
        ]
        
        mock_spreadsheet = Mock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        mock_open_spreadsheet.return_value = mock_spreadsheet
        
        # Create client with mocked initialization
        with patch('api.sheets.AirtableClient._initialize_client'):
            client = AirtableClient()
            client.client = Mock()
        
        data = client.read_sheet_data("test_sheet_id", "Sheet1")
        
        assert len(data) == 3
        assert data[0] == ["Header1", "Header2"]
        assert data[1] == ["Value1", "Value2"]
    
    @patch('api.sheets.AirtableClient.open_spreadsheet')
    def test_update_row_success(self, mock_open_spreadsheet):
        """Test successful row update."""
        # Mock worksheet
        mock_worksheet = Mock()
        mock_worksheet.row_values.return_value = ["Name", "Status", "Date"]
        
        mock_spreadsheet = Mock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        mock_open_spreadsheet.return_value = mock_spreadsheet
        
        # Create client with mocked initialization
        with patch('api.sheets.AirtableClient._initialize_client'):
            client = AirtableClient()
            client.client = Mock()
        
        updates = {"status": "Completed", "date": "2024-01-01"}
        client.update_row("test_sheet_id", "Sheet1", 2, updates)
        
        # Verify update_cell was called for each update
        assert mock_worksheet.update_cell.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__])
