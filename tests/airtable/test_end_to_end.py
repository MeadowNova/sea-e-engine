
#!/usr/bin/env python3
"""
End-to-end integration tests for the complete SEA-E Engine workflow.
"""

import pytest
import logging
import time
from typing import Dict, Any
from unittest.mock import Mock, patch
from tests.factories import RelationshipTestData
from tests.utils_relations import assert_relationship_integrity, assert_no_orphaned_records


@pytest.mark.e2e
class TestCompleteWorkflow:
    """End-to-end tests for complete product lifecycle."""
    
    def test_design_to_publication_workflow(self, airtable_client, test_data_factory):
        """Test complete workflow from design creation to Etsy publication."""
        # Step 1: Create collection
        collection = test_data_factory.create_test_collection("e2e_workflow")
        assert collection.fields['Status'] == 'Planning'
        
        # Step 2: Create product in Design status
        product = test_data_factory.create_test_product(collection.id, "e2e_workflow")
        assert product.fields['Status'] == 'Design'
        
        # Step 3: Create variations for the product
        variations = []
        colors = ['Black', 'White', 'Navy']
        sizes = ['M', 'L', 'XL']
        
        for color in colors:
            for size in sizes:
                data = {
                    'Name': f'E2E Variation {color} {size}',
                    'Product': [product.id],
                    'Product Type': 'T-Shirt',
                    'Color': color,
                    'Size': size,
                    'Status': 'Active',
                    'Printify Blueprint ID': 12,
                    'Printify Print Provider ID': 29,
                    'Base Cost': 10.00,
                    'Profit Margin': 0.6
                }
                variation = airtable_client.create_record('variations', data)
                test_data_factory.created_records['variations'].append(variation.id)
                variations.append(variation)
        
        assert len(variations) == 9  # 3 colors × 3 sizes
        
        # Step 4: Progress product to Mockup status
        updated_product = airtable_client.update_record('products', product.id, {
            'Status': 'Mockup'
        })
        assert updated_product.fields['Status'] == 'Mockup'
        
        # Step 5: Generate mockups for each variation
        mockups = []
        for i, variation in enumerate(variations):
            data = {
                'Name': f'E2E Mockup {i+1}',
                'Variation': [variation.id],
                'Status': 'Generated',
                'Quality Score': 85 + (i % 10),  # Vary quality scores
                'File Path': f'/mockups/e2e_mockup_{i+1}.png',
                'Generation Date': '2025-06-12'
            }
            mockup = airtable_client.create_record('mockups', data)
            test_data_factory.created_records['mockups'].append(mockup.id)
            mockups.append(mockup)
        
        # Step 6: Approve high-quality mockups
        approved_mockups = []
        for mockup in mockups:
            if mockup.fields['Quality Score'] >= 90:
                updated_mockup = airtable_client.update_record('mockups', mockup.id, {
                    'Status': 'Approved'
                })
                approved_mockups.append(updated_mockup)
        
        # Step 7: Progress product to Product status
        updated_product = airtable_client.update_record('products', product.id, {
            'Status': 'Product'
        })
        assert updated_product.fields['Status'] == 'Product'
        
        # Step 8: Create Etsy listing
        listing_data = {
            'Title': 'E2E Test Product - Premium Quality Design',
            'Product': [product.id],
            'Status': 'Draft',
            'Price': 24.99,
            'Platform': 'Etsy',
            'Created Date': '2025-06-12',
            'Description': 'High-quality test product created through E2E workflow'
        }
        listing = airtable_client.create_record('listings', listing_data)
        test_data_factory.created_records['listings'].append(listing.id)
        
        # Step 9: Progress product to Listed status
        updated_product = airtable_client.update_record('products', product.id, {
            'Status': 'Listed'
        })
        assert updated_product.fields['Status'] == 'Listed'
        
        # Step 10: Simulate Etsy publication
        updated_listing = airtable_client.update_record('listings', listing.id, {
            'Status': 'Active',
            'External ID': 'etsy_123456789',
            'URL': 'https://etsy.com/listing/123456789',
            'Views': 0,
            'Favorites': 0,
            'Sales': 0
        })
        
        # Step 11: Progress product to Published status
        final_product = airtable_client.update_record('products', product.id, {
            'Status': 'Published'
        })
        assert final_product.fields['Status'] == 'Published'
        
        # Step 12: Verify complete workflow integrity
        hierarchy_data = {
            'collection': collection,
            'product': final_product,
            'variations': variations,
            'mockups': mockups,
            'listing': updated_listing
        }
        
        assert_relationship_integrity(airtable_client, hierarchy_data)
        
        # Step 13: Verify no orphaned records
        assert_no_orphaned_records(airtable_client)
    
    @patch('src.api.etsy_client.EtsyClient')
    @patch('src.api.printify_client.PrintifyClient')
    def test_full_api_integration_workflow(self, mock_printify, mock_etsy, airtable_client, test_data_factory, mock_api_responses):
        """Test complete workflow with real API integrations (mocked)."""
        # Setup mocks
        mock_etsy_instance = Mock()
        mock_etsy.return_value = mock_etsy_instance
        mock_etsy_instance.create_listing.return_value = mock_api_responses['etsy']['create_listing']
        
        mock_printify_instance = Mock()
        mock_printify.return_value = mock_printify_instance
        mock_printify_instance.create_product.return_value = mock_api_responses['printify']['create_product']
        
        # Create complete hierarchy
        hierarchy = RelationshipTestData.complete_product_hierarchy(
            test_data_factory, airtable_client, "api_integration"
        )
        
        # Add to cleanup
        test_data_factory.created_records['collections'].append(hierarchy['collection'].id)
        test_data_factory.created_records['products'].append(hierarchy['product'].id)
        for variation in hierarchy['variations']:
            test_data_factory.created_records['variations'].append(variation.id)
        for mockup in hierarchy['mockups']:
            test_data_factory.created_records['mockups'].append(mockup.id)
        test_data_factory.created_records['listings'].append(hierarchy['listing'].id)
        
        # Simulate Printify integration
        for variation in hierarchy['variations']:
            printify_response = mock_printify_instance.create_product.return_value
            airtable_client.update_record('variations', variation.id, {
                'Printify Product ID': printify_response['id']
            })
        
        # Simulate Etsy integration
        etsy_response = mock_etsy_instance.create_listing.return_value
        airtable_client.update_record('listings', hierarchy['listing'].id, {
            'External ID': str(etsy_response['listing_id']),
            'URL': etsy_response['url'],
            'Status': 'Active'
        })
        
        # Verify API calls were made
        assert mock_printify_instance.create_product.call_count == len(hierarchy['variations'])
        assert mock_etsy_instance.create_listing.called
        
        # Verify final state
        final_listing = airtable_client.get_record('listings', hierarchy['listing'].id)
        assert final_listing.fields['Status'] == 'Active'
        assert final_listing.fields['External ID'] == str(etsy_response['listing_id'])


