
#!/usr/bin/env python3
"""
Test suite for workflow orchestration and end-to-end processes.
"""

import pytest
import logging
from typing import Dict, Any
from unittest.mock import Mock, patch
from tests.factories import AirtableTestDataFactory, RelationshipTestData
from tests.utils_relations import assert_relationship_integrity


@pytest.mark.integration
class TestWorkflowOrchestration:
    """Test complete workflow orchestration."""
    
    def test_complete_product_workflow(self, airtable_client, test_data_factory):
        """Test complete product workflow from design to publication."""
        # Create complete hierarchy
        hierarchy = RelationshipTestData.complete_product_hierarchy(
            test_data_factory, airtable_client, "workflow_test"
        )
        
        # Add all created records to cleanup
        test_data_factory.created_records['collections'].append(hierarchy['collection'].id)
        test_data_factory.created_records['products'].append(hierarchy['product'].id)
        for variation in hierarchy['variations']:
            test_data_factory.created_records['variations'].append(variation.id)
        for mockup in hierarchy['mockups']:
            test_data_factory.created_records['mockups'].append(mockup.id)
        test_data_factory.created_records['listings'].append(hierarchy['listing'].id)
        
        # Verify complete workflow
        assert_relationship_integrity(airtable_client, hierarchy)
        
        # Test workflow progression
        product = hierarchy['product']
        
        # Progress through workflow stages
        stages = ['Design', 'Mockup', 'Product', 'Listed', 'Published']
        for stage in stages:
            updated_product = airtable_client.update_record(
                'products', product.id, {'Status': stage}
            )
            assert updated_product.fields['Status'] == stage
    
    def test_batch_product_processing(self, airtable_client, test_data_factory):
        """Test batch processing of multiple products."""
        # Create multiple products
        products = []
        for i in range(5):
            product = test_data_factory.create_test_product(name_suffix=f"batch_{i}")
            products.append(product)
        
        # Batch update all products to 'Mockup' status
        for product in products:
            airtable_client.update_record('products', product.id, {'Status': 'Mockup'})
        
        # Verify all updates
        for product in products:
            updated_product = airtable_client.get_record('products', product.id)
            assert updated_product.fields['Status'] == 'Mockup'
    
    def test_workflow_error_recovery(self, airtable_client, test_data_factory):
        """Test workflow error handling and recovery."""
        # Create product
        product = test_data_factory.create_test_product("error_recovery_test")
        
        # Simulate error during status update
        try:
            # Try to update with invalid status
            airtable_client.update_record('products', product.id, {'Status': 'InvalidStatus'})
        except Exception:
            # Expected error - verify product is still in original state
            current_product = airtable_client.get_record('products', product.id)
            assert current_product.fields['Status'] == 'Design'  # Original status
        
        # Verify recovery - valid update should work
        updated_product = airtable_client.update_record('products', product.id, {'Status': 'Mockup'})
        assert updated_product.fields['Status'] == 'Mockup'


@pytest.mark.integration
class TestAPIIntegrationWorkflow:
    """Test workflow integration with external APIs."""
    
    @patch('src.api.etsy_client.EtsyClient')
    def test_etsy_listing_workflow(self, mock_etsy_client, airtable_client, test_data_factory, mock_api_responses):
        """Test Etsy listing creation workflow."""
        # Setup mock
        mock_etsy_instance = Mock()
        mock_etsy_client.return_value = mock_etsy_instance
        mock_etsy_instance.create_listing.return_value = mock_api_responses['etsy']['create_listing']
        
        # Create product ready for listing
        product = test_data_factory.create_test_product("etsy_workflow_test")
        airtable_client.update_record('products', product.id, {'Status': 'Product'})
        
        # Create listing
        listing = test_data_factory.create_test_listing(product.id, "etsy_workflow_test")
        
        # Simulate Etsy listing creation
        etsy_response = mock_etsy_instance.create_listing.return_value
        
        # Update listing with Etsy data
        updated_listing = airtable_client.update_record('listings', listing.id, {
            'Status': 'Active',
            'External ID': str(etsy_response['listing_id']),
            'URL': etsy_response['url']
        })
        
        # Verify integration
        assert updated_listing.fields['Status'] == 'Active'
        assert updated_listing.fields['External ID'] == str(etsy_response['listing_id'])
        assert mock_etsy_instance.create_listing.called
    
    @patch('src.api.printify_client.PrintifyClient')
    def test_printify_product_workflow(self, mock_printify_client, airtable_client, test_data_factory, mock_api_responses):
        """Test Printify product creation workflow."""
        # Setup mock
        mock_printify_instance = Mock()
        mock_printify_client.return_value = mock_printify_instance
        mock_printify_instance.create_product.return_value = mock_api_responses['printify']['create_product']
        
        # Create variation ready for Printify
        variation = test_data_factory.create_test_variation("printify_workflow_test")
        
        # Simulate Printify product creation
        printify_response = mock_printify_instance.create_product.return_value
        
        # Update variation with Printify data
        updated_variation = airtable_client.update_record('variations', variation.id, {
            'Status': 'Active',
            'Printify Product ID': printify_response['id']
        })
        
        # Verify integration
        assert updated_variation.fields['Status'] == 'Active'
        assert updated_variation.fields.get('Printify Product ID') == printify_response['id']
        assert mock_printify_instance.create_product.called
    
    def test_mockup_generation_workflow(self, airtable_client, test_data_factory):
        """Test mockup generation workflow."""
        # Create variation
        variation = test_data_factory.create_test_variation("mockup_workflow_test")
        
        # Create mockup in 'Pending' status
        data = AirtableTestDataFactory.mockup_data("mockup_workflow_test")
        data['Variation'] = [variation.id]
        data['Status'] = 'Pending'
        data['Quality Score'] = 0  # Not yet generated
        
        mockup_record = airtable_client.create_record('mockups', data)
        test_data_factory.created_records['mockups'].append(mockup_record.id)
        
        # Simulate mockup generation completion
        updated_mockup = airtable_client.update_record('mockups', mockup_record.id, {
            'Status': 'Generated',
            'Quality Score': 88,
            'File Path': '/generated/mockups/test_mockup.png'
        })
        
        # Verify workflow progression
        assert updated_mockup.fields['Status'] == 'Generated'
        assert updated_mockup.fields['Quality Score'] == 88
        assert updated_mockup.fields['File Path'] == '/generated/mockups/test_mockup.png'


