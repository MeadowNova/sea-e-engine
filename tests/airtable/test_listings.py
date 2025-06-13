
#!/usr/bin/env python3
"""
Test suite for Airtable Listings table CRUD operations.
"""

import pytest
import logging
from typing import Dict, Any
from tests.factories import AirtableTestDataFactory
from tests.utils_relations import RelationshipValidator


@pytest.mark.integration
class TestListingsCRUD:
    """Test CRUD operations for Listings table."""
    
    def test_create_listing_success(self, airtable_client, test_data_factory):
        """Test successful listing creation."""
        # Create test listing
        listing = test_data_factory.create_test_listing(name_suffix="crud_create")
        
        # Verify creation
        assert listing is not None
        assert listing.id is not None
        assert listing.fields['Title'] == 'Test Listing crud_create'
        assert listing.fields['Status'] == 'Draft'
        assert listing.fields['Price'] == 19.99
        assert listing.fields['Platform'] == 'Etsy'
        assert 'Product' in listing.fields
    
    def test_create_listing_with_all_fields(self, airtable_client, test_data_factory):
        """Test listing creation with all fields."""
        # Create product first
        product = test_data_factory.create_test_product("listing_complete")
        
        data = {
            'Title': 'Complete Test Listing',
            'Product': [product.id],
            'Status': 'Active',
            'Price': 29.99,
            'Platform': 'Etsy',
            'Created Date': '2025-06-12',
            'Views': 150,
            'Favorites': 25,
            'Sales': 5,
            'External ID': 'etsy_12345',
            'URL': 'https://etsy.com/listing/12345',
            'Description': 'Complete test listing description'
        }
        
        record = airtable_client.create_record('listings', data)
        test_data_factory.created_records['listings'].append(record.id)
        
        # Verify all fields
        assert record.fields['Title'] == 'Complete Test Listing'
        assert record.fields['Status'] == 'Active'
        assert record.fields['Price'] == 29.99
        assert record.fields['Views'] == 150
        assert record.fields['Favorites'] == 25
        assert record.fields['Sales'] == 5
    
    def test_read_listing_success(self, airtable_client, test_data_factory):
        """Test successful listing retrieval."""
        # Create test listing
        created_listing = test_data_factory.create_test_listing("crud_read")
        
        # Read listing
        retrieved_listing = airtable_client.get_record('listings', created_listing.id)
        
        # Verify retrieval
        assert retrieved_listing is not None
        assert retrieved_listing.id == created_listing.id
        assert retrieved_listing.fields['Title'] == created_listing.fields['Title']
    
    def test_update_listing_success(self, airtable_client, test_data_factory):
        """Test successful listing update."""
        # Create test listing
        listing = test_data_factory.create_test_listing("crud_update")
        
        # Update listing
        update_data = {
            'Title': 'Updated Listing Title',
            'Status': 'Active',
            'Price': 24.99,
            'Views': 200,
            'Favorites': 30,
            'Sales': 8
        }
        
        updated_listing = airtable_client.update_record('listings', listing.id, update_data)
        
        # Verify update
        assert updated_listing.fields['Title'] == 'Updated Listing Title'
        assert updated_listing.fields['Status'] == 'Active'
        assert updated_listing.fields['Price'] == 24.99
        assert updated_listing.fields['Views'] == 200
        assert updated_listing.fields['Sales'] == 8
    
    def test_delete_listing_success(self, airtable_client, test_data_factory):
        """Test successful listing deletion."""
        # Create test listing
        listing = test_data_factory.create_test_listing("crud_delete")
        listing_id = listing.id
        
        # Remove from cleanup list since we're testing deletion
        test_data_factory.created_records['listings'].remove(listing_id)
        
        # Delete listing
        success = airtable_client.delete_record('listings', listing_id)
        assert success is True
        
        # Verify deletion
        deleted_listing = airtable_client.get_record('listings', listing_id)
        assert deleted_listing is None
    
    @pytest.mark.parametrize("status", ["Draft", "Active", "Inactive", "Sold Out"])
    def test_listing_status_values(self, airtable_client, test_data_factory, status):
        """Test different listing status values."""
        data = AirtableTestDataFactory.listing_data(name_suffix="status_test")
        data['Status'] = status
        
        record = airtable_client.create_record('listings', data)
        test_data_factory.created_records['listings'].append(record.id)
        
        assert record.fields['Status'] == status
    
    @pytest.mark.parametrize("platform", ["Etsy", "Amazon", "Shopify", "eBay"])
    def test_listing_platforms(self, airtable_client, test_data_factory, platform):
        """Test different platform values."""
        data = AirtableTestDataFactory.listing_data(name_suffix="platform_test")
        data['Platform'] = platform
        
        record = airtable_client.create_record('listings', data)
        test_data_factory.created_records['listings'].append(record.id)
        
        assert record.fields['Platform'] == platform


