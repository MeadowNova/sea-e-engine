#!/usr/bin/env python3
"""
Google Drive Manager for Phase 3 Premium Digital Products
========================================================

Manages Google Drive operations for premium digital product delivery:
- Creates folders for each design
- Uploads 5 sized SVG files per design
- Generates shareable links for customer access
- Organizes files professionally

Features:
- OAuth 2.0 authentication (user can access created folders)
- Batch file uploads
- Shareable link generation
- Error handling and retry logic
- Professional folder organization
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Google API imports
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# OAuth authentication
from src.auth.google_oauth import GoogleOAuthManager

logger = logging.getLogger(__name__)

@dataclass
class UploadResult:
    """Result of a file upload operation."""
    success: bool
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    error: Optional[str] = None

@dataclass
class FolderResult:
    """Result of folder creation and file upload."""
    success: bool
    folder_id: Optional[str] = None
    folder_name: Optional[str] = None
    shareable_link: Optional[str] = None
    uploaded_files: List[UploadResult] = None
    error: Optional[str] = None

class GoogleDriveManager:
    """Manages Google Drive operations for digital product delivery."""

    def __init__(self, oauth_client_secrets: str = "credentials/google_oauth_client.json"):
        """Initialize Google Drive manager with OAuth authentication.

        Args:
            oauth_client_secrets: Path to OAuth client secrets JSON file
        """
        self.oauth_client_secrets = oauth_client_secrets
        self.service = None
        self.parent_folder_id = None  # Will be set for digital products folder
        self.oauth_manager = None

        # Initialize Google Drive service with OAuth
        self._initialize_service()

        logger.info("Google Drive Manager initialized with OAuth authentication")
    
    def _initialize_service(self):
        """Initialize Google Drive API service with OAuth authentication."""
        try:
            # Initialize OAuth manager
            self.oauth_manager = GoogleOAuthManager(self.oauth_client_secrets)

            # Authenticate with OAuth
            if not self.oauth_manager.authenticate():
                raise Exception("OAuth authentication failed")

            # Get authenticated Drive service
            self.service = self.oauth_manager.get_drive_service()

            # Test the connection and get user info
            success, message = self.oauth_manager.test_authentication()
            if success:
                logger.info(f"Google Drive OAuth authentication successful: {message}")
            else:
                raise Exception(f"Authentication test failed: {message}")

        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {e}")
            raise
    
    def set_parent_folder(self, folder_id: str):
        """Set the parent folder for all design folders.
        
        Args:
            folder_id: Google Drive folder ID where design folders will be created
        """
        self.parent_folder_id = folder_id
        logger.info(f"Parent folder set: {folder_id}")
    
    def create_design_folder(self, design_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Create a folder for a specific design.
        
        Args:
            design_name: Name of the design (used as folder name)
            
        Returns:
            Tuple of (success, folder_id, error_message)
        """
        try:
            # Clean design name for folder
            clean_name = self._clean_folder_name(design_name)
            
            # Folder metadata
            folder_metadata = {
                'name': clean_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            # Set parent folder if specified
            if self.parent_folder_id:
                folder_metadata['parents'] = [self.parent_folder_id]
            
            # Create folder
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            folder_id = folder.get('id')
            folder_name = folder.get('name')
            
            logger.info(f"✅ Created folder: {folder_name} (ID: {folder_id})")
            return True, folder_id, None
            
        except HttpError as e:
            error_msg = f"HTTP error creating folder: {e}"
            logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Error creating folder: {e}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def upload_files_to_folder(self, folder_id: str, file_paths: List[str]) -> List[UploadResult]:
        """Upload multiple files to a Google Drive folder.
        
        Args:
            folder_id: Target folder ID
            file_paths: List of file paths to upload
            
        Returns:
            List of UploadResult objects
        """
        results = []
        
        for file_path in file_paths:
            result = self._upload_single_file(folder_id, file_path)
            results.append(result)
            
            # Small delay between uploads to avoid rate limits
            time.sleep(0.5)
        
        return results
    
    def _upload_single_file(self, folder_id: str, file_path: str) -> UploadResult:
        """Upload a single file to Google Drive folder.
        
        Args:
            folder_id: Target folder ID
            file_path: Path to file to upload
            
        Returns:
            UploadResult object
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return UploadResult(
                success=False,
                file_name=file_path.name,
                error=f"File not found: {file_path}"
            )
        
        try:
            # File metadata
            file_metadata = {
                'name': file_path.name,
                'parents': [folder_id]
            }
            
            # Create media upload
            media = MediaFileUpload(
                str(file_path),
                mimetype='image/svg+xml' if file_path.suffix.lower() == '.svg' else None,
                resumable=True
            )
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, size'
            ).execute()
            
            file_id = file.get('id')
            file_name = file.get('name')
            file_size = int(file.get('size', 0)) / 1024  # KB
            
            logger.info(f"✅ Uploaded: {file_name} ({file_size:.1f} KB)")
            
            return UploadResult(
                success=True,
                file_id=file_id,
                file_name=file_name
            )
            
        except HttpError as e:
            error_msg = f"HTTP error uploading {file_path.name}: {e}"
            logger.error(error_msg)
            return UploadResult(
                success=False,
                file_name=file_path.name,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Error uploading {file_path.name}: {e}"
            logger.error(error_msg)
            return UploadResult(
                success=False,
                file_name=file_path.name,
                error=error_msg
            )
    
    def make_folder_shareable(self, folder_id: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Make a folder shareable with a public link.
        
        Args:
            folder_id: Google Drive folder ID
            
        Returns:
            Tuple of (success, shareable_link, error_message)
        """
        try:
            # Create permission for anyone with link
            permission = {
                'role': 'reader',
                'type': 'anyone'
            }
            
            self.service.permissions().create(
                fileId=folder_id,
                body=permission
            ).execute()
            
            # Get the shareable link
            file = self.service.files().get(
                fileId=folder_id,
                fields='webViewLink'
            ).execute()
            
            shareable_link = file.get('webViewLink')
            logger.info(f"✅ Folder made shareable: {shareable_link}")
            
            return True, shareable_link, None
            
        except HttpError as e:
            error_msg = f"HTTP error making folder shareable: {e}"
            logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Error making folder shareable: {e}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def create_design_package(self, design_name: str, jpeg_files: List[str] = None,
                             png_files: List[str] = None, svg_files: List[str] = None) -> FolderResult:
        """Create complete design package: folder + files + shareable link.

        Args:
            design_name: Name of the design
            jpeg_files: List of JPEG file paths to upload (Phase 3)
            png_files: List of PNG file paths to upload (legacy)
            svg_files: List of SVG file paths to upload (legacy)
            
        Returns:
            FolderResult with complete operation results
        """
        # Determine which files to upload (priority: JPEG > PNG > SVG)
        if jpeg_files:
            files_to_upload = jpeg_files
            file_type = "JPEG"
        elif png_files:
            files_to_upload = png_files
            file_type = "PNG"
        else:
            files_to_upload = svg_files
            file_type = "SVG"

        logger.info(f"🚀 Creating design package: {design_name}")
        logger.info(f"   {file_type} files to upload: {len(files_to_upload)}")

        # Step 1: Create folder
        success, folder_id, error = self.create_design_folder(design_name)
        if not success:
            return FolderResult(
                success=False,
                error=f"Failed to create folder: {error}"
            )

        # Step 2: Upload files
        upload_results = self.upload_files_to_folder(folder_id, files_to_upload)
        successful_uploads = [r for r in upload_results if r.success]
        failed_uploads = [r for r in upload_results if not r.success]
        
        if failed_uploads:
            logger.warning(f"⚠️  {len(failed_uploads)} files failed to upload")
            for failed in failed_uploads:
                logger.warning(f"   Failed: {failed.file_name} - {failed.error}")
        
        # Step 3: Make folder shareable
        success, shareable_link, error = self.make_folder_shareable(folder_id)
        if not success:
            return FolderResult(
                success=False,
                folder_id=folder_id,
                uploaded_files=upload_results,
                error=f"Failed to make folder shareable: {error}"
            )
        
        # Success!
        logger.info(f"🎉 Design package created successfully!")
        logger.info(f"   Folder ID: {folder_id}")
        logger.info(f"   Uploaded {file_type} files: {len(successful_uploads)}/{len(files_to_upload)}")
        logger.info(f"   Shareable link: {shareable_link}")
        
        return FolderResult(
            success=True,
            folder_id=folder_id,
            folder_name=self._clean_folder_name(design_name),
            shareable_link=shareable_link,
            uploaded_files=upload_results
        )
    
    def _clean_folder_name(self, design_name: str) -> str:
        """Clean design name for use as folder name.
        
        Args:
            design_name: Original design name
            
        Returns:
            Cleaned folder name
        """
        # Replace underscores with spaces and title case
        clean_name = design_name.replace('_', ' ').title()
        
        # Remove any invalid characters for folder names
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            clean_name = clean_name.replace(char, '')
        
        return clean_name.strip()
    
    def list_files_in_folder(self, folder_id: str) -> List[Dict]:
        """List all files in a Google Drive folder.
        
        Args:
            folder_id: Google Drive folder ID
            
        Returns:
            List of file information dictionaries
        """
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents",
                fields="files(id, name, size, mimeType, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            return files
            
        except Exception as e:
            logger.error(f"Error listing files in folder: {e}")
            return []
