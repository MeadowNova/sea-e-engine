
#!/usr/bin/env python3
"""
Airtable Data Models for SEA-E Engine
====================================

Data model classes for working with Airtable records in a structured way.
These models provide type safety and validation for the relational data structure.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ProductStatus(Enum):
    """Product workflow status enumeration."""
    DESIGN = "Design"
    MOCKUP = "Mockup"
    PRODUCT = "Product"
    LISTED = "Listed"
    PUBLISHED = "Published"


class Priority(Enum):
    """Product priority enumeration."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class CollectionStatus(Enum):
    """Collection status enumeration."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PLANNING = "Planning"


class VariationStatus(Enum):
    """Variation status enumeration."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    OUT_OF_STOCK = "Out of Stock"


class MockupStatus(Enum):
    """Mockup generation status enumeration."""
    PENDING = "Pending"
    GENERATED = "Generated"
    FAILED = "Failed"


class MockupType(Enum):
    """Mockup type enumeration."""
    FRONT = "Front"
    BACK = "Back"
    LIFESTYLE = "Lifestyle"
    FLAT_LAY = "Flat Lay"


class PublicationStatus(Enum):
    """Listing publication status enumeration."""
    DRAFT = "Draft"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SOLD_OUT = "Sold Out"


@dataclass
class Collection:
    """Collection data model."""
    record_id: Optional[str] = None
    collection_name: str = ""
    collection_id: str = ""
    description: str = ""
    status: CollectionStatus = CollectionStatus.PLANNING
    products: List[str] = field(default_factory=list)  # Product record IDs
    
    @classmethod
    def from_airtable_record(cls, record) -> 'Collection':
        """Create Collection from Airtable record."""
        fields = record.fields
        return cls(
            record_id=record.id,
            collection_name=fields.get('Collection Name', ''),
            collection_id=fields.get('Collection ID', ''),
            description=fields.get('Description', ''),
            status=CollectionStatus(fields.get('Status', 'Planning')),
            products=fields.get('Products', [])
        )
    
    def to_airtable_fields(self) -> Dict[str, Any]:
        """Convert to Airtable fields dictionary."""
        fields = {
            'Collection Name': self.collection_name,
            'Collection ID': self.collection_id,
            'Description': self.description,
            'Status': self.status.value
        }
        
        if self.products:
            fields['Products'] = self.products
            
        return fields


@dataclass
class Product:
    """Product data model."""
    record_id: Optional[str] = None
    product_name: str = ""
    product_id: str = ""
    description: str = ""
    product_type: str = ""
    status: ProductStatus = ProductStatus.DESIGN
    priority: Priority = Priority.MEDIUM
    blueprint_key: str = ""
    print_provider: str = ""
    batch_group: str = ""
    base_price: float = 0.0
    selling_price: float = 0.0
    error_logs: str = ""
    collection: List[str] = field(default_factory=list)  # Collection record IDs
    variations: List[str] = field(default_factory=list)  # Variation record IDs
    listings: List[str] = field(default_factory=list)  # Listing record IDs
    
    @classmethod
    def from_airtable_record(cls, record) -> 'Product':
        """Create Product from Airtable record."""
        fields = record.fields
        return cls(
            record_id=record.id,
            product_name=fields.get('Product Name', ''),
            product_id=fields.get('Product ID', ''),
            description=fields.get('Description', ''),
            product_type=fields.get('Product Type', ''),
            status=ProductStatus(fields.get('Status', 'Design')),
            priority=Priority(fields.get('Priority', 'Medium')),
            blueprint_key=fields.get('Blueprint Key', ''),
            print_provider=fields.get('Print Provider', ''),
            batch_group=fields.get('Batch Group', ''),
            base_price=fields.get('Base Price', 0.0),
            selling_price=fields.get('Selling Price', 0.0),
            error_logs=fields.get('Error Logs', ''),
            collection=fields.get('Collection', []),
            variations=fields.get('Variations', []),
            listings=fields.get('Listings', [])
        )
    
    def to_airtable_fields(self) -> Dict[str, Any]:
        """Convert to Airtable fields dictionary."""
        fields = {
            'Product Name': self.product_name,
            'Product ID': self.product_id,
            'Description': self.description,
            'Product Type': self.product_type,
            'Status': self.status.value,
            'Priority': self.priority.value,
            'Blueprint Key': self.blueprint_key,
            'Print Provider': self.print_provider,
            'Batch Group': self.batch_group,
            'Base Price': self.base_price,
            'Selling Price': self.selling_price,
            'Error Logs': self.error_logs
        }
        
        if self.collection:
            fields['Collection'] = self.collection
        if self.variations:
            fields['Variations'] = self.variations
        if self.listings:
            fields['Listings'] = self.listings
            
        return fields


