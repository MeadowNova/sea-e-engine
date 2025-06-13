
#!/usr/bin/env python3
"""
Test suite for Airtable Mockups table CRUD operations.
"""

import pytest
import logging
from typing import Dict, Any
from tests.factories import AirtableTestDataFactory
from tests.utils_relations import RelationshipValidator


@pytest.mark.integration
class TestMockupsCRUD:
    """Test CRUD operations for Mockups table."""
    
    def test_create_mockup_success(self, airtable_client, test_data_factory):
        """Test successful mockup creation."""
        # Create test mockup
        mockup = test_data_factory.create_test_mockup(name_suffix="crud_create")
        
        # Verify creation
        assert mockup is not None
        assert mockup.id is not None
        assert mockup.fields['Name'] == 'Test Mockup crud_create'
        assert mockup.fields['Status'] == 'Generated'
        assert mockup.fields['Quality Score'] == 85
        assert 'Variation' in mockup.fields
    
    def test_create_mockup_with_all_fields(self, airtable_client, test_data_factory):
        """Test mockup creation with all fields."""
        # Create variation first
        variation = test_data_factory.create_test_variation("mockup_complete")
        
        data = {
            'Name': 'Complete Test Mockup',
            'Variation': [variation.id],
            'Status': 'Approved',
            'Quality Score': 95,
            'File Path': '/test/mockups/complete_test_mockup.png',
            'Generation Date': '2025-06-12',
            'File Size': 1500000,
            'Resolution': '2000x2000',
            'Notes': 'High quality test mockup'
        }
        
        record = airtable_client.create_record('mockups', data)
        test_data_factory.created_records['mockups'].append(record.id)
        
        # Verify all fields
        assert record.fields['Name'] == 'Complete Test Mockup'
        assert record.fields['Status'] == 'Approved'
        assert record.fields['Quality Score'] == 95
        assert record.fields['File Size'] == 1500000
        assert record.fields['Resolution'] == '2000x2000'
    
    def test_read_mockup_success(self, airtable_client, test_data_factory):
        """Test successful mockup retrieval."""
        # Create test mockup
        created_mockup = test_data_factory.create_test_mockup("crud_read")
        
        # Read mockup
        retrieved_mockup = airtable_client.get_record('mockups', created_mockup.id)
        
        # Verify retrieval
        assert retrieved_mockup is not None
        assert retrieved_mockup.id == created_mockup.id
        assert retrieved_mockup.fields['Name'] == created_mockup.fields['Name']
    
    def test_update_mockup_success(self, airtable_client, test_data_factory):
        """Test successful mockup update."""
        # Create test mockup
        mockup = test_data_factory.create_test_mockup("crud_update")
        
        # Update mockup
        update_data = {
            'Name': 'Updated Mockup Name',
            'Status': 'Approved',
            'Quality Score': 92,
            'Notes': 'Updated during testing',
            'Resolution': '1200x1200'
        }
        
        updated_mockup = airtable_client.update_record('mockups', mockup.id, update_data)
        
        # Verify update
        assert updated_mockup.fields['Name'] == 'Updated Mockup Name'
        assert updated_mockup.fields['Status'] == 'Approved'
        assert updated_mockup.fields['Quality Score'] == 92
        assert updated_mockup.fields['Notes'] == 'Updated during testing'
    
    def test_delete_mockup_success(self, airtable_client, test_data_factory):
        """Test successful mockup deletion."""
        # Create test mockup
        mockup = test_data_factory.create_test_mockup("crud_delete")
        mockup_id = mockup.id
        
        # Remove from cleanup list since we're testing deletion
        test_data_factory.created_records['mockups'].remove(mockup_id)
        
        # Delete mockup
        success = airtable_client.delete_record('mockups', mockup_id)
        assert success is True
        
        # Verify deletion
        deleted_mockup = airtable_client.get_record('mockups', mockup_id)
        assert deleted_mockup is None
    
    @pytest.mark.parametrize("status", ["Generated", "Approved", "Rejected", "Pending"])
    def test_mockup_status_values(self, airtable_client, test_data_factory, status):
        """Test different mockup status values."""
        data = AirtableTestDataFactory.mockup_data(name_suffix="status_test")
        data['Status'] = status
        
        record = airtable_client.create_record('mockups', data)
        test_data_factory.created_records['mockups'].append(record.id)
        
        assert record.fields['Status'] == status
    
    @pytest.mark.parametrize("quality_score", [60, 75, 85, 95, 100])
    def test_mockup_quality_scores(self, airtable_client, test_data_factory, quality_score):
        """Test different quality score values."""
        data = AirtableTestDataFactory.mockup_data(name_suffix="quality_test")
        data['Quality Score'] = quality_score
        
        record = airtable_client.create_record('mockups', data)
        test_data_factory.created_records['mockups'].append(record.id)
        
        assert record.fields['Quality Score'] == quality_score


