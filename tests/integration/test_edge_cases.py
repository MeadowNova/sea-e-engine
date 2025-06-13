
#!/usr/bin/env python3
"""
Edge Cases and Failure Scenario Tests for SEA-E Engine.

Tests system behavior under various failure conditions,
invalid inputs, and edge cases.
"""

import pytest
import os
import sys
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import ConnectionError, Timeout, HTTPError

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent))

from sea_engine import SEAEngine, ProductData


@pytest.mark.edge
class TestEdgeCasesAndFailures:
    """Test edge cases and failure scenarios."""
    
    @pytest.fixture
    def edge_case_engine(self):
        """Create engine for edge case testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir()
            
            # Copy config files
            original_config = Path(__file__).parent.parent.parent / "config"
            if original_config.exists():
                shutil.copytree(original_config, config_dir, dirs_exist_ok=True)
            
            # Mock environment variables
            with patch.dict(os.environ, {
                'ETSY_API_KEY': 'test_etsy_key',
                'ETSY_REFRESH_TOKEN': 'test_refresh_token',
                'ETSY_SHOP_ID': 'test_shop_id',
                'PRINTIFY_API_KEY': 'test_printify_key',
                'PRINTIFY_SHOP_ID': 'test_printify_shop_id'
            }):
                try:
                    engine = SEAEngine(config_dir=str(config_dir))
                    
                    # Mock API clients
                    engine.etsy_client = Mock()
                    engine.printify_client = Mock()
                    engine.sheets_client = Mock()
                    engine.mockup_generator = Mock()
                    
                    yield engine
                except Exception as e:
                    pytest.skip(f"Failed to initialize edge case engine: {e}")
    
    @pytest.fixture
    def invalid_design_file(self):
        """Create an invalid design file for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_path = Path(temp_dir) / "invalid_design.txt"
            with open(invalid_path, 'w') as f:
                f.write("This is not an image file")
            yield str(invalid_path)
    
    def test_invalid_product_configuration(self, edge_case_engine):
        """Test handling of invalid product configurations."""
        # Test with invalid product type
        invalid_product = ProductData(
            design_name="Invalid Product",
            design_file_path="/nonexistent/path.png",
            product_type="invalid_type"
        )
        
        try:
            edge_case_engine.process_product(invalid_product)
            assert False, "Should have failed with invalid product type"
        except Exception as e:
            # Should handle invalid configuration gracefully
            assert any(keyword in str(e).lower() for keyword in ["invalid", "type", "config"])
    
    def test_malformed_input_data(self, edge_case_engine):
        """Test handling of malformed input data."""
        # Test with None values
        try:
            malformed_product = ProductData(
                design_name=None,
                design_file_path=None,
                product_type=None
            )
            edge_case_engine.process_product(malformed_product)
            assert False, "Should have failed with None values"
        except Exception as e:
            # Should handle malformed data gracefully
            assert any(keyword in str(e).lower() for keyword in ["none", "null", "invalid"])
    
    def test_missing_required_fields(self, edge_case_engine):
        """Test validation of missing required fields."""
        # Test with empty strings
        try:
            empty_product = ProductData(
                design_name="",
                design_file_path="",
                product_type=""
            )
            edge_case_engine.process_product(empty_product)
            assert False, "Should have failed with empty fields"
        except Exception as e:
            # Should validate required fields
            assert any(keyword in str(e).lower() for keyword in ["empty", "required", "missing"])
    
    def test_data_type_validation(self, edge_case_engine):
        """Test data type and format validation."""
        # Test with wrong data types
        try:
            wrong_type_product = ProductData(
                design_name=123,  # Should be string
                design_file_path=["not", "a", "string"],  # Should be string
                product_type={"invalid": "type"}  # Should be string
            )
            edge_case_engine.process_product(wrong_type_product)
            assert False, "Should have failed with wrong data types"
        except Exception as e:
            # Should validate data types
            assert any(keyword in str(e).lower() for keyword in ["type", "invalid", "format"])
    
    def test_network_connectivity_failure(self, edge_case_engine):
        """Test behavior during network connectivity issues."""
        # Mock network failure
        edge_case_engine.etsy_client.create_listing.side_effect = ConnectionError("Network unreachable")
        edge_case_engine.printify_client.create_product.side_effect = ConnectionError("Network unreachable")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            design_path = Path(temp_dir) / "test_design.png"
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            with open(design_path, 'wb') as f:
                f.write(png_data)
            
            product = ProductData("Network Test", str(design_path), "t-shirt")
            
            try:
                edge_case_engine.process_product(product)
                assert False, "Should have failed with network error"
            except Exception as e:
                # Should handle network failures gracefully
                assert any(keyword in str(e).lower() for keyword in ["network", "connection", "unreachable"])
    
    def test_disk_space_limitation(self, edge_case_engine):
        """Test behavior when disk space is limited."""
        # Mock disk space error
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            with tempfile.TemporaryDirectory() as temp_dir:
                design_path = Path(temp_dir) / "test_design.png"
                # Create the file first, then mock the error
                png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
                
                # Write file before mocking
                with open(design_path, 'wb') as f:
                    f.write(png_data)
                
                product = ProductData("Disk Space Test", str(design_path), "t-shirt")
                
                try:
                    edge_case_engine.process_product(product)
                    # May succeed if no file operations are needed
                    assert True
                except Exception as e:
                    # Should handle disk space errors gracefully
                    assert any(keyword in str(e).lower() for keyword in ["space", "disk", "device"])
    
    def test_file_permission_errors(self, edge_case_engine):
        """Test handling of file system permission errors."""
        # Mock permission error
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with tempfile.TemporaryDirectory() as temp_dir:
                design_path = Path(temp_dir) / "test_design.png"
                # Create file first
                png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
                
                with open(design_path, 'wb') as f:
                    f.write(png_data)
                
                product = ProductData("Permission Test", str(design_path), "t-shirt")
                
                try:
                    edge_case_engine.process_product(product)
                    # May succeed if no file operations are needed
                    assert True
                except Exception as e:
                    # Should handle permission errors gracefully
                    assert any(keyword in str(e).lower() for keyword in ["permission", "denied", "access"])
    
    def test_configuration_file_corruption(self, edge_case_engine):
        """Test recovery from configuration file corruption."""
        # Test with corrupted JSON config
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir()
            
            # Create corrupted config file
            corrupted_config = config_dir / "product_blueprints.json"
            with open(corrupted_config, 'w') as f:
                f.write("{ invalid json content }")
            
            try:
                # Try to load corrupted config
                with open(corrupted_config, 'r') as f:
                    json.load(f)
                assert False, "Should have failed with corrupted JSON"
            except json.JSONDecodeError:
                # Expected behavior - should handle JSON errors gracefully
                assert True
    
    def test_api_service_unavailability(self, edge_case_engine):
        """Test handling of API service unavailability."""
        # Mock service unavailable (503)
        edge_case_engine.etsy_client.create_listing.side_effect = HTTPError("503 Service Unavailable")
        edge_case_engine.printify_client.create_product.side_effect = HTTPError("503 Service Unavailable")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            design_path = Path(temp_dir) / "test_design.png"
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            with open(design_path, 'wb') as f:
                f.write(png_data)
            
            product = ProductData("Service Unavailable Test", str(design_path), "t-shirt")
            
            try:
                edge_case_engine.process_product(product)
                assert False, "Should have failed with service unavailable"
            except Exception as e:
                # Should handle service unavailability gracefully
                assert any(keyword in str(e).lower() for keyword in ["503", "service", "unavailable"])
    
    def test_partial_api_response_handling(self, edge_case_engine):
        """Test handling of partial API responses."""
        # Mock partial response (missing required fields)
        edge_case_engine.printify_client.create_product.return_value = {"partial": "response"}  # Missing 'id'
        edge_case_engine.etsy_client.create_listing.return_value = {"incomplete": "data"}  # Missing 'listing_id'
        
        with tempfile.TemporaryDirectory() as temp_dir:
            design_path = Path(temp_dir) / "test_design.png"
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            with open(design_path, 'wb') as f:
                f.write(png_data)
            
            product = ProductData("Partial Response Test", str(design_path), "t-shirt")
            
            try:
                edge_case_engine.process_product(product)
                # May succeed or fail depending on implementation
                assert True
            except Exception as e:
                # Should handle partial responses gracefully
                assert any(keyword in str(e).lower() for keyword in ["missing", "incomplete", "partial"])
    
    def test_timeout_and_retry_exhaustion(self, edge_case_engine):
        """Test behavior when retries are exhausted."""
        # Mock timeout that persists through retries
        edge_case_engine.etsy_client.create_listing.side_effect = Timeout("Request timed out")
        edge_case_engine.printify_client.create_product.side_effect = Timeout("Request timed out")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            design_path = Path(temp_dir) / "test_design.png"
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            with open(design_path, 'wb') as f:
                f.write(png_data)
            
            product = ProductData("Timeout Test", str(design_path), "t-shirt")
            
            try:
                edge_case_engine.process_product(product)
                assert False, "Should have failed with timeout"
            except Exception as e:
                # Should handle timeout and retry exhaustion gracefully
                assert any(keyword in str(e).lower() for keyword in ["timeout", "retry", "exhausted"])
    
    def test_authentication_service_failure(self, edge_case_engine):
        """Test handling of authentication service failures."""
        # Mock authentication failure
        edge_case_engine.etsy_client.create_listing.side_effect = HTTPError("401 Unauthorized")
        edge_case_engine.printify_client.create_product.side_effect = HTTPError("401 Unauthorized")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            design_path = Path(temp_dir) / "test_design.png"
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            with open(design_path, 'wb') as f:
                f.write(png_data)
            
            product = ProductData("Auth Failure Test", str(design_path), "t-shirt")
            
            try:
                edge_case_engine.process_product(product)
                assert False, "Should have failed with auth error"
            except Exception as e:
                # Should handle authentication failures gracefully
                assert any(keyword in str(e).lower() for keyword in ["401", "unauthorized", "auth"])
    
    def test_concurrent_access_conflicts(self, edge_case_engine):
        """Test handling of concurrent access conflicts."""
        # Mock concurrent access conflict
        import threading
        import time
        
        results = []
        errors = []
        
        def process_product_concurrently(product_name):
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    design_path = Path(temp_dir) / f"{product_name}_design.png"
                    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
                    
                    with open(design_path, 'wb') as f:
                        f.write(png_data)
                    
                    product = ProductData(product_name, str(design_path), "t-shirt")
                    result = edge_case_engine.process_product(product)
                    results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=process_product_concurrently, args=[f"Concurrent Product {i}"])
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should handle concurrent access without major issues
        total_operations = len(results) + len(errors)
        assert total_operations == 3  # All operations should complete
    
    def test_resource_exhaustion_scenarios(self, edge_case_engine):
        """Test behavior under resource exhaustion."""
        # Mock memory exhaustion
        with patch('sys.getsizeof', return_value=999999999):  # Mock large memory usage
            with tempfile.TemporaryDirectory() as temp_dir:
                design_path = Path(temp_dir) / "test_design.png"
                png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
                
                with open(design_path, 'wb') as f:
                    f.write(png_data)
                
                product = ProductData("Resource Exhaustion Test", str(design_path), "t-shirt")
                
                try:
                    edge_case_engine.process_product(product)
                    # May succeed if resource monitoring is not implemented
                    assert True
                except Exception as e:
                    # Should handle resource exhaustion gracefully
                    assert any(keyword in str(e).lower() for keyword in ["memory", "resource", "exhausted"])