@dataclass
class Variation:
    """Variation data model."""
    record_id: Optional[str] = None
    variation_id: str = ""
    color: str = ""
    size: str = ""
    sku: str = ""
    printify_variant_id: str = ""
    status: VariationStatus = VariationStatus.ACTIVE
    price: float = 0.0
    availability: bool = True
    product: List[str] = field(default_factory=list)  # Product record IDs
    mockups: List[str] = field(default_factory=list)  # Mockup record IDs
    
    @classmethod
    def from_airtable_record(cls, record) -> 'Variation':
        """Create Variation from Airtable record."""
        fields = record.fields
        return cls(
            record_id=record.id,
            variation_id=fields.get('Variation ID', ''),
            color=fields.get('Color', ''),
            size=fields.get('Size', ''),
            sku=fields.get('SKU', ''),
            printify_variant_id=fields.get('Printify Variant ID', ''),
            status=VariationStatus(fields.get('Status', 'Active')),
            price=fields.get('Price', 0.0),
            availability=fields.get('Availability', True),
            product=fields.get('Product', []),
            mockups=fields.get('Mockups', [])
        )
    
    def to_airtable_fields(self) -> Dict[str, Any]:
        """Convert to Airtable fields dictionary."""
        fields = {
            'Variation ID': self.variation_id,
            'Color': self.color,
            'Size': self.size,
            'SKU': self.sku,
            'Printify Variant ID': self.printify_variant_id,
            'Status': self.status.value,
            'Price': self.price,
            'Availability': self.availability
        }
        
        if self.product:
            fields['Product'] = self.product
        if self.mockups:
            fields['Mockups'] = self.mockups
            
        return fields


@dataclass
class Mockup:
    """Mockup data model."""
    record_id: Optional[str] = None
    mockup_id: str = ""
    mockup_type: MockupType = MockupType.FRONT
    generation_status: MockupStatus = MockupStatus.PENDING
    quality_score: int = 0
    file_path: str = ""
    approved: bool = False
    variation: List[str] = field(default_factory=list)  # Variation record IDs
    
    @classmethod
    def from_airtable_record(cls, record) -> 'Mockup':
        """Create Mockup from Airtable record."""
        fields = record.fields
        return cls(
            record_id=record.id,
            mockup_id=fields.get('Mockup ID', ''),
            mockup_type=MockupType(fields.get('Mockup Type', 'Front')),
            generation_status=MockupStatus(fields.get('Generation Status', 'Pending')),
            quality_score=fields.get('Quality Score', 0),
            file_path=fields.get('File Path', ''),
            approved=fields.get('Approved', False),
            variation=fields.get('Variation', [])
        )
    
    def to_airtable_fields(self) -> Dict[str, Any]:
        """Convert to Airtable fields dictionary."""
        fields = {
            'Mockup ID': self.mockup_id,
            'Mockup Type': self.mockup_type.value,
            'Generation Status': self.generation_status.value,
            'Quality Score': self.quality_score,
            'File Path': self.file_path,
            'Approved': self.approved
        }
        
        if self.variation:
            fields['Variation'] = self.variation
            
        return fields


