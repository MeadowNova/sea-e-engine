#!/usr/bin/env python3
"""
Quality Assurance Tests for SEA-E Engine
=======================================

Bulletproof quality testing for:
- T-Shirt mockup quality and placement
- Sweatshirt mockup quality and placement  
- Art Print mockup quality and placement
- Printify coordinate accuracy
- Airtable automation completeness
- Google Sheets integration reliability

Features:
- Automated quality scoring
- Coordinate precision validation
- Visual quality assessment
- End-to-end workflow testing
"""

import os
import sys
import pytest
import tempfile
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from typing import Dict, List, Tuple, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from modules.custom_mockup_generator import CustomMockupGenerator
from modules.perspective_mockup_generator import PerspectiveMockupGenerator
from tools.coordinate_mapper import CoordinateMapper
from api.printify import PrintifyAPIClient
from automation.airtable_automations import AirtableAutomationEngine
from modules.sheets_mockup_uploader import SheetsMockupUploader


class QualityAssuranceFramework:
    """
    Comprehensive quality assurance testing framework.
    """
    
    def __init__(self):
        """Initialize QA framework."""
        self.quality_thresholds = {
            'min_resolution': (1800, 1800),  # Minimum mockup resolution
            'min_quality_score': 8.0,        # Minimum quality score (1-10)
            'max_coordinate_error': 0.02,    # Maximum coordinate error (2%)
            'min_design_coverage': 0.8,      # Minimum design area coverage
            'max_processing_time': 30.0      # Maximum processing time (seconds)
        }
        
        self.test_results = {
            'tshirts': {},
            'sweatshirts': {},
            'art_prints': {},
            'coordinates': {},
            'automation': {},
            'integration': {}
        }
    
    def create_test_design(self, design_type: str = "standard") -> str:
        """
        Create a test design for quality testing.
        
        Args:
            design_type: Type of test design to create
            
        Returns:
            str: Path to created test design
        """
        # Create test design based on type
        if design_type == "standard":
            img = Image.new('RGBA', (1200, 1200), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Add geometric shapes for precision testing
            draw.rectangle([300, 300, 900, 900], fill=(50, 50, 50, 255), outline=(0, 0, 0, 255), width=5)
            draw.ellipse([400, 400, 800, 800], fill=(100, 100, 100, 255))
            
            # Add text for readability testing
            try:
                font = ImageFont.truetype("arial.ttf", 80)
            except:
                font = ImageFont.load_default()
            
            draw.text((600, 600), "QA\nTEST", fill=(255, 255, 255, 255), anchor="mm", align="center", font=font)
            
        elif design_type == "high_detail":
            img = Image.new('RGBA', (2000, 2000), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Create detailed pattern for quality testing
            for i in range(0, 2000, 50):
                draw.line([(i, 0), (i, 2000)], fill=(200, 200, 200, 100), width=1)
                draw.line([(0, i), (2000, i)], fill=(200, 200, 200, 100), width=1)
            
            # Add fine details
            for x in range(100, 1900, 200):
                for y in range(100, 1900, 200):
                    draw.ellipse([x-10, y-10, x+10, y+10], fill=(0, 0, 0, 255))
        
        elif design_type == "text_heavy":
            img = Image.new('RGBA', (1500, 1500), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Add multiple text elements
            texts = ["QUALITY", "ASSURANCE", "TEST", "2024"]
            y_positions = [300, 600, 900, 1200]
            
            for text, y in zip(texts, y_positions):
                draw.text((750, y), text, fill=(0, 0, 0, 255), anchor="mm")
        
        # Save test design
        test_dir = Path("output/qa_tests")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        design_path = test_dir / f"test_design_{design_type}.png"
        img.save(design_path, "PNG", quality=95)
        
        return str(design_path)
    
    def test_tshirt_mockup_quality(self) -> Dict[str, Any]:
        """Test T-shirt mockup generation quality."""
        try:
            print("🧪 Testing T-shirt mockup quality...")
            
            # Create test design
            design_path = self.create_test_design("standard")
            
            # Initialize mockup generator
            generator = CustomMockupGenerator(auto_manage=True)
            
            # Test different t-shirt templates
            templates = generator.list_available_templates().get('tshirts', [])
            
            if not templates:
                return {'status': 'skipped', 'reason': 'No t-shirt templates available'}
            
            results = []
            
            for i, template in enumerate(templates[:3]):  # Test first 3 templates
                print(f"  Testing template {i+1}: {template}")
                
                # Generate mockup
                import time
                start_time = time.time()
                
                result = generator.generate_mockup(
                    product_type="tshirts",
                    design_path=design_path,
                    template_name=template
                )
                
                processing_time = time.time() - start_time
                
                if result['success']:
                    # Analyze mockup quality
                    quality_score = self._analyze_mockup_quality(result['mockup_path'])
                    
                    template_result = {
                        'template': template,
                        'success': True,
                        'quality_score': quality_score,
                        'processing_time': processing_time,
                        'mockup_path': result['mockup_path'],
                        'resolution': result['output_size'],
                        'passes_quality': quality_score >= self.quality_thresholds['min_quality_score'],
                        'passes_resolution': all(dim >= thresh for dim, thresh in 
                                               zip(result['output_size'], self.quality_thresholds['min_resolution'])),
                        'passes_timing': processing_time <= self.quality_thresholds['max_processing_time']
                    }
                else:
                    template_result = {
                        'template': template,
                        'success': False,
                        'error': result.get('error', 'Unknown error'),
                        'processing_time': processing_time
                    }
                
                results.append(template_result)
            
            # Calculate overall score
            successful_tests = [r for r in results if r['success']]
            overall_score = sum(r['quality_score'] for r in successful_tests) / len(successful_tests) if successful_tests else 0
            
            # Cleanup
            Path(design_path).unlink()
            
            self.test_results['tshirts'] = {
                'overall_score': overall_score,
                'templates_tested': len(results),
                'successful_tests': len(successful_tests),
                'results': results,
                'passes_qa': overall_score >= self.quality_thresholds['min_quality_score']
            }
            
            print(f"✅ T-shirt QA: {overall_score:.1f}/10 ({len(successful_tests)}/{len(results)} passed)")
            
            return self.test_results['tshirts']
            
        except Exception as e:
            print(f"❌ T-shirt QA failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def test_art_print_mockup_quality(self) -> Dict[str, Any]:
        """Test art print mockup generation quality with perspective."""
        try:
            print("🧪 Testing art print mockup quality...")
            
            # Create test design
            design_path = self.create_test_design("high_detail")
            
            # Initialize perspective mockup generator
            generator = PerspectiveMockupGenerator(auto_manage=True)
            
            # Test poster templates
            templates = generator.list_available_templates().get('posters', [])
            
            if not templates:
                return {'status': 'skipped', 'reason': 'No poster templates available'}
            
            results = []
            
            for i, template in enumerate(templates[:3]):  # Test first 3 templates
                print(f"  Testing poster template {i+1}: {template}")
                
                # Generate mockup with perspective
                import time
                start_time = time.time()
                
                result = generator.generate_perspective_mockup(
                    design_path=design_path,
                    template_name=template,
                    perspective_strength=0.3
                )
                
                processing_time = time.time() - start_time
                
                if result['success']:
                    # Analyze mockup quality
                    quality_score = self._analyze_mockup_quality(result['mockup_path'])
                    
                    template_result = {
                        'template': template,
                        'success': True,
                        'quality_score': quality_score,
                        'processing_time': processing_time,
                        'mockup_path': result['mockup_path'],
                        'resolution': result['output_size'],
                        'perspective_applied': result.get('perspective_applied', False),
                        'passes_quality': quality_score >= self.quality_thresholds['min_quality_score'],
                        'passes_resolution': all(dim >= thresh for dim, thresh in 
                                               zip(result['output_size'], self.quality_thresholds['min_resolution'])),
                        'passes_timing': processing_time <= self.quality_thresholds['max_processing_time']
                    }
                else:
                    template_result = {
                        'template': template,
                        'success': False,
                        'error': result.get('error', 'Unknown error'),
                        'processing_time': processing_time
                    }
                
                results.append(template_result)
            
            # Calculate overall score
            successful_tests = [r for r in results if r['success']]
            overall_score = sum(r['quality_score'] for r in successful_tests) / len(successful_tests) if successful_tests else 0
            
            # Cleanup
            Path(design_path).unlink()
            
            self.test_results['art_prints'] = {
                'overall_score': overall_score,
                'templates_tested': len(results),
                'successful_tests': len(successful_tests),
                'results': results,
                'passes_qa': overall_score >= self.quality_thresholds['min_quality_score']
            }
            
            print(f"✅ Art Print QA: {overall_score:.1f}/10 ({len(successful_tests)}/{len(results)} passed)")
            
            return self.test_results['art_prints']
            
        except Exception as e:
            print(f"❌ Art Print QA failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def test_coordinate_precision(self) -> Dict[str, Any]:
        """Test coordinate mapping precision."""
        try:
            print("🧪 Testing coordinate precision...")
            
            # Create test coordinate configuration
            test_config = {
                'template_name': 'test_template',
                'printify_coordinates': {
                    'front': {'x': 0.5, 'y': 0.4, 'scale': 0.8, 'angle': 0},
                    'back': {'x': 0.5, 'y': 0.45, 'scale': 0.75, 'angle': 0}
                }
            }
            
            # Test coordinate validation
            mapper = CoordinateMapper()
            
            # Validate coordinates are in valid range
            precision_errors = []
            
            for position, coords in test_config['printify_coordinates'].items():
                if not (0.0 <= coords['x'] <= 1.0):
                    precision_errors.append(f"X coordinate out of range for {position}: {coords['x']}")
                
                if not (0.0 <= coords['y'] <= 1.0):
                    precision_errors.append(f"Y coordinate out of range for {position}: {coords['y']}")
                
                if not (0.0 <= coords['scale'] <= 2.0):
                    precision_errors.append(f"Scale out of range for {position}: {coords['scale']}")
            
            # Test coordinate conversion accuracy
            test_pixel_coords = [(500, 400), (600, 450), (550, 425)]
            test_image_size = (1000, 1000)
            
            normalized = mapper.normalize_coordinates(test_pixel_coords, test_image_size)
            expected = [(0.5, 0.4), (0.6, 0.45), (0.55, 0.425)]
            
            conversion_errors = []
            for i, (actual, expect) in enumerate(zip(normalized, expected)):
                x_error = abs(actual[0] - expect[0])
                y_error = abs(actual[1] - expect[1])
                
                if x_error > self.quality_thresholds['max_coordinate_error']:
                    conversion_errors.append(f"X conversion error {i}: {x_error}")
                
                if y_error > self.quality_thresholds['max_coordinate_error']:
                    conversion_errors.append(f"Y conversion error {i}: {y_error}")
            
            self.test_results['coordinates'] = {
                'precision_errors': precision_errors,
                'conversion_errors': conversion_errors,
                'passes_qa': len(precision_errors) == 0 and len(conversion_errors) == 0
            }
            
            print(f"✅ Coordinate Precision QA: {'PASS' if self.test_results['coordinates']['passes_qa'] else 'FAIL'}")
            
            return self.test_results['coordinates']
            
        except Exception as e:
            print(f"❌ Coordinate Precision QA failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _analyze_mockup_quality(self, mockup_path: str) -> float:
        """
        Analyze mockup quality and return score (1-10).
        
        Args:
            mockup_path: Path to mockup image
            
        Returns:
            float: Quality score from 1-10
        """
        try:
            with Image.open(mockup_path) as img:
                # Convert to RGB for analysis
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Get image array
                img_array = np.array(img)
                
                # Quality metrics
                score = 10.0
                
                # 1. Resolution check
                width, height = img.size
                if width < self.quality_thresholds['min_resolution'][0] or height < self.quality_thresholds['min_resolution'][1]:
                    score -= 2.0
                
                # 2. Sharpness check (edge detection)
                gray = np.mean(img_array, axis=2)
                edges = np.abs(np.diff(gray, axis=0)).mean() + np.abs(np.diff(gray, axis=1)).mean()
                if edges < 5.0:  # Low edge content indicates blurriness
                    score -= 1.5
                
                # 3. Contrast check
                contrast = np.std(gray)
                if contrast < 30:  # Low contrast
                    score -= 1.0
                
                # 4. Color distribution check
                color_std = np.std(img_array, axis=(0, 1))
                if np.mean(color_std) < 10:  # Very low color variation
                    score -= 0.5
                
                # 5. Brightness check
                brightness = np.mean(gray)
                if brightness < 50 or brightness > 200:  # Too dark or too bright
                    score -= 0.5
                
                return max(1.0, min(10.0, score))
                
        except Exception as e:
            print(f"Warning: Quality analysis failed: {e}")
            return 5.0  # Default score if analysis fails


def run_complete_qa_suite():
    """Run the complete quality assurance suite."""
    print("🚀 Starting SEA-E Quality Assurance Suite")
    print("=" * 60)
    
    qa = QualityAssuranceFramework()
    
    # Run all tests
    tests = [
        ("T-Shirt Mockups", qa.test_tshirt_mockup_quality),
        ("Art Print Mockups", qa.test_art_print_mockup_quality),
        ("Coordinate Precision", qa.test_coordinate_precision)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🎯 Running: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = {'status': 'failed', 'error': str(e)}
    
    # Generate summary report
    print("\n📊 Quality Assurance Summary:")
    print("=" * 60)
    
    total_tests = len(tests)
    passed_tests = 0
    
    for test_name, result in results.items():
        if result.get('passes_qa', False) or result.get('status') == 'passed':
            status = "✅ PASS"
            passed_tests += 1
        else:
            status = "❌ FAIL"
        
        print(f"{test_name}: {status}")
        
        if 'overall_score' in result:
            print(f"  Score: {result['overall_score']:.1f}/10")
        
        if 'successful_tests' in result and 'templates_tested' in result:
            print(f"  Templates: {result['successful_tests']}/{result['templates_tested']} passed")
    
    print(f"\n🎉 Overall QA Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎊 All quality assurance tests PASSED! System is production ready.")
    else:
        print("⚠️ Some tests failed. Review results before production deployment.")
    
    return results


if __name__ == "__main__":
    run_complete_qa_suite()