@pytest.mark.integration
class TestWorkflowStateManagement:
    """Test workflow state management and transitions."""
    
    def test_product_status_transitions(self, airtable_client, test_data_factory):
        """Test valid product status transitions."""
        product = test_data_factory.create_test_product("status_transition_test")
        
        # Test valid progression: Design -> Mockup -> Product -> Listed -> Published
        transitions = [
            ('Design', 'Mockup'),
            ('Mockup', 'Product'),
            ('Product', 'Listed'),
            ('Listed', 'Published')
        ]
        
        current_status = 'Design'
        for from_status, to_status in transitions:
            assert current_status == from_status
            
            updated_product = airtable_client.update_record('products', product.id, {
                'Status': to_status
            })
            assert updated_product.fields['Status'] == to_status
            current_status = to_status
    
    def test_workflow_rollback(self, airtable_client, test_data_factory):
        """Test workflow rollback capabilities."""
        product = test_data_factory.create_test_product("rollback_test")
        
        # Progress to 'Product' status
        airtable_client.update_record('products', product.id, {'Status': 'Mockup'})
        airtable_client.update_record('products', product.id, {'Status': 'Product'})
        
        # Rollback to 'Mockup' (e.g., due to quality issues)
        rolled_back_product = airtable_client.update_record('products', product.id, {
            'Status': 'Mockup'
        })
        
        assert rolled_back_product.fields['Status'] == 'Mockup'
    
    def test_concurrent_workflow_operations(self, airtable_client, test_data_factory):
        """Test concurrent workflow operations."""
        # Create multiple products
        products = []
        for i in range(3):
            product = test_data_factory.create_test_product(name_suffix=f"concurrent_{i}")
            products.append(product)
        
        # Simulate concurrent status updates
        import threading
        import time
        
        def update_product_status(product, status):
            time.sleep(0.1)  # Simulate processing time
            airtable_client.update_record('products', product.id, {'Status': status})
        
        threads = []
        for i, product in enumerate(products):
            status = ['Mockup', 'Product', 'Listed'][i]
            thread = threading.Thread(target=update_product_status, args=(product, status))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all updates completed successfully
        expected_statuses = ['Mockup', 'Product', 'Listed']
        for i, product in enumerate(products):
            updated_product = airtable_client.get_record('products', product.id)
            assert updated_product.fields['Status'] == expected_statuses[i]


@pytest.mark.stress
class TestWorkflowStressTesting:
    """Test workflow under stress conditions."""
    
    def test_high_volume_product_creation(self, airtable_client, test_data_factory):
        """Test creating many products in sequence."""
        products = []
        
        # Create 20 products
        for i in range(20):
            product = test_data_factory.create_test_product(name_suffix=f"stress_{i}")
            products.append(product)
        
        # Verify all products created successfully
        assert len(products) == 20
        for product in products:
            assert product.id is not None
            assert 'stress_' in product.fields['Product Name']
    
    def test_rapid_status_updates(self, airtable_client, test_data_factory):
        """Test rapid status updates on single product."""
        product = test_data_factory.create_test_product("rapid_update_test")
        
        # Perform rapid status updates
        statuses = ['Mockup', 'Product', 'Listed', 'Published', 'Listed', 'Product']
        
        for status in statuses:
            updated_product = airtable_client.update_record('products', product.id, {
                'Status': status
            })
            assert updated_product.fields['Status'] == status
    
    def test_complex_relationship_creation(self, airtable_client, test_data_factory):
        """Test creating complex relationship hierarchies."""
        # Create collection with multiple products, each with multiple variations and mockups
        collection = test_data_factory.create_test_collection("complex_hierarchy")
        
        products = []
        for i in range(3):
            product = test_data_factory.create_test_product(collection.id, f"complex_product_{i}")
            products.append(product)
            
            # Create variations for each product
            for j in range(2):
                variation = test_data_factory.create_test_variation(product.id, f"complex_var_{i}_{j}")
                
                # Create mockups for each variation
                for k in range(2):
                    mockup = test_data_factory.create_test_mockup(variation.id, f"complex_mock_{i}_{j}_{k}")
        
        # Verify complex hierarchy
        updated_collection = airtable_client.get_record('collections', collection.id)
        assert len(updated_collection.fields.get('Products', [])) == 3
        
        for product in products:
            updated_product = airtable_client.get_record('products', product.id)
            assert len(updated_product.fields.get('Variations', [])) == 2
