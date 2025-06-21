"""
Market-Validated SEO Optimizer for Phase 4.

This module provides an enhanced SEO optimization engine that prioritizes
market-validated design concepts with proven SEO data, and falls back to
AI-optimized naming system for maximum success rate.
"""

import os
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from openai import OpenAI

from .design_concept_mapper import DesignConceptMapper
from .openai_seo_optimizer import OpenAISEOOptimizer

logger = logging.getLogger(__name__)

class MarketValidatedSEOOptimizer:
    """Enhanced SEO optimizer using market-validated concepts and AI naming system."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """Initialize the market-validated SEO optimizer.
        
        Args:
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            model: OpenAI model to use for optimization
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        # Initialize components
        self.concept_mapper = DesignConceptMapper()
        self.fallback_optimizer = OpenAISEOOptimizer(api_key=self.api_key, model=self.model)
        
        # Load AI-optimized keyword mappings
        self.keyword_mappings = self._load_keyword_mappings()
        
        logger.info("🚀 Market-Validated SEO Optimizer initialized")
        logger.info(f"   Concept mapper: {len(self.concept_mapper.concepts)} designs loaded")
        logger.info(f"   Fallback optimizer: OpenAI {self.model}")
        logger.info(f"   Keyword mappings: {len(self.keyword_mappings)} categories")
    
    def _load_keyword_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """Load AI-optimized keyword mappings from the naming system."""
        # Based on your AI-Optimized File Naming System document
        return {
            "art_movement_keywords": {
                "surreal": ["surreal art", "dali style", "dreamlike", "abstract art", "impossible", "symbolic"],
                "surrealism": ["surreal art", "dali style", "dreamlike", "abstract art", "impossible", "symbolic"],
                "pop": ["pop art", "modern art", "bold art", "contemporary", "iconic", "graphic"],
                "pop_art": ["pop art", "modern art", "bold art", "contemporary", "iconic", "graphic"],
                "renaissance": ["renaissance art", "classical art", "masterpiece", "da vinci style", "traditional"],
                "impressionist": ["impressionist", "dreamy art", "painted style", "monet style", "soft colors"],
                "impressionism": ["impressionist", "dreamy art", "painted style", "monet style", "soft colors"],
                "ukiyo": ["japanese art", "zen art", "eastern art", "hokusai style", "tranquil", "minimalist"],
                "japanese_ukiyo_e": ["japanese art", "zen art", "eastern art", "hokusai style", "tranquil", "minimalist"]
            },
            
            "seasonal_keywords": {
                "summer": ["summer decor", "vacation art", "bright wall art", "tropical", "sunny"],
                "july": ["summer decor", "vacation art", "bright wall art", "tropical", "sunny"],
                "backschool": ["dorm wall art", "college decor", "student gift", "academic", "campus"],
                "august": ["dorm wall art", "college decor", "student gift", "academic", "campus"],
                "fall": ["fall decor", "autumn art", "seasonal print", "harvest decor", "maple"],
                "september": ["fall decor", "autumn art", "seasonal print", "harvest decor", "maple"],
                "halloween": ["halloween decor", "spooky art", "october decor", "costume", "gothic"],
                "october": ["halloween decor", "spooky art", "october decor", "costume", "gothic"],
                "thanksgiving": ["thanksgiving decor", "gratitude art", "harvest print", "family"],
                "november": ["thanksgiving decor", "gratitude art", "harvest print", "family"],
                "holiday": ["christmas decor", "holiday art", "winter print", "christmas gift", "festive"],
                "december": ["christmas decor", "holiday art", "winter print", "christmas gift", "festive"]
            },
            
            "archetype_keywords": {
                "zen": ["peaceful art", "meditation", "calm decor", "mindful", "serene"],
                "zen_master": ["peaceful art", "meditation", "calm decor", "mindful", "serene"],
                "trickster": ["funny cat art", "mischievous", "playful", "humorous", "silly"],
                "scholar": ["intellectual art", "scholarly", "book lover", "academic", "wise"],
                "party": ["celebration art", "fun decor", "energetic", "social", "festive"],
                "party_animal": ["celebration art", "fun decor", "energetic", "social", "festive"],
                "cozy": ["cozy decor", "comfort art", "hygge", "homebody", "snuggle"],
                "cozy_homebody": ["cozy decor", "comfort art", "hygge", "homebody", "snuggle"]
            },
            
            "theme_keywords": {
                "harvest": ["harvest decor", "autumn art", "fall print", "seasonal"],
                "autumn": ["harvest decor", "autumn art", "fall print", "seasonal"],
                "spooky": ["spooky art", "halloween decor", "mysterious", "gothic"],
                "comfort": ["cozy decor", "comfort art", "hygge", "warm"],
                "cozy": ["cozy decor", "comfort art", "hygge", "warm"],
                "academic": ["academic art", "scholarly", "educational", "learning"],
                "vacation": ["vacation art", "travel decor", "leisure", "relaxing"],
                "bright": ["bright colors", "vibrant art", "energetic", "cheerful"],
                "warm_colors": ["warm tones", "golden art", "cozy colors", "autumn palette"],
                "mystical": ["mystical art", "magical", "ethereal", "enchanting"],
                "celebration": ["celebration art", "festive", "party decor", "joyful"]
            }
        }
    
    def generate_seo_content(self, design_identifier: str) -> Dict[str, Any]:
        """Generate SEO-optimized content using market-validated approach.
        
        Args:
            design_identifier: Design filename or slug
            
        Returns:
            Dictionary containing optimized SEO content
        """
        logger.info(f"🎯 Generating SEO content for: {design_identifier}")
        
        # Method 1: Try to find in market-validated concepts first
        concept_data = self.concept_mapper.get_seo_data(design_identifier)
        
        if concept_data:
            logger.info(f"✅ Found market-validated concept: {concept_data['concept_name']}")
            return self._enhance_concept_seo(concept_data)
        else:
            logger.info(f"⚠️ No concept found, using AI naming system fallback")
            return self._generate_from_naming_system(design_identifier)
    
    def _enhance_concept_seo(self, concept_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance market-validated concept SEO data.
        
        Args:
            concept_data: Concept data from mapper
            
        Returns:
            Enhanced SEO content
        """
        # Use the proven SEO data from concept as base
        base_title = concept_data['title']
        base_tags = concept_data['tags'].copy()
        
        # Enhance with keyword mappings for better optimization
        enhanced_tags = self._enhance_tags_with_mappings(
            base_tags, 
            concept_data['art_movement'],
            concept_data['target_month'],
            concept_data['cat_archetype'],
            concept_data['primary_theme']
        )
        
        # Ensure title meets requirements (120-140 chars, includes Digital Download)
        enhanced_title = self._optimize_title(base_title)
        
        # Generate enhanced description
        enhanced_description = self._generate_enhanced_description(concept_data)
        
        logger.info(f"🎨 Enhanced concept SEO:")
        logger.info(f"   Title: {len(enhanced_title)} chars")
        logger.info(f"   Tags: {len(enhanced_tags)} tags")
        logger.info(f"   Price: ${concept_data['price']}")
        
        return {
            'title': enhanced_title,
            'tags': enhanced_tags,
            'description': enhanced_description,
            'price': concept_data['price'],
            'concept_data': concept_data,
            'source': 'market_validated'
        }
    
    def _enhance_tags_with_mappings(self, base_tags: List[str], art_movement: str, 
                                  target_month: str, cat_archetype: str, 
                                  primary_theme: str) -> List[str]:
        """Enhance tags using keyword mappings.
        
        Args:
            base_tags: Original tags from concept
            art_movement: Art movement category
            target_month: Target month
            cat_archetype: Cat archetype
            primary_theme: Primary theme
            
        Returns:
            Enhanced tag list (exactly 13 tags)
        """
        enhanced_tags = base_tags.copy()
        
        # Add keywords from mappings if not already present
        categories = [
            (art_movement, self.keyword_mappings["art_movement_keywords"]),
            (target_month, self.keyword_mappings["seasonal_keywords"]),
            (cat_archetype, self.keyword_mappings["archetype_keywords"]),
            (primary_theme, self.keyword_mappings["theme_keywords"])
        ]
        
        for category_value, mapping in categories:
            if category_value in mapping:
                for keyword in mapping[category_value]:
                    if keyword not in enhanced_tags and len(enhanced_tags) < 13:
                        enhanced_tags.append(keyword)
        
        # Ensure we have exactly 13 tags
        while len(enhanced_tags) < 13:
            default_tags = ["art print", "digital download", "wall art", "home decor", 
                          "cat art", "printable art", "instant download"]
            for tag in default_tags:
                if tag not in enhanced_tags and len(enhanced_tags) < 13:
                    enhanced_tags.append(tag)
        
        return enhanced_tags[:13]
    
    def _optimize_title(self, base_title: str) -> str:
        """Optimize title to meet Etsy requirements.

        Args:
            base_title: Original title from concept

        Returns:
            Optimized title (120-140 chars with Digital Download)
        """
        title = base_title.strip()

        # Ensure Digital Download is included
        digital_keywords = ["digital download", "digital art print", "digital print"]
        has_digital = any(keyword in title.lower() for keyword in digital_keywords)

        if not has_digital:
            if len(title) < 125:
                title += " | Digital Download"
            else:
                title = title[:125] + " | Digital Download"

        # Ensure minimum 120 characters by adding descriptive extensions
        extensions = [
            " | Instant Download",
            " | Printable Wall Art",
            " | Home Decor Gift",
            " | Cat Lover Gift",
            " | Art Print Poster",
            " | Digital File",
            " | Printable Art",
            " | Wall Decor"
        ]

        for ext in extensions:
            if len(title) < 120 and len(title) + len(ext) <= 140:
                title += ext
            elif len(title) >= 120:
                break

        # If still too short, add more descriptive content
        if len(title) < 120:
            remaining_chars = 120 - len(title)
            if remaining_chars > 15:
                title += " | Cat Art Print Decor"

        return title[:140]
    
    def _generate_enhanced_description(self, concept_data: Dict[str, Any]) -> str:
        """Generate enhanced description for concept.
        
        Args:
            concept_data: Concept data
            
        Returns:
            Enhanced description
        """
        # Create engaging description based on concept data
        name = concept_data['concept_name']
        theme = concept_data['primary_theme']
        movement = concept_data['art_movement']
        
        description = f"Transform your space with this stunning {name.lower()} design. "
        description += f"This {movement} inspired artwork captures the essence of {theme} "
        description += "in a way that speaks to cat lovers and art enthusiasts alike. "
        description += "Perfect for adding personality and sophistication to any room."
        
        # Load and append template
        template_content = self._load_description_template()
        full_description = f"{description}\n\n{template_content}"
        
        return full_description

    def _generate_from_naming_system(self, design_identifier: str) -> Dict[str, Any]:
        """Generate SEO content using AI-optimized naming system fallback.

        Args:
            design_identifier: Design filename or slug

        Returns:
            SEO content generated from naming system
        """
        logger.info(f"🤖 Using AI naming system for: {design_identifier}")

        # Parse AI-optimized naming if it follows the format
        parsed_components = self._parse_ai_naming(design_identifier)

        if parsed_components:
            # Generate SEO using parsed components
            return self._generate_from_components(parsed_components)
        else:
            # Fallback to original OpenAI optimizer
            logger.info(f"📝 Using OpenAI fallback for: {design_identifier}")
            fallback_content = self.fallback_optimizer.generate_seo_content(design_identifier)
            fallback_content['source'] = 'openai_fallback'
            fallback_content['price'] = 20  # Default price for non-concept designs
            return fallback_content

    def _parse_ai_naming(self, filename: str) -> Optional[Dict[str, str]]:
        """Parse AI-optimized naming format.

        Format: {Priority}-{ArtMovement}-{Season}-{CatArchetype}-{Theme}-{ID}
        Example: A-Surreal-Fall-Zen-Harvest-032.jpg

        Args:
            filename: Design filename

        Returns:
            Parsed components or None if not AI-optimized format
        """
        # Remove extension and clean filename
        clean_name = Path(filename).stem

        # Check if it matches AI-optimized format
        parts = clean_name.split('-')

        if len(parts) >= 6:
            return {
                'priority': parts[0],
                'art_movement': parts[1].lower(),
                'season': parts[2].lower(),
                'cat_archetype': parts[3].lower(),
                'theme': parts[4].lower(),
                'id': parts[5]
            }

        return None

    def _generate_from_components(self, components: Dict[str, str]) -> Dict[str, Any]:
        """Generate SEO content from parsed AI naming components.

        Args:
            components: Parsed naming components

        Returns:
            Generated SEO content
        """
        # Map components to keywords
        art_keywords = self.keyword_mappings["art_movement_keywords"].get(components['art_movement'], [])
        seasonal_keywords = self.keyword_mappings["seasonal_keywords"].get(components['season'], [])
        archetype_keywords = self.keyword_mappings["archetype_keywords"].get(components['cat_archetype'], [])
        theme_keywords = self.keyword_mappings["theme_keywords"].get(components['theme'], [])

        # Generate title
        title_parts = []
        if art_keywords:
            title_parts.append(art_keywords[0].title())
        if theme_keywords:
            title_parts.append(theme_keywords[0].title())
        title_parts.extend(["Cat Art Print", "Wall Art", "Digital Download"])

        title = " | ".join(title_parts)
        title = self._optimize_title(title)

        # Generate tags
        tags = []
        for keyword_list in [art_keywords, seasonal_keywords, archetype_keywords, theme_keywords]:
            tags.extend(keyword_list[:3])  # Take top 3 from each category

        # Add essential tags
        essential_tags = ["cat art", "digital download", "wall art", "art print"]
        for tag in essential_tags:
            if tag not in tags:
                tags.append(tag)

        tags = tags[:13]  # Limit to 13

        # Generate description
        description = f"Stunning {components['art_movement']} inspired cat art perfect for {components['season']} decorating. "
        description += f"This {components['theme']} design appeals to cat lovers who appreciate {components['cat_archetype']} aesthetics."

        # Add template
        template_content = self._load_description_template()
        full_description = f"{description}\n\n{template_content}"

        # Determine price based on priority
        price_map = {'A': 25, 'B': 22, 'C': 20}
        price = price_map.get(components['priority'], 20)

        return {
            'title': title,
            'tags': tags,
            'description': full_description,
            'price': price,
            'components': components,
            'source': 'ai_naming_system'
        }

    def _load_description_template(self) -> str:
        """Load the digital download description template."""
        template_path = Path(__file__).parent.parent.parent / "docs" / "DD Description Template.md"

        try:
            with open(template_path, 'r') as f:
                content = f.read()

            # Extract everything after the first line
            lines = content.split('\n')
            template_content = '\n'.join(lines[2:])  # Skip first line and empty line

            return template_content.strip()

        except FileNotFoundError:
            logger.warning(f"Description template not found at {template_path}")
            return self._get_fallback_template()

    def _get_fallback_template(self) -> str:
        """Fallback template if file is not found."""
        return """
🌟 Instant Digital Download
No need to wait! Once your purchase is confirmed, you'll receive high-resolution files that you can print at home, through a professional printer, or use as a digital screensaver.

🎨 Perfect for Any Space
With a variety of file sizes included, you can customize your print to fit your style and space.

What's Included?
High-resolution files (300 dpi) formatted for multiple aspect ratios and print sizes.

Important Notes:
• This listing is for a digital download only—no physical item will be shipped.
• The artwork is for personal use only and may not be resold or redistributed.
"""

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get statistics about the optimizer performance.

        Returns:
            Dictionary with optimizer statistics
        """
        concept_stats = self.concept_mapper.get_stats()

        return {
            'total_concepts_available': concept_stats['total_concepts'],
            'concept_coverage': concept_stats,
            'keyword_mappings': {
                'art_movements': len(self.keyword_mappings['art_movement_keywords']),
                'seasonal': len(self.keyword_mappings['seasonal_keywords']),
                'archetypes': len(self.keyword_mappings['archetype_keywords']),
                'themes': len(self.keyword_mappings['theme_keywords'])
            },
            'fallback_optimizer': 'OpenAI GPT-4o'
        }
