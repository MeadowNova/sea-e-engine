
#!/usr/bin/env python3
"""
Test suite for Airtable Variations table CRUD operations.
"""

import pytest
import logging
from typing import Dict, Any
from tests.factories import AirtableTestDataFactory
from tests.utils_relations import RelationshipValidator


@pytest.mark.integration
class TestVariationsCRUD:
    """Test CRUD operations for Variations table."""
    
    def test_create_variation_success(self, airtable_client, test_data_factory):
        """Test successful variation creation."""
        # Create test variation
        variation = test_data_factory.create_test_variation(name_suffix="crud_create")
        
        # Verify creation
        assert variation is not None
        assert variation.id is not None
        assert variation.fields['Name'] == 'Test Variation crud_create'
        assert variation.fields['Status'] == 'Active'
        assert 'Product' in variation.fields
    
    def test_create_variation_with_all_fields(self, airtable_client, test_data_factory):
        """Test variation creation with all fields."""
        # Create product first
        product = test_data_factory.create_test_product("variation_complete")
        
        data = {
            'Name': 'Complete Test Variation',
            'Product': [product.id],
            'Product Type': 'Hoodie',
            'Color': 'Navy',
            'Size': 'L',
            'Status': 'Active',
            'Printify Blueprint ID': 25,
            'Printify Print Provider ID': 35,
            'Base Cost': 12.50,
            'Profit Margin': 0.6,
            'SKU': 'TEST-HOODIE-NAVY-L'
        }
        
        record = airtable_client.create_record('variations', data)
        test_data_factory.created_records['variations'].append(record.id)
        
        # Verify all fields
        assert record.fields['Name'] == 'Complete Test Variation'
        assert record.fields['Product Type'] == 'Hoodie'
        assert record.fields['Color'] == 'Navy'
        assert record.fields['Size'] == 'L'
        assert record.fields['Base Cost'] == 12.50
        assert record.fields['Profit Margin'] == 0.6
    
    def test_read_variation_success(self, airtable_client, test_data_factory):
        """Test successful variation retrieval."""
        # Create test variation
        created_variation = test_data_factory.create_test_variation("crud_read")
        
        # Read variation
        retrieved_variation = airtable_client.get_record('variations', created_variation.id)
        
        # Verify retrieval
        assert retrieved_variation is not None
        assert retrieved_variation.id == created_variation.id
        assert retrieved_variation.fields['Name'] == created_variation.fields['Name']
    
    def test_update_variation_success(self, airtable_client, test_data_factory):
        """Test successful variation update."""
        # Create test variation
        variation = test_data_factory.create_test_variation("crud_update")
        
        # Update variation
        update_data = {
            'Name': 'Updated Variation Name',
            'Color': 'Red',
            'Size': 'XL',
            'Status': 'Inactive',
            'Base Cost': 15.00,
            'Profit Margin': 0.5
        }
        
        updated_variation = airtable_client.update_record('variations', variation.id, update_data)
        
        # Verify update
        assert updated_variation.fields['Name'] == 'Updated Variation Name'
        assert updated_variation.fields['Color'] == 'Red'
        assert updated_variation.fields['Size'] == 'XL'
        assert updated_variation.fields['Status'] == 'Inactive'
        assert updated_variation.fields['Base Cost'] == 15.00
    
    def test_delete_variation_success(self, airtable_client, test_data_factory):
        """Test successful variation deletion."""
        # Create test variation
        variation = test_data_factory.create_test_variation("crud_delete")
        variation_id = variation.id
        
        # Remove from cleanup list since we're testing deletion
        test_data_factory.created_records['variations'].remove(variation_id)
        
        # Delete variation
        success = airtable_client.delete_record('variations', variation_id)
        assert success is True
        
        # Verify deletion
        deleted_variation = airtable_client.get_record('variations', variation_id)
        assert deleted_variation is None
    
    @pytest.mark.parametrize("product_type", ["T-Shirt", "Hoodie", "Tank Top", "Long Sleeve", "Poster"])
    def test_variation_product_types(self, airtable_client, test_data_factory, product_type):
        """Test different product type values."""
        data = AirtableTestDataFactory.variation_data(name_suffix="type_test")
        data['Product Type'] = product_type
        
        record = airtable_client.create_record('variations', data)
        test_data_factory.created_records['variations'].append(record.id)
        
        assert record.fields['Product Type'] == product_type
    
    @pytest.mark.parametrize("color", ["Black", "White", "Navy", "Red", "Green", "Blue"])
    def test_variation_colors(self, airtable_client, test_data_factory, color):
        """Test different color values."""
        data = AirtableTestDataFactory.variation_data(name_suffix="color_test")
        data['Color'] = color
        
        record = airtable_client.create_record('variations', data)
        test_data_factory.created_records['variations'].append(record.id)
        
        assert record.fields['Color'] == color
    
    @pytest.mark.parametrize("size", ["XS", "S", "M", "L", "XL", "XXL"])
    def test_variation_sizes(self, airtable_client, test_data_factory, size):
        """Test different size values."""
        data = AirtableTestDataFactory.variation_data(name_suffix="size_test")
        data['Size'] = size
        
        record = airtable_client.create_record('variations', data)
        test_data_factory.created_records['variations'].append(record.id)
        
        assert record.fields['Size'] == size


