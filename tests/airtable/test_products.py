
#!/usr/bin/env python3
"""
Test suite for Airtable Products table CRUD operations.
"""

import pytest
import logging
from typing import Dict, Any
from tests.factories import AirtableTestDataFactory, RelationshipTestData
from tests.utils_relations import RelationshipValidator, assert_relationship_integrity


@pytest.mark.integration
class TestProductsCRUD:
    """Test CRUD operations for Products table."""
    
    def test_create_product_success(self, airtable_client, test_data_factory):
        """Test successful product creation."""
        # Create test product
        product = test_data_factory.create_test_product(name_suffix="crud_create")
        
        # Verify creation
        assert product is not None
        assert product.id is not None
        assert product.fields['Name'] == 'Test Product crud_create'
        assert product.fields['Status'] == 'Design'
        assert product.fields['Priority'] == 'Medium'
        assert 'Collection' in product.fields
    
    def test_create_product_with_collection(self, airtable_client, test_data_factory):
        """Test product creation with collection relationship."""
        # Create collection first
        collection = test_data_factory.create_test_collection("product_collection")
        
        # Create product linked to collection
        product = test_data_factory.create_test_product(
            collection_id=collection.id, 
            name_suffix="with_collection"
        )
        
        # Verify relationship
        assert product.fields['Collection'] == [collection.id]
        
        # Verify back-link in collection
        updated_collection = airtable_client.get_record('collections', collection.id)
        assert product.id in updated_collection.fields.get('Products', [])
    
    def test_read_product_success(self, airtable_client, test_data_factory):
        """Test successful product retrieval."""
        # Create test product
        created_product = test_data_factory.create_test_product("crud_read")
        
        # Read product
        retrieved_product = airtable_client.get_record('products', created_product.id)
        
        # Verify retrieval
        assert retrieved_product is not None
        assert retrieved_product.id == created_product.id
        assert retrieved_product.fields['Name'] == created_product.fields['Name']
    
    def test_update_product_success(self, airtable_client, test_data_factory):
        """Test successful product update."""
        # Create test product
        product = test_data_factory.create_test_product("crud_update")
        
        # Update product
        update_data = {
            'Name': 'Updated Product Name',
            'Status': 'Mockup',
            'Priority': 'High',
            'Target Price': 29.99,
            'Tags': ['updated', 'test']
        }
        
        updated_product = airtable_client.update_record('products', product.id, update_data)
        
        # Verify update
        assert updated_product.fields['Name'] == 'Updated Product Name'
        assert updated_product.fields['Status'] == 'Mockup'
        assert updated_product.fields['Priority'] == 'High'
        assert updated_product.fields['Target Price'] == 29.99
        assert 'updated' in updated_product.fields['Tags']
    
    def test_delete_product_success(self, airtable_client, test_data_factory):
        """Test successful product deletion."""
        # Create test product
        product = test_data_factory.create_test_product("crud_delete")
        product_id = product.id
        
        # Remove from cleanup list since we're testing deletion
        test_data_factory.created_records['products'].remove(product_id)
        
        # Delete product
        success = airtable_client.delete_record('products', product_id)
        assert success is True
        
        # Verify deletion
        deleted_product = airtable_client.get_record('products', product_id)
        assert deleted_product is None
    
    @pytest.mark.parametrize("status", ["Design", "Mockup", "Product", "Listed", "Published"])
    def test_product_status_workflow(self, airtable_client, test_data_factory, status):
        """Test different product status values in workflow."""
        data = AirtableTestDataFactory.product_data(name_suffix="status_test")
        data['Status'] = status
        
        record = airtable_client.create_record('products', data)
        test_data_factory.created_records['products'].append(record.id)
        
        assert record.fields['Status'] == status


