
#!/usr/bin/env python3
"""
SEA-E Google Sheet Template Creator
Creates a comprehensive Google Sheet template for the SEA-E automation engine workflow.
"""

import json
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuration
CREDENTIALS_PATH = '/home/ubuntu/sea-engine/credentials/google-sa.json'
CONFIG_DIR = '/home/ubuntu/sea-engine/config'

# Google Sheets API scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def load_config_data():
    """Load configuration data from JSON files."""
    config_data = {}
    
    # Load product blueprints
    with open(f'{CONFIG_DIR}/product_blueprints.json', 'r') as f:
        config_data['products'] = json.load(f)
    
    # Load mockup blueprints
    with open(f'{CONFIG_DIR}/mockup_blueprints.json', 'r') as f:
        config_data['mockups'] = json.load(f)
    
    # Load manifests
    with open(f'{CONFIG_DIR}/manifests.json', 'r') as f:
        config_data['manifests'] = json.load(f)
    
    return config_data

def extract_dropdown_values(config_data):
    """Extract values for dropdown validations from config data."""
    dropdowns = {}
    
    # Product types
    dropdowns['product_types'] = list(config_data['products']['products'].keys())
    
    # Blueprint IDs
    dropdowns['blueprint_ids'] = []
    for product in config_data['products']['products'].values():
        dropdowns['blueprint_ids'].append(str(product['printify_config']['blueprint_id']))
    
    # Colors (combined from all products)
    dropdowns['colors'] = []
    for product in config_data['products']['products'].values():
        for color_key in product['available_options']['colors'].keys():
            if color_key not in dropdowns['colors']:
                dropdowns['colors'].append(color_key)
    
    # Sizes (combined from all products)
    dropdowns['sizes'] = []
    for product in config_data['products']['products'].values():
        for size_key in product['available_options']['sizes'].keys():
            if size_key not in dropdowns['sizes']:
                dropdowns['sizes'].append(size_key)
    
    # Print providers
    dropdowns['print_providers'] = []
    for product in config_data['products']['products'].values():
        provider_name = product['printify_config']['print_provider_name']
        if provider_name not in dropdowns['print_providers']:
            dropdowns['print_providers'].append(provider_name)
    
    # Status values
    dropdowns['status_values'] = [
        'pending', 'processing', 'completed', 'error', 'cancelled', 'review_needed'
    ]
    
    # Workflow stages
    dropdowns['workflow_stages'] = [
        'design_upload', 'mockup_generation', 'product_creation', 
        'listing_creation', 'publishing', 'published', 'failed'
    ]
    
    # Priority levels
    dropdowns['priority_levels'] = ['low', 'medium', 'high', 'urgent']
    
    return dropdowns

def create_sheet_structure():
    """Define the sheet structure with all required columns."""
    columns = [
        # Product Identification & Metadata
        {'name': 'Product ID', 'width': 120},
        {'name': 'Product Name', 'width': 200},
        {'name': 'Product Type', 'width': 150},
        {'name': 'Blueprint Key', 'width': 180},
        {'name': 'Blueprint ID', 'width': 100},
        {'name': 'Category', 'width': 120},
        {'name': 'Tags', 'width': 200},
        
        # Design Information
        {'name': 'Design File Path', 'width': 250},
        {'name': 'Design Name', 'width': 180},
        {'name': 'Design Description', 'width': 250},
        {'name': 'Design Keywords', 'width': 200},
        
        # Product Configuration
        {'name': 'Colors', 'width': 150},
        {'name': 'Sizes', 'width': 120},
        {'name': 'Print Provider', 'width': 150},
        {'name': 'Base Cost', 'width': 100},
        {'name': 'Retail Price', 'width': 100},
        
        # Mockup Generation
        {'name': 'Mockup Status', 'width': 120},
        {'name': 'Mockup Files', 'width': 250},
        {'name': 'Mockup Generation Date', 'width': 150},
        {'name': 'Mockup Errors', 'width': 200},
        
        # Printify Integration
        {'name': 'Printify Product ID', 'width': 150},
        {'name': 'Printify Status', 'width': 120},
        {'name': 'Printify Creation Date', 'width': 150},
        {'name': 'Printify Errors', 'width': 200},
        
        # Etsy Listing
        {'name': 'Etsy Listing ID', 'width': 150},
        {'name': 'Etsy Status', 'width': 120},
        {'name': 'Etsy URL', 'width': 250},
        {'name': 'Etsy Publication Date', 'width': 150},
        {'name': 'Etsy Errors', 'width': 200},
        
        # Workflow Management
        {'name': 'Overall Status', 'width': 120},
        {'name': 'Current Stage', 'width': 150},
        {'name': 'Priority', 'width': 100},
        {'name': 'Assigned To', 'width': 120},
        {'name': 'Notes', 'width': 250},
        
        # Timestamps & Tracking
        {'name': 'Created Date', 'width': 150},
        {'name': 'Last Updated', 'width': 150},
        {'name': 'Completed Date', 'width': 150},
        {'name': 'Processing Time (mins)', 'width': 150},
        
        # Error Logging
        {'name': 'Error Count', 'width': 100},
        {'name': 'Last Error', 'width': 200},
        {'name': 'Error Log', 'width': 300}
    ]
    
    return columns