@pytest.mark.integration
class TestVariationsRelationships:
    """Test relationship management for Variations table."""
    
    def test_variation_product_relationship(self, airtable_client, test_data_factory):
        """Test variation-product relationship integrity."""
        # Create product
        product = test_data_factory.create_test_product("relationship_test")
        
        # Create variation with product
        variation = test_data_factory.create_test_variation(
            product_id=product.id,
            name_suffix="relationship_test"
        )
        
        # Validate relationship
        validator = RelationshipValidator(airtable_client)
        is_valid = validator.validate_product_variation_relationship(product.id, variation.id)
        assert is_valid is True
    
    def test_variation_mockups_relationship(self, airtable_client, test_data_factory):
        """Test variation-mockups relationship."""
        # Create variation
        variation = test_data_factory.create_test_variation("mockups_test")
        
        # Create multiple mockups
        mockups = []
        for i in range(2):
            mockup = test_data_factory.create_test_mockup(
                variation_id=variation.id,
                name_suffix=f"mockups_test_{i}"
            )
            mockups.append(mockup)
        
        # Verify variation has all mockups linked
        updated_variation = airtable_client.get_record('variations', variation.id)
        mockup_ids = updated_variation.fields.get('Mockups', [])
        
        for mockup in mockups:
            assert mockup.id in mockup_ids


@pytest.mark.integration
class TestVariationsValidation:
    """Test data validation for Variations table."""
    
    def test_create_variation_missing_name(self, airtable_client):
        """Test variation creation fails without required name field."""
        data = {
            'Product Type': 'T-Shirt',
            'Color': 'Black',
            'Size': 'M'
        }
        
        with pytest.raises(Exception):
            airtable_client.create_record('variations', data)
    
    def test_variation_cost_validation(self, airtable_client, test_data_factory):
        """Test variation cost field validation."""
        data = AirtableTestDataFactory.variation_data("cost_test")
        data['Base Cost'] = 14.99
        data['Profit Margin'] = 0.45
        
        record = airtable_client.create_record('variations', data)
        test_data_factory.created_records['variations'].append(record.id)
        
        assert record.fields['Base Cost'] == 14.99
        assert record.fields['Profit Margin'] == 0.45
    
    def test_variation_printify_ids(self, airtable_client, test_data_factory):
        """Test Printify ID fields."""
        data = AirtableTestDataFactory.variation_data("printify_test")
        data['Printify Blueprint ID'] = 42
        data['Printify Print Provider ID'] = 28
        
        record = airtable_client.create_record('variations', data)
        test_data_factory.created_records['variations'].append(record.id)
        
        assert record.fields['Printify Blueprint ID'] == 42
        assert record.fields['Printify Print Provider ID'] == 28


@pytest.mark.integration
class TestVariationsSearch:
    """Test search and filtering for Variations table."""
    
    def test_filter_variations_by_product_type(self, airtable_client, test_data_factory):
        """Test filtering variations by product type."""
        # Create variations with different product types
        product_types = ['T-Shirt', 'Hoodie', 'Poster']
        created_variations = []
        
        for product_type in product_types:
            data = AirtableTestDataFactory.variation_data(f"filter_{product_type.lower()}")
            data['Product Type'] = product_type
            
            record = airtable_client.create_record('variations', data)
            test_data_factory.created_records['variations'].append(record.id)
            created_variations.append(record)
        
        # Filter by product type
        filter_formula = "{Product Type} = 'T-Shirt'"
        filtered_variations = airtable_client.list_records('variations', filter_formula=filter_formula)
        
        # Verify filtering
        tshirt_variations = [v for v in created_variations if v.fields['Product Type'] == 'T-Shirt']
        filtered_ids = [v.id for v in filtered_variations]
        
        for variation in tshirt_variations:
            assert variation.id in filtered_ids
    
    def test_filter_variations_by_status(self, airtable_client, test_data_factory):
        """Test filtering variations by status."""
        # Create variations with different statuses
        statuses = ['Active', 'Inactive', 'Out of Stock']
        created_variations = []
        
        for status in statuses:
            data = AirtableTestDataFactory.variation_data(f"filter_{status.lower()}")
            data['Status'] = status
            
            record = airtable_client.create_record('variations', data)
            test_data_factory.created_records['variations'].append(record.id)
            created_variations.append(record)
        
        # Filter by status
        filter_formula = "Status = 'Active'"
        filtered_variations = airtable_client.list_records('variations', filter_formula=filter_formula)
        
        # Verify filtering
        active_variations = [v for v in created_variations if v.fields['Status'] == 'Active']
        filtered_ids = [v.id for v in filtered_variations]
        
        for variation in active_variations:
            assert variation.id in filtered_ids
    
    def test_filter_variations_by_color_and_size(self, airtable_client, test_data_factory):
        """Test filtering variations by multiple criteria."""
        # Create variations with specific color and size
        target_color = 'Black'
        target_size = 'M'
        
        # Create matching variation
        matching_data = AirtableTestDataFactory.variation_data("filter_match")
        matching_data['Color'] = target_color
        matching_data['Size'] = target_size
        
        matching_record = airtable_client.create_record('variations', matching_data)
        test_data_factory.created_records['variations'].append(matching_record.id)
        
        # Create non-matching variation
        non_matching_data = AirtableTestDataFactory.variation_data("filter_no_match")
        non_matching_data['Color'] = 'White'
        non_matching_data['Size'] = 'L'
        
        non_matching_record = airtable_client.create_record('variations', non_matching_data)
        test_data_factory.created_records['variations'].append(non_matching_record.id)
        
        # Filter by color and size
        filter_formula = f"AND(Color = '{target_color}', Size = '{target_size}')"
        filtered_variations = airtable_client.list_records('variations', filter_formula=filter_formula)
        
        # Verify filtering
        filtered_ids = [v.id for v in filtered_variations]
        
        assert matching_record.id in filtered_ids
        assert non_matching_record.id not in filtered_ids
