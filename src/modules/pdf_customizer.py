#!/usr/bin/env python3
"""
PDF Customizer for Phase 3 Premium Digital Products
==================================================

Customizes PDF templates with specific Google Drive folder links for each design.
Creates personalized download instructions for customers.

Features:
- PDF template modification
- Google Drive link embedding
- Professional branding maintenance
- Batch processing support
- Error handling and validation
"""

import os
import logging
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# PDF manipulation imports
try:
    import PyPDF2
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.colors import black, blue
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_LIBS_AVAILABLE = True
except ImportError:
    PDF_LIBS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class PDFCustomizationResult:
    """Result of PDF customization operation."""
    success: bool
    output_path: Optional[str] = None
    design_name: Optional[str] = None
    google_drive_link: Optional[str] = None
    error: Optional[str] = None

class PDFCustomizer:
    """Customizes PDF templates with Google Drive links."""
    
    def __init__(self, template_path: str = None, output_dir: str = "output/customized_pdfs"):
        """Initialize PDF customizer.
        
        Args:
            template_path: Path to PDF template file
            output_dir: Directory to save customized PDFs
        """
        if not PDF_LIBS_AVAILABLE:
            raise ImportError(
                "PDF libraries not available. Install with: pip install PyPDF2 reportlab"
            )
        
        self.template_path = Path(template_path) if template_path else None
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("PDF Customizer initialized")
        if self.template_path:
            logger.info(f"Template: {self.template_path}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def set_template(self, template_path: str):
        """Set the PDF template file.
        
        Args:
            template_path: Path to PDF template file
        """
        self.template_path = Path(template_path)
        
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template file not found: {self.template_path}")
        
        logger.info(f"Template set: {self.template_path}")
    
    def customize_pdf(self, design_name: str, google_drive_link: str, 
                     output_filename: str = None) -> PDFCustomizationResult:
        """Customize PDF template with specific Google Drive link.
        
        Args:
            design_name: Name of the design
            google_drive_link: Google Drive folder link for this design
            output_filename: Custom output filename (optional)
            
        Returns:
            PDFCustomizationResult with operation details
        """
        if not self.template_path:
            return PDFCustomizationResult(
                success=False,
                error="No template file set. Use set_template() first."
            )
        
        if not self.template_path.exists():
            return PDFCustomizationResult(
                success=False,
                error=f"Template file not found: {self.template_path}"
            )
        
        logger.info(f"🎨 Customizing PDF for: {design_name}")
        logger.info(f"   Google Drive link: {google_drive_link}")
        
        try:
            # Generate output filename
            if not output_filename:
                clean_name = self._clean_filename(design_name)
                output_filename = f"{clean_name}_download_instructions.pdf"
            
            output_path = self.output_dir / output_filename
            
            # Method 1: Try simple overlay approach first
            success = self._create_overlay_pdf(design_name, google_drive_link, output_path)
            
            if success:
                logger.info(f"✅ PDF customized successfully: {output_filename}")
                return PDFCustomizationResult(
                    success=True,
                    output_path=str(output_path),
                    design_name=design_name,
                    google_drive_link=google_drive_link
                )
            else:
                # Method 2: Fallback to template copying with text overlay
                success = self._create_template_copy_with_overlay(
                    design_name, google_drive_link, output_path
                )
                
                if success:
                    logger.info(f"✅ PDF customized with fallback method: {output_filename}")
                    return PDFCustomizationResult(
                        success=True,
                        output_path=str(output_path),
                        design_name=design_name,
                        google_drive_link=google_drive_link
                    )
                else:
                    return PDFCustomizationResult(
                        success=False,
                        design_name=design_name,
                        error="Both PDF customization methods failed"
                    )
                    
        except Exception as e:
            error_msg = f"Error customizing PDF: {e}"
            logger.error(error_msg)
            return PDFCustomizationResult(
                success=False,
                design_name=design_name,
                error=error_msg
            )
    
    def _create_overlay_pdf(self, design_name: str, google_drive_link: str,
                           output_path: Path) -> bool:
        """Create PDF by modifying existing links in template.

        Args:
            design_name: Name of the design
            google_drive_link: Google Drive folder link
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            # Read the template PDF
            with open(self.template_path, 'rb') as template_file:
                template_reader = PyPDF2.PdfReader(template_file)

                # Create a new PDF writer
                pdf_writer = PyPDF2.PdfWriter()

                # Process each page
                for page_num, page in enumerate(template_reader.pages):
                    # Modify existing annotations (links) on this page
                    if '/Annots' in page:
                        annotations = page['/Annots']
                        for annot_ref in annotations:
                            annot = annot_ref.get_object()
                            # Check if this is a link annotation
                            if annot.get('/Subtype') == '/Link':
                                # Check if it has an action with a URI (web link)
                                if '/A' in annot and '/URI' in annot['/A']:
                                    old_uri = annot['/A']['/URI']
                                    logger.info(f"Found existing link: {old_uri}")
                                    # Replace with our Google Drive link
                                    annot['/A'][PyPDF2.generic.NameObject('/URI')] = PyPDF2.generic.TextStringObject(google_drive_link)
                                    logger.info(f"Replaced with: {google_drive_link}")

                    # No overlay needed - just replace the existing link

                    # Add page to output
                    pdf_writer.add_page(page)

                # Write the customized PDF
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)

                return True

        except Exception as e:
            logger.error(f"Overlay PDF creation failed: {e}")
            return False
    
    def _create_template_copy_with_overlay(self, design_name: str, google_drive_link: str, 
                                         output_path: Path) -> bool:
        """Fallback method: Copy template and add overlay page.
        
        Args:
            design_name: Name of the design
            google_drive_link: Google Drive folder link
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            # Read the template PDF
            with open(self.template_path, 'rb') as template_file:
                template_reader = PyPDF2.PdfReader(template_file)
                pdf_writer = PyPDF2.PdfWriter()
                
                # Copy all template pages
                for page in template_reader.pages:
                    pdf_writer.add_page(page)
                
                # Create a new page with the custom information
                info_page_pdf = self._create_info_page(design_name, google_drive_link)
                
                if info_page_pdf:
                    info_reader = PyPDF2.PdfReader(info_page_pdf)
                    pdf_writer.add_page(info_reader.pages[0])
                
                # Write the customized PDF
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                
                return True
                
        except Exception as e:
            logger.error(f"Template copy with overlay failed: {e}")
            return False
    
    def _create_text_overlay(self, design_name: str, google_drive_link: str, 
                           page_num: int = 0) -> Optional[str]:
        """Create a text overlay for the PDF.
        
        Args:
            design_name: Name of the design
            google_drive_link: Google Drive folder link
            page_num: Page number (for positioning)
            
        Returns:
            Path to temporary overlay PDF file
        """
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_path = temp_file.name
            temp_file.close()
            
            # Create overlay PDF with ReportLab
            c = canvas.Canvas(temp_path, pagesize=letter)
            width, height = letter
            
            # Based on the user's template, the "CLICK HERE" button appears to be
            # positioned in the lower portion of the page. We'll add an invisible
            # clickable area over where the button should be.

            # Estimated coordinates for "CLICK HERE" button based on typical PDF layout
            # These coordinates may need adjustment based on the actual template
            button_left = 295    # X coordinate of left edge of button
            button_bottom = 200  # Y coordinate of bottom edge of button
            button_right = 505   # X coordinate of right edge of button
            button_top = 250     # Y coordinate of top edge of button

            # Add invisible clickable link over the "CLICK HERE" button area
            c.linkURL(google_drive_link, (button_left, button_bottom, button_right, button_top))

            # Also add the design name in a subtle way at the top (only on first page)
            if page_num == 0:
                c.setFont("Helvetica", 10)
                c.setFillColor(black)

                # Clean design name for display
                display_name = design_name.replace('_', ' ').title()

                # Position at top of page, small and unobtrusive
                c.drawString(50, height - 50, f"Design: {display_name}")
            
            c.save()
            return temp_path
            
        except Exception as e:
            logger.error(f"Text overlay creation failed: {e}")
            return None

    def _create_design_name_overlay(self, design_name: str) -> Optional[str]:
        """Create a minimal overlay that only adds the design name.

        Args:
            design_name: Name of the design

        Returns:
            Path to temporary overlay PDF file
        """
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_path = temp_file.name
            temp_file.close()

            # Create overlay PDF with ReportLab
            c = canvas.Canvas(temp_path, pagesize=letter)
            width, height = letter

            # Add the design name in a subtle way at the top
            c.setFont("Helvetica", 10)
            c.setFillColor(black)

            # Clean design name for display
            display_name = design_name.replace('_', ' ').title()

            # Position at top of page, small and unobtrusive
            c.drawString(50, height - 50, f"Design: {display_name}")

            c.save()
            return temp_path

        except Exception as e:
            logger.error(f"Design name overlay creation failed: {e}")
            return None

    def _create_info_page(self, design_name: str, google_drive_link: str) -> Optional[str]:
        """Create a dedicated information page.
        
        Args:
            design_name: Name of the design
            google_drive_link: Google Drive folder link
            
        Returns:
            Path to temporary info page PDF file
        """
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_path = temp_file.name
            temp_file.close()
            
            # Create info page with ReportLab
            c = canvas.Canvas(temp_path, pagesize=letter)
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 24)
            c.setFillColor(black)
            title_text = "Your Digital Download"
            text_width = c.stringWidth(title_text, "Helvetica-Bold", 24)
            c.drawString(width/2 - text_width/2, height - 100, title_text)

            # Design name
            c.setFont("Helvetica-Bold", 18)
            display_name = design_name.replace('_', ' ').title()
            name_width = c.stringWidth(display_name, "Helvetica-Bold", 18)
            c.drawString(width/2 - name_width/2, height - 150, display_name)

            # Instructions
            c.setFont("Helvetica", 14)
            instruction_text = "Click the link below to access your files:"
            inst_width = c.stringWidth(instruction_text, "Helvetica", 14)
            c.drawString(width/2 - inst_width/2, height - 200, instruction_text)

            # Google Drive link
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(blue)
            link_width = c.stringWidth(google_drive_link, "Helvetica-Bold", 12)
            c.drawString(width/2 - link_width/2, height - 250, google_drive_link)

            # Make it clickable
            c.linkURL(google_drive_link,
                     (width/2 - link_width/2, height - 260,
                      width/2 + link_width/2, height - 240))

            # Additional info
            c.setFont("Helvetica", 12)
            c.setFillColor(black)
            sizes_text = "Your download includes 5 sizes:"
            sizes_width = c.stringWidth(sizes_text, "Helvetica", 12)
            c.drawString(width/2 - sizes_width/2, height - 300, sizes_text)

            sizes = ["24x36 inches", "18x24 inches", "16x20 inches", "11x14 inches", "5x7 inches"]
            for i, size in enumerate(sizes):
                size_text = f"• {size}"
                size_width = c.stringWidth(size_text, "Helvetica", 12)
                c.drawString(width/2 - size_width/2, height - 330 - (i * 20), size_text)
            
            c.save()
            return temp_path
            
        except Exception as e:
            logger.error(f"Info page creation failed: {e}")
            return None
    
    def _clean_filename(self, design_name: str) -> str:
        """Clean design name for use as filename.
        
        Args:
            design_name: Original design name
            
        Returns:
            Cleaned filename
        """
        # Replace spaces and special characters
        clean_name = design_name.replace(' ', '_').replace('_', '_')
        
        # Remove invalid filename characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            clean_name = clean_name.replace(char, '')
        
        return clean_name.lower()
    
    def validate_template(self, template_path: str = None) -> Tuple[bool, Optional[str]]:
        """Validate that the template PDF is readable.
        
        Args:
            template_path: Path to template (optional, uses set template if not provided)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        path_to_check = Path(template_path) if template_path else self.template_path
        
        if not path_to_check:
            return False, "No template path provided"
        
        if not path_to_check.exists():
            return False, f"Template file not found: {path_to_check}"
        
        try:
            with open(path_to_check, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                page_count = len(reader.pages)
                
                logger.info(f"Template validation successful: {page_count} pages")
                return True, None
                
        except Exception as e:
            error_msg = f"Template validation failed: {e}"
            logger.error(error_msg)
            return False, error_msg