@pytest.mark.integration
class TestListingsRelationships:
    """Test relationship management for Listings table."""
    
    def test_listing_product_relationship(self, airtable_client, test_data_factory):
        """Test listing-product relationship integrity."""
        # Create product
        product = test_data_factory.create_test_product("relationship_test")
        
        # Create listing with product
        listing = test_data_factory.create_test_listing(
            product_id=product.id,
            name_suffix="relationship_test"
        )
        
        # Validate relationship
        validator = RelationshipValidator(airtable_client)
        is_valid = validator.validate_product_listing_relationship(product.id, listing.id)
        assert is_valid is True
    
    def test_multiple_listings_per_product(self, airtable_client, test_data_factory):
        """Test multiple listings for single product."""
        # Create product
        product = test_data_factory.create_test_product("multiple_listings")
        
        # Create multiple listings
        listings = []
        platforms = ['Etsy', 'Amazon', 'Shopify']
        for i, platform in enumerate(platforms):
            data = AirtableTestDataFactory.listing_data(f"multiple_listings_{i}")
            data['Product'] = [product.id]
            data['Platform'] = platform
            
            listing = airtable_client.create_record('listings', data)
            test_data_factory.created_records['listings'].append(listing.id)
            listings.append(listing)
        
        # Verify product has all listings linked
        updated_product = airtable_client.get_record('products', product.id)
        listing_ids = updated_product.fields.get('Listings', [])
        
        for listing in listings:
            assert listing.id in listing_ids


@pytest.mark.integration
class TestListingsValidation:
    """Test data validation for Listings table."""
    
    def test_create_listing_missing_title(self, airtable_client):
        """Test listing creation fails without required title field."""
        data = {
            'Status': 'Draft',
            'Price': 19.99,
            'Platform': 'Etsy'
        }
        
        with pytest.raises(Exception):
            airtable_client.create_record('listings', data)
    
    def test_listing_price_validation(self, airtable_client, test_data_factory):
        """Test listing price field validation."""
        data = AirtableTestDataFactory.listing_data("price_test")
        data['Price'] = 34.99
        
        record = airtable_client.create_record('listings', data)
        test_data_factory.created_records['listings'].append(record.id)
        
        assert record.fields['Price'] == 34.99
    
    def test_listing_metrics_validation(self, airtable_client, test_data_factory):
        """Test listing metrics fields validation."""
        data = AirtableTestDataFactory.listing_data("metrics_test")
        data['Views'] = 500
        data['Favorites'] = 75
        data['Sales'] = 12
        
        record = airtable_client.create_record('listings', data)
        test_data_factory.created_records['listings'].append(record.id)
        
        assert record.fields['Views'] == 500
        assert record.fields['Favorites'] == 75
        assert record.fields['Sales'] == 12
    
    def test_listing_external_id_validation(self, airtable_client, test_data_factory):
        """Test external ID field validation."""
        data = AirtableTestDataFactory.listing_data("external_id_test")
        data['External ID'] = 'etsy_987654321'
        data['URL'] = 'https://etsy.com/listing/987654321'
        
        record = airtable_client.create_record('listings', data)
        test_data_factory.created_records['listings'].append(record.id)
        
        assert record.fields['External ID'] == 'etsy_987654321'
        assert record.fields['URL'] == 'https://etsy.com/listing/987654321'


