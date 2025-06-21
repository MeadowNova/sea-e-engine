"""
Google OAuth 2.0 authentication module for SEA-E Engine.

This module handles OAuth authentication for Google APIs, allowing the user
to access Google Drive folders and files created by the application.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional, Tuple

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


class GoogleOAuthManager:
    """Manages Google OAuth 2.0 authentication for SEA-E Engine."""
    
    # Required scopes for Google APIs
    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    
    def __init__(self, 
                 client_secrets_file: str = "credentials/google_oauth_client.json",
                 token_file: str = "credentials/google_oauth_token.json"):
        """Initialize OAuth manager.
        
        Args:
            client_secrets_file: Path to OAuth client secrets JSON file
            token_file: Path to store/load OAuth tokens
        """
        self.client_secrets_file = Path(client_secrets_file)
        self.token_file = Path(token_file)
        self.credentials = None
        
        # Validate client secrets file exists
        if not self.client_secrets_file.exists():
            raise FileNotFoundError(f"OAuth client secrets file not found: {self.client_secrets_file}")
        
        logger.info("Google OAuth Manager initialized")
    
    def authenticate(self) -> bool:
        """Authenticate with Google OAuth 2.0.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Try to load existing credentials
            if self.token_file.exists():
                logger.info("Loading existing OAuth credentials...")
                self.credentials = Credentials.from_authorized_user_file(
                    str(self.token_file), self.SCOPES
                )
            
            # If credentials are invalid or don't exist, run OAuth flow
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    logger.info("Refreshing expired OAuth credentials...")
                    self.credentials.refresh(Request())
                else:
                    logger.info("Starting OAuth 2.0 flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.client_secrets_file), self.SCOPES
                    )
                    # Try local server first, fall back to console flow if redirect URI mismatch
                    try:
                        self.credentials = flow.run_local_server(port=8080)
                    except Exception as e:
                        if "redirect_uri_mismatch" in str(e).lower():
                            logger.warning("Redirect URI mismatch. Falling back to console flow...")
                            logger.info("Please visit the URL that will be displayed and enter the authorization code.")
                            self.credentials = flow.run_console()
                        else:
                            raise e
                
                # Save credentials for future use
                self._save_credentials()
            
            logger.info("✅ Google OAuth authentication successful!")
            return True
            
        except Exception as e:
            logger.error(f"❌ OAuth authentication failed: {e}")
            return False
    
    def _save_credentials(self):
        """Save OAuth credentials to file."""
        try:
            # Ensure credentials directory exists
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save credentials
            with open(self.token_file, 'w') as token:
                token.write(self.credentials.to_json())
            
            logger.info(f"OAuth credentials saved to: {self.token_file}")
            
        except Exception as e:
            logger.error(f"Failed to save OAuth credentials: {e}")
    
    def get_drive_service(self):
        """Get authenticated Google Drive service.
        
        Returns:
            Google Drive API service object
        """
        if not self.credentials:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        return build('drive', 'v3', credentials=self.credentials)
    
    def get_sheets_service(self):
        """Get authenticated Google Sheets service.
        
        Returns:
            Google Sheets API service object
        """
        if not self.credentials:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        return build('sheets', 'v4', credentials=self.credentials)
    
    def get_gspread_client(self):
        """Get authenticated gspread client.
        
        Returns:
            gspread.Client object
        """
        if not self.credentials:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        return gspread.authorize(self.credentials)
    
    def test_authentication(self) -> Tuple[bool, str]:
        """Test authentication by accessing Google APIs.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.credentials:
                return False, "Not authenticated"
            
            # Test Drive API
            drive_service = self.get_drive_service()
            about = drive_service.about().get(fields='user').execute()
            user_email = about.get('user', {}).get('emailAddress', 'Unknown')
            
            # Test Sheets API
            sheets_service = self.get_sheets_service()
            # Just test that we can build the service
            
            message = f"✅ Authenticated as: {user_email}"
            logger.info(message)
            return True, message
            
        except Exception as e:
            error_msg = f"❌ Authentication test failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def revoke_credentials(self):
        """Revoke OAuth credentials and delete token file."""
        try:
            if self.credentials:
                # Revoke the credentials
                self.credentials.revoke(Request())
                logger.info("OAuth credentials revoked")
            
            # Delete token file
            if self.token_file.exists():
                self.token_file.unlink()
                logger.info(f"Token file deleted: {self.token_file}")
            
            self.credentials = None
            
        except Exception as e:
            logger.error(f"Error revoking credentials: {e}")


def get_authenticated_services(client_secrets_file: str = "credentials/google_oauth_client.json") -> Tuple[Optional[object], Optional[object], Optional[object]]:
    """Convenience function to get authenticated Google services.
    
    Args:
        client_secrets_file: Path to OAuth client secrets file
        
    Returns:
        Tuple of (drive_service, sheets_service, gspread_client)
    """
    try:
        oauth_manager = GoogleOAuthManager(client_secrets_file)
        
        if oauth_manager.authenticate():
            drive_service = oauth_manager.get_drive_service()
            sheets_service = oauth_manager.get_sheets_service()
            gspread_client = oauth_manager.get_gspread_client()
            
            return drive_service, sheets_service, gspread_client
        else:
            return None, None, None
            
    except Exception as e:
        logger.error(f"Failed to get authenticated services: {e}")
        return None, None, None


if __name__ == "__main__":
    # Test OAuth authentication
    logging.basicConfig(level=logging.INFO)
    
    oauth_manager = GoogleOAuthManager()
    
    if oauth_manager.authenticate():
        success, message = oauth_manager.test_authentication()
        print(message)
    else:
        print("❌ Authentication failed")
