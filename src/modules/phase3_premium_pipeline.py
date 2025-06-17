#!/usr/bin/env python3
"""
Phase 3 Premium Digital Products Pipeline
========================================

Complete automation pipeline for premium digital product creation:
1. Detects PNG+SVG file pairs
2. Creates 5 sized SVG files (24x36, 18x24, 16x20, 11x14, 5x7)
3. Uploads to Google Drive with shareable links
4. Customizes PDF template with Google Drive link
5. Generates mockups for Etsy listing
6. Creates AI-optimized SEO content
7. Creates Etsy listing with mockups + digital PDF

This is the ULTIMATE automation system for digital product businesses!
"""

import os
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Import all Phase 3 modules
from modules.google_drive_manager import GoogleDriveManager
from modules.pdf_customizer import PDFCustomizer
from api.etsy import EtsyAPIClient
from modules.openai_seo_optimizer import OpenAISEOOptimizer
from modules.custom_mockup_generator import CustomMockupGenerator

logger = logging.getLogger(__name__)

@dataclass
class Phase3Result:
    """Result of Phase 3 premium digital product processing."""
    success: bool
    design_name: str
    jpeg_files_created: int = 0
    total_file_size_mb: float = 0.0
    google_drive_folder: Optional[str] = None
    google_drive_link: Optional[str] = None
    customized_pdf: Optional[str] = None
    mockup_files: List[str] = None
    etsy_listing_id: Optional[str] = None
    seo_content: Optional[Dict] = None
    processing_time: float = 0.0
    error: Optional[str] = None

