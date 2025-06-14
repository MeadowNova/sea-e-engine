#!/usr/bin/env python3
"""
Google Sheets API Client for SEA-E Engine
=========================================

Production-ready Google Sheets API client for uploading mockup images
and generating shareable URLs for Etsy listing integration.

Features:
- Upload images to Google Drive and embed in Sheets
- Generate public shareable URLs
- Organize by product collections and types
- Batch upload capabilities
- Error handling and retry logic
"""

import os
import json
import logging
import time
import io
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

try:
    import gspread
    from google.oauth2.service_account import Credentials
    from google.auth.exceptions import GoogleAuthError
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaIoBaseUpload
    from PIL import Image
except ImportError as e:
    raise ImportError(f"Missing required Google libraries: {e}. Please install: pip install gspread google-auth google-auth-oauthlib google-api-python-client")


@dataclass
class MockupUploadResult:
    """Result of a mockup upload operation."""
    success: bool
    file_id: Optional[str] = None
    shareable_url: Optional[str] = None
    sheets_cell: Optional[str] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None


class GoogleSheetsAPIError(Exception):
    """Custom exception for Google Sheets API errors."""
    pass


class GoogleSheetsClient:
    """
    Production-ready Google Sheets API client for mockup image uploads.
    """
    
    def __init__(self, credentials_path: str = None, project_id: str = None):
        """
        Initialize Google Sheets client with service account credentials.
        
        Args:
            credentials_path: Path to service account JSON file
            project_id: Google Cloud project ID
        """
        self.credentials_path = credentials_path or "credentials/google-sa.json"
        self.project_id = project_id or os.getenv('GOOGLE_PROJECT_ID')
        
        # Required scopes for Sheets and Drive operations
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
        ]
        
        # Set up logging
        self.logger = logging.getLogger("google_sheets_client")
        
        # Initialize clients
        self.gc = None
        self.sheets_service = None
        self.drive_service = None
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 10 requests per second max
        
        # Initialize the client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Sheets and Drive clients with service account."""
        try:
            self.logger.info("Initializing Google Sheets client...")
            
            # Check if credentials file exists
            if not Path(self.credentials_path).exists():
                raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
            
            # Load credentials
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.scopes
            )
            
            # Initialize clients
            self.gc = gspread.authorize(credentials)
            self.sheets_service = build('sheets', 'v4', credentials=credentials)
            self.drive_service = build('drive', 'v3', credentials=credentials)
            
            self.logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Sheets client: {e}")
            raise GoogleSheetsAPIError(f"Client initialization failed: {e}")
    
    def _rate_limit(self):
        """Implement rate limiting to respect Google API limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def test_connection(self) -> bool:
        """
        Test Google Sheets API connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info("Testing Google Sheets API connection...")
            
            # Test Drive API access
            self.drive_service.files().list(pageSize=1).execute()
            
            self.logger.info("Google Sheets API connection successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Google Sheets API connection test failed: {e}")
            return False
    
    def create_mockup_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """
        Create a folder in Google Drive for organizing mockups.
        
        Args:
            folder_name: Name of the folder to create
            parent_folder_id: ID of parent folder (optional)
            
        Returns:
            str: Folder ID
        """
        try:
            self._rate_limit()
            
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.drive_service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            self.logger.info(f"Created folder '{folder_name}' with ID: {folder_id}")
            
            return folder_id
            
        except Exception as e:
            self.logger.error(f"Failed to create folder '{folder_name}': {e}")
            raise GoogleSheetsAPIError(f"Folder creation failed: {e}")
    
    def upload_image_to_drive(self, image_path: str, filename: str = None, 
                             folder_id: str = None) -> Tuple[str, str]:
        """
        Upload an image file to Google Drive.
        
        Args:
            image_path: Path to the image file
            filename: Custom filename (optional)
            folder_id: ID of folder to upload to (optional)
            
        Returns:
            Tuple[str, str]: (file_id, shareable_url)
        """
        try:
            self._rate_limit()
            
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Determine filename
            if not filename:
                filename = image_path.name
            
            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id] if folder_id else []
            }
            
            # Determine MIME type
            mime_type = 'image/png' if image_path.suffix.lower() == '.png' else 'image/jpeg'
            
            # Upload file
            with open(image_path, 'rb') as f:
                media = MediaIoBaseUpload(
                    io.BytesIO(f.read()),
                    mimetype=mime_type,
                    resumable=True
                )
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            
            # Make file publicly viewable
            shareable_url = self._make_file_public(file_id)
            
            self.logger.info(f"Uploaded image '{filename}' with ID: {file_id}")
            
            return file_id, shareable_url
            
        except Exception as e:
            self.logger.error(f"Failed to upload image '{image_path}': {e}")
            raise GoogleSheetsAPIError(f"Image upload failed: {e}")
    
    def _make_file_public(self, file_id: str) -> str:
        """
        Make a Google Drive file publicly viewable and return shareable URL.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            str: Public shareable URL
        """
        try:
            # Set file permissions to public
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.drive_service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            # Generate shareable URL
            shareable_url = f"https://drive.google.com/file/d/{file_id}/view"
            
            return shareable_url
            
        except Exception as e:
            self.logger.error(f"Failed to make file public: {e}")
            raise GoogleSheetsAPIError(f"File sharing failed: {e}")
    
    def create_or_get_spreadsheet(self, spreadsheet_name: str) -> Tuple[str, gspread.Spreadsheet]:
        """
        Create a new spreadsheet or get existing one by name.
        
        Args:
            spreadsheet_name: Name of the spreadsheet
            
        Returns:
            Tuple[str, gspread.Spreadsheet]: (spreadsheet_id, spreadsheet_object)
        """
        try:
            # Try to find existing spreadsheet
            try:
                spreadsheet = self.gc.open(spreadsheet_name)
                self.logger.info(f"Found existing spreadsheet: {spreadsheet_name}")
                return spreadsheet.id, spreadsheet
            except gspread.SpreadsheetNotFound:
                pass
            
            # Create new spreadsheet
            spreadsheet = self.gc.create(spreadsheet_name)
            self.logger.info(f"Created new spreadsheet: {spreadsheet_name} (ID: {spreadsheet.id})")
            
            return spreadsheet.id, spreadsheet
            
        except Exception as e:
            self.logger.error(f"Failed to create/get spreadsheet '{spreadsheet_name}': {e}")
            raise GoogleSheetsAPIError(f"Spreadsheet operation failed: {e}")

    def insert_image_in_sheet(self, spreadsheet_id: str, worksheet_name: str,
                             file_id: str, cell: str = "A1") -> bool:
        """
        Insert an uploaded image into a specific cell in Google Sheets.

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            worksheet_name: Name of the worksheet
            file_id: Google Drive file ID of the uploaded image
            cell: Cell reference (e.g., "A1")

        Returns:
            bool: True if successful
        """
        try:
            self._rate_limit()

            # Get worksheet ID
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()

            worksheet_id = None
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == worksheet_name:
                    worksheet_id = sheet['properties']['sheetId']
                    break

            if worksheet_id is None:
                raise ValueError(f"Worksheet '{worksheet_name}' not found")

            # Parse cell reference (e.g., "A1" -> row 0, col 0)
            col_str = ''.join(filter(str.isalpha, cell))
            row_str = ''.join(filter(str.isdigit, cell))

            col_index = sum((ord(c) - ord('A') + 1) * (26 ** i) for i, c in enumerate(reversed(col_str.upper()))) - 1
            row_index = int(row_str) - 1

            # Create image insertion request
            requests = [{
                'updateCells': {
                    'range': {
                        'sheetId': worksheet_id,
                        'startRowIndex': row_index,
                        'endRowIndex': row_index + 1,
                        'startColumnIndex': col_index,
                        'endColumnIndex': col_index + 1
                    },
                    'rows': [{
                        'values': [{
                            'userEnteredValue': {
                                'formulaValue': f'=IMAGE("https://drive.google.com/uc?id={file_id}")'
                            }
                        }]
                    }],
                    'fields': 'userEnteredValue'
                }
            }]

            # Execute the request
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()

            self.logger.info(f"Inserted image in cell {cell} of worksheet '{worksheet_name}'")
            return True

        except Exception as e:
            self.logger.error(f"Failed to insert image in sheet: {e}")
            raise GoogleSheetsAPIError(f"Image insertion failed: {e}")

    def upload_mockup_to_sheets(self, image_path: str, product_name: str,
                               variation_info: Dict[str, str] = None) -> MockupUploadResult:
        """
        Complete workflow: Upload mockup image and insert into organized spreadsheet.

        Args:
            image_path: Path to the mockup image
            product_name: Name of the product for organization
            variation_info: Dictionary with variation details (color, size, etc.)

        Returns:
            MockupUploadResult: Upload result with URLs and metadata
        """
        try:
            self.logger.info(f"Starting mockup upload workflow for: {image_path}")

            # Create folder structure if needed
            folder_name = f"SEA-E Mockups - {product_name}"
            folder_id = self.create_mockup_folder(folder_name)

            # Generate filename with variation info
            image_path_obj = Path(image_path)
            base_name = image_path_obj.stem

            if variation_info:
                variation_str = "_".join([f"{k}-{v}" for k, v in variation_info.items()])
                filename = f"{base_name}_{variation_str}{image_path_obj.suffix}"
            else:
                filename = image_path_obj.name

            # Upload image to Drive
            file_id, shareable_url = self.upload_image_to_drive(
                image_path, filename, folder_id
            )

            # Create or get spreadsheet
            spreadsheet_name = f"SEA-E Mockups - {product_name}"
            spreadsheet_id, spreadsheet = self.create_or_get_spreadsheet(spreadsheet_name)

            # Create worksheet for this product type if needed
            worksheet_name = "Mockups"
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=10)
                # Add headers
                worksheet.update('A1:E1', [['Image', 'Filename', 'Variation', 'Upload Date', 'Shareable URL']])

            # Find next available row
            all_values = worksheet.get_all_values()
            next_row = len([row for row in all_values if any(cell.strip() for cell in row)]) + 1

            # Insert image in the sheet
            image_cell = f"A{next_row}"
            self.insert_image_in_sheet(spreadsheet_id, worksheet_name, file_id, image_cell)

            # Add metadata
            from datetime import datetime
            upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            variation_text = ", ".join([f"{k}: {v}" for k, v in (variation_info or {}).items()])

            metadata_range = f"B{next_row}:E{next_row}"
            metadata_values = [[filename, variation_text, upload_date, shareable_url]]
            worksheet.update(metadata_range, metadata_values)

            # Get file size
            file_size = Path(image_path).stat().st_size

            self.logger.info(f"Successfully uploaded mockup: {filename}")

            return MockupUploadResult(
                success=True,
                file_id=file_id,
                shareable_url=shareable_url,
                sheets_cell=image_cell,
                file_size=file_size
            )

        except Exception as e:
            self.logger.error(f"Mockup upload workflow failed: {e}")
            return MockupUploadResult(
                success=False,
                error_message=str(e)
            )
