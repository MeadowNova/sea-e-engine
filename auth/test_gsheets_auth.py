#!/usr/bin/env python3
"""
Google Sheets API Authentication Test Script

This script tests Google Sheets API authentication using service account
credentials and performs basic authenticated actions (create, read, write).

Requirements:
- Google Cloud project with Sheets API enabled
- Service account credentials JSON file at credentials/google-sa.json
- GOOGLE_PROJECT_ID in .env file
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

try:
    import gspread
    from google.oauth2.service_account import Credentials
    from google.auth.exceptions import GoogleAuthError
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"❌ Missing required Google libraries: {e}")
    print("Please install: pip install gspread google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))
from core.logger import setup_logger

# Load environment variables
load_dotenv()

# Set up logging
logger = setup_logger("gsheets_auth_test")


class GSheetsAuthTest:
    """Test class for Google Sheets API authentication with real service account."""
    
    def __init__(self):
        """Initialize with credentials from service account file."""
        self.project_id = os.getenv("GOOGLE_PROJECT_ID")
        self.service_account_file = Path("credentials/google-sa.json")
        
        # Define required scopes for Google Sheets
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Validate required configuration
        if not self.project_id:
            raise ValueError("Missing required environment variable: GOOGLE_PROJECT_ID")
        
        if not self.service_account_file.exists():
            raise ValueError(f"Service account file not found: {self.service_account_file}")
        
        self.gc = None
        self.sheets_service = None
        self.drive_service = None
        self.test_sheet = None
        self.test_sheet_id = None
    
    def load_service_account_credentials(self):
        """Load and validate service account credentials."""
        logger.info("Loading Google service account credentials...")
        
        try:
            # Load service account file
            with open(self.service_account_file, 'r') as f:
                service_account_data = json.load(f)
            
            # Validate required fields
            required_fields = ["type", "project_id", "private_key", "client_email"]
            missing_fields = [field for field in required_fields if field not in service_account_data]
            
            if missing_fields:
                logger.error(f"❌ Service account file missing required fields: {missing_fields}")
                return False
            
            # Validate project ID matches
            if service_account_data.get("project_id") != self.project_id:
                logger.warning(f"⚠️ Project ID mismatch: env={self.project_id}, sa={service_account_data.get('project_id')}")
            
            # Create credentials
            credentials = Credentials.from_service_account_file(
                self.service_account_file,
                scopes=self.scopes
            )
            
            # Initialize gspread client
            self.gc = gspread.authorize(credentials)
            
            # Initialize Google API services
            self.sheets_service = build('sheets', 'v4', credentials=credentials)
            self.drive_service = build('drive', 'v3', credentials=credentials)
            
            logger.info("✅ Service account credentials loaded successfully")
            logger.info(f"Project ID: {service_account_data.get('project_id')}")
            logger.info(f"Service Account Email: {service_account_data.get('client_email')}")
            
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in service account file: {e}")
            return False
        except GoogleAuthError as e:
            logger.error(f"❌ Google authentication error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error loading credentials: {e}")
            return False
    
    def test_authentication(self):
        """Test authentication by accessing Google Drive."""
        logger.info("Testing Google Sheets API authentication...")
        
        try:
            if not self.gc or not self.drive_service:
                logger.error("❌ Credentials not loaded")
                return False
            
            # Test Drive API access
            results = self.drive_service.files().list(
                pageSize=1,
                fields="nextPageToken, files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            
            logger.info("✅ Google Sheets authentication successful!")
            logger.info(f"Drive API access confirmed - found {len(files)} files")
            
            return True
            
        except HttpError as e:
            logger.error(f"❌ Google API error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error during authentication test: {e}")
            return False
    
    def create_test_spreadsheet(self):
        """Create a test spreadsheet for testing."""
        logger.info("Creating test spreadsheet...")
        
        try:
            # Create a new spreadsheet
            spreadsheet_body = {
                'properties': {
                    'title': 'SEA-Engine Test Sheet'
                },
                'sheets': [{
                    'properties': {
                        'title': 'Test Data',
                        'gridProperties': {
                            'rowCount': 100,
                            'columnCount': 10
                        }
                    }
                }]
            }
            
            spreadsheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()
            
            self.test_sheet_id = spreadsheet.get('spreadsheetId')
            
            # Also get gspread worksheet object
            self.test_sheet = self.gc.open_by_key(self.test_sheet_id).sheet1
            
            logger.info("✅ Test spreadsheet created successfully!")
            logger.info(f"Spreadsheet ID: {self.test_sheet_id}")
            logger.info(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{self.test_sheet_id}")
            
            return True
            
        except HttpError as e:
            logger.error(f"❌ Error creating spreadsheet: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error during spreadsheet creation: {e}")
            return False
    
    def test_write_operations(self):
        """Test writing data to the spreadsheet."""
        logger.info("Testing write operations...")
        
        try:
            if not self.test_sheet:
                logger.error("❌ Test spreadsheet not available")
                return False
            
            # Test 1: Write single cell
            self.test_sheet.update('A1', [['SEA-Engine Test']])
            logger.info("✅ Single cell write successful")
            
            # Test 2: Write multiple cells
            test_data = [
                ['Name', 'Value', 'Status'],
                ['Test 1', '100', 'Active'],
                ['Test 2', '200', 'Inactive'],
                ['Test 3', '300', 'Pending']
            ]
            
            self.test_sheet.update('A3:C6', test_data)
            logger.info("✅ Multiple cell write successful")
            
            # Test 3: Write with batch update
            batch_data = [
                {
                    'range': 'E1',
                    'values': [['Batch Test']]
                },
                {
                    'range': 'E2:E4',
                    'values': [['Item 1'], ['Item 2'], ['Item 3']]
                }
            ]
            
            self.test_sheet.batch_update(batch_data)
            logger.info("✅ Batch write successful")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during write operations: {e}")
            return False
    
    def test_read_operations(self):
        """Test reading data from the spreadsheet."""
        logger.info("Testing read operations...")
        
        try:
            if not self.test_sheet:
                logger.error("❌ Test spreadsheet not available")
                return False
            
            # Test 1: Read single cell
            cell_value = self.test_sheet.acell('A1').value
            logger.info(f"✅ Single cell read successful: A1 = '{cell_value}'")
            
            # Test 2: Read range
            range_values = self.test_sheet.get('A3:C6')
            logger.info(f"✅ Range read successful: {len(range_values)} rows")
            
            # Test 3: Read all values
            all_values = self.test_sheet.get_all_values()
            logger.info(f"✅ All values read successful: {len(all_values)} total rows")
            
            # Test 4: Read specific column
            column_values = self.test_sheet.col_values(1)  # Column A
            logger.info(f"✅ Column read successful: {len(column_values)} values in column A")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during read operations: {e}")
            return False
    
    def test_formatting_operations(self):
        """Test formatting operations on the spreadsheet."""
        logger.info("Testing formatting operations...")
        
        try:
            if not self.test_sheet_id:
                logger.error("❌ Test spreadsheet ID not available")
                return False
            
            # Test formatting with Sheets API
            requests = [
                {
                    'repeatCell': {
                        'range': {
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 3
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': 0.8,
                                    'green': 0.8,
                                    'blue': 1.0
                                },
                                'textFormat': {
                                    'bold': True
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                }
            ]
            
            body = {'requests': requests}
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=self.test_sheet_id,
                body=body
            ).execute()
            
            logger.info("✅ Formatting operations successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during formatting operations: {e}")
            return False
    
    def cleanup_test_spreadsheet(self):
        """Clean up the test spreadsheet."""
        logger.info("Cleaning up test spreadsheet...")
        
        try:
            if self.test_sheet_id and self.drive_service:
                # Delete the test spreadsheet
                self.drive_service.files().delete(fileId=self.test_sheet_id).execute()
                logger.info("✅ Test spreadsheet deleted successfully")
                return True
            else:
                logger.warning("⚠️ No test spreadsheet to clean up")
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ Error during cleanup (non-critical): {e}")
            return True  # Non-critical error


def main():
    """Main function to run all authentication tests."""
    logger.info("=" * 60)
    logger.info("GOOGLE SHEETS API AUTHENTICATION TEST")
    logger.info("=" * 60)
    
    try:
        # Initialize test class
        gsheets_test = GSheetsAuthTest()
        
        # Run credential loading test
        creds_success = gsheets_test.load_service_account_credentials()
        
        if creds_success:
            # Run authentication test
            auth_success = gsheets_test.test_authentication()
            
            if auth_success:
                # Run spreadsheet creation test
                create_success = gsheets_test.create_test_spreadsheet()
                
                if create_success:
                    # Run write operations test
                    write_success = gsheets_test.test_write_operations()
                    
                    # Run read operations test
                    read_success = gsheets_test.test_read_operations()
                    
                    # Run formatting operations test
                    format_success = gsheets_test.test_formatting_operations()
                    
                    # Clean up
                    gsheets_test.cleanup_test_spreadsheet()
                    
                    if write_success and read_success and format_success:
                        logger.info("🎉 All Google Sheets API tests passed successfully!")
                        logger.info("✅ Service account authentication working")
                        logger.info("✅ Spreadsheet creation working")
                        logger.info("✅ Write operations working")
                        logger.info("✅ Read operations working")
                        logger.info("✅ Formatting operations working")
                        return True
                    else:
                        logger.warning("⚠️ Authentication works but some operations failed")
                        return False
                else:
                    logger.warning("⚠️ Authentication works but spreadsheet creation failed")
                    return False
            else:
                logger.error("❌ Google Sheets authentication failed")
                return False
        else:
            logger.error("❌ Failed to load service account credentials")
            return False
            
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False
    finally:
        logger.info("=" * 60)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
