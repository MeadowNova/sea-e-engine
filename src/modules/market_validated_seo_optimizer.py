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
        
        # Generate compelling, market-driven title
        enhanced_title = self._create_compelling_title(concept_data)
        
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

    def _create_compelling_title(self, concept_data: Dict[str, Any]) -> str:
        """Create a compelling, market-driven title that actually sells.

        Args:
            concept_data: Concept data with all the details

        Returns:
            Compelling title optimized for conversions
        """
        # Extract key elements
        name = concept_data['concept_name']
        theme = concept_data['primary_theme']
        movement = concept_data['art_movement']
        cat_archetype = concept_data.get('cat_archetype', 'zen_master')

        # Create compelling title components
        # 1. Emotional hook + Art style
        emotional_hooks = {
            'autumn': "Cozy Fall Vibes",
            'winter': "Winter Magic",
            'spring': "Fresh Spring Energy",
            'summer': "Bright Summer Joy",
            'halloween': "Spooky Season Charm",
            'christmas': "Holiday Festive Spirit",
            'thanksgiving': "Grateful Autumn Warmth"
        }

        # 2. Art movement descriptors that sound appealing
        movement_descriptors = {
            'surrealism': "Dreamy Surreal",
            'impressionism': "Soft Impressionist",
            'pop_art': "Bold Pop Art",
            'renaissance': "Classic Renaissance",
            'japanese': "Zen Japanese",
            'vintage': "Charming Vintage",
            'gothic': "Dramatic Gothic",
            'minimalist': "Clean Modern"
        }

        # 3. Cat personality that appeals to buyers
        cat_personalities = {
            'zen_master': "Peaceful Cat",
            'mischief_maker': "Playful Cat",
            'cozy_companion': "Cuddly Cat",
            'adventure_seeker': "Bold Cat",
            'sophisticated_observer': "Elegant Cat"
        }

        # Build compelling title
        hook = emotional_hooks.get(theme, "Stunning")
        art_style = movement_descriptors.get(movement, movement.title())
        cat_type = cat_personalities.get(cat_archetype, "Adorable Cat")

        # Create title that focuses on benefits and emotions
        title_templates = [
            f"{hook} {art_style} {cat_type} Wall Art | Digital Download Print | Cat Lover Home Decor Gift",
            f"{art_style} {cat_type} Art Print | {hook} Digital Download | Instant Cat Wall Decor",
            f"{cat_type} {art_style} Digital Art | {hook} Printable Wall Decor | Cat Art Download"
        ]

        # Choose the template that fits best within character limits
        for template in title_templates:
            if 120 <= len(template) <= 140:
                return template

        # Fallback: use first template and optimize length
        title = title_templates[0]
        return self._optimize_title(title)

    def _generate_enhanced_description(self, concept_data: Dict[str, Any]) -> str:
        """Generate enhanced description for concept.

        Args:
            concept_data: Concept data

        Returns:
            Enhanced description
        """
        # Create compelling, market-driven description
        name = concept_data['concept_name']
        theme = concept_data['primary_theme']
        movement = concept_data['art_movement']
        humor_style = concept_data.get('humor_style', 'relatable_behavior')
        cat_archetype = concept_data.get('cat_archetype', 'zen_master')

        # Create engaging hook based on concept data
        hooks = {
            'autumn': "🍂 Fall vibes meet feline charm in this absolutely irresistible design!",
            'winter': "❄️ Cozy winter magic captured with the perfect touch of cat personality!",
            'spring': "🌸 Fresh spring energy meets adorable cat charm in this delightful piece!",
            'summer': "☀️ Bright summer vibes with a playful cat twist that'll make you smile!",
            'halloween': "🎃 Spooky season gets a purr-fect upgrade with this hauntingly cute design!",
            'christmas': "🎄 Holiday magic meets cat cuteness in this festive masterpiece!",
            'thanksgiving': "🦃 Grateful vibes and cat charm combine for the perfect seasonal decor!"
        }

        # Get theme-specific hook or create dynamic one
        hook = hooks.get(theme, f"✨ {movement.title()} artistry meets irresistible cat charm!")

        # Create personality-driven description
        personality_traits = {
            'zen_master': "wise and contemplative energy",
            'mischief_maker': "playful and cheeky personality",
            'cozy_companion': "warm and comforting presence",
            'adventure_seeker': "bold and adventurous spirit",
            'sophisticated_observer': "elegant and refined demeanor"
        }

        trait = personality_traits.get(cat_archetype, "captivating feline charm")

        description = f"{hook}\n\n"
        description += f"This isn't just another cat print – it's a conversation starter that brings {trait} "
        description += f"to any space. Whether you're a devoted cat parent, art lover, or someone who appreciates "
        description += f"unique decor that actually has personality, this {movement}-inspired piece delivers.\n\n"
        description += f"Perfect for cat lovers who want their walls to reflect their passion with style and sophistication!"

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
            # Try art movement detection fallback
            art_movement = self._detect_art_movement(design_identifier)

            if art_movement:
                logger.info(f"🎨 Detected art movement: {art_movement}")
                return self._generate_from_art_movement(design_identifier, art_movement)
            else:
                # Final fallback to original OpenAI optimizer
                logger.info(f"📝 Using OpenAI fallback for: {design_identifier}")
                fallback_content = self.fallback_optimizer.generate_seo_content(design_identifier)
                fallback_content['source'] = 'openai_fallback'
                fallback_content['price'] = 20  # Default price for non-concept designs
                return fallback_content

    def _detect_art_movement(self, filename: str) -> Optional[str]:
        """Detect art movement from filename.

        Args:
            filename: Design filename

        Returns:
            Detected art movement or None
        """
        # Remove extension and convert to lowercase
        clean_name = Path(filename).stem.lower()

        # Art movement detection patterns
        movement_patterns = {
            'japanese': ['japanese', 'japan', 'ukiyo', 'zen', 'hokusai', 'sumi', 'ink'],
            'surreal': ['surreal', 'dali', 'dream', 'impossible', 'abstract', 'weird'],
            'surrealism': ['surreal', 'dali', 'dream', 'impossible', 'abstract', 'weird'],
            'pop': ['pop', 'warhol', 'modern', 'bold', 'graphic', 'contemporary'],
            'pop_art': ['pop', 'warhol', 'modern', 'bold', 'graphic', 'contemporary'],
            'renaissance': ['renaissance', 'classical', 'davinci', 'masterpiece', 'traditional'],
            'impressionist': ['impressionist', 'monet', 'painted', 'dreamy', 'soft'],
            'impressionism': ['impressionist', 'monet', 'painted', 'dreamy', 'soft'],
            'cubism': ['cubism', 'picasso', 'geometric', 'angular', 'fragmented'],
            'art_nouveau': ['nouveau', 'floral', 'organic', 'decorative', 'ornate'],
            'minimalist': ['minimal', 'simple', 'clean', 'geometric', 'basic'],
            'vintage': ['vintage', 'retro', 'classic', 'old', 'antique'],
            'gothic': ['gothic', 'dark', 'medieval', 'ornate', 'dramatic']
        }

        # Check for movement patterns in filename
        for movement, patterns in movement_patterns.items():
            for pattern in patterns:
                if pattern in clean_name:
                    logger.debug(f"Detected '{movement}' from pattern '{pattern}' in {filename}")
                    return movement

        return None

    def _generate_from_art_movement(self, filename: str, art_movement: str) -> Dict[str, Any]:
        """Generate SEO content based on detected art movement.

        Args:
            filename: Design filename
            art_movement: Detected art movement

        Returns:
            Generated SEO content
        """
        # Get keywords for this art movement
        movement_keywords = self.keyword_mappings["art_movement_keywords"].get(art_movement, [])

        # Extract design elements from filename
        clean_name = Path(filename).stem.lower()
        design_elements = self._extract_design_elements(clean_name)

        # Generate compelling title based on art movement and design elements
        title = self._create_art_movement_title(art_movement, design_elements, movement_keywords)

        # Generate tags
        tags = []

        # Add art movement keywords
        tags.extend(movement_keywords[:4])

        # Add design element tags
        if design_elements['colors']:
            tags.extend(design_elements['colors'][:2])
        if design_elements['style']:
            tags.extend(design_elements['style'][:2])

        # Add essential cat art tags
        essential_tags = ["cat art", "digital download", "wall art", "art print", "home decor"]
        for tag in essential_tags:
            if tag not in tags and len(tags) < 13:
                tags.append(tag)

        # Fill remaining slots with movement-specific tags
        filler_tags = ["printable art", "instant download", "digital file", "wall decor", "cat lover gift",
                      "modern art", "contemporary", "unique design", "artistic", "creative", "decorative", "stylish"]
        for tag in filler_tags:
            if tag not in tags and len(tags) < 13:
                tags.append(tag)
            if len(tags) >= 13:
                break

        # Ensure we have exactly 13 tags - add generic tags if needed
        while len(tags) < 13:
            generic_tags = ["artwork", "design", "print", "poster", "decor", "gift", "beautiful", "elegant"]
            added_any = False
            for tag in generic_tags:
                if tag not in tags:
                    tags.append(tag)
                    added_any = True
                    break
            if not added_any:  # Safety break if no more unique tags can be added
                break

        tags = tags[:13]  # Ensure exactly 13 tags

        # Generate compelling description
        description = self._create_art_movement_description(art_movement, design_elements)

        # Add template
        template_content = self._load_description_template()
        full_description = f"{description}\n\n{template_content}"

        return {
            'title': title,
            'tags': tags,
            'description': full_description,
            'price': 20,  # Default price for art movement detection
            'art_movement': art_movement,
            'design_elements': design_elements,
            'source': 'art_movement_detection'
        }

    def _extract_design_elements(self, clean_name: str) -> Dict[str, List[str]]:
        """Extract design elements from filename.

        Args:
            clean_name: Cleaned filename (lowercase, no extension)

        Returns:
            Dictionary with extracted design elements
        """
        # Common design element patterns
        color_patterns = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'gold', 'silver']
        style_patterns = ['vintage', 'modern', 'minimalist', 'ornate', 'simple', 'complex', 'detailed', 'abstract']
        subject_patterns = ['cat', 'kitten', 'feline', 'kitty', 'tabby', 'persian', 'siamese']

        elements = {
            'colors': [color for color in color_patterns if color in clean_name],
            'style': [style for style in style_patterns if style in clean_name],
            'subject': next((subject for subject in subject_patterns if subject in clean_name), 'cat')
        }

        return elements

    def _create_art_movement_title(self, art_movement: str, design_elements: Dict, movement_keywords: List[str]) -> str:
        """Create compelling title for art movement detection.

        Args:
            art_movement: Detected art movement
            design_elements: Extracted design elements
            movement_keywords: Keywords for the movement

        Returns:
            Compelling title optimized for sales
        """
        # Art movement to compelling descriptor mapping
        movement_descriptors = {
            'japanese': "Zen Japanese Style",
            'surreal': "Dreamy Surreal",
            'surrealism': "Dreamy Surreal",
            'pop': "Bold Pop Art",
            'pop_art': "Bold Pop Art",
            'renaissance': "Classic Renaissance",
            'impressionist': "Soft Impressionist",
            'impressionism': "Soft Impressionist",
            'cubism': "Geometric Cubist",
            'art_nouveau': "Elegant Art Nouveau",
            'minimalist': "Clean Minimalist",
            'vintage': "Charming Vintage",
            'gothic': "Dramatic Gothic"
        }

        # Get compelling descriptor
        style_desc = movement_descriptors.get(art_movement, art_movement.title())

        # Get subject with personality
        subject = design_elements.get('subject', 'cat')
        if subject == 'cat':
            subject = "Cat"
        else:
            subject = subject.title()

        # Get color if available
        colors = design_elements.get('colors', [])
        color_desc = colors[0].title() if colors else ""

        # Create compelling title templates
        if color_desc:
            title_templates = [
                f"{style_desc} {color_desc} {subject} Wall Art | Digital Download Print | Cat Lover Home Decor",
                f"{color_desc} {style_desc} {subject} Art Print | Digital Download | Instant Cat Wall Decor",
                f"Stunning {style_desc} {color_desc} {subject} Digital Art | Printable Wall Decor Download"
            ]
        else:
            title_templates = [
                f"{style_desc} {subject} Wall Art | Digital Download Print | Cat Lover Home Decor Gift",
                f"Beautiful {style_desc} {subject} Art Print | Digital Download | Instant Cat Wall Decor",
                f"Stunning {style_desc} {subject} Digital Art | Printable Wall Decor Download"
            ]

        # Choose the template that fits best within character limits
        for template in title_templates:
            if 120 <= len(template) <= 140:
                return template

        # Fallback: use first template and optimize length
        title = title_templates[0]
        return self._optimize_title(title)

    def _create_art_movement_description(self, art_movement: str, design_elements: Dict) -> str:
        """Create compelling description for art movement detection.

        Args:
            art_movement: Detected art movement
            design_elements: Extracted design elements

        Returns:
            Compelling description that sells
        """
        # Movement-specific compelling descriptions
        movement_descriptions = {
            'japanese': "🎋 Bring zen tranquility to your space with this beautiful Japanese-inspired cat art! The serene aesthetic and peaceful vibes make it perfect for creating a calming atmosphere.",
            'surreal': "✨ Step into a world of imagination with this dreamy surreal cat art! This whimsical piece sparks conversation and adds a touch of mystery to any room.",
            'surrealism': "✨ Step into a world of imagination with this dreamy surreal cat art! This whimsical piece sparks conversation and adds a touch of mystery to any room.",
            'pop': "🎨 Bold, bright, and absolutely irresistible! This pop art cat design brings instant energy and personality to your walls with its vibrant colors and modern style.",
            'pop_art': "🎨 Bold, bright, and absolutely irresistible! This pop art cat design brings instant energy and personality to your walls with its vibrant colors and modern style.",
            'renaissance': "🏛️ Timeless elegance meets feline charm in this classical Renaissance-inspired piece. Perfect for cat lovers who appreciate sophisticated, museum-quality art.",
            'impressionist': "🌸 Soft, dreamy, and utterly charming! This impressionist cat art captures the gentle beauty of the movement while celebrating our beloved feline friends.",
            'impressionism': "🌸 Soft, dreamy, and utterly charming! This impressionist cat art captures the gentle beauty of the movement while celebrating our beloved feline friends.",
            'vintage': "📻 Nostalgic charm meets cat cuteness in this delightful vintage-inspired design! Perfect for adding retro personality to any space.",
            'gothic': "🖤 Dramatic and mysterious, this gothic cat art brings sophisticated dark elegance to your decor. Perfect for those who love unique, statement pieces."
        }

        # Get movement-specific description or create generic one
        base_desc = movement_descriptions.get(art_movement,
            f"🎨 Stunning {art_movement.replace('_', ' ').title()} inspired cat art that brings sophisticated artistic style to any space!")

        # Add universal appeal
        universal_appeal = "\n\nWhether you're a devoted cat parent, art enthusiast, or someone who loves unique decor with personality, this piece delivers both style and charm. Perfect for living rooms, bedrooms, offices, or anywhere you want to showcase your love for cats with artistic flair!"

        return base_desc + universal_appeal

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
