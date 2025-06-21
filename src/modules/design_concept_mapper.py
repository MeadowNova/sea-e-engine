"""
Design Concept Mapper for Phase 4 Market-Validated SEO Engine.

This module provides mapping between design filenames and the 100 market-validated
design concepts with their proven SEO metadata, pricing, and targeting data.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class DesignConceptMapper:
    """Maps design filenames to market-validated concept metadata."""
    
    def __init__(self, concepts_file: str = "100_design_concepts.json"):
        """Initialize the design concept mapper.
        
        Args:
            concepts_file: Path to the 100 design concepts JSON file
        """
        self.concepts_file = Path(concepts_file)
        self.concepts = []
        self.id_to_concept = {}
        self.name_to_concept = {}
        
        self._load_design_concepts()
        logger.info(f"✅ Loaded {len(self.concepts)} design concepts for mapping")
    
    def _load_design_concepts(self):
        """Load and index the 100 design concepts."""
        try:
            if not self.concepts_file.exists():
                raise FileNotFoundError(f"Design concepts file not found: {self.concepts_file}")
            
            with open(self.concepts_file, 'r', encoding='utf-8') as f:
                self.concepts = json.load(f)
            
            # Create lookup indexes for fast mapping
            self.id_to_concept = {concept['id']: concept for concept in self.concepts}
            self.name_to_concept = {concept['name']: concept for concept in self.concepts}
            
            logger.info(f"📊 Indexed {len(self.concepts)} design concepts")
            logger.info(f"   ID index: {len(self.id_to_concept)} entries")
            logger.info(f"   Name index: {len(self.name_to_concept)} entries")
            
        except Exception as e:
            logger.error(f"❌ Failed to load design concepts: {e}")
            raise
    
    def get_concept_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get design concept by filename.
        
        Args:
            filename: Design filename (e.g., "september_032.jpg")
            
        Returns:
            Design concept dictionary or None if not found
        """
        # Extract concept ID from filename (remove extension)
        concept_id = Path(filename).stem
        
        concept = self.id_to_concept.get(concept_id)
        
        if concept:
            logger.debug(f"✅ Found concept for {filename}: {concept['name']}")
        else:
            logger.debug(f"⚠️ No concept found for filename: {filename}")
        
        return concept
    
    def get_concept_by_id(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """Get design concept by ID.
        
        Args:
            concept_id: Concept ID (e.g., "september_032")
            
        Returns:
            Design concept dictionary or None if not found
        """
        return self.id_to_concept.get(concept_id)
    
    def get_concept_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get design concept by name.
        
        Args:
            name: Concept name (e.g., "Harvest Surreal Cat #32")
            
        Returns:
            Design concept dictionary or None if not found
        """
        return self.name_to_concept.get(name)
    
    def get_seo_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Extract SEO data from concept for a filename.
        
        Args:
            filename: Design filename
            
        Returns:
            Dictionary with SEO data or None if concept not found
        """
        concept = self.get_concept_by_filename(filename)
        
        if not concept:
            return None
        
        return {
            'concept_id': concept['id'],
            'concept_name': concept['name'],
            'title': concept['seo_title'],
            'tags': concept['seo_tags'],
            'keywords': concept['seo_keywords'],
            'description_base': self._extract_description_from_title(concept['seo_title']),
            'price': concept['optimal_price'],
            'target_month': concept['target_month'],
            'primary_theme': concept['primary_theme'],
            'art_movement': concept['art_movement'],
            'cat_archetype': concept['cat_archetype'],
            'target_demographics': concept['target_demographics'],
            'predictive_scores': concept['predictive_scores'],
            'launch_date': concept['launch_date']
        }
    
    def _extract_description_from_title(self, title: str) -> str:
        """Generate description base from SEO title.
        
        Args:
            title: SEO title from concept
            
        Returns:
            Description base for further enhancement
        """
        # Extract key elements from title for description
        title_clean = title.replace('Cat Art Print', '').replace('Digital Download', '').strip()
        
        # Create engaging description base
        description = f"Transform your space with this stunning {title_clean.lower()} design. "
        description += "Perfect for cat lovers and art enthusiasts who appreciate unique, "
        description += "high-quality digital art that brings personality to any room."
        
        return description
    
    def get_concepts_by_month(self, month: str) -> List[Dict[str, Any]]:
        """Get all concepts for a specific target month.
        
        Args:
            month: Target month (e.g., "september", "october")
            
        Returns:
            List of concepts for the specified month
        """
        return [concept for concept in self.concepts if concept['target_month'] == month.lower()]
    
    def get_concepts_by_art_movement(self, movement: str) -> List[Dict[str, Any]]:
        """Get all concepts for a specific art movement.
        
        Args:
            movement: Art movement (e.g., "surrealism", "pop_art", "renaissance")
            
        Returns:
            List of concepts for the specified art movement
        """
        return [concept for concept in self.concepts if concept['art_movement'] == movement.lower()]
    
    def get_high_priority_concepts(self, min_score: float = 75.0) -> List[Dict[str, Any]]:
        """Get concepts with high overall scores.
        
        Args:
            min_score: Minimum overall score threshold
            
        Returns:
            List of high-priority concepts
        """
        return [
            concept for concept in self.concepts 
            if concept['predictive_scores']['overall_score'] >= min_score
        ]
    
    def validate_concept_coverage(self, filenames: List[str]) -> Dict[str, Any]:
        """Validate that filenames map to concepts and identify gaps.
        
        Args:
            filenames: List of design filenames to validate
            
        Returns:
            Validation report with mapped, unmapped, and missing concepts
        """
        mapped_concepts = []
        unmapped_files = []
        
        for filename in filenames:
            concept = self.get_concept_by_filename(filename)
            if concept:
                mapped_concepts.append(concept['id'])
            else:
                unmapped_files.append(filename)
        
        # Find concepts that don't have corresponding files
        all_concept_ids = set(self.id_to_concept.keys())
        mapped_concept_ids = set(mapped_concepts)
        missing_concepts = all_concept_ids - mapped_concept_ids
        
        return {
            'total_files': len(filenames),
            'mapped_files': len(mapped_concepts),
            'unmapped_files': unmapped_files,
            'missing_concepts': list(missing_concepts),
            'coverage_percentage': (len(mapped_concepts) / len(all_concept_ids)) * 100,
            'mapping_success_rate': (len(mapped_concepts) / len(filenames)) * 100 if filenames else 0
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded concepts.
        
        Returns:
            Dictionary with concept statistics
        """
        if not self.concepts:
            return {}
        
        # Count by month
        month_counts = {}
        for concept in self.concepts:
            month = concept['target_month']
            month_counts[month] = month_counts.get(month, 0) + 1
        
        # Count by art movement
        movement_counts = {}
        for concept in self.concepts:
            movement = concept['art_movement']
            movement_counts[movement] = movement_counts.get(movement, 0) + 1
        
        # Score statistics
        scores = [concept['predictive_scores']['overall_score'] for concept in self.concepts]
        
        return {
            'total_concepts': len(self.concepts),
            'month_distribution': month_counts,
            'art_movement_distribution': movement_counts,
            'score_stats': {
                'min_score': min(scores),
                'max_score': max(scores),
                'avg_score': sum(scores) / len(scores)
            },
            'price_range': {
                'min_price': min(concept['optimal_price'] for concept in self.concepts),
                'max_price': max(concept['optimal_price'] for concept in self.concepts)
            }
        }
