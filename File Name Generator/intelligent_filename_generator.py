#!/usr/bin/env python3
"""
Intelligent Filename Generator for SEA-E Designs
===============================================

This script analyzes design images and generates SEO-optimized filenames
that automatically trigger the best SEO content generation in the pipeline.

Features:
- AI-powered image analysis to detect art movement, themes, and style
- Generates filenames optimized for SEA-E's art movement detection
- Copies files with new names to output directory
- Supports batch processing of multiple designs
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional
import base64
import json

# Add parent directory to path for SEA-E imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI library not found. Please install: pip install openai")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntelligentFilenameGenerator:
    """Generates SEO-optimized filenames by analyzing image content."""
    
    def __init__(self):
        """Initialize the filename generator."""
        self.openai_client = OpenAI()
        self.import_dir = Path("import")
        self.output_dir = Path("output/Output")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Art movement patterns for filename optimization
        self.movement_keywords = {
            'surrealism': ['surreal', 'dream', 'impossible', 'abstract', 'dali'],
            'impressionism': ['impressionist', 'painted', 'soft', 'dreamy', 'monet'],
            'pop_art': ['pop', 'bold', 'bright', 'modern', 'warhol'],
            'japanese': ['zen', 'minimalist', 'calm', 'peaceful', 'eastern'],
            'renaissance': ['classical', 'traditional', 'elegant', 'masterpiece'],
            'vintage': ['retro', 'classic', 'nostalgic', 'old-fashioned'],
            'gothic': ['dark', 'dramatic', 'mysterious', 'ornate'],
            'minimalist': ['simple', 'clean', 'geometric', 'minimal']
        }
        
        logger.info("🎨 Intelligent Filename Generator initialized")
    
    def analyze_image(self, image_path: Path) -> Dict[str, str]:
        """Analyze image content using OpenAI Vision API.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with detected elements
        """
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create analysis prompt
            prompt = """
            Analyze this cat art image and identify the following elements for SEO optimization:
            
            1. ART MOVEMENT: What art movement/style does this most resemble? 
               (surrealism, impressionism, pop_art, japanese, renaissance, vintage, gothic, minimalist, etc.)
            
            2. THEME/MOOD: What's the primary theme or mood?
               (dreamy, peaceful, bold, mysterious, cozy, elegant, playful, etc.)
            
            3. SEASON/SETTING: Any seasonal or setting elements?
               (autumn, winter, spring, summer, christmas, halloween, nature, urban, etc.)
            
            4. COLOR PALETTE: Dominant colors?
               (black, white, blue, red, gold, pastel, vibrant, monochrome, etc.)
            
            5. CAT PERSONALITY: How would you describe the cat's personality/archetype?
               (zen, mischievous, cozy, adventurous, sophisticated, playful, etc.)
            
            Respond in JSON format:
            {
                "art_movement": "detected_movement",
                "theme": "primary_theme", 
                "season": "seasonal_element_or_none",
                "color": "dominant_color",
                "cat_personality": "cat_archetype",
                "style_descriptors": ["descriptor1", "descriptor2"]
            }
            """
            
            # Call OpenAI Vision API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            
            # Extract JSON from response
            try:
                # Find JSON in the response
                start_idx = analysis_text.find('{')
                end_idx = analysis_text.rfind('}') + 1
                json_str = analysis_text[start_idx:end_idx]
                analysis = json.loads(json_str)
                
                logger.info(f"✅ Analyzed {image_path.name}: {analysis['art_movement']} style")
                return analysis
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"⚠️ Could not parse analysis for {image_path.name}: {e}")
                return self._fallback_analysis(image_path)
                
        except Exception as e:
            logger.error(f"❌ Error analyzing {image_path.name}: {e}")
            return self._fallback_analysis(image_path)
    
    def _fallback_analysis(self, image_path: Path) -> Dict[str, str]:
        """Fallback analysis based on filename patterns.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Basic analysis based on filename
        """
        filename_lower = image_path.name.lower()
        
        # Detect art movement from filename
        detected_movement = "surrealism"  # Default based on your examples
        for movement, keywords in self.movement_keywords.items():
            if any(keyword in filename_lower for keyword in keywords):
                detected_movement = movement
                break
        
        return {
            "art_movement": detected_movement,
            "theme": "dreamy",
            "season": "none",
            "color": "mixed",
            "cat_personality": "zen",
            "style_descriptors": ["artistic", "unique"]
        }
    
    def generate_filename(self, analysis: Dict[str, str], index: int) -> str:
        """Generate SEO-optimized filename from analysis.
        
        Args:
            analysis: Image analysis results
            index: File index for uniqueness
            
        Returns:
            Optimized filename
        """
        # Extract components
        movement = analysis.get('art_movement', 'surreal')
        theme = analysis.get('theme', 'dreamy')
        season = analysis.get('season', 'none')
        color = analysis.get('color', 'mixed')
        personality = analysis.get('cat_personality', 'zen')
        
        # Build filename components
        components = []
        
        # Art movement (primary trigger for SEO)
        components.append(movement.replace('_', '-'))
        
        # Theme/mood
        if theme and theme != 'none':
            components.append(theme)
        
        # Color if distinctive
        if color and color not in ['mixed', 'various', 'none']:
            components.append(color)
        
        # Season if applicable
        if season and season != 'none':
            components.append(season)
        
        # Cat personality
        if personality and personality != 'none':
            components.append(personality)
        
        # Always end with 'cat' and number
        components.extend(['cat', f'{index:03d}'])
        
        # Join with hyphens
        filename = '-'.join(components) + '.jpg'
        
        # Ensure filename is reasonable length
        if len(filename) > 50:
            # Simplify if too long
            filename = f"{movement}-{theme}-cat-{index:03d}.jpg"
        
        return filename
    
    def process_images(self) -> bool:
        """Process all images in the import directory.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find all image files
            image_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg']:
                image_files.extend(self.import_dir.glob(ext))
            
            if not image_files:
                logger.error(f"❌ No image files found in {self.import_dir}")
                return False
            
            logger.info(f"🔍 Found {len(image_files)} images to process")
            
            # Process each image
            processed = 0
            for i, image_path in enumerate(image_files, 1):
                logger.info(f"\n📸 Processing {i}/{len(image_files)}: {image_path.name}")
                
                # Analyze image
                analysis = self.analyze_image(image_path)
                
                # Generate new filename
                new_filename = self.generate_filename(analysis, i)
                
                # Copy file with new name
                output_path = self.output_dir / new_filename
                shutil.copy2(image_path, output_path)
                
                logger.info(f"✅ Created: {new_filename}")
                logger.info(f"   Art Movement: {analysis['art_movement']}")
                logger.info(f"   Theme: {analysis['theme']}")
                logger.info(f"   Personality: {analysis['cat_personality']}")
                
                processed += 1
            
            logger.info(f"\n🎉 Successfully processed {processed}/{len(image_files)} images!")
            logger.info(f"📁 Output files saved to: {self.output_dir}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing images: {e}")
            return False


def main():
    """Main entry point."""
    print("🎨 Intelligent Filename Generator for SEA-E Designs")
    print("=" * 60)
    print("Analyzing images and generating SEO-optimized filenames...")
    print()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key and try again.")
        return 1
    
    try:
        # Initialize generator
        generator = IntelligentFilenameGenerator()
        
        # Process images
        success = generator.process_images()
        
        if success:
            print("\n🎯 NEXT STEPS:")
            print("1. Review the generated filenames in output/Output/")
            print("2. Copy these files to your SEA-E pipeline directory")
            print("3. Run: python phase3_pipeline.py --mode batch")
            print("4. Enjoy automatic SEO optimization! 🚀")
            return 0
        else:
            print("\n❌ Processing failed. Check the logs above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Processing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
