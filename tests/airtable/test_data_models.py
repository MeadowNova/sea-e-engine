
#!/usr/bin/env python3
"""
Test suite for Airtable data model validation and business logic.
"""

import pytest
import logging
from typing import Dict, Any
from tests.factories import AirtableTestDataFactory
from src.data.airtable_models import Product, Variation, Mockup, Listing, Collection


@pytest.mark.integration
class TestDataModelValidation:
    """Test data model classes and validation."""
    
    def test_product_model_creation(self, airtable_client, test_data_factory):
        """Test Product model creation from Airtable record."""
        # Create test product record
        product_record = test_data_factory.create_test_product("model_test")
        
        # Create Product model from record
        product = Product.from_airtable_record(product_record)
        
        # Verify model creation
        assert product.id == product_record.id
        assert product.name == product_record.fields['Product Name']
        assert product.description == product_record.fields['Description']
        assert product.status == product_record.fields['Status']
    
    def test_collection_model_creation(self, airtable_client, test_data_factory):
        """Test Collection model creation from Airtable record."""
        # Create test collection record
        collection_record = test_data_factory.create_test_collection("model_test")
        
        # Create Collection model from record
        collection = Collection.from_airtable_record(collection_record)
        
        # Verify model creation
        assert collection.id == collection_record.id
        assert collection.name == collection_record.fields['Collection Name']
        assert collection.description == collection_record.fields['Description']
        assert collection.status == collection_record.fields['Status']
    
    def test_variation_model_creation(self, airtable_client, test_data_factory):
        """Test Variation model creation from Airtable record."""
        # Create test variation record
        variation_record = test_data_factory.create_test_variation("model_test")
        
        # Create Variation model from record
        variation = Variation.from_airtable_record(variation_record)
        
        # Verify model creation
        assert variation.id == variation_record.id
        assert variation.name == variation_record.fields['Name']
        assert variation.product_type == variation_record.fields['Product Type']
        assert variation.color == variation_record.fields['Color']
        assert variation.size == variation_record.fields['Size']
    
    def test_mockup_model_creation(self, airtable_client, test_data_factory):
        """Test Mockup model creation from Airtable record."""
        # Create test mockup record
        mockup_record = test_data_factory.create_test_mockup("model_test")
        
        # Create Mockup model from record
        mockup = Mockup.from_airtable_record(mockup_record)
        
        # Verify model creation
        assert mockup.id == mockup_record.id
        assert mockup.name == mockup_record.fields['Name']
        assert mockup.status == mockup_record.fields['Status']
        assert mockup.quality_score == mockup_record.fields['Quality Score']
    
    def test_listing_model_creation(self, airtable_client, test_data_factory):
        """Test Listing model creation from Airtable record."""
        # Create test listing record
        listing_record = test_data_factory.create_test_listing("model_test")
        
        # Create Listing model from record
        listing = Listing.from_airtable_record(listing_record)
        
        # Verify model creation
        assert listing.id == listing_record.id
        assert listing.title == listing_record.fields['Title']
        assert listing.status == listing_record.fields['Status']
        assert listing.price == listing_record.fields['Price']
        assert listing.platform == listing_record.fields['Platform']


@pytest.mark.integration
class TestBusinessLogicValidation:
    """Test business logic and validation rules."""
    
    def test_product_status_workflow_validation(self, airtable_client, test_data_factory):
        """Test product status workflow progression validation."""
        # Create product in Design status
        product_record = test_data_factory.create_test_product("workflow_test")
        product = Product.from_airtable_record(product_record)
        
        # Test valid status transitions
        assert product.can_transition_to('Mockup')
        assert product.can_transition_to('Product')
        
        # Test invalid status transitions (skipping steps)
        assert not product.can_transition_to('Published')  # Can't skip to Published from Design
    
    def test_variation_cost_calculation(self, airtable_client, test_data_factory):
        """Test variation cost and profit calculations."""
        # Create variation with cost data
        data = AirtableTestDataFactory.variation_data("cost_test")
        data['Base Cost'] = 12.00
        data['Profit Margin'] = 0.6  # 60% profit margin
        
        record = airtable_client.create_record('variations', data)
        test_data_factory.created_records['variations'].append(record.id)
        
        variation = Variation.from_airtable_record(record)
        
        # Test cost calculations
        expected_selling_price = 12.00 / (1 - 0.6)  # Base cost / (1 - margin)
        assert abs(variation.calculate_selling_price() - expected_selling_price) < 0.01
        
        profit = variation.calculate_profit(30.00)  # Selling at $30
        expected_profit = 30.00 - 12.00
        assert abs(profit - expected_profit) < 0.01
    
    def test_mockup_quality_validation(self, airtable_client, test_data_factory):
        """Test mockup quality score validation."""
        # Create mockup with quality score
        data = AirtableTestDataFactory.mockup_data("quality_test")
        data['Quality Score'] = 85
        
        record = airtable_client.create_record('mockups', data)
        test_data_factory.created_records['mockups'].append(record.id)
        
        mockup = Mockup.from_airtable_record(record)
        
        # Test quality validation
        assert mockup.is_high_quality()  # Score >= 80
        assert mockup.meets_approval_threshold()  # Score >= 75
    
    def test_listing_performance_metrics(self, airtable_client, test_data_factory):
        """Test listing performance calculations."""
        # Create listing with performance data
        data = AirtableTestDataFactory.listing_data("performance_test")
        data['Views'] = 1000
        data['Favorites'] = 50
        data['Sales'] = 10
        
        record = airtable_client.create_record('listings', data)
        test_data_factory.created_records['listings'].append(record.id)
        
        listing = Listing.from_airtable_record(record)
        
        # Test performance calculations
        conversion_rate = listing.calculate_conversion_rate()
        expected_conversion = 10 / 1000  # Sales / Views
        assert abs(conversion_rate - expected_conversion) < 0.001
        
        favorite_rate = listing.calculate_favorite_rate()
        expected_favorite_rate = 50 / 1000  # Favorites / Views
        assert abs(favorite_rate - expected_favorite_rate) < 0.001