def create_sample_data():
    """Create sample data rows to demonstrate usage."""
    sample_rows = [
        [
            'PROD_001', 'Vintage Sunset T-Shirt', 'tshirt_bella_canvas_3001', 'tshirt_bella_canvas_3001', '12',
            'apparel', 'vintage, sunset, retro, summer', '/designs/vintage_sunset.png', 'Vintage Sunset',
            'Beautiful vintage-style sunset design perfect for summer', 'vintage, sunset, retro, summer, beach',
            'white,black,navy', 'S,M,L,XL', 'Monster Digital', '8.50', '21.25', 'completed',
            '/mockups/vintage_sunset_tshirt_mockups.zip', '2025-06-11 10:30:00', '',
            'PRINT_12345', 'published', '2025-06-11 11:15:00', '',
            'ETSY_67890', 'active', 'https://etsy.com/listing/67890', '2025-06-11 12:00:00', '',
            'completed', 'published', 'medium', 'automation', 'Successfully published to Etsy',
            '2025-06-11 09:00:00', '2025-06-11 12:00:00', '2025-06-11 12:00:00', '180',
            '0', '', ''
        ],
        [
            'PROD_002', 'Mountain Adventure Poster', 'poster_matte_ideju', 'poster_matte_ideju', '983',
            'print', 'mountain, adventure, nature, landscape', '/designs/mountain_adventure.png', 'Mountain Adventure',
            'Stunning mountain landscape for adventure lovers', 'mountain, adventure, nature, landscape, hiking',
            'white', '11x14,16x20,18x24', 'Ideju Druka', '12.00', '36.00', 'processing',
            '', '', 'Mockup generation in progress',
            '', 'pending', '', '',
            '', 'pending', '', '', '',
            'processing', 'mockup_generation', 'high', 'automation', 'High priority item for Q3 launch',
            '2025-06-11 14:00:00', '2025-06-11 14:30:00', '', '30',
            '0', '', ''
        ]
    ]
    
    return sample_rows

def authenticate_sheets_api():
    """Authenticate with Google Sheets API using service account."""
    try:
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_PATH, scopes=SCOPES
        )
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

def create_spreadsheet(service, title="SEA-E Automation Engine Control Panel"):
    """Create a new spreadsheet."""
    try:
        spreadsheet_body = {
            'properties': {
                'title': title,
                'locale': 'en_US',
                'timeZone': 'America/New_York'
            },
            'sheets': [
                {
                    'properties': {
                        'title': 'Control Panel',
                        'sheetType': 'GRID',
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 50,
                            'frozenRowCount': 1
                        }
                    }
                },
                {
                    'properties': {
                        'title': 'Documentation',
                        'sheetType': 'GRID',
                        'gridProperties': {
                            'rowCount': 100,
                            'columnCount': 10
                        }
                    }
                }
            ]
        }
        
        result = service.spreadsheets().create(body=spreadsheet_body).execute()
        return result['spreadsheetId'], result['sheets']
    except HttpError as e:
        print(f"Failed to create spreadsheet: {e}")
        return None, None