@pytest.mark.integration
class TestListingsSearch:
    """Test search and filtering for Listings table."""
    
    def test_filter_listings_by_status(self, airtable_client, test_data_factory):
        """Test filtering listings by status."""
        # Create listings with different statuses
        statuses = ['Draft', 'Active', 'Inactive']
        created_listings = []
        
        for status in statuses:
            data = AirtableTestDataFactory.listing_data(f"filter_{status.lower()}")
            data['Status'] = status
            
            record = airtable_client.create_record('listings', data)
            test_data_factory.created_records['listings'].append(record.id)
            created_listings.append(record)
        
        # Filter by status
        filter_formula = "Status = 'Active'"
        filtered_listings = airtable_client.list_records('listings', filter_formula=filter_formula)
        
        # Verify filtering
        active_listings = [l for l in created_listings if l.fields['Status'] == 'Active']
        filtered_ids = [l.id for l in filtered_listings]
        
        for listing in active_listings:
            assert listing.id in filtered_ids
    
    def test_filter_listings_by_platform(self, airtable_client, test_data_factory):
        """Test filtering listings by platform."""
        # Create listings on different platforms
        platforms = ['Etsy', 'Amazon', 'Shopify']
        created_listings = []
        
        for platform in platforms:
            data = AirtableTestDataFactory.listing_data(f"filter_{platform.lower()}")
            data['Platform'] = platform
            
            record = airtable_client.create_record('listings', data)
            test_data_factory.created_records['listings'].append(record.id)
            created_listings.append(record)
        
        # Filter by platform
        filter_formula = "Platform = 'Etsy'"
        filtered_listings = airtable_client.list_records('listings', filter_formula=filter_formula)
        
        # Verify filtering
        etsy_listings = [l for l in created_listings if l.fields['Platform'] == 'Etsy']
        filtered_ids = [l.id for l in filtered_listings]
        
        for listing in etsy_listings:
            assert listing.id in filtered_ids
    
    def test_filter_listings_by_price_range(self, airtable_client, test_data_factory):
        """Test filtering listings by price range."""
        # Create listings with different prices
        prices = [15.99, 25.99, 35.99]
        created_listings = []
        
        for price in prices:
            data = AirtableTestDataFactory.listing_data(f"filter_price_{price}")
            data['Price'] = price
            
            record = airtable_client.create_record('listings', data)
            test_data_factory.created_records['listings'].append(record.id)
            created_listings.append(record)
        
        # Filter by price range
        filter_formula = "AND(Price >= 20, Price <= 30)"
        filtered_listings = airtable_client.list_records('listings', filter_formula=filter_formula)
        
        # Verify filtering
        mid_price_listings = [l for l in created_listings if 20 <= l.fields['Price'] <= 30]
        filtered_ids = [l.id for l in filtered_listings]
        
        for listing in mid_price_listings:
            assert listing.id in filtered_ids
    
    def test_filter_listings_by_performance(self, airtable_client, test_data_factory):
        """Test filtering listings by performance metrics."""
        # Create listings with different performance
        performances = [
            {'Views': 100, 'Favorites': 10, 'Sales': 2},
            {'Views': 500, 'Favorites': 50, 'Sales': 10},
            {'Views': 1000, 'Favorites': 100, 'Sales': 25}
        ]
        created_listings = []
        
        for i, perf in enumerate(performances):
            data = AirtableTestDataFactory.listing_data(f"filter_perf_{i}")
            data.update(perf)
            
            record = airtable_client.create_record('listings', data)
            test_data_factory.created_records['listings'].append(record.id)
            created_listings.append(record)
        
        # Filter by high performance (Views > 300 AND Sales > 5)
        filter_formula = "AND(Views > 300, Sales > 5)"
        filtered_listings = airtable_client.list_records('listings', filter_formula=filter_formula)
        
        # Verify filtering
        high_perf_listings = [l for l in created_listings 
                             if l.fields['Views'] > 300 and l.fields['Sales'] > 5]
        filtered_ids = [l.id for l in filtered_listings]
        
        for listing in high_perf_listings:
            assert listing.id in filtered_ids
