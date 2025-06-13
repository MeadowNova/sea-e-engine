
#!/usr/bin/env python3
"""
Airtable API Client for SEA-E Engine
===================================

Production-ready Airtable API client for managing relational product data
and workflow orchestration across multiple linked tables.
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import requests
from dataclasses import dataclass


@dataclass
class AirtableRecord:
    """Represents an Airtable record with ID and fields."""
    id: str
    fields: Dict[str, Any]
    created_time: Optional[str] = None


class AirtableAPIError(Exception):
    """Custom exception for Airtable API errors."""
    pass


class AirtableClient:
    """
    Production-ready Airtable API client with comprehensive CRUD operations,
    relationship management, error handling, and retry mechanisms.
    """
    
    # Table IDs from the Airtable base
    TABLE_IDS = {
        'collections': 'tblvisompxGo5cznM',
        'products': 'tblCmRSspMhKnLqfi',
        'variations': 'tblBARUvILonZ3i86',
        'mockups': 'tbl3ZtltnQ2Hyn1rT',
        'listings': 'tbll44wQCo9DPct0g',
        'dashboard': 'tbl6TieG8vqUtPuZV'
    }
    
    # Field mappings for each table
    FIELD_MAPPINGS = {
        'collections': {
            'name': 'Collection Name',
            'collection_id': 'Collection ID',
            'description': 'Description',
            'status': 'Status',
            'products': 'Products'
        },
        'products': {
            'name': 'Product Name',
            'product_id': 'Product ID',
            'description': 'Description',
            'product_type': 'Product Type',
            'status': 'Status',
            'priority': 'Priority',
            'blueprint_key': 'Blueprint Key',
            'print_provider': 'Print Provider',
            'batch_group': 'Batch Group',
            'base_price': 'Base Price',
            'selling_price': 'Selling Price',
            'error_logs': 'Error Logs',
            'collection': 'Collection',
            'variations': 'Variations',
            'listings': 'Listings'
        },
        'variations': {
            'variation_id': 'Variation ID',
            'color': 'Color',
            'size': 'Size',
            'sku': 'SKU',
            'printify_variant_id': 'Printify Variant ID',
            'status': 'Status',
            'price': 'Price',
            'availability': 'Availability',
            'product': 'Product',
            'mockups': 'Mockups'
        },
        'mockups': {
            'mockup_id': 'Mockup ID',
            'mockup_type': 'Mockup Type',
            'generation_status': 'Generation Status',
            'quality_score': 'Quality Score',
            'file_path': 'File Path',
            'approved': 'Approved',
            'variation': 'Variation'
        },
        'listings': {
            'listing_id': 'Listing ID',
            'etsy_listing_id': 'Etsy Listing ID',
            'etsy_url': 'Etsy URL',
            'publication_status': 'Publication Status',
            'seo_tags': 'SEO Tags',
            'optimized_tags': 'Optimized Tags',
            'views': 'Views',
            'favorites': 'Favorites',
            'sales': 'Sales',
            'last_sync_date': 'Last Sync Date',
            'product': 'Product'
        },
        'dashboard': {
            'dashboard_id': 'Dashboard ID',
            'metric_name': 'Metric Name',
            'metric_value': 'Metric Value',
            'category': 'Category',
            'trend': 'Trend'
        }
    }
    
    def __init__(self, api_key: str = None, base_id: str = None):
        """
        Initialize Airtable client with API credentials.
        
        Args:
            api_key: Airtable API key (defaults to environment variable)
            base_id: Airtable base ID (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv('AIRTABLE_API_KEY')
        self.base_id = base_id or os.getenv('AIRTABLE_BASE_ID')
        
        if not self.api_key:
            raise ValueError("Airtable API key is required")
        if not self.base_id:
            raise ValueError("Airtable base ID is required")
        
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Set up logging
        self.logger = logging.getLogger("airtable_api")
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 5 requests per second max
    
    def _rate_limit(self):
        """Implement rate limiting to respect Airtable API limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, 
                     params: Dict = None, retries: int = 3) -> Dict:
        """
        Make HTTP request to Airtable API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            retries: Number of retry attempts
            
        Returns:
            Dict: API response data
            
        Raises:
            AirtableAPIError: If request fails after retries
        """
        self._rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(retries + 1):
            try:
                self.logger.debug(f"Making {method} request to {url}")
                
                if method == 'GET':
                    response = requests.get(url, headers=self.headers, params=params)
                elif method == 'POST':
                    response = requests.post(url, headers=self.headers, json=data)
                elif method == 'PATCH':
                    response = requests.patch(url, headers=self.headers, json=data)
                elif method == 'DELETE':
                    response = requests.delete(url, headers=self.headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 30))
                    self.logger.warning(f"Rate limited, waiting {retry_after} seconds")
                    time.sleep(retry_after)
                    continue
                
                # Check for success
                response.raise_for_status()
                
                return response.json() if response.content else {}
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                if attempt == retries:
                    raise AirtableAPIError(f"Request failed after {retries + 1} attempts: {e}")
                
                # Exponential backoff
                wait_time = 2 ** attempt
                self.logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    def test_connection(self) -> bool:
        """
        Test Airtable API connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info("Testing Airtable API connection...")
            
            # Try to list records from products table (limit 1)
            self._make_request('GET', f"{self.TABLE_IDS['products']}", 
                             params={'maxRecords': 1})
            
            self.logger.info("Airtable API connection successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Airtable API connection test failed: {e}")
            return False
    
    def list_records(self, table_name: str, view: str = None, 
                    filter_formula: str = None, sort: List[Dict] = None,
                    max_records: int = None) -> List[AirtableRecord]:
        """
        List records from a table.
        
        Args:
            table_name: Name of the table
            view: View name to use
            filter_formula: Airtable formula to filter records
            sort: List of sort specifications
            max_records: Maximum number of records to return
            
        Returns:
            List[AirtableRecord]: List of records
        """
        try:
            table_id = self.TABLE_IDS.get(table_name)
            if not table_id:
                raise ValueError(f"Unknown table: {table_name}")
            
            params = {}
            if view:
                params['view'] = view
            if filter_formula:
                params['filterByFormula'] = filter_formula
            if sort:
                params['sort'] = sort
            if max_records:
                params['maxRecords'] = max_records
            
            self.logger.info(f"Listing records from table: {table_name}")
            
            all_records = []
            offset = None
            
            while True:
                if offset:
                    params['offset'] = offset
                
                response = self._make_request('GET', table_id, params=params)
                
                records = response.get('records', [])
                for record in records:
                    all_records.append(AirtableRecord(
                        id=record['id'],
                        fields=record['fields'],
                        created_time=record.get('createdTime')
                    ))
                
                offset = response.get('offset')
                if not offset:
                    break
            
            self.logger.info(f"Retrieved {len(all_records)} records from {table_name}")
            return all_records
            
        except Exception as e:
            self.logger.error(f"Failed to list records from {table_name}: {e}")
            raise
    
    def get_record(self, table_name: str, record_id: str) -> AirtableRecord:
        """
        Get a specific record by ID.
        
        Args:
            table_name: Name of the table
            record_id: Record ID
            
        Returns:
            AirtableRecord: The record
        """
        try:
            table_id = self.TABLE_IDS.get(table_name)
            if not table_id:
                raise ValueError(f"Unknown table: {table_name}")
            
            self.logger.info(f"Getting record {record_id} from {table_name}")
            
            response = self._make_request('GET', f"{table_id}/{record_id}")
            
            return AirtableRecord(
                id=response['id'],
                fields=response['fields'],
                created_time=response.get('createdTime')
            )
            
        except AirtableAPIError as e:
            # Check if it's a 404/403 error (record not found)
            if "404" in str(e) or "403" in str(e):
                self.logger.info(f"Record {record_id} not found in {table_name}")
                return None
            else:
                self.logger.error(f"Failed to get record {record_id} from {table_name}: {e}")
                raise
        except Exception as e:
            self.logger.error(f"Failed to get record {record_id} from {table_name}: {e}")
            raise
    
    def create_record(self, table_name: str, fields: Dict[str, Any]) -> AirtableRecord:
        """
        Create a new record.
        
        Args:
            table_name: Name of the table
            fields: Record fields
            
        Returns:
            AirtableRecord: Created record
        """
        try:
            table_id = self.TABLE_IDS.get(table_name)
            if not table_id:
                raise ValueError(f"Unknown table: {table_name}")
            
            self.logger.info(f"Creating record in {table_name}")
            
            data = {'fields': fields}
            response = self._make_request('POST', table_id, data=data)
            
            return AirtableRecord(
                id=response['id'],
                fields=response['fields'],
                created_time=response.get('createdTime')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create record in {table_name}: {e}")
            raise
    
    def update_record(self, table_name: str, record_id: str, 
                     fields: Dict[str, Any]) -> AirtableRecord:
        """
        Update an existing record.
        
        Args:
            table_name: Name of the table
            record_id: Record ID to update
            fields: Fields to update
            
        Returns:
            AirtableRecord: Updated record
        """
        try:
            table_id = self.TABLE_IDS.get(table_name)
            if not table_id:
                raise ValueError(f"Unknown table: {table_name}")
            
            self.logger.info(f"Updating record {record_id} in {table_name}")
            
            data = {'fields': fields}
            response = self._make_request('PATCH', f"{table_id}/{record_id}", data=data)
            
            return AirtableRecord(
                id=response['id'],
                fields=response['fields'],
                created_time=response.get('createdTime')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update record {record_id} in {table_name}: {e}")
            raise
    
    def delete_record(self, table_name: str, record_id: str) -> bool:
        """
        Delete a record.
        
        Args:
            table_name: Name of the table
            record_id: Record ID to delete
            
        Returns:
            bool: True if successful
        """
        try:
            table_id = self.TABLE_IDS.get(table_name)
            if not table_id:
                raise ValueError(f"Unknown table: {table_name}")
            
            self.logger.info(f"Deleting record {record_id} from {table_name}")
            
            self._make_request('DELETE', f"{table_id}/{record_id}")
            
            self.logger.info(f"Record {record_id} deleted successfully")
            return True
            
        except AirtableAPIError as e:
            # Check if it's a 404/403 error (record not found)
            if "404" in str(e) or "403" in str(e):
                self.logger.info(f"Record {record_id} not found in {table_name} for deletion")
                return False
            else:
                self.logger.error(f"Failed to delete record {record_id} from {table_name}: {e}")
                raise
        except Exception as e:
            self.logger.error(f"Failed to delete record {record_id} from {table_name}: {e}")
            raise
    
    def batch_create(self, table_name: str, records: List[Dict[str, Any]]) -> List[AirtableRecord]:
        """
        Create multiple records in batch (up to 10 at a time).
        
        Args:
            table_name: Name of the table
            records: List of record fields
            
        Returns:
            List[AirtableRecord]: Created records
        """
        try:
            table_id = self.TABLE_IDS.get(table_name)
            if not table_id:
                raise ValueError(f"Unknown table: {table_name}")
            
            all_created = []
            
            # Process in batches of 10 (Airtable limit)
            for i in range(0, len(records), 10):
                batch = records[i:i+10]
                
                self.logger.info(f"Creating batch of {len(batch)} records in {table_name}")
                
                data = {
                    'records': [{'fields': record} for record in batch]
                }
                
                response = self._make_request('POST', table_id, data=data)
                
                for record in response.get('records', []):
                    all_created.append(AirtableRecord(
                        id=record['id'],
                        fields=record['fields'],
                        created_time=record.get('createdTime')
                    ))
            
            self.logger.info(f"Created {len(all_created)} records in {table_name}")
            return all_created
            
        except Exception as e:
            self.logger.error(f"Failed to batch create records in {table_name}: {e}")
            raise
    
    def batch_update(self, table_name: str, updates: List[Dict[str, Any]]) -> List[AirtableRecord]:
        """
        Update multiple records in batch (up to 10 at a time).
        
        Args:
            table_name: Name of the table
            updates: List of {'id': record_id, 'fields': fields} dictionaries
            
        Returns:
            List[AirtableRecord]: Updated records
        """
        try:
            table_id = self.TABLE_IDS.get(table_name)
            if not table_id:
                raise ValueError(f"Unknown table: {table_name}")
            
            all_updated = []
            
            # Process in batches of 10 (Airtable limit)
            for i in range(0, len(updates), 10):
                batch = updates[i:i+10]
                
                self.logger.info(f"Updating batch of {len(batch)} records in {table_name}")
                
                data = {
                    'records': [{'id': update['id'], 'fields': update['fields']} 
                              for update in batch]
                }
                
                response = self._make_request('PATCH', table_id, data=data)
                
                for record in response.get('records', []):
                    all_updated.append(AirtableRecord(
                        id=record['id'],
                        fields=record['fields'],
                        created_time=record.get('createdTime')
                    ))
            
            self.logger.info(f"Updated {len(all_updated)} records in {table_name}")
            return all_updated
            
        except Exception as e:
            self.logger.error(f"Failed to batch update records in {table_name}: {e}")
            raise
    
    def search_records(self, table_name: str, search_term: str, 
                      fields: List[str] = None) -> List[AirtableRecord]:
        """
        Search for records containing specific text.
        
        Args:
            table_name: Name of the table
            search_term: Text to search for
            fields: Specific fields to search in (optional)
            
        Returns:
            List[AirtableRecord]: Matching records
        """
        try:
            # Build search formula
            if fields:
                field_mappings = self.FIELD_MAPPINGS.get(table_name, {})
                search_conditions = []
                
                for field in fields:
                    airtable_field = field_mappings.get(field, field)
                    search_conditions.append(f"SEARCH('{search_term}', {{{airtable_field}}})")
                
                filter_formula = f"OR({', '.join(search_conditions)})"
            else:
                # Search in all text fields (basic implementation)
                filter_formula = f"SEARCH('{search_term}', CONCATENATE(VALUES))"
            
            return self.list_records(table_name, filter_formula=filter_formula)
            
        except Exception as e:
            self.logger.error(f"Failed to search records in {table_name}: {e}")
            raise
    
    def get_linked_records(self, table_name: str, record_id: str, 
                          link_field: str) -> List[AirtableRecord]:
        """
        Get records linked to a specific record.
        
        Args:
            table_name: Name of the source table
            record_id: Source record ID
            link_field: Name of the link field
            
        Returns:
            List[AirtableRecord]: Linked records
        """
        try:
            # Get the source record
            source_record = self.get_record(table_name, record_id)
            
            # Get linked record IDs
            field_mappings = self.FIELD_MAPPINGS.get(table_name, {})
            airtable_field = field_mappings.get(link_field, link_field)
            linked_ids = source_record.fields.get(airtable_field, [])
            
            if not linked_ids:
                return []
            
            # Determine target table based on link field
            target_table = self._get_target_table(table_name, link_field)
            
            # Get linked records
            linked_records = []
            for linked_id in linked_ids:
                try:
                    record = self.get_record(target_table, linked_id)
                    linked_records.append(record)
                except Exception as e:
                    self.logger.warning(f"Failed to get linked record {linked_id}: {e}")
            
            return linked_records
            
        except Exception as e:
            self.logger.error(f"Failed to get linked records: {e}")
            raise
    
    def _get_target_table(self, source_table: str, link_field: str) -> str:
        """
        Determine target table for a link field.
        
        Args:
            source_table: Source table name
            link_field: Link field name
            
        Returns:
            str: Target table name
        """
        # Define relationships
        relationships = {
            'products': {
                'collection': 'collections',
                'variations': 'variations',
                'listings': 'listings'
            },
            'variations': {
                'product': 'products',
                'mockups': 'mockups'
            },
            'mockups': {
                'variation': 'variations'
            },
            'listings': {
                'product': 'products'
            },
            'collections': {
                'products': 'products'
            }
        }
        
        return relationships.get(source_table, {}).get(link_field, source_table)
    
    def create_linked_record(self, table_name: str, fields: Dict[str, Any],
                           parent_table: str, parent_id: str, 
                           link_field: str) -> AirtableRecord:
        """
        Create a record and link it to a parent record.
        
        Args:
            table_name: Name of the table to create record in
            fields: Record fields
            parent_table: Parent table name
            parent_id: Parent record ID
            link_field: Link field name in child table
            
        Returns:
            AirtableRecord: Created record
        """
        try:
            # Add parent link to fields
            field_mappings = self.FIELD_MAPPINGS.get(table_name, {})
            airtable_field = field_mappings.get(link_field, link_field)
            fields[airtable_field] = [parent_id]
            
            # Create the record
            return self.create_record(table_name, fields)
            
        except Exception as e:
            self.logger.error(f"Failed to create linked record: {e}")
            raise
    
    def update_dashboard_metric(self, metric_name: str, metric_value: str, 
                               category: str, trend: str = None) -> AirtableRecord:
        """
        Update or create a dashboard metric.
        
        Args:
            metric_name: Name of the metric
            metric_value: Value of the metric
            category: Category of the metric
            trend: Trend information (optional)
            
        Returns:
            AirtableRecord: Updated or created record
        """
        try:
            # Search for existing metric
            filter_formula = f"{{Metric Name}} = '{metric_name}'"
            existing = self.list_records('dashboard', filter_formula=filter_formula)
            
            fields = {
                'Metric Name': metric_name,
                'Metric Value': metric_value,
                'Category': category
            }
            
            if trend:
                fields['Trend'] = trend
            
            if existing:
                # Update existing record
                return self.update_record('dashboard', existing[0].id, fields)
            else:
                # Create new record
                fields['Dashboard ID'] = f"metric_{int(time.time())}"
                return self.create_record('dashboard', fields)
                
        except Exception as e:
            self.logger.error(f"Failed to update dashboard metric: {e}")
            raise