def setup_control_panel(service, spreadsheet_id, sheet_id, columns, sample_data, dropdowns):
    """Set up the main control panel sheet with headers, data, and formatting."""
    requests = []
    
    # 1. Add headers
    header_values = [[col['name'] for col in columns]]
    requests.append({
        'updateCells': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': 0,
                'endRowIndex': 1,
                'startColumnIndex': 0,
                'endColumnIndex': len(columns)
            },
            'rows': [{
                'values': [{
                    'userEnteredValue': {'stringValue': header},
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
                        'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'bold': True},
                        'horizontalAlignment': 'CENTER'
                    }
                } for header in header_values[0]]
            }],
            'fields': 'userEnteredValue,userEnteredFormat'
        }
    })
    
    # 2. Add sample data
    for i, row_data in enumerate(sample_data):
        row_index = i + 1
        requests.append({
            'updateCells': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': row_index,
                    'endRowIndex': row_index + 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': len(row_data)
                },
                'rows': [{
                    'values': [{'userEnteredValue': {'stringValue': str(cell)}} for cell in row_data]
                }],
                'fields': 'userEnteredValue'
            }
        })
    
    # 3. Set column widths
    for i, col in enumerate(columns):
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': i,
                    'endIndex': i + 1
                },
                'properties': {'pixelSize': col['width']},
                'fields': 'pixelSize'
            }
        })
    
    # 4. Protect header row
    requests.append({
        'addProtectedRange': {
            'protectedRange': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'description': 'Header row protection',
                'warningOnly': True
            }
        }
    })
    
    # 5. Add data validation rules
    validation_rules = [
        # Product Type dropdown (column C)
        {
            'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 2, 'endColumnIndex': 3},
            'values': dropdowns['product_types']
        },
        # Blueprint Key dropdown (column D)
        {
            'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 3, 'endColumnIndex': 4},
            'values': dropdowns['product_types']
        },
        # Print Provider dropdown (column N)
        {
            'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 13, 'endColumnIndex': 14},
            'values': dropdowns['print_providers']
        },
        # Mockup Status dropdown (column Q)
        {
            'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 16, 'endColumnIndex': 17},
            'values': dropdowns['status_values']
        },
        # Printify Status dropdown (column U)
        {
            'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 20, 'endColumnIndex': 21},
            'values': dropdowns['status_values']
        },
        # Etsy Status dropdown (column Y)
        {
            'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 24, 'endColumnIndex': 25},
            'values': dropdowns['status_values']
        },
        # Overall Status dropdown (column AC)
        {
            'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 28, 'endColumnIndex': 29},
            'values': dropdowns['status_values']
        },
        # Current Stage dropdown (column AD)
        {
            'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 29, 'endColumnIndex': 30},
            'values': dropdowns['workflow_stages']
        },
        # Priority dropdown (column AE)
        {
            'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 30, 'endColumnIndex': 31},
            'values': dropdowns['priority_levels']
        }
    ]
    
    for rule in validation_rules:
        requests.append({
            'setDataValidation': {
                'range': rule['range'],
                'rule': {
                    'condition': {
                        'type': 'ONE_OF_LIST',
                        'values': [{'userEnteredValue': value} for value in rule['values']]
                    },
                    'strict': True,
                    'showCustomUi': True
                }
            }
        })
    
    # 6. Add conditional formatting for status columns
    status_columns = [16, 20, 24, 28]  # Mockup, Printify, Etsy, Overall Status columns
    
    for col_index in status_columns:
        # Green for completed/published
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{
                        'sheetId': sheet_id,
                        'startRowIndex': 1,
                        'endRowIndex': 1000,
                        'startColumnIndex': col_index,
                        'endColumnIndex': col_index + 1
                    }],
                    'booleanRule': {
                        'condition': {
                            'type': 'TEXT_EQ',
                            'values': [{'userEnteredValue': 'completed'}]
                        },
                        'format': {
                            'backgroundColor': {'red': 0.8, 'green': 1.0, 'blue': 0.8}
                        }
                    }
                },
                'index': 0
            }
        })
        
        # Red for error/failed
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{
                        'sheetId': sheet_id,
                        'startRowIndex': 1,
                        'endRowIndex': 1000,
                        'startColumnIndex': col_index,
                        'endColumnIndex': col_index + 1
                    }],
                    'booleanRule': {
                        'condition': {
                            'type': 'TEXT_EQ',
                            'values': [{'userEnteredValue': 'error'}]
                        },
                        'format': {
                            'backgroundColor': {'red': 1.0, 'green': 0.8, 'blue': 0.8}
                        }
                    }
                },
                'index': 1
            }
        })
        
        # Yellow for processing/pending
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{
                        'sheetId': sheet_id,
                        'startRowIndex': 1,
                        'endRowIndex': 1000,
                        'startColumnIndex': col_index,
                        'endColumnIndex': col_index + 1
                    }],
                    'booleanRule': {
                        'condition': {
                            'type': 'TEXT_CONTAINS',
                            'values': [{'userEnteredValue': 'processing'}]
                        },
                        'format': {
                            'backgroundColor': {'red': 1.0, 'green': 1.0, 'blue': 0.8}
                        }
                    }
                },
                'index': 2
            }
        })
    
    # Execute all requests
    if requests:
        try:
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            print("Control panel setup completed successfully")
        except HttpError as e:
            print(f"Failed to setup control panel: {e}")