@pytest.mark.e2e
class TestErrorRecoveryWorkflow:
    """Test error recovery in end-to-end workflows."""
    
    def test_workflow_interruption_recovery(self, airtable_client, test_data_factory):
        """Test recovery from workflow interruption."""
        # Start workflow
        collection = test_data_factory.create_test_collection("interruption_test")
        product = test_data_factory.create_test_product(collection.id, "interruption_test")
        
        # Progress to Mockup status
        airtable_client.update_record('products', product.id, {'Status': 'Mockup'})
        
        # Create variation
        variation = test_data_factory.create_test_variation(product.id, "interruption_test")
        
        # Simulate interruption during mockup generation
        mockup_data = {
            'Name': 'Interrupted Mockup',
            'Variation': [variation.id],
            'Status': 'Pending',
            'Quality Score': 0
        }
        mockup = airtable_client.create_record('mockups', mockup_data)
        test_data_factory.created_records['mockups'].append(mockup.id)
        
        # Simulate recovery - complete mockup generation
        recovered_mockup = airtable_client.update_record('mockups', mockup.id, {
            'Status': 'Generated',
            'Quality Score': 88,
            'File Path': '/recovered/mockup.png'
        })
        
        # Continue workflow
        airtable_client.update_record('products', product.id, {'Status': 'Product'})
        
        # Verify recovery successful
        assert recovered_mockup.fields['Status'] == 'Generated'
        final_product = airtable_client.get_record('products', product.id)
        assert final_product.fields['Status'] == 'Product'
    
    def test_data_consistency_after_errors(self, airtable_client, test_data_factory):
        """Test data consistency after various error conditions."""
        # Create hierarchy
        hierarchy = RelationshipTestData.complete_product_hierarchy(
            test_data_factory, airtable_client, "consistency_test"
        )
        
        # Add to cleanup
        test_data_factory.created_records['collections'].append(hierarchy['collection'].id)
        test_data_factory.created_records['products'].append(hierarchy['product'].id)
        for variation in hierarchy['variations']:
            test_data_factory.created_records['variations'].append(variation.id)
        for mockup in hierarchy['mockups']:
            test_data_factory.created_records['mockups'].append(mockup.id)
        test_data_factory.created_records['listings'].append(hierarchy['listing'].id)
        
        # Simulate various error conditions and verify consistency
        
        # 1. Invalid status update
        try:
            airtable_client.update_record('products', hierarchy['product'].id, {
                'Status': 'InvalidStatus'
            })
        except Exception:
            pass  # Expected error
        
        # 2. Invalid relationship
        try:
            airtable_client.update_record('variations', hierarchy['variations'][0].id, {
                'Product': ['recInvalidProduct123']
            })
        except Exception:
            pass  # Expected error
        
        # Verify data consistency maintained
        assert_relationship_integrity(airtable_client, hierarchy)
        assert_no_orphaned_records(airtable_client)