@pytest.mark.integration
class TestProductsRelationships:
    """Test relationship management for Products table."""
    
    def test_product_collection_relationship(self, airtable_client, test_data_factory):
        """Test product-collection relationship integrity."""
        # Create collection
        collection = test_data_factory.create_test_collection("relationship_test")
        
        # Create product with collection
        product = test_data_factory.create_test_product(
            collection_id=collection.id,
            name_suffix="relationship_test"
        )
        
        # Validate relationship
        validator = RelationshipValidator(airtable_client)
        is_valid = validator.validate_collection_product_relationship(collection.id, product.id)
        assert is_valid is True
    
    def test_product_variations_relationship(self, airtable_client, test_data_factory):
        """Test product-variations relationship."""
        # Create product
        product = test_data_factory.create_test_product("variations_test")
        
        # Create multiple variations
        variations = []
        for i in range(3):
            variation = test_data_factory.create_test_variation(
                product_id=product.id,
                name_suffix=f"variations_test_{i}"
            )
            variations.append(variation)
        
        # Verify product has all variations linked
        updated_product = airtable_client.get_record('products', product.id)
        variation_ids = updated_product.fields.get('Variations', [])
        
        for variation in variations:
            assert variation.id in variation_ids
    
    def test_product_listings_relationship(self, airtable_client, test_data_factory):
        """Test product-listings relationship."""
        # Create product
        product = test_data_factory.create_test_product("listings_test")
        
        # Create listing
        listing = test_data_factory.create_test_listing(
            product_id=product.id,
            name_suffix="listings_test"
        )
        
        # Verify relationship
        validator = RelationshipValidator(airtable_client)
        is_valid = validator.validate_product_listing_relationship(product.id, listing.id)
        assert is_valid is True
    
    def test_complete_product_hierarchy(self, airtable_client, test_data_factory):
        """Test complete product hierarchy creation and relationships."""
        # Create complete hierarchy
        hierarchy = RelationshipTestData.complete_product_hierarchy(
            test_data_factory, airtable_client, "hierarchy_test"
        )
        
        # Add all created records to cleanup
        test_data_factory.created_records['collections'].append(hierarchy['collection'].id)
        test_data_factory.created_records['products'].append(hierarchy['product'].id)
        for variation in hierarchy['variations']:
            test_data_factory.created_records['variations'].append(variation.id)
        for mockup in hierarchy['mockups']:
            test_data_factory.created_records['mockups'].append(mockup.id)
        test_data_factory.created_records['listings'].append(hierarchy['listing'].id)
        
        # Validate all relationships
        assert_relationship_integrity(airtable_client, hierarchy)


@pytest.mark.integration
class TestProductsValidation:
    """Test data validation for Products table."""
    
    def test_create_product_missing_name(self, airtable_client):
        """Test product creation fails without required name field."""
        data = {
            'Description': 'Product without name',
            'Status': 'Design'
        }
        
        with pytest.raises(Exception):
            airtable_client.create_record('products', data)
    
    def test_product_price_validation(self, airtable_client, test_data_factory):
        """Test product price field validation."""
        data = AirtableTestDataFactory.product_data("price_test")
        data['Target Price'] = 25.99
        
        record = airtable_client.create_record('products', data)
        test_data_factory.created_records['products'].append(record.id)
        
        assert record.fields['Target Price'] == 25.99
    
    def test_product_tags_array(self, airtable_client, test_data_factory):
        """Test product tags as array field."""
        data = AirtableTestDataFactory.product_data("tags_test")
        data['Tags'] = ['tag1', 'tag2', 'tag3']
        
        record = airtable_client.create_record('products', data)
        test_data_factory.created_records['products'].append(record.id)
        
        assert 'tag1' in record.fields['Tags']
        assert 'tag2' in record.fields['Tags']
        assert 'tag3' in record.fields['Tags']


@pytest.mark.integration
class TestProductsSearch:
    """Test search and filtering for Products table."""
    
    def test_filter_products_by_status(self, airtable_client, test_data_factory):
        """Test filtering products by status."""
        # Create products with different statuses
        statuses = ['Design', 'Mockup', 'Product']
        created_products = []
        
        for status in statuses:
            data = AirtableTestDataFactory.product_data(f"filter_{status.lower()}")
            data['Status'] = status
            
            record = airtable_client.create_record('products', data)
            test_data_factory.created_records['products'].append(record.id)
            created_products.append(record)
        
        # Filter by status
        filter_formula = "Status = 'Design'"
        filtered_products = airtable_client.list_records('products', filter_formula=filter_formula)
        
        # Verify filtering
        design_products = [p for p in created_products if p.fields['Status'] == 'Design']
        filtered_ids = [p.id for p in filtered_products]
        
        for product in design_products:
            assert product.id in filtered_ids
    
    def test_filter_products_by_collection(self, airtable_client, test_data_factory):
        """Test filtering products by collection."""
        # Create collection
        collection = test_data_factory.create_test_collection("filter_collection")
        
        # Create products in collection
        products_in_collection = []
        for i in range(2):
            product = test_data_factory.create_test_product(
                collection_id=collection.id,
                name_suffix=f"filter_collection_{i}"
            )
            products_in_collection.append(product)
        
        # Create product not in collection
        other_product = test_data_factory.create_test_product("filter_other")
        
        # Filter by collection
        filter_formula = f"FIND('{collection.id}', ARRAYJOIN(Collection, ',')) > 0"
        filtered_products = airtable_client.list_records('products', filter_formula=filter_formula)
        
        # Verify filtering
        filtered_ids = [p.id for p in filtered_products]
        
        for product in products_in_collection:
            assert product.id in filtered_ids
        
        assert other_product.id not in filtered_ids