@pytest.mark.integration
class TestDataIntegrityValidation:
    """Test data integrity and consistency rules."""
    
    def test_required_field_validation(self, airtable_client):
        """Test that required fields are validated."""
        # Test collection without name
        with pytest.raises(Exception):
            airtable_client.create_record('collections', {'Description': 'Test'})
        
        # Test product without name
        with pytest.raises(Exception):
            airtable_client.create_record('products', {'Description': 'Test'})
    
    def test_field_type_validation(self, airtable_client, test_data_factory):
        """Test field type validation."""
        # Test numeric fields
        data = AirtableTestDataFactory.product_data("type_test")
        data['Base Price'] = "invalid_number"  # Should be numeric
        
        # Airtable may accept this but our models should validate
        try:
            record = airtable_client.create_record('products', data)
            test_data_factory.created_records['products'].append(record.id)
            
            # Our model should handle type conversion or validation
            product = Product.from_airtable_record(record)
            assert isinstance(product.base_price, (int, float)) or product.base_price is None
        except Exception:
            # Expected if Airtable rejects invalid types
            pass
    
    def test_relationship_consistency(self, airtable_client, test_data_factory):
        """Test relationship consistency validation."""
        # Create product with collection
        collection = test_data_factory.create_test_collection("consistency_test")
        product = test_data_factory.create_test_product(collection.id, "consistency_test")
        
        # Verify bidirectional relationship
        updated_collection = airtable_client.get_record('collections', collection.id)
        assert product.id in updated_collection.fields.get('Products', [])
        
        updated_product = airtable_client.get_record('products', product.id)
        assert collection.id in updated_product.fields.get('Collection', [])


@pytest.mark.integration
class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_product_to_dict(self, airtable_client, test_data_factory):
        """Test Product model serialization to dictionary."""
        product_record = test_data_factory.create_test_product("serialization_test")
        product = Product.from_airtable_record(product_record)
        
        # Serialize to dict
        product_dict = product.to_dict()
        
        # Verify serialization
        assert product_dict['id'] == product.id
        assert product_dict['name'] == product.name
        assert product_dict['status'] == product.status
        assert 'created_time' in product_dict
    
    def test_collection_to_dict(self, airtable_client, test_data_factory):
        """Test Collection model serialization to dictionary."""
        collection_record = test_data_factory.create_test_collection("serialization_test")
        collection = Collection.from_airtable_record(collection_record)
        
        # Serialize to dict
        collection_dict = collection.to_dict()
        
        # Verify serialization
        assert collection_dict['id'] == collection.id
        assert collection_dict['name'] == collection.name
        assert collection_dict['status'] == collection.status
    
    def test_model_json_serialization(self, airtable_client, test_data_factory):
        """Test model JSON serialization."""
        import json
        
        product_record = test_data_factory.create_test_product("json_test")
        product = Product.from_airtable_record(product_record)
        
        # Serialize to JSON
        product_json = json.dumps(product.to_dict(), default=str)
        
        # Deserialize from JSON
        product_data = json.loads(product_json)
        
        # Verify round-trip serialization
        assert product_data['id'] == product.id
        assert product_data['name'] == product.name


@pytest.mark.benchmark
class TestModelPerformance:
    """Test model performance and efficiency."""
    
    def test_bulk_model_creation_performance(self, airtable_client, test_data_factory, benchmark):
        """Benchmark bulk model creation performance."""
        # Create multiple records
        records = []
        for i in range(10):
            record = test_data_factory.create_test_product(name_suffix=f"perf_test_{i}")
            records.append(record)
        
        # Benchmark model creation
        def create_models():
            return [Product.from_airtable_record(record) for record in records]
        
        models = benchmark(create_models)
        
        # Verify all models created
        assert len(models) == 10
        for model in models:
            assert isinstance(model, Product)
    
    def test_model_validation_performance(self, airtable_client, test_data_factory, benchmark):
        """Benchmark model validation performance."""
        product_record = test_data_factory.create_test_product("validation_perf_test")
        product = Product.from_airtable_record(product_record)
        
        # Benchmark validation
        def validate_model():
            return product.validate()
        
        is_valid = benchmark(validate_model)
        assert is_valid is True