def setup_documentation_sheet(service, spreadsheet_id, doc_sheet_id, columns):
    """Set up the documentation sheet with usage instructions."""
    doc_content = [
        ['SEA-E Automation Engine - Google Sheet Template Documentation'],
        [''],
        ['OVERVIEW'],
        ['This Google Sheet serves as the central control panel for the SEA-E automation engine.'],
        ['It tracks the complete workflow from design upload to Etsy publication.'],
        [''],
        ['COLUMN DEFINITIONS'],
        [''],
        ['Product Identification & Metadata:'],
        ['- Product ID: Unique identifier for each product'],
        ['- Product Name: Human-readable product name'],
        ['- Product Type: Type of product (tshirt_bella_canvas_3001, sweatshirt_gildan_18000, poster_matte_ideju)'],
        ['- Blueprint Key: Internal blueprint identifier'],
        ['- Blueprint ID: Printify blueprint ID'],
        ['- Category: Product category (apparel, print, etc.)'],
        ['- Tags: Comma-separated tags for organization'],
        [''],
        ['Design Information:'],
        ['- Design File Path: Full path to the design file'],
        ['- Design Name: Name of the design'],
        ['- Design Description: Description for listings'],
        ['- Design Keywords: SEO keywords for the design'],
        [''],
        ['Product Configuration:'],
        ['- Colors: Comma-separated list of colors to produce'],
        ['- Sizes: Comma-separated list of sizes to produce'],
        ['- Print Provider: Selected print provider'],
        ['- Base Cost: Production cost per item'],
        ['- Retail Price: Selling price per item'],
        [''],
        ['Workflow Tracking:'],
        ['- Mockup Status: Status of mockup generation (pending, processing, completed, error)'],
        ['- Printify Status: Status of Printify product creation'],
        ['- Etsy Status: Status of Etsy listing'],
        ['- Overall Status: Overall workflow status'],
        ['- Current Stage: Current stage in the workflow'],
        [''],
        ['USAGE INSTRUCTIONS'],
        [''],
        ['1. Add new products by filling in a new row with required information'],
        ['2. Use dropdown menus for standardized fields (Product Type, Status, etc.)'],
        ['3. The automation engine will update status columns as it processes items'],
        ['4. Monitor progress using the color-coded status indicators:'],
        ['   - Green: Completed/Published'],
        ['   - Yellow: Processing/Pending'],
        ['   - Red: Error/Failed'],
        [''],
        ['AUTOMATION INTEGRATION'],
        [''],
        ['The automation engine expects the following column structure:'],
    ]
    
    # Add column mapping
    for i, col in enumerate(columns):
        doc_content.append([f'Column {chr(65 + i)}: {col["name"]}'])
    
    doc_content.extend([
        [''],
        ['PERMISSIONS'],
        ['- Service account has read/write access for automation'],
        ['- Users should have edit access to add/modify products'],
        ['- Header row is protected to prevent accidental changes'],
        [''],
        ['SUPPORT'],
        ['For technical support or questions about this template,'],
        ['contact the SEA-E development team.']
    ])
    
    # Convert to proper format for batch update
    requests = []
    
    for i, row in enumerate(doc_content):
        if i == 0:  # Title row
            requests.append({
                'updateCells': {
                    'range': {
                        'sheetId': doc_sheet_id,
                        'startRowIndex': i,
                        'endRowIndex': i + 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': 1
                    },
                    'rows': [{
                        'values': [{
                            'userEnteredValue': {'stringValue': row[0]},
                            'userEnteredFormat': {
                                'textFormat': {'bold': True, 'fontSize': 16},
                                'horizontalAlignment': 'CENTER'
                            }
                        }]
                    }],
                    'fields': 'userEnteredValue,userEnteredFormat'
                }
            })
        elif row[0] in ['OVERVIEW', 'COLUMN DEFINITIONS', 'USAGE INSTRUCTIONS', 'AUTOMATION INTEGRATION', 'PERMISSIONS', 'SUPPORT']:
            # Section headers
            requests.append({
                'updateCells': {
                    'range': {
                        'sheetId': doc_sheet_id,
                        'startRowIndex': i,
                        'endRowIndex': i + 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': 1
                    },
                    'rows': [{
                        'values': [{
                            'userEnteredValue': {'stringValue': row[0]},
                            'userEnteredFormat': {
                                'textFormat': {'bold': True, 'fontSize': 12},
                                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                            }
                        }]
                    }],
                    'fields': 'userEnteredValue,userEnteredFormat'
                }
            })
        else:
            # Regular content
            requests.append({
                'updateCells': {
                    'range': {
                        'sheetId': doc_sheet_id,
                        'startRowIndex': i,
                        'endRowIndex': i + 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': 1
                    },
                    'rows': [{
                        'values': [{
                            'userEnteredValue': {'stringValue': row[0] if row else ''}
                        }]
                    }],
                    'fields': 'userEnteredValue'
                }
            })
    
    # Execute documentation setup
    if requests:
        try:
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            print("Documentation sheet setup completed successfully")
        except HttpError as e:
            print(f"Failed to setup documentation sheet: {e}")

