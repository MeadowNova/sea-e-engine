
#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Airtable integration testing.
"""

import pytest
import os
import sys
import tempfile
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent))

from src.api.airtable_client import AirtableClient
from src.data.airtable_models import Product, Variation, Mockup, Listing, Collection


@pytest.fixture(scope="session")
def test_env_vars():
    """Set up test environment variables."""
    test_vars = {
        'AIRTABLE_API_KEY': 'patYbpqb73JmDs8J2.4bcb296dca4a34545eb7439c442e31b7779756bb8b8fbd5d874a2abbfed5c160',
        'AIRTABLE_BASE_ID': 'appF5TYNhZ71SCjco',
        'ETSY_API_KEY': 'test_etsy_key',
        'PRINTIFY_API_KEY': 'test_printify_key'
    }
    
    # Store original values
    original_values = {}
    for key, value in test_vars.items():
        original_values[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield test_vars
    
    # Restore original values
    for key, original_value in original_values.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture(scope="session")
def airtable_client(test_env_vars):
    """Create Airtable client for testing."""
    return AirtableClient()


@pytest.fixture(scope="function")
def test_data_factory(airtable_client):
    """Factory for creating and cleaning up test data."""
    created_records = {
        'collections': [],
        'products': [],
        'variations': [],
        'mockups': [],
        'listings': [],
        'dashboard': []
    }
    
    class TestDataFactory:
        def __init__(self, client):
            self.client = client
            self.created_records = created_records
        
        def create_test_collection(self, name_suffix="test"):
            """Create a test collection record."""
            data = {
                'Collection Name': f'Test Collection {name_suffix}',
                'Description': f'Test collection for integration testing {name_suffix}',
                'Status': 'Planning'
            }
            record = self.client.create_record('collections', data)
            self.created_records['collections'].append(record.id)
            return record
        
        def create_test_product(self, collection_id=None, name_suffix="test"):
            """Create a test product record."""
            if not collection_id:
                collection = self.create_test_collection(name_suffix)
                collection_id = collection.id
            
            data = {
                'Product Name': f'Test Product {name_suffix}',
                'Description': f'Test product for integration testing {name_suffix}',
                'Product Type': 'T-Shirt',
                'Status': 'Design',
                'Priority': 'Medium',
                'Blueprint Key': f'bp_{name_suffix}',
                'Print Provider': 'Printify',
                'Batch Group': f'batch_{name_suffix}',
                'Base Price': 10,
                'Selling Price': 25
            }
            if collection_id:
                data['Collection'] = [collection_id]
            record = self.client.create_record('products', data)
            self.created_records['products'].append(record.id)
            return record
        
        def create_test_variation(self, product_id=None, name_suffix="test"):
            """Create a test variation record."""
            if not product_id:
                product = self.create_test_product(name_suffix=name_suffix)
                product_id = product.id
            
            data = {
                'Name': f'Test Variation {name_suffix}',
                'Product': [product_id],
                'Product Type': 'T-Shirt',
                'Color': 'Black',
                'Size': 'M',
                'Status': 'Active',
                'Printify Blueprint ID': 12,
                'Printify Print Provider ID': 29
            }
            record = self.client.create_record('variations', data)
            self.created_records['variations'].append(record.id)
            return record
        
        def create_test_mockup(self, variation_id=None, name_suffix="test"):
            """Create a test mockup record."""
            if not variation_id:
                variation = self.create_test_variation(name_suffix=name_suffix)
                variation_id = variation.id
            
            data = {
                'Name': f'Test Mockup {name_suffix}',
                'Variation': [variation_id],
                'Status': 'Generated',
                'Quality Score': 85,
                'File Path': f'/test/mockups/test_mockup_{name_suffix}.png',
                'Generation Date': '2025-06-12'
            }
            record = self.client.create_record('mockups', data)
            self.created_records['mockups'].append(record.id)
            return record
        
        def create_test_listing(self, product_id=None, name_suffix="test"):
            """Create a test listing record."""
            if not product_id:
                product = self.create_test_product(name_suffix=name_suffix)
                product_id = product.id
            
            data = {
                'Title': f'Test Listing {name_suffix}',
                'Product': [product_id],
                'Status': 'Draft',
                'Price': 19.99,
                'Platform': 'Etsy',
                'Created Date': '2025-06-12'
            }
            record = self.client.create_record('listings', data)
            self.created_records['listings'].append(record.id)
            return record
        
        def cleanup_all(self):
            """Clean up all created test records."""
            for table_name, record_ids in self.created_records.items():
                for record_id in record_ids:
                    try:
                        self.client.delete_record(table_name, record_id)
                    except Exception as e:
                        logging.warning(f"Failed to delete {table_name} record {record_id}: {e}")
                self.created_records[table_name] = []
    
    factory = TestDataFactory(airtable_client)
    yield factory
    
    # Cleanup after test
    factory.cleanup_all()


@pytest.fixture
def temp_directory():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_api_responses():
    """Mock API responses for external services."""
    return {
        'etsy': {
            'create_listing': {
                'listing_id': 12345,
                'state': 'draft',
                'url': 'https://etsy.com/listing/12345'
            }
        },
        'printify': {
            'create_product': {
                'id': 'prod_123',
                'title': 'Test Product',
                'variants': [{'id': 'var_123', 'price': 1999}]
            }
        }
    }
