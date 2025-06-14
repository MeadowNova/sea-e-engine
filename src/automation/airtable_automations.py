#!/usr/bin/env python3
"""
Airtable Automations for SEA-E Engine
====================================

Enhanced Airtable integration with automatic population of:
- Blueprint IDs
- Print Provider details
- SKUs and variant information
- Etsy Listing IDs
- Titles, Tags, and metadata
- Google Sheets URLs and status tracking

Features:
- Bulletproof automation workflows
- Data validation and error handling
- Automatic field population
- Status tracking and monitoring
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from api.airtable_client import AirtableClient
from api.printify import PrintifyAPIClient
from api.etsy import EtsyAPIClient

logger = logging.getLogger("airtable_automations")


class AirtableAutomationEngine:
    """
    Bulletproof Airtable automation engine for SEA-E workflow.
    """
    
    def __init__(self, airtable_client: AirtableClient = None,
                 printify_client: PrintifyAPIClient = None,
                 etsy_client: EtsyAPIClient = None):
        """
        Initialize automation engine.
        
        Args:
            airtable_client: Existing Airtable client
            printify_client: Existing Printify client
            etsy_client: Existing Etsy client
        """
        self.airtable = airtable_client or AirtableClient()
        self.printify = printify_client or PrintifyAPIClient()
        self.etsy = etsy_client or EtsyAPIClient()
        
        # Validation rules
        self.required_fields = {
            'products': ['product_name', 'blueprint_id', 'print_provider_id'],
            'variations': ['variation_name', 'color', 'size'],
            'mockups': ['mockup_type', 'file_path'],
            'listings': ['title', 'description', 'price']
        }
        
        logger.info("AirtableAutomationEngine initialized")
    
    def create_complete_product_record(self, product_data: Dict[str, Any]) -> str:
        """
        Create a complete product record with all automated fields populated.
        
        Args:
            product_data: Product information
            
        Returns:
            str: Created product record ID
        """
        try:
            logger.info(f"Creating complete product record: {product_data.get('product_name')}")
            
            # Validate required fields
            self._validate_product_data(product_data)
            
            # Get blueprint and print provider details
            blueprint_details = self._get_blueprint_details(product_data['blueprint_id'])
            print_provider_details = self._get_print_provider_details(
                product_data['blueprint_id'], 
                product_data['print_provider_id']
            )
            
            # Build complete product record
            complete_record = {
                # Basic product info
                'product_name': product_data['product_name'],
                'description': product_data.get('description', ''),
                'category': product_data.get('category', 'Apparel'),
                'status': 'Draft',
                'priority': product_data.get('priority', 'Medium'),
                
                # Printify details
                'blueprint_id': product_data['blueprint_id'],
                'blueprint_title': blueprint_details.get('title', ''),
                'blueprint_brand': blueprint_details.get('brand', ''),
                'blueprint_model': blueprint_details.get('model', ''),
                'print_provider_id': product_data['print_provider_id'],
                'print_provider_name': print_provider_details.get('title', ''),
                'print_provider_location': self._format_location(print_provider_details.get('location', {})),
                
                # Timestamps
                'created_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                
                # Automation tracking
                'automation_status': 'Initialized',
                'automation_log': f"Product record created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
            # Add optional fields if provided
            optional_fields = ['design_file_path', 'target_price', 'profit_margin', 'tags']
            for field in optional_fields:
                if field in product_data:
                    complete_record[field] = product_data[field]
            
            # Create product record
            product_record_id = self.airtable.create_record('products', complete_record)
            
            logger.info(f"✅ Created product record: {product_record_id}")
            
            # Create variations if provided
            if 'variations' in product_data:
                self._create_product_variations(product_record_id, product_data['variations'])
            
            return product_record_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create complete product record: {e}")
            raise
    
    def populate_printify_product_details(self, product_record_id: str, printify_product_id: str):
        """
        Populate Airtable record with Printify product details after creation.
        
        Args:
            product_record_id: Airtable product record ID
            printify_product_id: Printify product ID
        """
        try:
            logger.info(f"Populating Printify details for record: {product_record_id}")
            
            # Get Printify product details
            printify_product = self.printify.get_product(printify_product_id)
            
            # Extract variant information
            variants = printify_product.get('variants', [])
            variant_info = self._extract_variant_info(variants)
            
            # Update product record
            updates = {
                'printify_product_id': printify_product_id,
                'printify_status': printify_product.get('status', 'unknown'),
                'total_variants': len(variants),
                'available_colors': variant_info['colors'],
                'available_sizes': variant_info['sizes'],
                'variant_skus': variant_info['skus'],
                'printify_created_date': printify_product.get('created_at', ''),
                'automation_status': 'Printify Created',
                'automation_log': self._append_log(
                    product_record_id, 
                    f"Printify product created: {printify_product_id}"
                )
            }
            
            self.airtable.update_record('products', product_record_id, updates)
            
            logger.info(f"✅ Updated product record with Printify details")
            
        except Exception as e:
            logger.error(f"❌ Failed to populate Printify details: {e}")
            raise
    
    def populate_etsy_listing_details(self, product_record_id: str, etsy_listing_id: str):
        """
        Populate Airtable record with Etsy listing details after creation.
        
        Args:
            product_record_id: Airtable product record ID
            etsy_listing_id: Etsy listing ID
        """
        try:
            logger.info(f"Populating Etsy details for record: {product_record_id}")
            
            # Get Etsy listing details
            etsy_listing = self.etsy.get_listing(etsy_listing_id)
            
            # Update product record
            updates = {
                'etsy_listing_id': etsy_listing_id,
                'etsy_title': etsy_listing.get('title', ''),
                'etsy_url': f"https://www.etsy.com/listing/{etsy_listing_id}",
                'etsy_status': etsy_listing.get('state', 'unknown'),
                'etsy_price': etsy_listing.get('price', ''),
                'etsy_tags': ', '.join(etsy_listing.get('tags', [])),
                'etsy_created_date': etsy_listing.get('creation_timestamp', ''),
                'automation_status': 'Etsy Listed',
                'automation_log': self._append_log(
                    product_record_id, 
                    f"Etsy listing created: {etsy_listing_id}"
                )
            }
            
            self.airtable.update_record('products', product_record_id, updates)
            
            logger.info(f"✅ Updated product record with Etsy details")
            
        except Exception as e:
            logger.error(f"❌ Failed to populate Etsy details: {e}")
            raise
    
    def update_mockup_status(self, mockup_record_id: str, status_updates: Dict[str, Any]):
        """
        Update mockup record with generation and upload status.
        
        Args:
            mockup_record_id: Airtable mockup record ID
            status_updates: Status update information
        """
        try:
            logger.info(f"Updating mockup status: {mockup_record_id}")
            
            # Build update record
            updates = {
                'last_updated': datetime.now().isoformat()
            }
            
            # Add status updates
            if 'generation_status' in status_updates:
                updates['generation_status'] = status_updates['generation_status']
            
            if 'quality_score' in status_updates:
                updates['quality_score'] = status_updates['quality_score']
            
            if 'file_path' in status_updates:
                updates['file_path'] = status_updates['file_path']
            
            if 'google_sheets_url' in status_updates:
                updates['google_sheets_url'] = status_updates['google_sheets_url']
                updates['sheets_upload_status'] = 'Uploaded'
                updates['sheets_upload_date'] = datetime.now().isoformat()
            
            if 'google_drive_file_id' in status_updates:
                updates['google_drive_file_id'] = status_updates['google_drive_file_id']
            
            if 'approved' in status_updates:
                updates['approved'] = status_updates['approved']
            
            # Update record
            self.airtable.update_record('mockups', mockup_record_id, updates)
            
            logger.info(f"✅ Updated mockup status")
            
        except Exception as e:
            logger.error(f"❌ Failed to update mockup status: {e}")
            raise
    
    def _validate_product_data(self, product_data: Dict[str, Any]):
        """Validate required product data fields."""
        required = self.required_fields['products']
        missing = [field for field in required if field not in product_data]
        
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
    
    def _get_blueprint_details(self, blueprint_id: int) -> Dict[str, Any]:
        """Get blueprint details from Printify."""
        try:
            return self.printify.get_blueprint_details(blueprint_id)
        except Exception as e:
            logger.warning(f"Failed to get blueprint details: {e}")
            return {}
    
    def _get_print_provider_details(self, blueprint_id: int, print_provider_id: int) -> Dict[str, Any]:
        """Get print provider details from Printify."""
        try:
            providers = self.printify.get_print_providers(blueprint_id)
            for provider in providers:
                if provider.get('id') == print_provider_id:
                    return provider
            return {}
        except Exception as e:
            logger.warning(f"Failed to get print provider details: {e}")
            return {}
    
    def _format_location(self, location: Dict[str, Any]) -> str:
        """Format print provider location."""
        if not location:
            return ""
        
        parts = []
        if location.get('city'):
            parts.append(location['city'])
        if location.get('region'):
            parts.append(location['region'])
        if location.get('country'):
            parts.append(location['country'])
        
        return ", ".join(parts)
    
    def _extract_variant_info(self, variants: List[Dict]) -> Dict[str, List]:
        """Extract variant information for Airtable storage."""
        colors = set()
        sizes = set()
        skus = []
        
        for variant in variants:
            options = variant.get('options', {})
            
            if 'color' in options:
                colors.add(options['color'])
            if 'size' in options:
                sizes.add(options['size'])
            
            if 'sku' in variant:
                skus.append(variant['sku'])
        
        return {
            'colors': list(colors),
            'sizes': list(sizes),
            'skus': skus
        }
    
    def _create_product_variations(self, product_record_id: str, variations: List[Dict]):
        """Create variation records for a product."""
        try:
            for variation in variations:
                variation_record = {
                    'product': [product_record_id],  # Link to product
                    'variation_name': variation.get('name', ''),
                    'color': variation.get('color', ''),
                    'size': variation.get('size', ''),
                    'sku': variation.get('sku', ''),
                    'price': variation.get('price', 0),
                    'status': 'Active'
                }
                
                self.airtable.create_record('variations', variation_record)
            
            logger.info(f"✅ Created {len(variations)} variation records")
            
        except Exception as e:
            logger.error(f"❌ Failed to create variations: {e}")
            raise
    
    def _append_log(self, record_id: str, message: str) -> str:
        """Append message to automation log."""
        try:
            # Get current log
            record = self.airtable.get_record('products', record_id)
            current_log = record.get('automation_log', '')
            
            # Append new message
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_entry = f"\n{timestamp}: {message}"
            
            return current_log + new_entry
            
        except Exception as e:
            logger.warning(f"Failed to append log: {e}")
            return message