@pytest.mark.integration
class TestMockupsRelationships:
    """Test relationship management for Mockups table."""
    
    def test_mockup_variation_relationship(self, airtable_client, test_data_factory):
        """Test mockup-variation relationship integrity."""
        # Create variation
        variation = test_data_factory.create_test_variation("relationship_test")
        
        # Create mockup with variation
        mockup = test_data_factory.create_test_mockup(
            variation_id=variation.id,
            name_suffix="relationship_test"
        )
        
        # Validate relationship
        validator = RelationshipValidator(airtable_client)
        is_valid = validator.validate_variation_mockup_relationship(variation.id, mockup.id)
        assert is_valid is True
    
    def test_multiple_mockups_per_variation(self, airtable_client, test_data_factory):
        """Test multiple mockups for single variation."""
        # Create variation
        variation = test_data_factory.create_test_variation("multiple_mockups")
        
        # Create multiple mockups
        mockups = []
        for i in range(3):
            mockup = test_data_factory.create_test_mockup(
                variation_id=variation.id,
                name_suffix=f"multiple_mockups_{i}"
            )
            mockups.append(mockup)
        
        # Verify variation has all mockups linked
        updated_variation = airtable_client.get_record('variations', variation.id)
        mockup_ids = updated_variation.fields.get('Mockups', [])
        
        for mockup in mockups:
            assert mockup.id in mockup_ids
        
        # Verify each mockup links back to variation
        for mockup in mockups:
            updated_mockup = airtable_client.get_record('mockups', mockup.id)
            assert variation.id in updated_mockup.fields['Variation']


@pytest.mark.integration
class TestMockupsValidation:
    """Test data validation for Mockups table."""
    
    def test_create_mockup_missing_name(self, airtable_client):
        """Test mockup creation fails without required name field."""
        data = {
            'Status': 'Generated',
            'Quality Score': 85
        }
        
        with pytest.raises(Exception):
            airtable_client.create_record('mockups', data)
    
    def test_mockup_quality_score_range(self, airtable_client, test_data_factory):
        """Test quality score validation."""
        # Test valid scores
        valid_scores = [0, 50, 85, 100]
        
        for score in valid_scores:
            data = AirtableTestDataFactory.mockup_data(f"score_{score}")
            data['Quality Score'] = score
            
            record = airtable_client.create_record('mockups', data)
            test_data_factory.created_records['mockups'].append(record.id)
            
            assert record.fields['Quality Score'] == score
    
    def test_mockup_file_size_validation(self, airtable_client, test_data_factory):
        """Test file size field validation."""
        data = AirtableTestDataFactory.mockup_data("file_size_test")
        data['File Size'] = 2500000  # 2.5MB
        
        record = airtable_client.create_record('mockups', data)
        test_data_factory.created_records['mockups'].append(record.id)
        
        assert record.fields['File Size'] == 2500000
    
    def test_mockup_resolution_formats(self, airtable_client, test_data_factory):
        """Test different resolution format values."""
        resolutions = ['1080x1080', '1200x1200', '2000x2000', '3000x3000']
        
        for resolution in resolutions:
            data = AirtableTestDataFactory.mockup_data(f"resolution_{resolution}")
            data['Resolution'] = resolution
            
            record = airtable_client.create_record('mockups', data)
            test_data_factory.created_records['mockups'].append(record.id)
            
            assert record.fields['Resolution'] == resolution


@pytest.mark.integration
class TestMockupsSearch:
    """Test search and filtering for Mockups table."""
    
    def test_filter_mockups_by_status(self, airtable_client, test_data_factory):
        """Test filtering mockups by status."""
        # Create mockups with different statuses
        statuses = ['Generated', 'Approved', 'Rejected']
        created_mockups = []
        
        for status in statuses:
            data = AirtableTestDataFactory.mockup_data(f"filter_{status.lower()}")
            data['Status'] = status
            
            record = airtable_client.create_record('mockups', data)
            test_data_factory.created_records['mockups'].append(record.id)
            created_mockups.append(record)
        
        # Filter by status
        filter_formula = "Status = 'Approved'"
        filtered_mockups = airtable_client.list_records('mockups', filter_formula=filter_formula)
        
        # Verify filtering
        approved_mockups = [m for m in created_mockups if m.fields['Status'] == 'Approved']
        filtered_ids = [m.id for m in filtered_mockups]
        
        for mockup in approved_mockups:
            assert mockup.id in filtered_ids
    
    def test_filter_mockups_by_quality_score(self, airtable_client, test_data_factory):
        """Test filtering mockups by quality score range."""
        # Create mockups with different quality scores
        scores = [65, 80, 95]
        created_mockups = []
        
        for score in scores:
            data = AirtableTestDataFactory.mockup_data(f"filter_score_{score}")
            data['Quality Score'] = score
            
            record = airtable_client.create_record('mockups', data)
            test_data_factory.created_records['mockups'].append(record.id)
            created_mockups.append(record)
        
        # Filter by quality score >= 80
        filter_formula = "{Quality Score} >= 80"
        filtered_mockups = airtable_client.list_records('mockups', filter_formula=filter_formula)
        
        # Verify filtering
        high_quality_mockups = [m for m in created_mockups if m.fields['Quality Score'] >= 80]
        filtered_ids = [m.id for m in filtered_mockups]
        
        for mockup in high_quality_mockups:
            assert mockup.id in filtered_ids
    
    def test_filter_mockups_by_generation_date(self, airtable_client, test_data_factory):
        """Test filtering mockups by generation date."""
        # Create mockups with different dates
        dates = ['2025-06-10', '2025-06-11', '2025-06-12']
        created_mockups = []
        
        for date in dates:
            data = AirtableTestDataFactory.mockup_data(f"filter_date_{date}")
            data['Generation Date'] = date
            
            record = airtable_client.create_record('mockups', data)
            test_data_factory.created_records['mockups'].append(record.id)
            created_mockups.append(record)
        
        # Filter by specific date
        target_date = '2025-06-12'
        filter_formula = f"{{Generation Date}} = '{target_date}'"
        filtered_mockups = airtable_client.list_records('mockups', filter_formula=filter_formula)
        
        # Verify filtering
        target_mockups = [m for m in created_mockups if m.fields['Generation Date'] == target_date]
        filtered_ids = [m.id for m in filtered_mockups]
        
        for mockup in target_mockups:
            assert mockup.id in filtered_ids
