
#!/usr/bin/env python3
"""
Utilities for testing relational data integrity in Airtable.
"""

import logging
from typing import Dict, List, Any, Optional
from src.api.airtable_client import AirtableClient, AirtableRecord


class RelationshipValidator:
    """Validates relational data integrity across Airtable tables."""
    
    def __init__(self, client: AirtableClient):
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    def validate_collection_product_relationship(self, collection_id: str, product_id: str) -> bool:
        """Validate that product is properly linked to collection."""
        try:
            # Get product record
            product = self.client.get_record('products', product_id)
            if not product:
                self.logger.error(f"Product {product_id} not found")
                return False
            
            # Check if collection is linked
            collection_links = product.fields.get('Collection', [])
            if collection_id not in collection_links:
                self.logger.error(f"Product {product_id} not linked to collection {collection_id}")
                return False
            
            # Get collection record and verify back-link
            collection = self.client.get_record('collections', collection_id)
            if not collection:
                self.logger.error(f"Collection {collection_id} not found")
                return False
            
            product_links = collection.fields.get('Products', [])
            if product_id not in product_links:
                self.logger.error(f"Collection {collection_id} not back-linked to product {product_id}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating collection-product relationship: {e}")
            return False
    
    def validate_product_variation_relationship(self, product_id: str, variation_id: str) -> bool:
        """Validate that variation is properly linked to product."""
        try:
            # Get variation record
            variation = self.client.get_record('variations', variation_id)
            if not variation:
                self.logger.error(f"Variation {variation_id} not found")
                return False
            
            # Check if product is linked
            product_links = variation.fields.get('Product', [])
            if product_id not in product_links:
                self.logger.error(f"Variation {variation_id} not linked to product {product_id}")
                return False
            
            # Get product record and verify back-link
            product = self.client.get_record('products', product_id)
            if not product:
                self.logger.error(f"Product {product_id} not found")
                return False
            
            variation_links = product.fields.get('Variations', [])
            if variation_id not in variation_links:
                self.logger.error(f"Product {product_id} not back-linked to variation {variation_id}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating product-variation relationship: {e}")
            return False
    
    def validate_variation_mockup_relationship(self, variation_id: str, mockup_id: str) -> bool:
        """Validate that mockup is properly linked to variation."""
        try:
            # Get mockup record
            mockup = self.client.get_record('mockups', mockup_id)
            if not mockup:
                self.logger.error(f"Mockup {mockup_id} not found")
                return False
            
            # Check if variation is linked
            variation_links = mockup.fields.get('Variation', [])
            if variation_id not in variation_links:
                self.logger.error(f"Mockup {mockup_id} not linked to variation {variation_id}")
                return False
            
            # Get variation record and verify back-link
            variation = self.client.get_record('variations', variation_id)
            if not variation:
                self.logger.error(f"Variation {variation_id} not found")
                return False
            
            mockup_links = variation.fields.get('Mockups', [])
            if mockup_id not in mockup_links:
                self.logger.error(f"Variation {variation_id} not back-linked to mockup {mockup_id}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating variation-mockup relationship: {e}")
            return False
    
    def validate_product_listing_relationship(self, product_id: str, listing_id: str) -> bool:
        """Validate that listing is properly linked to product."""
        try:
            # Get listing record
            listing = self.client.get_record('listings', listing_id)
            if not listing:
                self.logger.error(f"Listing {listing_id} not found")
                return False
            
            # Check if product is linked
            product_links = listing.fields.get('Product', [])
            if product_id not in product_links:
                self.logger.error(f"Listing {listing_id} not linked to product {product_id}")
                return False
            
            # Get product record and verify back-link
            product = self.client.get_record('products', product_id)
            if not product:
                self.logger.error(f"Product {product_id} not found")
                return False
            
            listing_links = product.fields.get('Listings', [])
            if listing_id not in listing_links:
                self.logger.error(f"Product {product_id} not back-linked to listing {listing_id}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating product-listing relationship: {e}")
            return False
    
    def validate_complete_hierarchy(self, hierarchy_data: Dict[str, Any]) -> Dict[str, bool]:
        """Validate complete product hierarchy relationships."""
        results = {}
        
        collection_id = hierarchy_data['collection'].id
        product_id = hierarchy_data['product'].id
        
        # Validate collection-product relationship
        results['collection_product'] = self.validate_collection_product_relationship(
            collection_id, product_id
        )
        
        # Validate product-variation relationships
        results['product_variations'] = []
        for variation in hierarchy_data['variations']:
            is_valid = self.validate_product_variation_relationship(product_id, variation.id)
            results['product_variations'].append(is_valid)
        
        # Validate variation-mockup relationships
        results['variation_mockups'] = []
        for i, mockup in enumerate(hierarchy_data['mockups']):
            variation_id = hierarchy_data['variations'][i].id
            is_valid = self.validate_variation_mockup_relationship(variation_id, mockup.id)
            results['variation_mockups'].append(is_valid)
        
        # Validate product-listing relationship
        listing_id = hierarchy_data['listing'].id
        results['product_listing'] = self.validate_product_listing_relationship(
            product_id, listing_id
        )
        
        return results
    
    def check_orphaned_records(self) -> Dict[str, List[str]]:
        """Check for orphaned records across all tables."""
        orphaned = {
            'products': [],
            'variations': [],
            'mockups': [],
            'listings': []
        }
        
        try:
            # Check for products without collections
            products = self.client.list_records('products')
            for product in products:
                if not product.fields.get('Collection'):
                    orphaned['products'].append(product.id)
            
            # Check for variations without products
            variations = self.client.list_records('variations')
            for variation in variations:
                if not variation.fields.get('Product'):
                    orphaned['variations'].append(variation.id)
            
            # Check for mockups without variations
            mockups = self.client.list_records('mockups')
            for mockup in mockups:
                if not mockup.fields.get('Variation'):
                    orphaned['mockups'].append(mockup.id)
            
            # Check for listings without products
            listings = self.client.list_records('listings')
            for listing in listings:
                if not listing.fields.get('Product'):
                    orphaned['listings'].append(listing.id)
        
        except Exception as e:
            self.logger.error(f"Error checking for orphaned records: {e}")
        
        return orphaned


def assert_relationship_integrity(client: AirtableClient, hierarchy_data: Dict[str, Any]):
    """Assert that all relationships in hierarchy are valid."""
    validator = RelationshipValidator(client)
    results = validator.validate_complete_hierarchy(hierarchy_data)
    
    # Assert collection-product relationship
    assert results['collection_product'], "Collection-Product relationship validation failed"
    
    # Assert all product-variation relationships
    for i, is_valid in enumerate(results['product_variations']):
        assert is_valid, f"Product-Variation relationship validation failed for variation {i}"
    
    # Assert all variation-mockup relationships
    for i, is_valid in enumerate(results['variation_mockups']):
        assert is_valid, f"Variation-Mockup relationship validation failed for mockup {i}"
    
    # Assert product-listing relationship
    assert results['product_listing'], "Product-Listing relationship validation failed"


def assert_no_orphaned_records(client: AirtableClient):
    """Assert that there are no orphaned records in the database."""
    validator = RelationshipValidator(client)
    orphaned = validator.check_orphaned_records()
    
    for table, orphaned_ids in orphaned.items():
        assert len(orphaned_ids) == 0, f"Found orphaned records in {table}: {orphaned_ids}"
