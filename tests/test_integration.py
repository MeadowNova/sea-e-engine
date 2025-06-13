
#!/usr/bin/env python3
"""
Integration tests for SEA-E Engine.
"""

import pytest
import os
import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent))

from sea_engine import SEAEngine, ProductData


class TestSEAEngineIntegration:
    """Integration tests for the complete SEA Engine workflow."""
    
    @pytest.fixture
    def complete_test_environment(self):
        """Set up complete test environment with all required components."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create directory structure
            config_dir = Path(temp_dir) / "config"
            output_dir = Path(temp_dir) / "output"
            logs_dir = Path(temp_dir) / "logs"
            
            config_dir.mkdir()
            output_dir.mkdir()
            logs_dir.mkdir()
            
            # Create comprehensive product blueprints
            product_blueprints = {
                "products": {
                    "tshirt_bella_canvas_3001": {
                        "metadata": {
                            "name": "Unisex Jersey Short Sleeve Tee",
                            "brand": "Bella+Canvas",
                            "model": "3001"
                        },
                        "printify_config": {
                            "blueprint_id": 12,
                            "print_provider_id": 29
                        }
                    },
                    "sweatshirt_gildan_18000": {
                        "metadata": {
                            "name": "Heavy Blend Crewneck Sweatshirt",
                            "brand": "Gildan",
                            "model": "18000"
                        },
                        "printify_config": {
                            "blueprint_id": 49,
                            "print_provider_id": 29
                        }
                    }
                }
            }
            
            with open(config_dir / "product_blueprints.json", 'w') as f:
                json.dump(product_blueprints, f)
            
            # Create mockup blueprints
            mockup_blueprints = {
                "blueprints": {
                    "tshirt_bella_canvas_3001": {
                        "template_path": "templates/tshirt_template.png",
                        "colors": ["black", "white", "navy"]
                    },
                    "sweatshirt_gildan_18000": {
                        "template_path": "templates/sweatshirt_template.png",
                        "colors": ["black", "white"]
                    }
                }
            }
            
            with open(config_dir / "mockup_blueprints.json", 'w') as f:
                json.dump(mockup_blueprints, f)
            
            # Create test design file
            test_design = output_dir / "test_design.png"
            test_design.write_text("fake_image_data")
            
            yield {
                "config_dir": str(config_dir),
                "output_dir": str(output_dir),
                "logs_dir": str(logs_dir),
                "test_design": str(test_design)
            }
    
    @pytest.fixture
    def mock_all_apis(self):
        """Mock all API clients for integration testing."""
        with patch('sea_engine.EtsyAPIClient') as mock_etsy, \
             patch('sea_engine.PrintifyAPIClient') as mock_printify, \
             patch('sea_engine.AirtableClient') as mock_sheets, \
             patch('sea_engine.MockupGenerator') as mock_mockup, \
             patch('sea_engine.WorkflowStateManager') as mock_state:
            
            # Configure Etsy client mock
            etsy_instance = mock_etsy.return_value
            etsy_instance.test_connection.return_value = True
            etsy_instance.create_listing.return_value = "etsy_listing_123"
            
            # Configure Printify client mock
            printify_instance = mock_printify.return_value
            printify_instance.test_connection.return_value = True
            printify_instance.create_product.return_value = "printify_product_456"
            
            # Configure Sheets client mock
            sheets_instance = mock_sheets.return_value
            sheets_instance.test_connection.return_value = True
            sheets_instance.read_sheet_data.return_value = [
                ["design_name", "design_file_path", "product_type", "title", "description", "price", "tags"],
                ["test_design", "/path/to/design.png", "tshirt", "Test T-Shirt", "A test t-shirt", "19.99", "test,shirt"],
                ["test_sweatshirt", "/path/to/sweatshirt.png", "sweatshirt", "Test Sweatshirt", "A test sweatshirt", "29.99", "test,sweatshirt"]
            ]
            sheets_instance.update_row.return_value = None
            
            # Configure Mockup generator mock
            mockup_instance = mock_mockup.return_value
            mockup_instance.generate_mockup.return_value = {
                "success": True,
                "files": ["mockup1.png", "mockup2.png", "mockup3.png"]
            }
            
            # Configure State manager mock
            state_instance = mock_state.return_value
            state_instance.start_workflow.return_value = Mock()
            state_instance.update_workflow_step.return_value = Mock()
            state_instance.complete_workflow.return_value = Mock()
            state_instance.fail_workflow.return_value = Mock()
            
            yield {
                'etsy': etsy_instance,
                'printify': printify_instance,
                'sheets': sheets_instance,
                'mockup': mockup_instance,
                'state': state_instance
            }
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock all required environment variables."""
        env_vars = {
            "ETSY_API_KEY": "test_etsy_key",
            "ETSY_API_SECRET": "test_etsy_secret",
            "ETSY_ACCESS_TOKEN": "test_etsy_token",
            "ETSY_REFRESH_TOKEN": "test_etsy_refresh",
            "ETSY_SHOP_ID": "test_etsy_shop",
            "PRINTIFY_API_KEY": "test_printify_key",
            "PRINTIFY_SHOP_ID": "test_printify_shop"
        }
        
        with patch.dict(os.environ, env_vars):
            yield env_vars
    
    def test_complete_engine_initialization(self, complete_test_environment, mock_env_vars, mock_all_apis):
        """Test complete engine initialization with all components."""
        engine = SEAEngine(
            config_dir=complete_test_environment["config_dir"],
            output_dir=complete_test_environment["output_dir"]
        )
        
        # Verify all components are initialized
        assert engine.etsy_client is not None
        assert engine.printify_client is not None
        assert engine.sheets_client is not None
        assert engine.mockup_generator is not None
        assert engine.state_manager is not None
        
        # Verify configurations are loaded
        assert "products" in engine.product_blueprints
        assert "blueprints" in engine.mockup_blueprints
        
        # Verify environment validation passes
        assert engine.validate_environment() is True
    
    def test_complete_single_product_workflow(self, complete_test_environment, mock_env_vars, mock_all_apis):
        """Test complete workflow for a single product."""
        engine = SEAEngine(
            config_dir=complete_test_environment["config_dir"],
            output_dir=complete_test_environment["output_dir"]
        )
        
        # Create test product data
        product_data = ProductData(
            design_name="test_product",
            design_file_path=complete_test_environment["test_design"],
            product_type="tshirt",
            title="Test Product",
            description="A test product for integration testing",
            tags=["test", "integration"],
            price=19.99,
            colors=["black", "white"],
            variations=["crew_neck"],
            row_number=2
        )
        
        # Process the product
        result = engine.process_single_product(product_data)
        
        # Verify successful completion
        assert result.success is True
        assert result.printify_product_id == "printify_product_456"
        assert result.etsy_listing_id == "etsy_listing_123"
        assert len(result.mockup_files) == 6  # 2 colors × 1 variation × 3 files per mockup
        assert result.error_message is None
        assert result.execution_time > 0
        
        # Verify all API calls were made
        mock_all_apis['mockup'].generate_mockup.assert_called()
        mock_all_apis['printify'].create_product.assert_called()
        mock_all_apis['etsy'].create_listing.assert_called()
        
        # Verify state management calls
        mock_all_apis['state'].start_workflow.assert_called()
        mock_all_apis['state'].update_workflow_step.assert_called()
        mock_all_apis['state'].complete_workflow.assert_called()
    
    def test_complete_batch_processing_workflow(self, complete_test_environment, mock_env_vars, mock_all_apis):
        """Test complete batch processing workflow."""
        engine = SEAEngine(
            config_dir=complete_test_environment["config_dir"],
            output_dir=complete_test_environment["output_dir"]
        )
        
        # Process batch from mock sheet
        results = engine.process_batch("test_sheet_id", "Products")
        
        # Verify batch processing results
        assert len(results) == 2  # Two products in mock data
        
        # Verify first product
        assert results[0].success is True
        assert results[0].product_data.design_name == "test_design"
        assert results[0].product_data.product_type == "tshirt"
        
        # Verify second product
        assert results[1].success is True
        assert results[1].product_data.design_name == "test_sweatshirt"
        assert results[1].product_data.product_type == "sweatshirt"
        
        # Verify API calls were made for both products
        assert mock_all_apis['mockup'].generate_mockup.call_count == 2
        assert mock_all_apis['printify'].create_product.call_count == 2
        assert mock_all_apis['etsy'].create_listing.call_count == 2
        
        # Verify sheet updates were called
        assert mock_all_apis['sheets'].update_row.call_count == 2
    
    def test_workflow_error_handling(self, complete_test_environment, mock_env_vars, mock_all_apis):
        """Test error handling in complete workflow."""
        engine = SEAEngine(
            config_dir=complete_test_environment["config_dir"],
            output_dir=complete_test_environment["output_dir"]
        )
        
        # Configure mockup generator to fail
        mock_all_apis['mockup'].generate_mockup.side_effect = Exception("Mockup generation failed")
        
        # Create test product data
        product_data = ProductData(
            design_name="failing_product",
            design_file_path=complete_test_environment["test_design"],
            product_type="tshirt",
            title="Failing Product",
            description="A product that will fail",
            tags=["test", "fail"],
            price=19.99,
            colors=["black"],
            variations=["crew_neck"],
            row_number=2
        )
        
        # Process the product
        result = engine.process_single_product(product_data)
        
        # Verify failure handling
        assert result.success is False
        assert result.error_message is not None
        assert "Mockup generation failed" in result.error_message
        assert result.printify_product_id is None
        assert result.etsy_listing_id is None
        
        # Verify state management failure call
        mock_all_apis['state'].fail_workflow.assert_called()
    
    def test_api_connection_validation(self, complete_test_environment, mock_env_vars, mock_all_apis):
        """Test API connection validation in integration."""
        engine = SEAEngine(
            config_dir=complete_test_environment["config_dir"],
            output_dir=complete_test_environment["output_dir"]
        )
        
        # Test successful validation
        assert engine.validate_environment() is True
        
        # Test failed validation
        mock_all_apis['etsy'].test_connection.return_value = False
        assert engine.validate_environment() is False
    
    def test_configuration_validation(self, complete_test_environment, mock_env_vars, mock_all_apis):
        """Test configuration validation in integration."""
        # Test with missing configuration files
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir()
            
            # Only create one config file (missing the other)
            with open(config_dir / "product_blueprints.json", 'w') as f:
                json.dump({"products": {}}, f)
            
            with pytest.raises(FileNotFoundError):
                SEAEngine(config_dir=str(config_dir))
    
    def test_product_type_mapping_integration(self, complete_test_environment, mock_env_vars, mock_all_apis):
        """Test product type mapping in integration context."""
        engine = SEAEngine(
            config_dir=complete_test_environment["config_dir"],
            output_dir=complete_test_environment["output_dir"]
        )
        
        # Test different product type mappings
        test_cases = [
            ("tshirt", "tshirt_bella_canvas_3001"),
            ("t-shirt", "tshirt_bella_canvas_3001"),
            ("sweatshirt", "sweatshirt_gildan_18000"),
            ("hoodie", "sweatshirt_gildan_18000"),
            ("poster", "poster_matte_ideju"),
            ("unknown_type", "tshirt_bella_canvas_3001")  # Default
        ]
        
        for product_type, expected_blueprint in test_cases:
            blueprint_key = engine._get_blueprint_key(product_type)
            assert blueprint_key == expected_blueprint
    
    def test_sheet_data_parsing_integration(self, complete_test_environment, mock_env_vars, mock_all_apis):
        """Test Google Sheets data parsing in integration context."""
        engine = SEAEngine(
            config_dir=complete_test_environment["config_dir"],
            output_dir=complete_test_environment["output_dir"]
        )
        
        # Read products from mock sheet
        products = engine.read_products_from_sheet("test_sheet_id", "Products")
        
        # Verify parsing results
        assert len(products) == 2
        
        # Verify first product
        product1 = products[0]
        assert product1.design_name == "test_design"
        assert product1.product_type == "tshirt"
        assert product1.title == "Test T-Shirt"
        assert product1.price == 19.99
        assert product1.tags == ["test", "shirt"]
        
        # Verify second product
        product2 = products[1]
        assert product2.design_name == "test_sweatshirt"
        assert product2.product_type == "sweatshirt"
        assert product2.title == "Test Sweatshirt"
        assert product2.price == 29.99
        assert product2.tags == ["test", "sweatshirt"]
    
    def test_end_to_end_workflow_timing(self, complete_test_environment, mock_env_vars, mock_all_apis):
        """Test end-to-end workflow timing and performance."""
        engine = SEAEngine(
            config_dir=complete_test_environment["config_dir"],
            output_dir=complete_test_environment["output_dir"]
        )
        
        # Create test product
        product_data = ProductData(
            design_name="timing_test",
            design_file_path=complete_test_environment["test_design"],
            product_type="tshirt",
            title="Timing Test Product",
            description="Testing workflow timing",
            tags=["timing", "test"],
            price=19.99,
            colors=["black"],
            variations=["crew_neck"],
            row_number=2
        )
        
        # Process product and measure timing
        result = engine.process_single_product(product_data)
        
        # Verify timing is reasonable (should be very fast with mocks)
        assert result.execution_time > 0
        assert result.execution_time < 10  # Should be much faster with mocks
        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__])
