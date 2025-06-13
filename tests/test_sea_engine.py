
#!/usr/bin/env python3
"""
Unit tests for SEA Engine core functionality.
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

from sea_engine import SEAEngine, ProductData, WorkflowResult


class TestSEAEngine:
    """Test cases for SEA Engine core functionality."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory with test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir()
            
            # Create test product blueprints
            product_blueprints = {
                "products": {
                    "tshirt_bella_canvas_3001": {
                        "printify_config": {
                            "blueprint_id": 12,
                            "print_provider_id": 29
                        }
                    }
                }
            }
            
            with open(config_dir / "product_blueprints.json", 'w') as f:
                json.dump(product_blueprints, f)
            
            # Create test mockup blueprints
            mockup_blueprints = {
                "blueprints": {
                    "tshirt_bella_canvas_3001": {
                        "template_path": "test_template.png"
                    }
                }
            }
            
            with open(config_dir / "mockup_blueprints.json", 'w') as f:
                json.dump(mockup_blueprints, f)
            
            yield str(config_dir)
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables."""
        env_vars = {
            "ETSY_API_KEY": "test_etsy_key",
            "ETSY_REFRESH_TOKEN": "test_etsy_refresh",
            "ETSY_SHOP_ID": "test_shop_id",
            "PRINTIFY_API_KEY": "test_printify_key",
            "PRINTIFY_SHOP_ID": "test_printify_shop"
        }
        
        with patch.dict(os.environ, env_vars):
            yield env_vars
    
    @pytest.fixture
    def mock_clients(self):
        """Mock API clients."""
        with patch('sea_engine.EtsyAPIClient') as mock_etsy, \
             patch('sea_engine.PrintifyAPIClient') as mock_printify, \
             patch('sea_engine.AirtableClient') as mock_sheets, \
             patch('sea_engine.MockupGenerator') as mock_mockup, \
             patch('sea_engine.WorkflowStateManager') as mock_state:
            
            # Configure mocks
            mock_etsy.return_value.test_connection.return_value = True
            mock_printify.return_value.test_connection.return_value = True
            mock_sheets.return_value.test_connection.return_value = True
            
            yield {
                'etsy': mock_etsy,
                'printify': mock_printify,
                'sheets': mock_sheets,
                'mockup': mock_mockup,
                'state': mock_state
            }
    
    def test_engine_initialization(self, temp_config_dir, temp_output_dir, mock_env_vars, mock_clients):
        """Test SEA Engine initialization."""
        engine = SEAEngine(config_dir=temp_config_dir, output_dir=temp_output_dir)
        
        assert engine.config_dir == Path(temp_config_dir)
        assert engine.output_dir == Path(temp_output_dir)
        assert engine.product_blueprints is not None
        assert engine.mockup_blueprints is not None
    
    def test_configuration_loading(self, temp_config_dir, temp_output_dir, mock_env_vars, mock_clients):
        """Test configuration file loading."""
        engine = SEAEngine(config_dir=temp_config_dir, output_dir=temp_output_dir)
        
        # Check product blueprints loaded
        assert "products" in engine.product_blueprints
        assert "tshirt_bella_canvas_3001" in engine.product_blueprints["products"]
        
        # Check mockup blueprints loaded
        assert "blueprints" in engine.mockup_blueprints
        assert "tshirt_bella_canvas_3001" in engine.mockup_blueprints["blueprints"]
    
    def test_environment_validation_success(self, temp_config_dir, temp_output_dir, mock_env_vars, mock_clients):
        """Test successful environment validation."""
        engine = SEAEngine(config_dir=temp_config_dir, output_dir=temp_output_dir)
        
        result = engine.validate_environment()
        assert result is True
    
    def test_environment_validation_failure(self, temp_config_dir, temp_output_dir, mock_env_vars, mock_clients):
        """Test environment validation failure."""
        # Make one client fail
        mock_clients['etsy'].return_value.test_connection.return_value = False
        
        engine = SEAEngine(config_dir=temp_config_dir, output_dir=temp_output_dir)
        
        result = engine.validate_environment()
        assert result is False
    
    def test_parse_product_row_valid(self, temp_config_dir, temp_output_dir, mock_env_vars, mock_clients):
        """Test parsing valid product row."""
        engine = SEAEngine(config_dir=temp_config_dir, output_dir=temp_output_dir)
        
        headers = ["design_name", "design_file_path", "product_type", "title", "description", "price", "tags"]
        row = ["test_design", "/path/to/design.png", "tshirt", "Test Product", "Test Description", "19.99", "tag1,tag2"]
        
        product = engine._parse_product_row(row, headers, 2)
        
        assert product is not None
        assert product.design_name == "test_design"
        assert product.design_file_path == "/path/to/design.png"
        assert product.product_type == "tshirt"
        assert product.title == "Test Product"
        assert product.price == 19.99
        assert product.tags == ["tag1", "tag2"]
        assert product.row_number == 2
    
    def test_parse_product_row_missing_required(self, temp_config_dir, temp_output_dir, mock_env_vars, mock_clients):
        """Test parsing product row with missing required fields."""
        engine = SEAEngine(config_dir=temp_config_dir, output_dir=temp_output_dir)
        
        headers = ["design_name", "design_file_path", "product_type", "title"]
        row = ["test_design", "", "tshirt", "Test Product"]  # Missing design_file_path
        
        product = engine._parse_product_row(row, headers, 2)
        
        assert product is None
    
    def test_get_blueprint_key(self, temp_config_dir, temp_output_dir, mock_env_vars, mock_clients):
        """Test blueprint key mapping."""
        engine = SEAEngine(config_dir=temp_config_dir, output_dir=temp_output_dir)
        
        assert engine._get_blueprint_key("tshirt") == "tshirt_bella_canvas_3001"
        assert engine._get_blueprint_key("t-shirt") == "tshirt_bella_canvas_3001"
        assert engine._get_blueprint_key("sweatshirt") == "sweatshirt_gildan_18000"
        assert engine._get_blueprint_key("poster") == "poster_matte_ideju"
        assert engine._get_blueprint_key("unknown") == "tshirt_bella_canvas_3001"  # Default
    
    def test_process_single_product_success(self, temp_config_dir, temp_output_dir, mock_env_vars, mock_clients):
        """Test successful single product processing."""
        engine = SEAEngine(config_dir=temp_config_dir, output_dir=temp_output_dir)
        
        # Mock successful responses
        engine.mockup_generator.generate_mockup.return_value = {
            "success": True,
            "files": ["mockup1.png", "mockup2.png"]
        }
        engine.printify_client.create_product.return_value = "printify_123"
        engine.etsy_client.create_listing.return_value = "etsy_456"
        
        product_data = ProductData(
            design_name="test_design",
            design_file_path="/path/to/design.png",
            product_type="tshirt",
            title="Test Product",
            description="Test Description",
            tags=["tag1", "tag2"],
            price=19.99,
            colors=["black", "white"],
            variations=["crew_neck"],
            row_number=2
        )
        
        result = engine.process_single_product(product_data)
        
        assert result.success is True
        assert result.printify_product_id == "printify_123"
        assert result.etsy_listing_id == "etsy_456"
        assert len(result.mockup_files) == 4  # 2 colors × 1 variation × 2 files per mockup
        assert result.error_message is None
    
    def test_process_single_product_failure(self, temp_config_dir, temp_output_dir, mock_env_vars, mock_clients):
        """Test single product processing failure."""
        engine = SEAEngine(config_dir=temp_config_dir, output_dir=temp_output_dir)
        
        # Mock failure in mockup generation
        engine.mockup_generator.generate_mockup.side_effect = Exception("Mockup generation failed")
        
        product_data = ProductData(
            design_name="test_design",
            design_file_path="/path/to/design.png",
            product_type="tshirt",
            title="Test Product",
            description="Test Description",
            tags=["tag1", "tag2"],
            price=19.99,
            colors=["black"],
            variations=["crew_neck"],
            row_number=2
        )
        
        result = engine.process_single_product(product_data)
        
        assert result.success is False
        assert result.error_message is not None
        assert "Mockup generation failed" in result.error_message
    
    def test_read_products_from_sheet(self, temp_config_dir, temp_output_dir, mock_env_vars, mock_clients):
        """Test reading products from Google Sheets."""
        engine = SEAEngine(config_dir=temp_config_dir, output_dir=temp_output_dir)
        
        # Mock sheet data
        sheet_data = [
            ["design_name", "design_file_path", "product_type", "title", "description", "price"],
            ["design1", "/path/to/design1.png", "tshirt", "Product 1", "Description 1", "19.99"],
            ["design2", "/path/to/design2.png", "sweatshirt", "Product 2", "Description 2", "29.99"]
        ]
        
        engine.sheets_client.read_sheet_data.return_value = sheet_data
        
        products = engine.read_products_from_sheet("test_sheet_id", "Products")
        
        assert len(products) == 2
        assert products[0].design_name == "design1"
        assert products[0].product_type == "tshirt"
        assert products[1].design_name == "design2"
        assert products[1].product_type == "sweatshirt"
    
    def test_read_products_from_empty_sheet(self, temp_config_dir, temp_output_dir, mock_env_vars, mock_clients):
        """Test reading from empty sheet."""
        engine = SEAEngine(config_dir=temp_config_dir, output_dir=temp_output_dir)
        
        engine.sheets_client.read_sheet_data.return_value = []
        
        products = engine.read_products_from_sheet("test_sheet_id", "Products")
        
        assert len(products) == 0


class TestProductData:
    """Test cases for ProductData dataclass."""
    
    def test_product_data_creation(self):
        """Test ProductData creation with all fields."""
        product = ProductData(
            design_name="test_design",
            design_file_path="/path/to/design.png",
            product_type="tshirt",
            title="Test Product",
            description="Test Description",
            tags=["tag1", "tag2"],
            price=19.99,
            colors=["black", "white"],
            variations=["crew_neck", "v_neck"],
            row_number=2
        )
        
        assert product.design_name == "test_design"
        assert product.price == 19.99
        assert len(product.tags) == 2
        assert len(product.colors) == 2
        assert len(product.variations) == 2


class TestWorkflowResult:
    """Test cases for WorkflowResult dataclass."""
    
    def test_workflow_result_success(self):
        """Test successful WorkflowResult creation."""
        product_data = ProductData(
            design_name="test",
            design_file_path="/path",
            product_type="tshirt",
            title="Test",
            description="Test",
            tags=[],
            price=19.99,
            colors=[],
            variations=[],
            row_number=1
        )
        
        result = WorkflowResult(
            success=True,
            product_data=product_data,
            mockup_files=["file1.png", "file2.png"],
            printify_product_id="printify_123",
            etsy_listing_id="etsy_456",
            error_message=None,
            execution_time=45.5
        )
        
        assert result.success is True
        assert result.printify_product_id == "printify_123"
        assert result.etsy_listing_id == "etsy_456"
        assert result.execution_time == 45.5
        assert len(result.mockup_files) == 2
    
    def test_workflow_result_failure(self):
        """Test failed WorkflowResult creation."""
        product_data = ProductData(
            design_name="test",
            design_file_path="/path",
            product_type="tshirt",
            title="Test",
            description="Test",
            tags=[],
            price=19.99,
            colors=[],
            variations=[],
            row_number=1
        )
        
        result = WorkflowResult(
            success=False,
            product_data=product_data,
            mockup_files=[],
            printify_product_id=None,
            etsy_listing_id=None,
            error_message="Test error",
            execution_time=10.0
        )
        
        assert result.success is False
        assert result.error_message == "Test error"
        assert result.printify_product_id is None
        assert result.etsy_listing_id is None


if __name__ == "__main__":
    pytest.main([__file__])
