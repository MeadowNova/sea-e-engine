#!/usr/bin/env python3
"""
Test Google Drive Integration for Phase 3
=========================================

Tests the Google Drive manager with actual SVG files.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modules.google_drive_manager import GoogleDriveManager
from modules.svg_resizer import SVGResizer

def test_google_drive_connection():
    """Test basic Google Drive connection."""
    print("🧪 Testing Google Drive Connection")
    print("=" * 50)
    
    try:
        # Initialize Google Drive manager
        drive_manager = GoogleDriveManager()
        print("✅ Google Drive connection successful!")
        return drive_manager
        
    except Exception as e:
        print(f"❌ Google Drive connection failed: {e}")
        return None

def test_folder_creation(drive_manager):
    """Test folder creation."""
    print("\n🧪 Testing Folder Creation")
    print("=" * 50)
    
    test_folder_name = "SEA-E Test Design"
    
    try:
        success, folder_id, error = drive_manager.create_design_folder(test_folder_name)
        
        if success:
            print(f"✅ Folder created successfully!")
            print(f"   Name: {test_folder_name}")
            print(f"   ID: {folder_id}")
            return folder_id
        else:
            print(f"❌ Folder creation failed: {error}")
            return None
            
    except Exception as e:
        print(f"❌ Folder creation error: {e}")
        return None

def test_file_upload(drive_manager, folder_id):
    """Test file upload to folder."""
    print("\n🧪 Testing File Upload")
    print("=" * 50)
    
    # First, create some test SVG files
    print("📁 Creating test SVG files...")
    
    svg_dir = Path("assets/mockups/posters/Designs for Mockups")
    svg_files = [f for f in svg_dir.glob("*.svg")]
    
    if not svg_files:
        print("❌ No SVG files found for testing")
        return False
    
    # Use SVG resizer to create sized files
    resizer = SVGResizer(output_dir="output/test_google_drive")
    test_svg = svg_files[0]
    design_name = test_svg.stem
    
    print(f"🎨 Creating sized SVGs from: {test_svg.name}")
    
    try:
        created_files = resizer.create_sized_svgs(
            svg_path=str(test_svg),
            design_name=design_name
        )
        
        # Get list of file paths (exclude original if present)
        file_paths = [path for name, path in created_files.items() if name != 'original']
        
        print(f"📄 Created {len(file_paths)} files to upload")
        
        # Upload files to Google Drive
        print(f"☁️  Uploading files to Google Drive folder...")
        
        upload_results = drive_manager.upload_files_to_folder(folder_id, file_paths)
        
        # Analyze results
        successful = [r for r in upload_results if r.success]
        failed = [r for r in upload_results if not r.success]
        
        print(f"\n📊 Upload Results:")
        print(f"   ✅ Successful: {len(successful)}")
        print(f"   ❌ Failed: {len(failed)}")
        
        for result in successful:
            print(f"   ✅ {result.file_name}")
        
        for result in failed:
            print(f"   ❌ {result.file_name}: {result.error}")
        
        return len(successful) > 0
        
    except Exception as e:
        print(f"❌ File upload test failed: {e}")
        return False

def test_shareable_link(drive_manager, folder_id):
    """Test making folder shareable."""
    print("\n🧪 Testing Shareable Link Creation")
    print("=" * 50)
    
    try:
        success, shareable_link, error = drive_manager.make_folder_shareable(folder_id)
        
        if success:
            print(f"✅ Shareable link created!")
            print(f"   Link: {shareable_link}")
            return shareable_link
        else:
            print(f"❌ Shareable link creation failed: {error}")
            return None
            
    except Exception as e:
        print(f"❌ Shareable link error: {e}")
        return None

def test_complete_workflow():
    """Test the complete design package creation workflow."""
    print("\n🧪 Testing Complete Design Package Workflow")
    print("=" * 60)
    
    # Find SVG files
    svg_dir = Path("assets/mockups/posters/Designs for Mockups")
    svg_files = [f for f in svg_dir.glob("*.svg")]
    
    if not svg_files:
        print("❌ No SVG files found for testing")
        return False
    
    test_svg = svg_files[0]
    design_name = test_svg.stem
    
    print(f"🎨 Testing with design: {design_name}")
    
    try:
        # Step 1: Create sized SVG files
        print("📐 Creating sized SVG files...")
        resizer = SVGResizer(output_dir="output/test_complete_workflow")
        created_files = resizer.create_sized_svgs(
            svg_path=str(test_svg),
            design_name=design_name
        )
        
        # Get file paths (exclude original)
        file_paths = [path for name, path in created_files.items() if name != 'original']
        print(f"   Created {len(file_paths)} sized SVG files")
        
        # Step 2: Create complete Google Drive package
        print("☁️  Creating Google Drive package...")
        drive_manager = GoogleDriveManager()
        
        result = drive_manager.create_design_package(design_name, file_paths)
        
        if result.success:
            print(f"🎉 Complete workflow SUCCESS!")
            print(f"   Folder: {result.folder_name}")
            print(f"   Files uploaded: {len([r for r in result.uploaded_files if r.success])}")
            print(f"   Shareable link: {result.shareable_link}")
            
            # Verify files in folder
            files_in_folder = drive_manager.list_files_in_folder(result.folder_id)
            print(f"\n📂 Files in Google Drive folder:")
            for file_info in files_in_folder:
                file_size = int(file_info.get('size', 0)) / 1024  # KB
                print(f"   📄 {file_info['name']} ({file_size:.1f} KB)")
            
            return True
        else:
            print(f"❌ Complete workflow failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Complete workflow error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Google Drive Integration Test Suite")
    print("=" * 70)
    
    # Test 1: Connection
    drive_manager = test_google_drive_connection()
    if not drive_manager:
        sys.exit(1)
    
    # Test 2: Folder creation
    folder_id = test_folder_creation(drive_manager)
    if not folder_id:
        sys.exit(1)
    
    # Test 3: File upload
    upload_success = test_file_upload(drive_manager, folder_id)
    if not upload_success:
        sys.exit(1)
    
    # Test 4: Shareable link
    shareable_link = test_shareable_link(drive_manager, folder_id)
    if not shareable_link:
        sys.exit(1)
    
    # Test 5: Complete workflow
    complete_success = test_complete_workflow()
    
    if complete_success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   Google Drive integration is ready for Phase 3!")
        sys.exit(0)
    else:
        print(f"\n❌ Some tests failed")
        sys.exit(1)
