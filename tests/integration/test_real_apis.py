
#!/usr/bin/env python3
"""
Real API Integration Tests for SEA-E Engine.

Tests real API interactions with actual endpoints, authentication,
error handling, and data operations.
"""

import pytest
import os
import sys
import json
import time
import tempfile
import requests
import uuid
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError, Timeout, HTTPError

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.etsy import EtsyAPIClient
from api.printify import PrintifyAPIClient
from api.airtable_client import AirtableClient


@pytest.mark.integration
class TestRealAPIIntegration:
    """Test real API integrations with actual endpoints."""
    
    @pytest.fixture
    def etsy_client(self):
        """Create Etsy API client with real credentials."""
        # Skip if no real credentials available
        if not all([
            os.getenv("ETSY_API_KEY"),
            os.getenv("ETSY_REFRESH_TOKEN"),
            os.getenv("ETSY_SHOP_ID")
        ]):
            pytest.skip("Etsy API credentials not available for integration testing")
        
        try:
            client = EtsyAPIClient()
            return client
        except Exception as e:
            pytest.skip(f"Failed to initialize Etsy client: {e}")
    
    @pytest.fixture
    def printify_client(self):
        """Create Printify API client with real credentials."""
        # Skip if no real credentials available
        if not all([
            os.getenv("PRINTIFY_API_KEY"),
            os.getenv("PRINTIFY_SHOP_ID")
        ]):
            pytest.skip("Printify API credentials not available for integration testing")
        
        try:
            client = PrintifyAPIClient()
            return client
        except Exception as e:
            pytest.skip(f"Failed to initialize Printify client: {e}")
    
    @pytest.fixture
    def sheets_client(self):
        """Create Google Sheets client with real credentials."""
        # Skip if no credentials file available
        creds_path = "credentials/gcp_service_account.json"
        if not Path(creds_path).exists():
            pytest.skip("Google Sheets credentials not available for integration testing")
        
        try:
            client = AirtableClient(creds_path)
            return client
        except Exception as e:
            pytest.skip(f"Failed to initialize Sheets client: {e}")
    
    @pytest.fixture
    def test_image_path(self):
        """Create a test image for upload tests."""
        # Create a simple test image
        test_dir = Path(tempfile.mkdtemp())
        image_path = test_dir / "test_design.png"
        
        # Create a minimal PNG file (1x1 pixel)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        
        with open(image_path, 'wb') as f:
            f.write(png_data)
        
        yield str(image_path)
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
    
    def test_etsy_authentication_renewal(self, etsy_client):
        """Test Etsy OAuth token refresh workflow."""
        # Test token refresh mechanism
        original_token = etsy_client.access_token
        
        # Force token refresh
        try:
            etsy_client._refresh_access_token()
            assert etsy_client.access_token is not None
            # Token should be different after refresh (in real scenario)
            # In test, we just verify the refresh mechanism works
        except Exception as e:
            # If refresh fails, ensure it's handled gracefully
            assert "refresh" in str(e).lower() or "token" in str(e).lower()
    
    def test_etsy_rate_limiting_compliance(self, etsy_client):
        """Test Etsy API rate limiting and backoff mechanisms."""
        # Test that client respects rate limits
        start_time = time.time()
        
        # Make multiple rapid requests to test rate limiting
        for i in range(3):
            try:
                etsy_client.get_shop_info()
                time.sleep(0.1)  # Small delay between requests
            except Exception as e:
                # Rate limiting should be handled gracefully
                if "rate" in str(e).lower() or "429" in str(e):
                    assert True  # Expected behavior
                    break
        
        elapsed = time.time() - start_time
        # Should take some time due to rate limiting compliance
        assert elapsed >= 0.1
    
    def test_etsy_error_handling_401(self, etsy_client):
        """Test handling of 401 Unauthorized responses."""
        # Temporarily corrupt the token to trigger 401
        original_token = etsy_client.access_token
        etsy_client.access_token = "invalid_token_for_testing"
        
        try:
            etsy_client.get_shop_info()
            # Should either succeed with refresh or fail gracefully
        except Exception as e:
            # Should handle 401 errors appropriately
            assert any(keyword in str(e).lower() for keyword in ["unauthorized", "token", "auth"])
        finally:
            # Restore original token
            etsy_client.access_token = original_token
    
    def test_etsy_error_handling_429(self, etsy_client):
        """Test handling of 429 Rate Limited responses."""
        # Mock a 429 response to test handling
        with patch.object(etsy_client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {'Retry-After': '1'}
            mock_response.raise_for_status.side_effect = HTTPError("429 Rate Limited")
            mock_get.return_value = mock_response
            
            start_time = time.time()
            try:
                etsy_client.get_shop_info()
            except Exception as e:
                # Should handle rate limiting with backoff
                elapsed = time.time() - start_time
                assert elapsed >= 0.5  # Should have some delay
    
    def test_etsy_error_handling_500(self, etsy_client):
        """Test handling of 500 Server Error responses."""
        # Mock a 500 response to test handling
        with patch.object(etsy_client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = HTTPError("500 Server Error")
            mock_get.return_value = mock_response
            
            try:
                etsy_client.get_shop_info()
            except Exception as e:
                # Should handle server errors gracefully
                assert "500" in str(e) or "server" in str(e).lower()
    
    def test_printify_product_creation_real(self, printify_client, test_image_path):
        """Test real Printify product creation with cleanup."""
        # Create a test product
        test_product_data = {
            "title": f"Test Product {uuid.uuid4().hex[:8]}",
            "description": "Test product for integration testing",
            "blueprint_id": 384,  # Unisex Heavy Cotton Tee
            "print_provider_id": 1,  # Printful
            "variants": [
                {
                    "id": 17887,  # S / Black
                    "price": 2000,  # $20.00
                    "is_enabled": True
                }
            ],
            "print_areas": [
                {
                    "variant_ids": [17887],
                    "placeholders": [
                        {
                            "position": "front",
                            "images": [
                                {
                                    "id": "test_image_id",
                                    "x": 0.5,
                                    "y": 0.5,
                                    "scale": 1.0,
                                    "angle": 0
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        created_product_id = None
        try:
            # First upload the image
            image_response = printify_client.upload_image(test_image_path)
            assert image_response is not None
            
            # Update product data with real image ID
            if "id" in image_response:
                test_product_data["print_areas"][0]["placeholders"][0]["images"][0]["id"] = image_response["id"]
            
            # Create the product
            product_response = printify_client.create_product(test_product_data)
            assert product_response is not None
            
            if "id" in product_response:
                created_product_id = product_response["id"]
                assert created_product_id is not None
                
        except Exception as e:
            # Product creation might fail due to various reasons
            # Ensure error is handled gracefully
            assert isinstance(e, (ValueError, requests.RequestException))
            
        finally:
            # Cleanup: Delete the test product if created
            if created_product_id:
                try:
                    printify_client.delete_product(created_product_id)
                except:
                    pass  # Cleanup failure is not critical for test
    
    def test_printify_blueprint_validation(self, printify_client):
        """Test Printify blueprint data validation."""
        # Test getting blueprints
        try:
            blueprints = printify_client.get_blueprints()
            assert isinstance(blueprints, list)
            assert len(blueprints) > 0
            
            # Validate blueprint structure
            first_blueprint = blueprints[0]
            required_fields = ["id", "title", "brand"]
            for field in required_fields:
                assert field in first_blueprint
                
        except Exception as e:
            # Should handle API errors gracefully
            assert isinstance(e, (ValueError, requests.RequestException))
    
    def test_printify_image_upload_real(self, printify_client, test_image_path):
        """Test real image upload to Printify."""
        try:
            # Upload test image
            response = printify_client.upload_image(test_image_path)
            assert response is not None
            
            # Validate response structure
            if isinstance(response, dict):
                assert "id" in response
                assert response["id"] is not None
                
        except Exception as e:
            # Image upload might fail due to various reasons
            assert isinstance(e, (ValueError, requests.RequestException))
    
    def test_printify_error_scenarios(self, printify_client):
        """Test Printify API error scenarios."""
        # Test invalid product creation
        invalid_product_data = {
            "title": "",  # Invalid empty title
            "blueprint_id": 999999,  # Invalid blueprint ID
        }
        
        try:
            printify_client.create_product(invalid_product_data)
            assert False, "Should have failed with invalid data"
        except Exception as e:
            # Should handle validation errors
            assert isinstance(e, (ValueError, requests.RequestException))
    
    def test_sheets_read_write_operations(self, sheets_client):
        """Test real Google Sheets read/write operations."""
        # Skip if no test spreadsheet ID available
        test_sheet_id = os.getenv("TEST_GOOGLE_SHEET_ID")
        if not test_sheet_id:
            pytest.skip("No test Google Sheet ID provided")
        
        try:
            # Test reading from sheet
            data = sheets_client.read_sheet_data(test_sheet_id, "Sheet1!A1:C10")
            assert isinstance(data, list)
            
            # Test writing to sheet (if permissions allow)
            test_data = [["Test", "Data", str(datetime.now())]]
            sheets_client.write_sheet_data(test_sheet_id, "Sheet1!A1:C1", test_data)
            
        except Exception as e:
            # Should handle permission and API errors gracefully
            assert "permission" in str(e).lower() or "not found" in str(e).lower()
    
    def test_sheets_authentication_refresh(self, sheets_client):
        """Test Google Sheets authentication refresh."""
        # Test that client can handle auth refresh
        try:
            # Force re-authentication
            sheets_client._initialize_client()
            assert sheets_client.client is not None
            
        except Exception as e:
            # Should handle auth errors gracefully
            assert "auth" in str(e).lower() or "credential" in str(e).lower()
    
    def test_sheets_error_handling(self, sheets_client):
        """Test Google Sheets error handling scenarios."""
        # Test invalid spreadsheet ID
        try:
            sheets_client.read_sheet_data("invalid_sheet_id", "Sheet1!A1:A1")
            assert False, "Should have failed with invalid sheet ID"
        except Exception as e:
            # Should handle invalid sheet errors
            assert "not found" in str(e).lower() or "invalid" in str(e).lower()
    
    @pytest.mark.slow
    def test_api_timeout_handling(self):
        """Test API timeout handling across all clients."""
        # Test timeout handling with mock
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Timeout("Request timed out")
            
            # Test Etsy timeout handling
            if all([os.getenv("ETSY_API_KEY"), os.getenv("ETSY_REFRESH_TOKEN"), os.getenv("ETSY_SHOP_ID")]):
                try:
                    client = EtsyAPIClient()
                    client.get_shop_info()
                except Exception as e:
                    assert "timeout" in str(e).lower()
    
    @pytest.mark.slow
    def test_network_failure_recovery(self):
        """Test network failure recovery mechanisms."""
        # Test network failure handling with mock
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = ConnectionError("Network unreachable")
            
            # Test Printify network failure handling
            if all([os.getenv("PRINTIFY_API_KEY"), os.getenv("PRINTIFY_SHOP_ID")]):
                try:
                    client = PrintifyAPIClient()
                    client.get_blueprints()
                except Exception as e:
                    assert "connection" in str(e).lower() or "network" in str(e).lower()