class Phase3PremiumPipeline:
    """Complete Phase 3 Premium Digital Products Pipeline."""
    
    def __init__(self, mockups_directory: str = None, pdf_template_path: str = None, 
                 mode: str = "validate"):
        """Initialize Phase 3 Premium Pipeline.
        
        Args:
            mockups_directory: Directory containing PNG+SVG design files
            pdf_template_path: Path to PDF template file
            mode: Processing mode ('validate' or 'batch')
        """
        # Use new organized folder structure
        self.mockup_files_dir = Path("assets/digital_downloads/mockup_files")
        self.production_files_dir = Path("assets/digital_downloads/production_files")
        self.pdf_template_path = pdf_template_path or "DIGITAL DOWNLOAD TEMPLATE.pdf"
        self.mode = mode

        # Initialize all components
        self._initialize_components()

        # Initialize static images for Etsy listings
        self._initialize_static_images()

        logger.info("🚀 Phase 3 Premium Digital Products Pipeline initialized")
        logger.info(f"   Mockup files directory: {self.mockup_files_dir}")
        logger.info(f"   Production files directory: {self.production_files_dir}")
        logger.info(f"   PDF template: {self.pdf_template_path}")
        logger.info(f"   Static images: {len(self.static_image_ids)} found")
        logger.info(f"   Mode: {self.mode}")
    
    def _initialize_components(self):
        """Initialize all pipeline components."""
        try:
            # Phase 3 specific components (no JPEG resizer needed - using pre-sized files)
            self.drive_manager = GoogleDriveManager()
            self.pdf_customizer = PDFCustomizer(
                template_path=self.pdf_template_path,
                output_dir="output/phase3_custom_pdfs"
            )
            
            # Existing components
            self.etsy_client = EtsyAPIClient()
            self.seo_optimizer = OpenAISEOOptimizer()
            self.mockup_generator = CustomMockupGenerator(
                assets_dir="assets",
                output_dir="output/phase3_mockups",
                auto_manage=True,
                enable_sheets_upload=False
            )
            
            logger.info("✅ All pipeline components initialized")

        except Exception as e:
            logger.error(f"Failed to initialize pipeline components: {e}")
            raise

    def _initialize_static_images(self):
        """Find template listing and extract static image IDs."""
        try:
            logger.info("Searching for 'digital download template' listing...")

            # Search for template listing by title
            template_listing = self._find_template_listing()

            if template_listing:
                self.template_listing_id = template_listing.get('listing_id')
                logger.info(f"Found template listing: {self.template_listing_id}")

                # Extract static image IDs
                self.static_image_ids = self._extract_static_image_ids(template_listing)
                logger.info(f"Extracted {len(self.static_image_ids)} static image IDs")
            else:
                logger.warning("Template listing not found - will proceed without static images")
                self.static_image_ids = []

        except Exception as e:
            logger.error(f"Failed to initialize static images: {e}")
            logger.warning("Proceeding without static images")
            self.static_image_ids = []

    def _find_template_listing(self) -> Optional[Dict[str, Any]]:
        """Find the digital download template listing."""
        try:
            # Search for listings with "digital download template" in title
            endpoint = f"/application/shops/{self.etsy_client.shop_id}/listings"
            params = {
                'state': 'draft',
                'limit': 100,
                'includes': ['Images']
            }

            response = self.etsy_client.make_request("GET", endpoint, params=params)

            if response.status_code != 200:
                logger.error(f"Failed to search listings: {response.status_code}")
                return None

            listings = response.json().get('results', [])

            # Look for template listing
            for listing in listings:
                title = listing.get('title', '').lower()
                if 'digital download template' in title or 'template' in title:
                    logger.info(f"Found template listing: {listing.get('title')}")
                    return listing

            logger.warning("No template listing found")
            return None

        except Exception as e:
            logger.error(f"Error searching for template listing: {e}")
            return None

    def _extract_static_image_ids(self, template_listing: Dict[str, Any]) -> List[str]:
        """Extract static image IDs from template listing."""
        try:
            images = template_listing.get('images', [])

            if not images:
                logger.warning("Template listing has no images")
                return []

            # Extract image IDs (assuming last 3 images are static)
            image_ids = []
            for image in images:
                if isinstance(image, dict):
                    image_id = image.get('listing_image_id')
                    if image_id:
                        image_ids.append(str(image_id))

            # Take last 3 images as static images (instructions, what's included, size chart)
            static_ids = image_ids[-3:] if len(image_ids) >= 3 else image_ids

            logger.info(f"Extracted static image IDs: {static_ids}")
            return static_ids

        except Exception as e:
            logger.error(f"Error extracting static image IDs: {e}")
            return []
    
    def discover_design_pairs(self) -> List[Dict[str, Any]]:
        """Discover design files in organized folder structure.

        Returns:
            List of design dictionaries with mockup and production file info
        """
        logger.info(f"🔍 Discovering designs in organized folder structure")
        logger.info(f"   Mockup files: {self.mockup_files_dir}")
        logger.info(f"   Production files: {self.production_files_dir}")

        designs = []

        # Scan numbered folders (1-10)
        for folder_num in range(1, 11):
            mockup_folder = self.mockup_files_dir / str(folder_num)
            production_folder = self.production_files_dir / str(folder_num)

            if not mockup_folder.exists() or not production_folder.exists():
                continue

            # Find mockup file (single JPEG)
            mockup_files = list(mockup_folder.glob("*.jpeg")) + list(mockup_folder.glob("*.jpg"))
            if not mockup_files:
                logger.warning(f"No mockup file found in folder {folder_num}")
                continue

            mockup_file = mockup_files[0]  # Take first JPEG found

            # Extract base name from mockup file (remove ratio suffix)
            # e.g., "georgia_okeefe_black_cat_flower_print_3_4 Ratio" -> "georgia_okeefe_black_cat_flower_print"
            mockup_stem = mockup_file.stem
            if "_3_4 Ratio" in mockup_stem:
                base_name = mockup_stem.replace("_3_4 Ratio", "")
            elif " Ratio" in mockup_stem:
                # Handle other ratio patterns
                base_name = mockup_stem.split("_")[:-2]  # Remove last two parts (ratio + "Ratio")
                base_name = "_".join(base_name)
            else:
                base_name = mockup_stem

            # Find production files (ratio-based naming)
            expected_ratios = ["2_3 Ratio", "3_4 Ratio", "4_5 Ratio", "ISO", "11x14"]  # Based on your files
            production_files = {}

            for ratio in expected_ratios:
                ratio_file = production_folder / f"{base_name}_{ratio}.jpg"
                if not ratio_file.exists():
                    # Try .jpeg extension
                    ratio_file = production_folder / f"{base_name}_{ratio}.jpeg"

                if ratio_file.exists():
                    production_files[ratio] = ratio_file
                else:
                    logger.warning(f"Missing production file: {base_name}_{ratio}.jpg in folder {folder_num}")

            # Include designs with at least 3 production files (flexible requirement)
            if len(production_files) >= 3:
                design = {
                    'folder_number': folder_num,
                    'design_name': base_name,
                    'mockup_file': mockup_file,
                    'production_files': production_files
                }
                designs.append(design)
                logger.info(f"✅ Found design {folder_num}: {base_name} ({len(production_files)} ratio files)")
            else:
                logger.warning(f"❌ Insufficient files in folder {folder_num}: {base_name} (only {len(production_files)} files, need at least 3)")

        logger.info(f"📊 Discovery results:")
        logger.info(f"   🌟 Designs found: {len(designs)}")
        logger.info(f"   📁 Folders scanned: 1-10")
        logger.info(f"   📐 Using ratio-based naming (2:3, 3:4, 4:5, ISO, 11x14)")
        logger.info(f"   🎯 Customer-friendly ratio system for flexible sizing")

        return designs
    
    def process_premium_design(self, design: Dict[str, Any]) -> Phase3Result:
        """Process a single premium design through the complete Phase 3 pipeline.

        Args:
            design: Design dictionary with mockup and production file info

        Returns:
            Phase3Result with complete processing details
        """
        start_time = time.time()
        result = Phase3Result(success=False, design_name=design['design_name'])

        try:
            logger.info(f"🎨 Processing premium design: {design['design_name']}")
            logger.info(f"   Folder: {design['folder_number']}")
            logger.info(f"   Mockup file: {design['mockup_file'].name}")

            # Step 1: Use pre-sized ratio-based JPEG files (no creation needed)
            logger.info("📐 Step 1: Using pre-sized ratio-based JPEG files...")
            production_files = design['production_files']
            file_paths = list(production_files.values())

            # Calculate total file size
            total_size_mb = sum(f.stat().st_size for f in file_paths) / (1024 * 1024)

            result.jpeg_files_created = len(production_files)
            result.total_file_size_mb = total_size_mb

            # Log the ratios available
            ratios = list(production_files.keys())
            logger.info(f"✅ Using {len(production_files)} ratio-based JPEG files ({total_size_mb:.1f} MB)")
            logger.info(f"   Available ratios: {', '.join(ratios)}")
            
            # Step 2: Upload to Google Drive
            logger.info("☁️  Step 2: Uploading to Google Drive...")
            drive_result = self.drive_manager.create_design_package(
                design_name=design['design_name'],
                jpeg_files=file_paths  # Pre-sized JPEG files
            )
            
            if not drive_result.success:
                raise Exception(f"Google Drive upload failed: {drive_result.error}")
            
            result.google_drive_folder = drive_result.folder_id
            result.google_drive_link = drive_result.shareable_link
            logger.info(f"✅ Google Drive package created: {drive_result.shareable_link}")
            
            # Step 3: Customize PDF template
            logger.info("📄 Step 3: Customizing PDF template...")
            pdf_result = self.pdf_customizer.customize_pdf(
                design_name=design['design_name'],
                google_drive_link=drive_result.shareable_link
            )
            
            if not pdf_result.success:
                raise Exception(f"PDF customization failed: {pdf_result.error}")
            
            result.customized_pdf = pdf_result.output_path
            logger.info(f"✅ PDF customized: {Path(pdf_result.output_path).name}")
            
            # Step 4: Generate mockups (using mockup JPEG file)
            logger.info("🖼️  Step 4: Generating mockups...")
            mockup_files = self._generate_mockups(design)
            result.mockup_files = mockup_files
            logger.info(f"✅ Generated {len(mockup_files)} mockups")
            
            # Step 5: Generate SEO content
            logger.info("🔍 Step 5: Generating SEO content...")
            seo_content = self.seo_optimizer.generate_seo_content(design['design_name'])
            result.seo_content = seo_content
            logger.info(f"✅ SEO content generated")
            
            # Step 6: Create Etsy listing (if not in validate mode)
            if self.mode == "validate":
                result.etsy_listing_id = "draft_preview_only"
                logger.info("✅ Prepared for Etsy listing (validate mode)")
            else:
                logger.info("🛒 Step 6: Creating Etsy listing...")
                
                # Create digital download listing
                listing_id = self.etsy_client.create_digital_download_listing(
                    title=seo_content['title'],
                    description=seo_content['description'],
                    price=13.32,
                    tags=seo_content['tags'],
                    mockup_files=mockup_files,
                    static_image_ids=self.static_image_ids  # Copy 3 static images from template
                )
                
                # Upload the customized PDF as digital product
                pdf_uploaded = self.etsy_client.upload_digital_file(
                    listing_id=listing_id,
                    file_path=pdf_result.output_path,
                    file_name=f"{design['design_name']}_digital_download.pdf"
                )
                
                if not pdf_uploaded:
                    logger.warning("⚠️  PDF upload failed, but listing created")
                
                result.etsy_listing_id = listing_id
                logger.info(f"✅ Etsy listing created: {listing_id}")
            
            # Success!
            result.success = True
            result.processing_time = time.time() - start_time
            
            logger.info(f"🎉 Premium design processing complete!")
            logger.info(f"   Design: {design['design_name']}")
            logger.info(f"   Folder: {design['folder_number']}")
            logger.info(f"   JPEG files: {result.jpeg_files_created} ({result.total_file_size_mb:.1f} MB)")
            logger.info(f"   Google Drive: {result.google_drive_link}")
            logger.info(f"   PDF: {Path(result.customized_pdf).name}")
            logger.info(f"   Mockups: {len(result.mockup_files)}")
            logger.info(f"   Etsy listing: {result.etsy_listing_id}")
            logger.info(f"   Processing time: {result.processing_time:.1f}s")
            
            return result

        except Exception as e:
            result.error = str(e)
            result.processing_time = time.time() - start_time
            logger.error(f"❌ Premium design processing failed: {e}")
            return result

    def _generate_mockups(self, design: Dict[str, Any]) -> List[str]:
        """Generate poster mockups using the existing custom mockup generator.

        Args:
            design: Design dictionary with mockup file info

        Returns:
            List of mockup file paths (up to 7 mockups)
        """
        try:
            logger.info(f"Generating poster mockups for: {design['design_name']}")

            mockup_files = []

            # Get available poster templates (limit to 7 for Etsy)
            available_templates = self.mockup_generator.list_available_templates().get('posters', [])

            if not available_templates:
                logger.warning("No poster templates available, using original design file")
                return [str(design['mockup_file'])]

            # Generate mockups using up to 7 templates
            templates_to_use = available_templates[:7]
            logger.info(f"Using {len(templates_to_use)} poster templates: {templates_to_use}")

            for template_name in templates_to_use:
                try:
                    logger.info(f"Generating mockup with template: {template_name}")

                    # Generate mockup using custom mockup generator
                    result = self.mockup_generator.generate_mockup(
                        product_type='posters',
                        design_path=str(design['mockup_file']),
                        template_name=template_name,
                        upload_to_sheets=False  # We handle uploads separately
                    )

                    if result['success']:
                        mockup_files.append(result['mockup_path'])
                        logger.info(f"✅ Generated mockup: {Path(result['mockup_path']).name}")
                    else:
                        logger.error(f"❌ Failed to generate mockup with {template_name}: {result.get('error')}")

                except Exception as e:
                    logger.error(f"Error generating mockup with template {template_name}: {e}")
                    continue

            if not mockup_files:
                logger.warning("No mockups generated successfully, using original design file")
                return [str(design['mockup_file'])]

            logger.info(f"Successfully generated {len(mockup_files)} poster mockups")
            return mockup_files

        except Exception as e:
            logger.error(f"Failed to generate mockups: {e}")
            # Return original design file as fallback
            return [str(design['mockup_file'])]
    
    def run_batch_processing(self) -> Dict[str, Any]:
        """Run batch processing for all premium designs.
        
        Returns:
            Dictionary with batch processing results
        """
        start_time = time.time()
        
        logger.info("🚀 Starting Phase 3 Premium Batch Processing")
        logger.info("=" * 60)
        
        try:
            # Discover premium designs
            premium_designs = self.discover_design_pairs()

            if not premium_designs:
                return {
                    'success': False,
                    'message': 'No premium designs found in organized folders',
                    'processed_count': 0,
                    'total_time': time.time() - start_time
                }

            # Process designs
            results = []
            successful = 0
            failed = 0

            for i, design in enumerate(premium_designs, 1):
                logger.info(f"\n📦 Processing {i}/{len(premium_designs)}: {design['design_name']} (Folder {design['folder_number']})")

                result = self.process_premium_design(design)
                results.append(result)

                if result.success:
                    successful += 1
                    logger.info(f"✅ Success: {design['design_name']}")
                else:
                    failed += 1
                    logger.error(f"❌ Failed: {design['design_name']} - {result.error}")
                
                # Small delay between designs
                if i < len(premium_designs):
                    time.sleep(2)
            
            # Summary
            total_time = time.time() - start_time
            
            logger.info(f"\n🎉 Phase 3 Premium Batch Processing Complete!")
            logger.info("=" * 60)
            logger.info(f"📊 Results Summary:")
            logger.info(f"   ✅ Successful: {successful}")
            logger.info(f"   ❌ Failed: {failed}")
            logger.info(f"   📁 Total designs: {len(premium_designs)}")
            logger.info(f"   ⏱️  Total time: {total_time:.1f}s")
            logger.info(f"   📈 Average time per design: {total_time/len(premium_designs):.1f}s")
            
            if successful > 0:
                total_jpeg_files = sum(r.jpeg_files_created for r in results if r.success)
                logger.info(f"   📄 Total JPEG files processed: {total_jpeg_files}")
                logger.info(f"   ☁️  Google Drive folders created: {successful}")
                logger.info(f"   📋 Custom PDFs generated: {successful}")
                logger.info(f"   🛒 Etsy listings created: {successful}")
            
            return {
                'success': successful > 0,
                'message': f'Processed {successful}/{len(premium_designs)} designs successfully',
                'processed_count': successful,
                'failed_count': failed,
                'total_designs': len(premium_designs),
                'total_time': total_time,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return {
                'success': False,
                'message': f'Batch processing error: {e}',
                'processed_count': 0,
                'total_time': time.time() - start_time
            }
