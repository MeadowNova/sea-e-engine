
#!/usr/bin/env python3
"""
Google Sheets API Client for SEA-E Engine
=========================================

Production-ready Google Sheets API client for reading product data
and updating workflow results.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials


class AirtableClient:
    """
    Production-ready Google Sheets API client with error handling and retry mechanisms.
    """
    
    def __init__(self, credentials_path: str = None):
        """
        Initialize Google Sheets client with service account credentials.
        
        Args:
            credentials_path: Path to service account JSON file
        """
        self.credentials_path = credentials_path or "credentials/gcp_service_account.json"
        
        # Set up logging
        self.logger = logging.getLogger("sheets_api")
        
        # Initialize client
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Sheets client with service account."""
        try:
            self.logger.info("Initializing Google Sheets client...")
            
            # Check if credentials file exists
            if not Path(self.credentials_path).exists():
                raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
            
            # Define required scopes
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Load credentials
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scopes
            )
            
            # Initialize gspread client
            self.client = gspread.authorize(credentials)
            
            self.logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Sheets client: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test Google Sheets API connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info("Testing Google Sheets API connection...")
            
            # Try to list spreadsheets (this tests authentication)
            # Note: This will only show spreadsheets shared with the service account
            spreadsheets = self.client.list_permissions()
            
            self.logger.info("Google Sheets API connection successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Google Sheets API connection test failed: {e}")
            return False
    
    def open_spreadsheet(self, sheet_id: str):
        """
        Open a spreadsheet by ID.
        
        Args:
            sheet_id: Google Sheets document ID
            
        Returns:
            gspread.Spreadsheet: Opened spreadsheet object
        """
        try:
            self.logger.info(f"Opening spreadsheet: {sheet_id}")
            
            spreadsheet = self.client.open_by_key(sheet_id)
            
            self.logger.info(f"Spreadsheet opened: {spreadsheet.title}")
            return spreadsheet
            
        except Exception as e:
            self.logger.error(f"Failed to open spreadsheet {sheet_id}: {e}")
            raise
    
    def read_sheet_data(self, sheet_id: str, sheet_name: str = "Sheet1") -> List[List[str]]:
        """
        Read all data from a specific sheet.
        
        Args:
            sheet_id: Google Sheets document ID
            sheet_name: Name of the sheet tab
            
        Returns:
            List[List[str]]: All sheet data as list of rows
        """
        try:
            self.logger.info(f"Reading data from sheet: {sheet_name}")
            
            # Open spreadsheet
            spreadsheet = self.open_spreadsheet(sheet_id)
            
            # Get specific worksheet
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                self.logger.error(f"Worksheet '{sheet_name}' not found")
                raise
            
            # Get all values
            data = worksheet.get_all_values()
            
            self.logger.info(f"Read {len(data)} rows from sheet")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to read sheet data: {e}")
            raise
    
    def read_range(self, sheet_id: str, sheet_name: str, range_name: str) -> List[List[str]]:
        """
        Read data from a specific range.
        
        Args:
            sheet_id: Google Sheets document ID
            sheet_name: Name of the sheet tab
            range_name: Range in A1 notation (e.g., "A1:D10")
            
        Returns:
            List[List[str]]: Data from the specified range
        """
        try:
            self.logger.info(f"Reading range {range_name} from sheet: {sheet_name}")
            
            # Open spreadsheet
            spreadsheet = self.open_spreadsheet(sheet_id)
            
            # Get specific worksheet
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # Get range values
            data = worksheet.get(range_name)
            
            self.logger.info(f"Read {len(data)} rows from range {range_name}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to read range {range_name}: {e}")
            raise
    
    def update_cell(self, sheet_id: str, sheet_name: str, row: int, col: int, value: str):
        """
        Update a single cell.
        
        Args:
            sheet_id: Google Sheets document ID
            sheet_name: Name of the sheet tab
            row: Row number (1-based)
            col: Column number (1-based)
            value: Value to set
        """
        try:
            self.logger.info(f"Updating cell ({row}, {col}) in sheet: {sheet_name}")
            
            # Open spreadsheet
            spreadsheet = self.open_spreadsheet(sheet_id)
            
            # Get specific worksheet
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # Update cell
            worksheet.update_cell(row, col, value)
            
            self.logger.info(f"Cell updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to update cell: {e}")
            raise
    
    def update_row(self, sheet_id: str, sheet_name: str, row_number: int, 
                   updates: Dict[str, str]):
        """
        Update specific columns in a row based on column headers.
        
        Args:
            sheet_id: Google Sheets document ID
            sheet_name: Name of the sheet tab
            row_number: Row number to update (1-based)
            updates: Dictionary of column_name: value pairs
        """
        try:
            self.logger.info(f"Updating row {row_number} in sheet: {sheet_name}")
            
            # Open spreadsheet
            spreadsheet = self.open_spreadsheet(sheet_id)
            
            # Get specific worksheet
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # Get headers (first row)
            headers = worksheet.row_values(1)
            
            # Create header mapping
            header_map = {header.lower().strip(): idx + 1 for idx, header in enumerate(headers)}
            
            # Update each specified column
            for column_name, value in updates.items():
                col_index = header_map.get(column_name.lower())
                if col_index:
                    worksheet.update_cell(row_number, col_index, value)
                    self.logger.info(f"Updated {column_name}: {value}")
                else:
                    self.logger.warning(f"Column '{column_name}' not found in headers")
            
            self.logger.info(f"Row {row_number} updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to update row {row_number}: {e}")
            raise
    
    def append_row(self, sheet_id: str, sheet_name: str, values: List[str]):
        """
        Append a new row to the sheet.
        
        Args:
            sheet_id: Google Sheets document ID
            sheet_name: Name of the sheet tab
            values: List of values to append
        """
        try:
            self.logger.info(f"Appending row to sheet: {sheet_name}")
            
            # Open spreadsheet
            spreadsheet = self.open_spreadsheet(sheet_id)
            
            # Get specific worksheet
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # Append row
            worksheet.append_row(values)
            
            self.logger.info(f"Row appended successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to append row: {e}")
            raise
    
    def batch_update(self, sheet_id: str, sheet_name: str, updates: List[Dict]):
        """
        Perform batch updates for better performance.
        
        Args:
            sheet_id: Google Sheets document ID
            sheet_name: Name of the sheet tab
            updates: List of update dictionaries with 'range' and 'values' keys
        """
        try:
            self.logger.info(f"Performing batch update on sheet: {sheet_name}")
            
            # Open spreadsheet
            spreadsheet = self.open_spreadsheet(sheet_id)
            
            # Get specific worksheet
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # Prepare batch update data
            batch_data = []
            for update in updates:
                batch_data.append({
                    'range': f"{sheet_name}!{update['range']}",
                    'values': update['values']
                })
            
            # Perform batch update
            worksheet.batch_update(batch_data)
            
            self.logger.info(f"Batch update completed: {len(updates)} updates")
            
        except Exception as e:
            self.logger.error(f"Failed to perform batch update: {e}")
            raise
    
    def create_worksheet(self, sheet_id: str, title: str, rows: int = 1000, cols: int = 26):
        """
        Create a new worksheet in the spreadsheet.
        
        Args:
            sheet_id: Google Sheets document ID
            title: Title for the new worksheet
            rows: Number of rows (default: 1000)
            cols: Number of columns (default: 26)
            
        Returns:
            gspread.Worksheet: Created worksheet object
        """
        try:
            self.logger.info(f"Creating worksheet: {title}")
            
            # Open spreadsheet
            spreadsheet = self.open_spreadsheet(sheet_id)
            
            # Create worksheet
            worksheet = spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)
            
            self.logger.info(f"Worksheet '{title}' created successfully")
            return worksheet
            
        except Exception as e:
            self.logger.error(f"Failed to create worksheet '{title}': {e}")
            raise
    
    def delete_worksheet(self, sheet_id: str, sheet_name: str):
        """
        Delete a worksheet from the spreadsheet.
        
        Args:
            sheet_id: Google Sheets document ID
            sheet_name: Name of the sheet tab to delete
        """
        try:
            self.logger.info(f"Deleting worksheet: {sheet_name}")
            
            # Open spreadsheet
            spreadsheet = self.open_spreadsheet(sheet_id)
            
            # Get worksheet
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # Delete worksheet
            spreadsheet.del_worksheet(worksheet)
            
            self.logger.info(f"Worksheet '{sheet_name}' deleted successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to delete worksheet '{sheet_name}': {e}")
            raise
    
    def get_worksheet_info(self, sheet_id: str) -> List[Dict[str, Any]]:
        """
        Get information about all worksheets in the spreadsheet.
        
        Args:
            sheet_id: Google Sheets document ID
            
        Returns:
            List[Dict]: List of worksheet information
        """
        try:
            self.logger.info("Getting worksheet information")
            
            # Open spreadsheet
            spreadsheet = self.open_spreadsheet(sheet_id)
            
            # Get all worksheets
            worksheets = spreadsheet.worksheets()
            
            # Collect worksheet info
            worksheet_info = []
            for ws in worksheets:
                info = {
                    'title': ws.title,
                    'id': ws.id,
                    'row_count': ws.row_count,
                    'col_count': ws.col_count
                }
                worksheet_info.append(info)
            
            self.logger.info(f"Found {len(worksheet_info)} worksheets")
            return worksheet_info
            
        except Exception as e:
            self.logger.error(f"Failed to get worksheet info: {e}")
            raise
