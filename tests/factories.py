
#!/usr/bin/env python3
"""
Test data factories for Airtable integration testing.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class AirtableTestDataFactory:
    """Factory for generating test data for Airtable tables."""
    
    @staticmethod
    def random_string(length=8):
        """Generate random string for unique test data."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    @staticmethod
    def collection_data(name_suffix=None) -> Dict[str, Any]:
        """Generate test collection data."""
        suffix = name_suffix or AirtableTestDataFactory.random_string()
        return {
            'Collection Name': f'Test Collection {suffix}',
            'Description': f'Test collection for integration testing {suffix}',
            'Status': random.choice(['Active', 'Inactive', 'Planning'])
        }
    
    @staticmethod
    def product_data(collection_id: Optional[str] = None, name_suffix=None) -> Dict[str, Any]:
        """Generate test product data."""
        suffix = name_suffix or AirtableTestDataFactory.random_string()
        data = {
            'Product Name': f'Test Product {suffix}',
            'Description': f'Test product for integration testing {suffix}',
            'Product Type': random.choice(['T-Shirt', 'Hoodie', 'Poster', 'Tank Top']),
            'Status': random.choice(['Design', 'Mockup', 'Product', 'Listed', 'Published']),
            'Priority': random.choice(['High', 'Medium', 'Low']),
            'Blueprint Key': f'bp_{suffix}',
            'Print Provider': 'Printify',
            'Batch Group': f'batch_{suffix}',
            'Base Price': random.randint(8, 15),
            'Selling Price': random.randint(20, 50)
        }
        
        if collection_id:
            data['Collection'] = [collection_id]
        
        return data
    
    @staticmethod
    def variation_data(product_id: Optional[str] = None, name_suffix=None) -> Dict[str, Any]:
        """Generate test variation data."""
        suffix = name_suffix or AirtableTestDataFactory.random_string()
        colors = ['Black', 'White', 'Navy', 'Red', 'Green', 'Blue']
        sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        product_types = ['T-Shirt', 'Hoodie', 'Tank Top', 'Long Sleeve', 'Poster']
        
        data = {
            'Name': f'Test Variation {suffix}',
            'Product Type': random.choice(product_types),
            'Color': random.choice(colors),
            'Size': random.choice(sizes),
            'Status': random.choice(['Active', 'Inactive', 'Out of Stock']),
            'Printify Blueprint ID': random.randint(10, 50),
            'Printify Print Provider ID': random.randint(20, 40),
            'Base Cost': round(random.uniform(8.0, 15.0), 2),
            'Profit Margin': round(random.uniform(0.3, 0.7), 2)
        }
        
        if product_id:
            data['Product'] = [product_id]
        
        return data
    
    @staticmethod
    def mockup_data(variation_id: Optional[str] = None, name_suffix=None) -> Dict[str, Any]:
        """Generate test mockup data."""
        suffix = name_suffix or AirtableTestDataFactory.random_string()
        
        data = {
            'Name': f'Test Mockup {suffix}',
            'Status': random.choice(['Generated', 'Approved', 'Rejected', 'Pending']),
            'Quality Score': random.randint(60, 100),
            'File Path': f'/test/mockups/test_mockup_{suffix}.png',
            'Generation Date': datetime.now().strftime('%Y-%m-%d'),
            'File Size': random.randint(500000, 2000000),  # 500KB to 2MB
            'Resolution': random.choice(['1080x1080', '1200x1200', '2000x2000'])
        }
        
        if variation_id:
            data['Variation'] = [variation_id]
        
        return data
    
    @staticmethod
    def listing_data(product_id: Optional[str] = None, name_suffix=None) -> Dict[str, Any]:
        """Generate test listing data."""
        suffix = name_suffix or AirtableTestDataFactory.random_string()
        platforms = ['Etsy', 'Amazon', 'Shopify', 'eBay']
        
        data = {
            'Title': f'Test Listing {suffix}',
            'Status': random.choice(['Draft', 'Active', 'Inactive', 'Sold Out']),
            'Price': round(random.uniform(15.0, 50.0), 2),
            'Platform': random.choice(platforms),
            'Created Date': datetime.now().strftime('%Y-%m-%d'),
            'Views': random.randint(0, 1000),
            'Favorites': random.randint(0, 50),
            'Sales': random.randint(0, 10)
        }
        
        if product_id:
            data['Product'] = [product_id]
        
        return data
    
    @staticmethod
    def dashboard_data(name_suffix=None) -> Dict[str, Any]:
        """Generate test dashboard data."""
        suffix = name_suffix or AirtableTestDataFactory.random_string()
        
        return {
            'Metric Name': f'Test Metric {suffix}',
            'Value': random.randint(1, 1000),
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Category': random.choice(['Sales', 'Traffic', 'Conversion', 'Revenue']),
            'Notes': f'Test dashboard entry for integration testing {suffix}'
        }


class RelationshipTestData:
    """Helper for creating related test data across tables."""
    
    @staticmethod
    def complete_product_hierarchy(factory, client, name_suffix=None):
        """Create a complete product hierarchy with all relationships."""
        suffix = name_suffix or AirtableTestDataFactory.random_string()
        
        # Create collection
        collection_data = AirtableTestDataFactory.collection_data(suffix)
        collection = client.create_record('collections', collection_data)
        
        # Create product
        product_data = AirtableTestDataFactory.product_data(collection.id, suffix)
        product = client.create_record('products', product_data)
        
        # Create variations
        variations = []
        for i in range(2):  # Create 2 variations per product
            variation_data = AirtableTestDataFactory.variation_data(product.id, f"{suffix}_var{i}")
            variation = client.create_record('variations', variation_data)
            variations.append(variation)
        
        # Create mockups for each variation
        mockups = []
        for i, variation in enumerate(variations):
            mockup_data = AirtableTestDataFactory.mockup_data(variation.id, f"{suffix}_mock{i}")
            mockup = client.create_record('mockups', mockup_data)
            mockups.append(mockup)
        
        # Create listing
        listing_data = AirtableTestDataFactory.listing_data(product.id, suffix)
        listing = client.create_record('listings', listing_data)
        
        return {
            'collection': collection,
            'product': product,
            'variations': variations,
            'mockups': mockups,
            'listing': listing
        }
