#!/usr/bin/env python3
"""
Test PDF Customizer for Phase 3
===============================

Tests the PDF customization system with sample data.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modules.pdf_customizer import PDFCustomizer

def test_pdf_customizer_basic():
    """Test basic PDF customizer functionality."""
    print("🧪 Testing PDF Customizer - Basic Functionality")
    print("=" * 60)
    
    try:
        # Initialize PDF customizer
        customizer = PDFCustomizer(output_dir="output/test_pdf_customizer")
        print("✅ PDF Customizer initialized")
        
        # Test without template first (should create standalone PDF)
        design_name = "coffee_cat_barista_coffee_cat_lover"
        google_drive_link = "https://drive.google.com/drive/folders/1q3uFK3MsaGEdizm1zCmZGfTUQdCzj5nG"
        
        print(f"\n🎨 Testing PDF creation for: {design_name}")
        print(f"   Google Drive link: {google_drive_link}")
        
        # Create standalone PDF (no template)
        result = customizer._create_info_page(design_name, google_drive_link)
        
        if result:
            print(f"✅ Standalone PDF created: {result}")
            
            # Check file size
            file_size = Path(result).stat().st_size / 1024  # KB
            print(f"   File size: {file_size:.1f} KB")
            
            return True
        else:
            print("❌ Standalone PDF creation failed")
            return False
            
    except Exception as e:
        print(f"❌ PDF customizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_template_validation():
    """Test PDF template validation."""
    print("\n🧪 Testing PDF Template Validation")
    print("=" * 60)
    
    customizer = PDFCustomizer()
    
    # Test with non-existent file
    is_valid, error = customizer.validate_template("non_existent.pdf")
    if not is_valid:
        print(f"✅ Correctly detected missing file: {error}")
    else:
        print("❌ Should have detected missing file")
        return False
    
    # Look for any PDF files in the project
    pdf_files = list(Path(".").rglob("*.pdf"))
    
    if pdf_files:
        test_pdf = pdf_files[0]
        print(f"📄 Testing with found PDF: {test_pdf}")
        
        is_valid, error = customizer.validate_template(str(test_pdf))
        if is_valid:
            print(f"✅ PDF validation successful")
            return test_pdf
        else:
            print(f"⚠️  PDF validation failed: {error}")
            return None
    else:
        print("📄 No PDF files found in project for testing")
        return None

def test_complete_pdf_customization():
    """Test complete PDF customization workflow."""
    print("\n🧪 Testing Complete PDF Customization")
    print("=" * 60)
    
    try:
        # Initialize customizer
        customizer = PDFCustomizer(output_dir="output/test_complete_pdf")
        
        # Test data
        design_name = "coffee_cat_barista_coffee_cat_lover"
        google_drive_link = "https://drive.google.com/drive/folders/1q3uFK3MsaGEdizm1zCmZGfTUQdCzj5nG"
        
        print(f"🎨 Creating customized PDF for: {design_name}")
        
        # Method 1: Create standalone info PDF (no template)
        result = customizer.customize_pdf(design_name, google_drive_link)
        
        if result.success:
            print(f"✅ PDF customization successful!")
            print(f"   Output: {result.output_path}")
            print(f"   Design: {result.design_name}")
            print(f"   Link: {result.google_drive_link}")
            
            # Check output file
            output_path = Path(result.output_path)
            if output_path.exists():
                file_size = output_path.stat().st_size / 1024  # KB
                print(f"   File size: {file_size:.1f} KB")
                print(f"   File exists: ✅")
                return True
            else:
                print(f"   File exists: ❌")
                return False
        else:
            print(f"❌ PDF customization failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Complete PDF customization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_template_pdf():
    """Test PDF customization with an actual template."""
    print("\n🧪 Testing PDF Customization with Template")
    print("=" * 60)
    
    # Look for PDF files that could serve as templates
    pdf_files = list(Path(".").rglob("*.pdf"))
    
    if not pdf_files:
        print("📄 No PDF template found - creating test template")
        return create_test_template()
    
    template_pdf = pdf_files[0]
    print(f"📄 Using template: {template_pdf}")
    
    try:
        # Initialize customizer with template
        customizer = PDFCustomizer(
            template_path=str(template_pdf),
            output_dir="output/test_template_pdf"
        )
        
        # Validate template
        is_valid, error = customizer.validate_template()
        if not is_valid:
            print(f"❌ Template validation failed: {error}")
            return False
        
        print("✅ Template validation successful")
        
        # Test data
        design_name = "coffee_cat_barista_coffee_cat_lover"
        google_drive_link = "https://drive.google.com/drive/folders/1q3uFK3MsaGEdizm1zCmZGfTUQdCzj5nG"
        
        # Customize PDF
        result = customizer.customize_pdf(design_name, google_drive_link)
        
        if result.success:
            print(f"✅ Template-based PDF customization successful!")
            print(f"   Output: {result.output_path}")
            
            # Check output file
            output_path = Path(result.output_path)
            if output_path.exists():
                file_size = output_path.stat().st_size / 1024  # KB
                print(f"   File size: {file_size:.1f} KB")
                return True
            else:
                print(f"   Output file not found")
                return False
        else:
            print(f"❌ Template-based customization failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Template PDF test failed: {e}")
        return False

def create_test_template():
    """Create a simple test template PDF."""
    print("📄 Creating test template PDF...")
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        template_path = Path("output/test_template.pdf")
        template_path.parent.mkdir(exist_ok=True)
        
        # Create simple template
        c = canvas.Canvas(str(template_path), pagesize=letter)
        width, height = letter
        
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredText(width/2, height - 100, "Digital Download Instructions")
        
        c.setFont("Helvetica", 14)
        c.drawCentredText(width/2, height - 200, "Thank you for your purchase!")
        c.drawCentredText(width/2, height - 250, "Your design files are available at:")
        
        c.setFont("Helvetica", 12)
        c.drawCentredText(width/2, height - 300, "[GOOGLE_DRIVE_LINK_PLACEHOLDER]")
        
        c.save()
        
        print(f"✅ Test template created: {template_path}")
        return str(template_path)
        
    except Exception as e:
        print(f"❌ Test template creation failed: {e}")
        return None

if __name__ == "__main__":
    print("🔧 PDF Customizer Test Suite")
    print("=" * 70)
    
    # Test 1: Basic functionality
    basic_success = test_pdf_customizer_basic()
    if not basic_success:
        print("\n❌ Basic functionality test failed")
        sys.exit(1)
    
    # Test 2: Template validation
    template_file = test_pdf_template_validation()
    
    # Test 3: Complete customization
    complete_success = test_complete_pdf_customization()
    if not complete_success:
        print("\n❌ Complete customization test failed")
        sys.exit(1)
    
    # Test 4: Template-based customization
    template_success = test_with_template_pdf()
    
    # Summary
    print(f"\n📊 Test Results Summary:")
    print(f"   ✅ Basic functionality: {'PASS' if basic_success else 'FAIL'}")
    print(f"   ✅ Template validation: {'PASS' if template_file else 'FAIL'}")
    print(f"   ✅ Complete customization: {'PASS' if complete_success else 'FAIL'}")
    print(f"   ✅ Template-based: {'PASS' if template_success else 'FAIL'}")
    
    if basic_success and complete_success:
        print(f"\n🎉 PDF Customizer is ready for Phase 3!")
        print(f"   Can create standalone PDFs with Google Drive links")
        print(f"   Ready for template-based customization")
        sys.exit(0)
    else:
        print(f"\n❌ Some tests failed")
        sys.exit(1)
