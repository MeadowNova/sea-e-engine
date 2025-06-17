"""
OpenAI-based SEO Optimizer for Etsy listings.

This module provides an SEO optimization engine that uses OpenAI's API
to generate optimized titles, tags, and descriptions for Etsy listings
following the SEA-E automation guidelines.
"""

import os
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAISEOOptimizer:
    """SEO optimization engine using OpenAI API for Etsy listings."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """Initialize the SEO optimizer.

        Args:
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            model: OpenAI model to use for optimization
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")

        self.client = OpenAI(api_key=self.api_key)

        # Load Etsy listing guidelines
        self.system_prompt = self._load_etsy_guidelines()

        logger.info(f"Initialized OpenAI SEO Optimizer with model: {self.model}")

    def _load_etsy_guidelines(self) -> str:
        """Load Etsy listing guidelines from the user's proven guidelines."""
        try:
            # Load the user's specific listing guidelines
            guidelines_path = Path("docs/LISTING GUIDELINES.md")
            if guidelines_path.exists():
                with open(guidelines_path, 'r', encoding='utf-8') as f:
                    user_guidelines = f.read()

                # Create system prompt with user's guidelines
                system_prompt = f"""You are a world-class Etsy SEO copywriter specializing in digital art prints and wall art.

Follow these EXACT guidelines from the user's proven system:

{user_guidelines}

ADDITIONAL INSTRUCTIONS FOR DIGITAL DOWNLOADS:
- MUST include "Digital Download", "Digital Art Print", or "Digital Print" in title
- Write ONLY the intro paragraph for description (120-200 words) - this will be combined with a standard template
- Focus on the design's appeal and target audience in the description
- DO NOT include technical details about file formats, sizes, or printing - these are in the template

RESPONSE FORMAT:
Return your response in this exact format:

TITLE: [Your optimized title here]

TAGS: [tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10, tag11, tag12, tag13]

DESCRIPTION: [Your optimized intro description here - 120-200 words only]

Be creative and follow the guidelines above. Focus on making compelling, search-optimized content that converts browsers into buyers."""

                return system_prompt
            else:
                # Fallback to basic guidelines if file not found
                return self._get_fallback_guidelines()

        except Exception as e:
            logger.warning(f"Could not load listing guidelines: {e}")
            return self._get_fallback_guidelines()

    def _get_fallback_guidelines(self) -> str:
        """Fallback guidelines if file cannot be loaded."""
        return """You are a world-class Etsy SEO copywriter specializing in digital art prints and wall art.

Create compelling, search-optimized listings with:
- Titles: 120-140 characters with primary keywords first
- Tags: Exactly 13 tags, mix of broad and specific keywords
- Descriptions: Engaging copy with emotional triggers and clear use cases

RESPONSE FORMAT:
TITLE: [Your optimized title here]
TAGS: [tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10, tag11, tag12, tag13]
DESCRIPTION: [Your optimized description here]"""

    def _load_description_template(self) -> str:
        """Load the digital download description template."""
        template_path = Path(__file__).parent.parent.parent / "docs" / "DD Description Template.md"

        try:
            with open(template_path, 'r') as f:
                content = f.read()

            # Extract everything after the first line (which is the placeholder)
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

    def generate_seo_content(self, design_slug: str) -> Dict[str, Any]:
        """Generate SEO-optimized content for a design slug.

        This is the main method for Phase 2 digital download automation.

        Args:
            design_slug: Design slug extracted from filename (e.g., "floral_boho_cat")

        Returns:
            Dictionary containing:
            - title: SEO-optimized title (max 140 chars)
            - tags: List of 13 SEO tags (max 20 chars each)
            - description: SEO-optimized description (120-200 words)
        """
        logger.info(f"Generating SEO content for design slug: {design_slug}")

        try:
            # Create user prompt based on design slug
            user_prompt = f"""
Generate SEO content for an Etsy digital art print with design slug: "{design_slug}"

Design context: {self._extract_design_context(design_slug)}

Please provide EXACTLY in this format:

Title: [Your SEO-optimized title here, max 140 characters]

Tags: [tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10, tag11, tag12, tag13]

Description: [Your 120-200 word INTRO description here - this will be combined with a standard template]

Requirements:
- Title: Keyword-front-loaded, include "Art Print" or "Digital Download"
- Tags: Exactly 13 tags, max 20 characters each, comma-separated
- Description: ONLY write the intro paragraph (120-200 words). Focus on the design's appeal, target audience, and emotional triggers. Do NOT include technical details about file formats, sizes, or printing instructions - these will be added automatically from a template.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # Increased creativity
                max_tokens=1500   # More space for creative content
            )

            content = response.choices[0].message.content
            parsed_content = self._parse_seo_response_simple(content)

            # Combine the OpenAI intro description with the template
            intro_description = parsed_content['description']
            template_content = self._load_description_template()

            # Create the full description
            full_description = f"{intro_description}\n\n{template_content}"
            parsed_content['description'] = full_description

            logger.info(f"Successfully generated SEO content for: {design_slug}")
            logger.info(f"Combined intro ({len(intro_description)} chars) with template ({len(template_content)} chars)")
            return parsed_content

        except Exception as e:
            logger.error(f"Failed to generate SEO content for {design_slug}: {str(e)}")
            raise

    def _extract_design_context(self, design_slug: str) -> str:
        """Extract rich context from descriptive design slug for better SEO generation."""
        # Handle both underscore and space separators
        clean_slug = design_slug.replace('_', ' ').replace('-', ' ').lower()
        words = clean_slug.split()

        # Expanded categories for better detection
        subjects = [
            'cat', 'dog', 'bird', 'flower', 'tree', 'coffee', 'book', 'barista',
            'kitten', 'feline', 'pet', 'animal', 'plant', 'nature', 'cafe'
        ]

        styles = [
            'boho', 'vintage', 'modern', 'abstract', 'minimalist', 'renaissance',
            'cubist', 'geometric', 'japanese', 'floral', 'artistic', 'contemporary',
            'retro', 'classic', 'bohemian', 'eclectic'
        ]

        themes = [
            'floral', 'geometric', 'nature', 'cosmic', 'literary', 'botanical',
            'shower', 'bathroom', 'kitchen', 'home', 'lifestyle', 'cute', 'funny',
            'lover', 'enthusiast', 'zen', 'peaceful', 'cozy', 'warm'
        ]

        colors = [
            'black', 'white', 'blue', 'red', 'green', 'yellow', 'pink', 'purple',
            'orange', 'brown', 'gray', 'grey', 'gold', 'silver', 'rainbow'
        ]

        # Detect elements
        detected_subjects = [word for word in words if word in subjects]
        detected_styles = [word for word in words if word in styles]
        detected_themes = [word for word in words if word in themes]
        detected_colors = [word for word in words if word in colors]

        # Build rich context description
        context_parts = []

        if detected_subjects:
            context_parts.append(f"Subject: {', '.join(detected_subjects)}")

        if detected_styles:
            context_parts.append(f"Style: {', '.join(detected_styles)}")

        if detected_themes:
            context_parts.append(f"Theme: {', '.join(detected_themes)}")

        if detected_colors:
            context_parts.append(f"Colors: {', '.join(detected_colors)}")

        # Add the full descriptive slug for additional context
        context_parts.append(f"Full description: {clean_slug}")

        # Target audience inference
        if any(word in clean_slug for word in ['cat', 'kitten', 'feline']):
            context_parts.append("Target: Cat lovers, pet owners")
        if any(word in clean_slug for word in ['coffee', 'barista', 'cafe']):
            context_parts.append("Target: Coffee enthusiasts, cafe lovers")
        if any(word in clean_slug for word in ['japanese', 'zen', 'floral']):
            context_parts.append("Target: Art lovers, home decorators")

        return '; '.join(context_parts)

    def _parse_seo_response_simple(self, content: str) -> Dict[str, Any]:
        """Simple parsing that lets OpenAI be more creative."""
        logger.debug(f"Parsing OpenAI response: {content[:200]}...")

        title = ""
        tags = []
        description = ""

        # Simple pattern matching - less restrictive
        lines = content.strip().split('\n')

        for i, line in enumerate(lines):
            line = line.strip().replace('**', '').replace('*', '')

            if line.lower().startswith('title:'):
                title = line.split(':', 1)[1].strip()
            elif line.lower().startswith('tags:'):
                tag_text = line.split(':', 1)[1].strip()
                tags = [tag.strip() for tag in tag_text.split(',') if tag.strip()]
            elif line.lower().startswith('description:'):
                # Get description from this line and potentially following lines
                desc_parts = [line.split(':', 1)[1].strip()]
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line and not any(next_line.lower().startswith(prefix) for prefix in ['title:', 'tags:', 'description:']):
                        desc_parts.append(next_line)
                    else:
                        break
                description = ' '.join(desc_parts).strip()
                break

        # Basic validation and cleanup
        if not title:
            title = "Digital Art Print | Wall Art | Home Decor"
        if not tags:
            tags = ["art print", "digital download", "wall art"]
        if not description:
            description = "Beautiful digital art print perfect for your home decor."

        # Ensure we have exactly 13 tags
        while len(tags) < 13:
            default_tags = ["art print", "digital download", "wall art", "home decor", "printable art",
                          "instant download", "digital print", "poster", "artwork", "gift", "decor", "modern", "design"]
            for tag in default_tags:
                if tag not in tags and len(tags) < 13:
                    tags.append(tag)

        tags = tags[:13]  # Limit to 13

        logger.info(f"Parsed SEO content - Title: {len(title)} chars, Tags: {len(tags)}, Description: {len(description)} chars")

        return {
            'title': title,
            'tags': tags,
            'description': description
        }

    def _parse_seo_response(self, content: str) -> Dict[str, Any]:
        """Parse OpenAI response into structured SEO data."""
        logger.debug(f"Parsing OpenAI response: {content[:200]}...")

        # Try to extract structured data from the response
        title = ""
        tags = []
        description = ""

        # Look for common patterns in the response
        lines = content.strip().split('\n')

        # Method 1: Look for structured format with labels
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Remove markdown formatting
            line = line.replace('**', '').replace('*', '')

            # Look for title (be more specific to avoid false matches)
            if line.lower().startswith('title:') or (line.lower().startswith('1.') and 'title' in line.lower()):
                if ':' in line:
                    title = line.split(':', 1)[1].strip()
                elif '-' in line:
                    title = line.split('-', 1)[1].strip()
                else:
                    # Look at next line
                    if i + 1 < len(lines):
                        title = lines[i + 1].strip().replace('**', '').replace('*', '')

            # Look for tags (be more specific)
            elif line.lower().startswith('tags:') or (line.lower().startswith('2.') and 'tags' in line.lower()):
                if ':' in line:
                    tag_text = line.split(':', 1)[1].strip()
                    tags = [tag.strip().strip('"').replace('**', '').replace('*', '') for tag in tag_text.split(',')]
                elif '-' in line:
                    tag_text = line.split('-', 1)[1].strip()
                    tags = [tag.strip().strip('"').replace('**', '').replace('*', '') for tag in tag_text.split(',')]
                else:
                    # Look at next line
                    if i + 1 < len(lines):
                        tag_text = lines[i + 1].strip().replace('**', '').replace('*', '')
                        tags = [tag.strip().strip('"') for tag in tag_text.split(',')]

            # Look for description (be more specific)
            elif line.lower().startswith('description:') or (line.lower().startswith('3.') and 'description' in line.lower()):
                if ':' in line:
                    description = line.split(':', 1)[1].strip().replace('**', '').replace('*', '')
                elif '-' in line:
                    description = line.split('-', 1)[1].strip().replace('**', '').replace('*', '')
                else:
                    # Collect remaining lines as description
                    desc_lines = []
                    for j in range(i + 1, len(lines)):
                        desc_line = lines[j].strip().replace('**', '').replace('*', '')
                        if desc_line and not any(keyword in desc_line.lower() for keyword in ['title:', 'tags:', 'description:']):
                            desc_lines.append(desc_line)
                    description = ' '.join(desc_lines)
                    break

        # Method 2: If structured parsing failed, try to extract from unstructured text
        if not title or not tags or not description:
            logger.warning("Structured parsing failed, trying fallback method")

            # Clean the entire content
            clean_content = content.replace('**', '').replace('*', '').strip()

            # Split into sentences and look for patterns
            sentences = [s.strip() for s in clean_content.split('.') if s.strip()]

            # Use first meaningful sentence as title if not found
            if not title and sentences:
                title = sentences[0][:140]

            # Generate fallback tags if not found
            if not tags:
                design_words = self._extract_design_context(title or "art print").split()
                tags = ["art print", "digital download", "wall art"] + design_words[:10]

            # Use remaining content as description if not found
            if not description:
                description = clean_content[:500] if clean_content else "Beautiful digital art print perfect for your home decor."

        # Clean and validate title
        title = title.strip() if title else "Digital Art Print"

        # Clean title of problematic characters for Etsy
        title = title.replace('\n', ' ').replace('\r', ' ')

        # Remove any "Title:" prefix that might be included
        if title.lower().startswith('title:'):
            title = title[6:].strip()

        # Remove any "Tags:" or other content that got mixed in
        if 'tags:' in title.lower():
            title = title.split('tags:')[0].strip()
        if 'description:' in title.lower():
            title = title.split('description:')[0].strip()

        # Remove multiple colons (Etsy allows only one)
        while '::' in title:
            title = title.replace('::', ':')
        # Remove leading/trailing colons
        title = title.strip(':').strip()

        # Ensure title has required digital download keywords
        digital_keywords = ["digital download", "digital art print", "digital print"]
        has_digital_keyword = any(keyword in title.lower() for keyword in digital_keywords)

        if not has_digital_keyword:
            # Add "Digital Download" if missing
            if len(title) < 125:  # Room to add
                title = title + " | Digital Download"
            else:
                # Replace last part with digital download
                title = title[:125] + " | Digital Download"

        # Ensure minimum 120 characters
        if len(title) < 120:
            # Add descriptive keywords to reach minimum length
            extensions = [
                " | Instant Download",
                " | Printable Wall Art",
                " | Home Decor Gift",
                " | Digital File",
                " | Art Print Poster"
            ]

            for ext in extensions:
                if len(title) + len(ext) <= 140:
                    title += ext
                    if len(title) >= 120:
                        break

        # Final length check
        title = title[:140]

        tags = [tag.strip()[:20] for tag in tags if tag.strip()][:13]
        if len(tags) < 13:
            # Pad with default tags
            default_tags = ["art print", "digital download", "wall art", "home decor", "printable art",
                          "instant download", "digital print", "poster", "artwork", "gift", "decor", "modern", "design"]
            for default_tag in default_tags:
                if len(tags) >= 13:
                    break
                if default_tag not in tags:
                    tags.append(default_tag)

        description = description.strip() if description else "Beautiful digital art print perfect for your home decor."

        logger.info(f"Parsed SEO content - Title: {len(title)} chars, Tags: {len(tags)}, Description: {len(description)} chars")

        return {
            'title': title,
            'tags': tags,
            'description': description
        }

    def optimize_title_only(self, design_slug: str) -> str:
        """Generate optimized title for a design slug.

        Args:
            design_slug: Design slug from filename

        Returns:
            Optimized title (max 140 chars)
        """
        seo_content = self.generate_seo_content(design_slug)
        return seo_content['title']

    def optimize_tags_only(self, design_slug: str) -> List[str]:
        """Generate optimized tags for a design slug.

        Args:
            design_slug: Design slug from filename

        Returns:
            List of 13 optimized tags (max 20 chars each)
        """
        seo_content = self.generate_seo_content(design_slug)
        return seo_content['tags']

    def optimize_description_only(self, design_slug: str) -> str:
        """Generate optimized description for a design slug.

        Args:
            design_slug: Design slug from filename

        Returns:
            Optimized description (120-200 words)
        """
        seo_content = self.generate_seo_content(design_slug)
        return seo_content['description']

    def batch_generate_seo(self, design_slugs: List[str]) -> List[Dict[str, Any]]:
        """Generate SEO content for multiple design slugs in batch.

        Args:
            design_slugs: List of design slugs from filenames

        Returns:
            List of SEO content dictionaries
        """
        logger.info(f"Starting batch SEO generation for {len(design_slugs)} designs")

        seo_results = []
        for i, slug in enumerate(design_slugs):
            logger.info(f"Processing design {i+1}/{len(design_slugs)}: {slug}")
            try:
                seo_content = self.generate_seo_content(slug)
                seo_content['design_slug'] = slug
                seo_results.append(seo_content)
            except Exception as e:
                logger.error(f"Failed to generate SEO for design {slug}: {str(e)}")
                # Add fallback content if generation fails
                fallback_content = {
                    'design_slug': slug,
                    'title': f"{slug.replace('_', ' ').title()} Art Print | Digital Download | Wall Art",
                    'tags': ["art print", "digital download", "wall art", "home decor", "printable art"],
                    'description': f"Beautiful {slug.replace('_', ' ')} art print perfect for your home decor. Instant digital download.",
                    'error': str(e)
                }
                seo_results.append(fallback_content)

        logger.info(f"Batch SEO generation completed. Processed {len(seo_results)} designs")
        return seo_results

    def validate_seo_content(self, seo_content: Dict[str, Any]) -> Dict[str, bool]:
        """Validate SEO content against Etsy requirements.

        Args:
            seo_content: SEO content dictionary

        Returns:
            Dictionary with validation results
        """
        title = seo_content.get('title', '')
        digital_keywords = ["digital download", "digital art print", "digital print"]
        has_digital_keyword = any(keyword in title.lower() for keyword in digital_keywords)

        validation = {
            'title_length_valid': 120 <= len(title) <= 140,
            'title_not_empty': bool(title.strip()),
            'title_has_digital_keyword': has_digital_keyword,
            'tags_count_valid': len(seo_content.get('tags', [])) == 13,
            'tags_length_valid': all(len(tag) <= 20 for tag in seo_content.get('tags', [])),
            'description_not_empty': bool(seo_content.get('description', '').strip()),
            'description_length_valid': len(seo_content.get('description', '')) >= 120  # No upper limit for full template
        }

        validation['all_valid'] = all(validation.values())
        return validation

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics.

        Returns:
            Dictionary with optimization statistics
        """
        return {
            "api_provider": "OpenAI",
            "model": self.model,
            "status": "active",
            "guidelines_version": "SEA-E Phase 2",
            "supported_formats": ["design_slug"]
        }
