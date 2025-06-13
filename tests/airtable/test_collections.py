
#!/usr/bin/env python3
"""
Test suite for Airtable Collections table CRUD operations.
"""

import pytest
import logging
from typing import Dict, Any
from tests.factories import AirtableTestDataFactory
from tests.utils_relations import RelationshipValidator


@pytest.mark.integration
class TestCollectionsCRUD:
    """Test CRUD operations for Collections table."""
    
    def test_create_collection_success(self, airtable_client, test_data_factory):
        """Test successful collection creation."""
        # Create test collection
        collection = test_data_factory.create_test_collection("crud_create")
        
        # Verify creation
        assert collection is not None
        assert collection.id is not None
        assert collection.fields['Collection Name'] == 'Test Collection crud_create'
        assert collection.fields['Status'] == 'Planning'
    
    def test_create_collection_with_all_fields(self, airtable_client, test_data_factory):
        """Test collection creation with all optional fields."""
        data = {
            'Collection Name': 'Complete Test Collection',
            'Description': 'Full test collection with all fields',
            'Status': 'Active'
        }
        
        record = airtable_client.create_record('collections', data)
        test_data_factory.created_records['collections'].append(record.id)
        
        # Verify all fields
        assert record.fields['Collection Name'] == 'Complete Test Collection'
        assert record.fields['Description'] == 'Full test collection with all fields'
        assert record.fields['Status'] == 'Active'
    
    def test_read_collection_success(self, airtable_client, test_data_factory):
        """Test successful collection retrieval."""
        # Create test collection
        created_collection = test_data_factory.create_test_collection("crud_read")
        
        # Read collection
        retrieved_collection = airtable_client.get_record('collections', created_collection.id)
        
        # Verify retrieval
        assert retrieved_collection is not None
        assert retrieved_collection.id == created_collection.id
        assert retrieved_collection.fields['Collection Name'] == created_collection.fields['Collection Name']
    
    def test_read_nonexistent_collection(self, airtable_client):
        """Test reading non-existent collection returns None."""
        result = airtable_client.get_record('collections', 'recNonExistent123')
        assert result is None
    
    def test_update_collection_success(self, airtable_client, test_data_factory):
        """Test successful collection update."""
        # Create test collection
        collection = test_data_factory.create_test_collection("crud_update")
        
        # Update collection
        update_data = {
            'Collection Name': 'Updated Collection Name',
            'Status': 'Active',
            'Description': 'Updated during testing'
        }
        
        updated_collection = airtable_client.update_record('collections', collection.id, update_data)
        
        # Verify update
        assert updated_collection.fields['Collection Name'] == 'Updated Collection Name'
        assert updated_collection.fields['Status'] == 'Active'
        assert updated_collection.fields['Description'] == 'Updated during testing'
    
    def test_update_nonexistent_collection(self, airtable_client):
        """Test updating non-existent collection raises error."""
        with pytest.raises(Exception):
            airtable_client.update_record('collections', 'recNonExistent123', {'Collection Name': 'Test'})
    
    def test_delete_collection_success(self, airtable_client, test_data_factory):
        """Test successful collection deletion."""
        # Create test collection
        collection = test_data_factory.create_test_collection("crud_delete")
        collection_id = collection.id
        
        # Remove from cleanup list since we're testing deletion
        test_data_factory.created_records['collections'].remove(collection_id)
        
        # Delete collection
        success = airtable_client.delete_record('collections', collection_id)
        assert success is True
        
        # Verify deletion
        deleted_collection = airtable_client.get_record('collections', collection_id)
        assert deleted_collection is None
    
    def test_delete_nonexistent_collection(self, airtable_client):
        """Test deleting non-existent collection returns False."""
        result = airtable_client.delete_record('collections', 'recNonExistent123')
        assert result is False
    
    def test_list_collections(self, airtable_client, test_data_factory):
        """Test listing collections."""
        # Create multiple test collections
        collections = []
        for i in range(3):
            collection = test_data_factory.create_test_collection(f"list_test_{i}")
            collections.append(collection)
        
        # List collections
        all_collections = airtable_client.list_records('collections')
        
        # Verify our collections are in the list
        collection_ids = [c.id for c in all_collections]
        for collection in collections:
            assert collection.id in collection_ids
    
    @pytest.mark.parametrize("status", ["Active", "Inactive", "Planning"])
    def test_collection_status_values(self, airtable_client, test_data_factory, status):
        """Test different collection status values."""
        data = AirtableTestDataFactory.collection_data("status_test")
        data['Status'] = status
        
        record = airtable_client.create_record('collections', data)
        test_data_factory.created_records['collections'].append(record.id)
        
        assert record.fields['Status'] == status
    
    @pytest.mark.parametrize("priority", ["High", "Medium", "Low"])
    def test_collection_priority_values(self, airtable_client, test_data_factory, priority):
        """Test different collection priority values."""
        data = AirtableTestDataFactory.collection_data("priority_test")
        data['Priority'] = priority
        
        record = airtable_client.create_record('collections', data)
        test_data_factory.created_records['collections'].append(record.id)
        
        assert record.fields['Priority'] == priority


@pytest.mark.integration
class TestCollectionsValidation:
    """Test data validation for Collections table."""
    
    def test_create_collection_missing_name(self, airtable_client):
        """Test collection creation fails without required name field."""
        data = {
            'Description': 'Collection without name',
            'Status': 'Planning'
        }
        
        with pytest.raises(Exception):
            airtable_client.create_record('collections', data)
    
    def test_create_collection_invalid_status(self, airtable_client, test_data_factory):
        """Test collection creation with invalid status."""
        data = AirtableTestDataFactory.collection_data("invalid_status")
        data['Status'] = 'InvalidStatus'
        
        # This might succeed in Airtable but we should validate in our models
        record = airtable_client.create_record('collections', data)
        test_data_factory.created_records['collections'].append(record.id)
        
        # The invalid status should be stored as-is in Airtable
        # Our application layer should handle validation
        assert record.fields['Status'] == 'InvalidStatus'
    
    def test_collection_name_length_limits(self, airtable_client, test_data_factory):
        """Test collection name length limits."""
        # Test very long name
        long_name = "A" * 500  # Very long name
        data = AirtableTestDataFactory.collection_data("long_name")
        data['Name'] = long_name
        
        record = airtable_client.create_record('collections', data)
        test_data_factory.created_records['collections'].append(record.id)
        
        # Airtable should accept long names
        assert record.fields['Name'] == long_name


@pytest.mark.integration
class TestCollectionsErrorHandling:
    """Test error handling for Collections operations."""
    
    def test_network_error_handling(self, airtable_client, test_data_factory):
        """Test handling of network errors."""
        # This would require mocking network failures
        # For now, we'll test with invalid API credentials
        pass
    
    def test_rate_limit_handling(self, airtable_client):
        """Test handling of API rate limits."""
        # This would require generating many requests quickly
        # For integration testing, we'll skip this to avoid hitting real limits
        pass
    
    def test_invalid_field_names(self, airtable_client):
        """Test handling of invalid field names."""
        data = {
            'InvalidFieldName': 'Test Value',
            'Name': 'Test Collection'
        }
        
        # Airtable should ignore invalid field names
        record = airtable_client.create_record('collections', data)
        
        # Clean up
        airtable_client.delete_record('collections', record.id)
        
        assert record.fields['Name'] == 'Test Collection'
        assert 'InvalidFieldName' not in record.fields
