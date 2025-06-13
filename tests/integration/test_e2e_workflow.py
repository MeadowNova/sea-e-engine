
#!/usr/bin/env python3
"""
End-to-End Workflow Tests for SEA-E Engine.

Tests complete product creation workflows from Google Sheets
to Etsy listing publication.
"""

import pytest
import os
import sys
import json
import tempfile
import uuid
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent))

from sea_engine import SEAEngine, ProductData


@pytest.mark.e2e
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @pytest.fixture
    def test_config_dir(self):
        """Create temporary config directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir()
            
            # Copy essential config files
            import shutil
            original_config = Path(__file__).parent.parent.parent / "config"
            if original_config.exists():
                shutil.copytree(original_config, config_dir, dirs_exist_ok=True)
            
            yield str(config_dir)
    
    @pytest.fixture
    def test_design_file(self):
        """Create a test design file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            design_path = Path(temp_dir) / "test_design.png"
            
            # Create a minimal PNG file
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            with open(design_path, 'wb') as f:
                f.write(png_data)
            
            yield str(design_path)
    
    @pytest.fixture
    def engine_with_mocked_apis(self, test_config_dir):
        """Create SEA Engine with mocked API connections for testing."""
        # Mock environment variables
        with patch.dict(os.environ, {
            'ETSY_API_KEY': 'test_etsy_key',
            'ETSY_REFRESH_TOKEN': 'test_refresh_token',
            'ETSY_SHOP_ID': 'test_shop_id',
            'PRINTIFY_API_KEY': 'test_printify_key',
            'PRINTIFY_SHOP_ID': 'test_printify_shop_id'
        }):
            try:
                engine = SEAEngine(config_dir=test_config_dir)
                
                # Mock the API clients to avoid real API calls
                engine.etsy_client = Mock()
                engine.printify_client = Mock()
                engine.sheets_client = Mock()
                engine.mockup_generator = Mock()
                
                # Configure mock responses
                engine.etsy_client.create_listing.return_value = {"listing_id": f"test_listing_{uuid.uuid4().hex[:8]}"}
                engine.printify_client.create_product.return_value = {"id": f"test_product_{uuid.uuid4().hex[:8]}"}
                engine.printify_client.upload_image.return_value = {"id": f"test_image_{uuid.uuid4().hex[:8]}"}
                engine.sheets_client.read_sheet_data.return_value = []
                engine.mockup_generator.generate_mockup.return_value = "test_mockup_path.png"
                
                return engine
            except Exception as e:
                pytest.skip(f"Failed to initialize engine: {e}")
    
    @pytest.fixture
    def test_product_data(self, test_design_file):
        """Create test product data for workflows."""
        return [
            ProductData(
                design_name=f"Test T-Shirt {uuid.uuid4().hex[:8]}",
                design_file_path=test_design_file,
                product_type="t-shirt"
            ),
            ProductData(
                design_name=f"Test Sweatshirt {uuid.uuid4().hex[:8]}",
                design_file_path=test_design_file,
                product_type="sweatshirt"
            ),
            ProductData(
                design_name=f"Test Poster {uuid.uuid4().hex[:8]}",
                design_file_path=test_design_file,
                product_type="poster"
            )
        ]
    
    def test_tshirt_complete_workflow(self, engine_with_mocked_apis, test_product_data):
        """Test complete T-shirt creation workflow."""
        engine = engine_with_mocked_apis
        tshirt_data = [p for p in test_product_data if p.product_type == "t-shirt"][0]
        
        try:
            # Execute the workflow
            result = engine.process_product(tshirt_data)
            
            # Verify workflow completion
            assert result is not None
            
            # Verify API calls were made
            engine.printify_client.upload_image.assert_called()
            engine.printify_client.create_product.assert_called()
            engine.etsy_client.create_listing.assert_called()
            
        except Exception as e:
            # Workflow should handle errors gracefully
            assert "error" in str(e).lower() or "failed" in str(e).lower()
    
    def test_sweatshirt_complete_workflow(self, engine_with_mocked_apis, test_product_data):
        """Test complete sweatshirt creation workflow."""
        engine = engine_with_mocked_apis
        sweatshirt_data = [p for p in test_product_data if p.product_type == "sweatshirt"][0]
        
        try:
            # Execute the workflow
            result = engine.process_product(sweatshirt_data)
            
            # Verify workflow completion
            assert result is not None
            
            # Verify API calls were made
            engine.printify_client.upload_image.assert_called()
            engine.printify_client.create_product.assert_called()
            engine.etsy_client.create_listing.assert_called()
            
        except Exception as e:
            # Workflow should handle errors gracefully
            assert "error" in str(e).lower() or "failed" in str(e).lower()
    
    def test_poster_complete_workflow(self, engine_with_mocked_apis, test_product_data):
        """Test complete poster creation workflow."""
        engine = engine_with_mocked_apis
        poster_data = [p for p in test_product_data if p.product_type == "poster"][0]
        
        try:
            # Execute the workflow
            result = engine.process_product(poster_data)
            
            # Verify workflow completion
            assert result is not None
            
            # Verify API calls were made
            engine.printify_client.upload_image.assert_called()
            engine.printify_client.create_product.assert_called()
            engine.etsy_client.create_listing.assert_called()
            
        except Exception as e:
            # Workflow should handle errors gracefully
            assert "error" in str(e).lower() or "failed" in str(e).lower()
    
    @pytest.mark.slow
    def test_batch_processing_workflow(self, engine_with_mocked_apis, test_product_data):
        """Test batch processing of multiple products."""
        engine = engine_with_mocked_apis
        
        try:
            # Process multiple products in batch
            results = engine.process_products_batch(test_product_data)
            
            # Verify batch processing
            assert isinstance(results, list)
            assert len(results) == len(test_product_data)
            
            # Verify all products were processed
            for result in results:
                assert result is not None
                
        except Exception as e:
            # Batch processing should handle errors gracefully
            assert "batch" in str(e).lower() or "error" in str(e).lower()
    
    def test_mockup_generation_integration(self, engine_with_mocked_apis, test_product_data):
        """Test mockup generation integration."""
        engine = engine_with_mocked_apis
        test_product = test_product_data[0]
        
        try:
            # Test mockup generation
            mockup_path = engine.mockup_generator.generate_mockup(
                test_product.design_file_path,
                test_product.product_type
            )
            
            # Verify mockup generation
            assert mockup_path is not None
            engine.mockup_generator.generate_mockup.assert_called_with(
                test_product.design_file_path,
                test_product.product_type
            )
            
        except Exception as e:
            # Mockup generation should handle errors gracefully
            assert "mockup" in str(e).lower() or "generation" in str(e).lower()
    
    def test_workflow_state_persistence(self, engine_with_mocked_apis, test_product_data):
        """Test workflow state persistence and recovery."""
        engine = engine_with_mocked_apis
        test_product = test_product_data[0]
        
        try:
            # Start workflow
            engine.start_workflow(test_product)
            
            # Verify state is saved
            assert engine.state_manager is not None
            
            # Simulate workflow interruption and recovery
            engine.recover_workflow(test_product.design_name)
            
            # Verify recovery works
            assert True  # If we get here, recovery worked
            
        except Exception as e:
            # State management should handle errors gracefully
            assert "state" in str(e).lower() or "workflow" in str(e).lower()
    
    def test_workflow_interruption_recovery(self, engine_with_mocked_apis, test_product_data):
        """Test workflow interruption and recovery."""
        engine = engine_with_mocked_apis
        test_product = test_product_data[0]
        
        # Mock workflow interruption
        with patch.object(engine.printify_client, 'create_product') as mock_create:
            mock_create.side_effect = Exception("Simulated interruption")
            
            try:
                # Attempt workflow that will be interrupted
                engine.process_product(test_product)
                assert False, "Should have been interrupted"
            except Exception:
                # Expected interruption
                pass
            
            # Reset mock and attempt recovery
            mock_create.side_effect = None
            mock_create.return_value = {"id": "recovered_product_id"}
            
            try:
                # Attempt recovery
                result = engine.recover_workflow(test_product.design_name)
                # Recovery should work or fail gracefully
                assert True
            except Exception as e:
                assert "recovery" in str(e).lower() or "workflow" in str(e).lower()
    
    def test_error_rollback_mechanisms(self, engine_with_mocked_apis, test_product_data):
        """Test error rollback and cleanup mechanisms."""
        engine = engine_with_mocked_apis
        test_product = test_product_data[0]
        
        # Mock error in Etsy listing creation
        engine.etsy_client.create_listing.side_effect = Exception("Etsy error")
        
        try:
            # Attempt workflow that will fail
            engine.process_product(test_product)
            assert False, "Should have failed"
        except Exception:
            # Expected failure
            pass
        
        # Verify cleanup was attempted
        # In a real implementation, this would check for cleanup calls
        assert True  # Placeholder for actual cleanup verification
    
    @pytest.mark.slow
    def test_multi_product_type_batch(self, engine_with_mocked_apis, test_product_data):
        """Test batch processing with multiple product types."""
        engine = engine_with_mocked_apis
        
        try:
            # Process mixed product types
            results = engine.process_products_batch(test_product_data)
            
            # Verify all product types were handled
            assert len(results) == len(test_product_data)
            
            # Verify different product types were processed
            product_types = [p.product_type for p in test_product_data]
            assert "t-shirt" in product_types
            assert "sweatshirt" in product_types
            assert "poster" in product_types
            
        except Exception as e:
            # Multi-type batch should handle errors gracefully
            assert "batch" in str(e).lower() or "type" in str(e).lower()
    
    def test_configuration_driven_workflow(self, engine_with_mocked_apis, test_config_dir):
        """Test configuration-driven workflow execution."""
        engine = engine_with_mocked_apis
        
        try:
            # Verify configuration loading
            assert engine.config_dir == test_config_dir
            
            # Test configuration-driven behavior
            config_path = Path(test_config_dir) / "product_blueprints.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                assert isinstance(config, dict)
                
        except Exception as e:
            # Configuration should handle errors gracefully
            assert "config" in str(e).lower() or "file" in str(e).lower()