@dataclass
class Listing:
    """Listing data model."""
    record_id: Optional[str] = None
    listing_id: str = ""
    etsy_listing_id: str = ""
    etsy_url: str = ""
    publication_status: PublicationStatus = PublicationStatus.DRAFT
    seo_tags: str = ""
    optimized_tags: str = ""
    views: int = 0
    favorites: int = 0
    sales: int = 0
    last_sync_date: Optional[datetime] = None
    product: List[str] = field(default_factory=list)  # Product record IDs
    
    @classmethod
    def from_airtable_record(cls, record) -> 'Listing':
        """Create Listing from Airtable record."""
        fields = record.fields
        
        # Parse datetime if present
        last_sync = None
        if fields.get('Last Sync Date'):
            try:
                last_sync = datetime.fromisoformat(fields['Last Sync Date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        return cls(
            record_id=record.id,
            listing_id=fields.get('Listing ID', ''),
            etsy_listing_id=fields.get('Etsy Listing ID', ''),
            etsy_url=fields.get('Etsy URL', ''),
            publication_status=PublicationStatus(fields.get('Publication Status', 'Draft')),
            seo_tags=fields.get('SEO Tags', ''),
            optimized_tags=fields.get('Optimized Tags', ''),
            views=fields.get('Views', 0),
            favorites=fields.get('Favorites', 0),
            sales=fields.get('Sales', 0),
            last_sync_date=last_sync,
            product=fields.get('Product', [])
        )
    
    def to_airtable_fields(self) -> Dict[str, Any]:
        """Convert to Airtable fields dictionary."""
        fields = {
            'Listing ID': self.listing_id,
            'Etsy Listing ID': self.etsy_listing_id,
            'Etsy URL': self.etsy_url,
            'Publication Status': self.publication_status.value,
            'SEO Tags': self.seo_tags,
            'Optimized Tags': self.optimized_tags,
            'Views': self.views,
            'Favorites': self.favorites,
            'Sales': self.sales
        }
        
        if self.last_sync_date:
            fields['Last Sync Date'] = self.last_sync_date.isoformat()
        
        if self.product:
            fields['Product'] = self.product
            
        return fields


@dataclass
class DashboardMetric:
    """Dashboard metric data model."""
    record_id: Optional[str] = None
    dashboard_id: str = ""
    metric_name: str = ""
    metric_value: str = ""
    category: str = ""
    trend: str = ""
    
    @classmethod
    def from_airtable_record(cls, record) -> 'DashboardMetric':
        """Create DashboardMetric from Airtable record."""
        fields = record.fields
        return cls(
            record_id=record.id,
            dashboard_id=fields.get('Dashboard ID', ''),
            metric_name=fields.get('Metric Name', ''),
            metric_value=fields.get('Metric Value', ''),
            category=fields.get('Category', ''),
            trend=fields.get('Trend', '')
        )
    
    def to_airtable_fields(self) -> Dict[str, Any]:
        """Convert to Airtable fields dictionary."""
        return {
            'Dashboard ID': self.dashboard_id,
            'Metric Name': self.metric_name,
            'Metric Value': self.metric_value,
            'Category': self.category,
            'Trend': self.trend
        }


class AirtableDataManager:
    """
    High-level data manager for working with Airtable models.
    Provides convenient methods for common operations.
    """
    
    def __init__(self, airtable_client):
        """
        Initialize with an AirtableClient instance.
        
        Args:
            airtable_client: AirtableClient instance
        """
        self.client = airtable_client
        self.logger = logging.getLogger("airtable_data_manager")
    
    def get_products_by_status(self, status: ProductStatus) -> List[Product]:
        """Get all products with a specific status."""
        filter_formula = f"{{Status}} = '{status.value}'"
        records = self.client.list_records('products', filter_formula=filter_formula)
        return [Product.from_airtable_record(record) for record in records]
    
    def get_products_by_collection(self, collection_id: str) -> List[Product]:
        """Get all products in a specific collection."""
        # First find the collection record
        filter_formula = f"{{Collection ID}} = '{collection_id}'"
        collection_records = self.client.list_records('collections', filter_formula=filter_formula)
        
        if not collection_records:
            return []
        
        collection_record_id = collection_records[0].id
        
        # Find products linked to this collection
        filter_formula = f"FIND('{collection_record_id}', ARRAYJOIN({{Collection}}, ','))"
        records = self.client.list_records('products', filter_formula=filter_formula)
        return [Product.from_airtable_record(record) for record in records]
    
    def get_product_with_variations(self, product_id: str) -> tuple[Product, List[Variation]]:
        """Get a product and all its variations."""
        # Find product by ID
        filter_formula = f"{{Product ID}} = '{product_id}'"
        product_records = self.client.list_records('products', filter_formula=filter_formula)
        
        if not product_records:
            raise ValueError(f"Product not found: {product_id}")
        
        product = Product.from_airtable_record(product_records[0])
        
        # Get linked variations
        variations = []
        if product.variations:
            for var_id in product.variations:
                try:
                    var_record = self.client.get_record('variations', var_id)
                    variations.append(Variation.from_airtable_record(var_record))
                except Exception as e:
                    self.logger.warning(f"Failed to get variation {var_id}: {e}")
        
        return product, variations
    
    def get_variation_with_mockups(self, variation_id: str) -> tuple[Variation, List[Mockup]]:
        """Get a variation and all its mockups."""
        variation_record = self.client.get_record('variations', variation_id)
        variation = Variation.from_airtable_record(variation_record)
        
        # Get linked mockups
        mockups = []
        if variation.mockups:
            for mockup_id in variation.mockups:
                try:
                    mockup_record = self.client.get_record('mockups', mockup_id)
                    mockups.append(Mockup.from_airtable_record(mockup_record))
                except Exception as e:
                    self.logger.warning(f"Failed to get mockup {mockup_id}: {e}")
        
        return variation, mockups
    
    def create_product_workflow(self, product_data: Dict[str, Any], 
                               variations_data: List[Dict[str, Any]]) -> Product:
        """
        Create a complete product workflow with variations.
        
        Args:
            product_data: Product data dictionary
            variations_data: List of variation data dictionaries
            
        Returns:
            Product: Created product with linked variations
        """
        try:
            # Create product
            product = Product(**product_data)
            product_record = self.client.create_record('products', product.to_airtable_fields())
            product.record_id = product_record.id
            
            # Create variations and link to product
            variation_ids = []
            for var_data in variations_data:
                variation = Variation(**var_data)
                variation.product = [product_record.id]
                
                var_record = self.client.create_record('variations', variation.to_airtable_fields())
                variation_ids.append(var_record.id)
            
            # Update product with variation links
            if variation_ids:
                self.client.update_record('products', product_record.id, 
                                        {'Variations': variation_ids})
                product.variations = variation_ids
            
            self.logger.info(f"Created product workflow: {product.product_name}")
            return product
            
        except Exception as e:
            self.logger.error(f"Failed to create product workflow: {e}")
            raise
    
    def update_product_status(self, product_id: str, status: ProductStatus, 
                             error_message: str = None) -> Product:
        """Update product status and optionally log errors."""
        filter_formula = f"{{Product ID}} = '{product_id}'"
        product_records = self.client.list_records('products', filter_formula=filter_formula)
        
        if not product_records:
            raise ValueError(f"Product not found: {product_id}")
        
        update_fields = {'Status': status.value}
        
        if error_message:
            # Append to existing error logs
            existing_logs = product_records[0].fields.get('Error Logs', '')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_log = f"[{timestamp}] {error_message}"
            
            if existing_logs:
                update_fields['Error Logs'] = f"{existing_logs}\n{new_log}"
            else:
                update_fields['Error Logs'] = new_log
        
        updated_record = self.client.update_record('products', product_records[0].id, update_fields)
        return Product.from_airtable_record(updated_record)
    
    def get_workflow_statistics(self) -> Dict[str, int]:
        """Get workflow statistics for dashboard."""
        stats = {}
        
        # Product status counts
        for status in ProductStatus:
            count = len(self.get_products_by_status(status))
            stats[f"products_{status.value.lower()}"] = count
        
        # Total counts
        stats['total_products'] = len(self.client.list_records('products'))
        stats['total_variations'] = len(self.client.list_records('variations'))
        stats['total_mockups'] = len(self.client.list_records('mockups'))
        stats['total_listings'] = len(self.client.list_records('listings'))
        
        return stats