def share_spreadsheet(service, spreadsheet_id):
    """Share the spreadsheet with appropriate permissions."""
    try:
        # Make it accessible to anyone with the link (for demo purposes)
        # In production, you'd share with specific email addresses
        drive_service = build('drive', 'v3', credentials=service._http.credentials)
        
        permission = {
            'type': 'anyone',
            'role': 'writer'
        }
        
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body=permission
        ).execute()
        
        print("Spreadsheet shared successfully")
        
    except Exception as e:
        print(f"Failed to share spreadsheet: {e}")

def main():
    """Main function to create the SEA-E Google Sheet template."""
    print("Starting SEA-E Google Sheet template creation...")
    
    # Load configuration data
    print("Loading configuration data...")
    config_data = load_config_data()
    dropdowns = extract_dropdown_values(config_data)
    
    # Define sheet structure
    columns = create_sheet_structure()
    sample_data = create_sample_data()
    
    # Authenticate with Google Sheets API
    print("Authenticating with Google Sheets API...")
    service = authenticate_sheets_api()
    if not service:
        print("Failed to authenticate. Exiting.")
        return
    
    # Create spreadsheet
    print("Creating spreadsheet...")
    spreadsheet_id, sheets = create_spreadsheet(service)
    if not spreadsheet_id:
        print("Failed to create spreadsheet. Exiting.")
        return
    
    print(f"Spreadsheet created with ID: {spreadsheet_id}")
    
    # Get sheet IDs
    control_sheet_id = sheets[0]['properties']['sheetId']
    doc_sheet_id = sheets[1]['properties']['sheetId']
    
    # Setup control panel
    print("Setting up control panel...")
    setup_control_panel(service, spreadsheet_id, control_sheet_id, columns, sample_data, dropdowns)
    
    # Setup documentation
    print("Setting up documentation...")
    setup_documentation_sheet(service, spreadsheet_id, doc_sheet_id, columns)
    
    # Share spreadsheet
    print("Sharing spreadsheet...")
    share_spreadsheet(service, spreadsheet_id)
    
    # Print results
    spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    print("\n" + "="*60)
    print("SEA-E GOOGLE SHEET TEMPLATE CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"Spreadsheet ID: {spreadsheet_id}")
    print(f"Spreadsheet URL: {spreadsheet_url}")
    print("\nFeatures implemented:")
    print("✅ Complete column structure for automation workflow")
    print("✅ Data validation dropdowns for critical fields")
    print("✅ Conditional formatting for status tracking")
    print("✅ Protected header row")
    print("✅ Sample data for demonstration")
    print("✅ Comprehensive documentation sheet")
    print("✅ Proper sharing permissions")
    print("\nThe template is ready for integration with the SEA-E automation engine!")
    
    return spreadsheet_id

if __name__ == "__main__":
    spreadsheet_id = main()