@pytest.mark.e2e
@pytest.mark.slow
class TestPerformanceWorkflow:
    """Test workflow performance under realistic conditions."""
    
    def test_large_collection_workflow(self, airtable_client, test_data_factory):
        """Test workflow with large collection (many products)."""
        # Create collection
        collection = test_data_factory.create_test_collection("large_collection")
        
        # Create multiple products
        products = []
        for i in range(10):  # Reduced from 50 for testing speed
            product = test_data_factory.create_test_product(collection.id, f"large_product_{i}")
            products.append(product)
            
            # Create variations for each product
            for j in range(2):  # 2 variations per product
                variation = test_data_factory.create_test_variation(product.id, f"large_var_{i}_{j}")
        
        # Verify collection has all products
        updated_collection = airtable_client.get_record('collections', collection.id)
        assert len(updated_collection.fields.get('Products', [])) == 10
        
        # Batch update all products to 'Mockup' status
        for product in products:
            airtable_client.update_record('products', product.id, {'Status': 'Mockup'})
        
        # Verify all updates
        for product in products:
            updated_product = airtable_client.get_record('products', product.id)
            assert updated_product.fields['Status'] == 'Mockup'
    
    def test_concurrent_workflow_operations(self, airtable_client, test_data_factory):
        """Test concurrent workflow operations."""
        import threading
        import time
        
        # Create multiple products for concurrent processing
        products = []
        for i in range(5):
            product = test_data_factory.create_test_product(name_suffix=f"concurrent_{i}")
            products.append(product)
        
        results = {}
        
        def process_product(product, index):
            """Simulate product processing workflow."""
            try:
                # Progress through workflow stages
                stages = ['Mockup', 'Product', 'Listed']
                for stage in stages:
                    time.sleep(0.1)  # Simulate processing time
                    airtable_client.update_record('products', product.id, {'Status': stage})
                
                results[index] = 'success'
            except Exception as e:
                results[index] = f'error: {e}'
        
        # Start concurrent processing
        threads = []
        for i, product in enumerate(products):
            thread = threading.Thread(target=process_product, args=(product, i))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all operations succeeded
        for i in range(5):
            assert results[i] == 'success'
        
        # Verify final states
        for product in products:
            final_product = airtable_client.get_record('products', product.id)
            assert final_product.fields['Status'] == 'Listed'


@pytest.mark.e2e
class TestWorkflowMonitoring:
    """Test workflow monitoring and analytics."""
    
    def test_workflow_progress_tracking(self, airtable_client, test_data_factory):
        """Test tracking workflow progress across multiple products."""
        # Create products in different stages
        stages = ['Design', 'Mockup', 'Product', 'Listed', 'Published']
        products_by_stage = {}
        
        for stage in stages:
            products = []
            for i in range(2):  # 2 products per stage
                product = test_data_factory.create_test_product(name_suffix=f"{stage.lower()}_{i}")
                airtable_client.update_record('products', product.id, {'Status': stage})
                products.append(product)
            products_by_stage[stage] = products
        
        # Verify stage distribution
        for stage, products in products_by_stage.items():
            for product in products:
                current_product = airtable_client.get_record('products', product.id)
                assert current_product.fields['Status'] == stage
    
    def test_workflow_analytics(self, airtable_client, test_data_factory):
        """Test workflow analytics and metrics."""
        # Create products with performance data
        products = []
        for i in range(5):
            product = test_data_factory.create_test_product(name_suffix=f"analytics_{i}")
            
            # Create listing with performance metrics
            listing_data = {
                'Title': f'Analytics Test Product {i}',
                'Product': [product.id],
                'Status': 'Active',
                'Price': 20.00 + i * 5,  # Varying prices
                'Platform': 'Etsy',
                'Views': 100 * (i + 1),  # Varying views
                'Favorites': 10 * (i + 1),  # Varying favorites
                'Sales': i + 1  # Varying sales
            }
            listing = airtable_client.create_record('listings', listing_data)
            test_data_factory.created_records['listings'].append(listing.id)
            
            products.append((product, listing))
        
        # Calculate analytics
        total_views = sum(listing.fields['Views'] for _, listing in products)
        total_sales = sum(listing.fields['Sales'] for _, listing in products)
        avg_conversion = total_sales / total_views if total_views > 0 else 0
        
        # Verify analytics make sense
        assert total_views > 0
        assert total_sales > 0
        assert 0 <= avg_conversion <= 1
        
        # Test individual product analytics
        for product, listing in products:
            views = listing.fields['Views']
            sales = listing.fields['Sales']
            conversion = sales / views if views > 0 else 0
            
            assert conversion >= 0
            assert conversion <= 1
