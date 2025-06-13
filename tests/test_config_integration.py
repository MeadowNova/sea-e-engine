
#!/usr/bin/env python3
"""
SEA-E Configuration Integration Tests
====================================

Tests to verify that the JSON configuration files integrate properly with
the mockup generator module and automation engine workflow.

This test suite validates:
1. JSON configuration file loading and parsing
2. Blueprint key consistency between configs and mockup generator
3. Required field validation
4. Data structure integrity
5. Integration with MockupGenerator class

Author: SEA-E Development Team
Version: 1.0.0
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from src.modules.mockup_generator import MockupGenerator
    MOCKUP_GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: MockupGenerator not available: {e}")
    MOCKUP_GENERATOR_AVAILABLE = False


class ConfigIntegrationTester:
    """Test suite for configuration file integration."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"
        self.product_config_path = self.config_dir / "product_blueprints.json"
        self.mockup_config_path = self.config_dir / "mockup_blueprints.json"
        
        self.product_config = None
        self.mockup_config = None
        self.test_results = []
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "PASS" if passed else "FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {message}")
    
    def test_config_files_exist(self) -> bool:
        """Test that configuration files exist."""
        product_exists = self.product_config_path.exists()
        mockup_exists = self.mockup_config_path.exists()
        
        self.log_test(
            "Config Files Exist",
            product_exists and mockup_exists,
            f"Product config: {product_exists}, Mockup config: {mockup_exists}"
        )
        
        return product_exists and mockup_exists
    
    def test_json_parsing(self) -> bool:
        """Test that JSON files can be parsed."""
        try:
            with open(self.product_config_path, 'r') as f:
                self.product_config = json.load(f)
            
            with open(self.mockup_config_path, 'r') as f:
                self.mockup_config = json.load(f)
            
            self.log_test("JSON Parsing", True, "Both config files parsed successfully")
            return True
            
        except json.JSONDecodeError as e:
            self.log_test("JSON Parsing", False, f"JSON parsing error: {e}")
            return False
        except Exception as e:
            self.log_test("JSON Parsing", False, f"Unexpected error: {e}")
            return False
    
    def test_required_structure(self) -> bool:
        """Test that required structure exists in config files."""
        if not self.product_config or not self.mockup_config:
            self.log_test("Required Structure", False, "Config files not loaded")
            return False
        
        # Test product config structure
        required_product_keys = ["products", "global_settings", "validation_schema"]
        product_structure_valid = all(key in self.product_config for key in required_product_keys)
        
        # Test mockup config structure
        required_mockup_keys = ["mockup_templates", "image_processing", "static_assets", "output_configuration"]
        mockup_structure_valid = all(key in self.mockup_config for key in required_mockup_keys)
        
        structure_valid = product_structure_valid and mockup_structure_valid
        
        self.log_test(
            "Required Structure",
            structure_valid,
            f"Product config: {product_structure_valid}, Mockup config: {mockup_structure_valid}"
        )
        
        return structure_valid
    
    def test_blueprint_key_consistency(self) -> bool:
        """Test that blueprint keys are consistent between configs."""
        if not self.product_config or not self.mockup_config:
            self.log_test("Blueprint Key Consistency", False, "Config files not loaded")
            return False
        
        product_keys = set(self.product_config["products"].keys())
        mockup_keys = set(self.mockup_config["mockup_templates"].keys())
        
        keys_match = product_keys == mockup_keys
        
        if keys_match:
            message = f"All {len(product_keys)} blueprint keys match"
        else:
            missing_in_mockup = product_keys - mockup_keys
            missing_in_product = mockup_keys - product_keys
            message = f"Mismatch - Missing in mockup: {missing_in_mockup}, Missing in product: {missing_in_product}"
        
        self.log_test("Blueprint Key Consistency", keys_match, message)
        return keys_match
    
    def test_product_config_validation(self) -> bool:
        """Test product configuration validation."""
        if not self.product_config:
            self.log_test("Product Config Validation", False, "Product config not loaded")
            return False
        
        validation_errors = []
        
        for blueprint_key, product in self.product_config["products"].items():
            # Check required sections
            required_sections = ["metadata", "printify_config", "available_options", "pricing"]
            for section in required_sections:
                if section not in product:
                    validation_errors.append(f"{blueprint_key}: Missing {section}")
            
            # Check Printify config
            if "printify_config" in product:
                printify_config = product["printify_config"]
                required_printify = ["blueprint_id", "print_provider_id"]
                for field in required_printify:
                    if field not in printify_config:
                        validation_errors.append(f"{blueprint_key}: Missing printify_config.{field}")
            
            # Check available options
            if "available_options" in product:
                options = product["available_options"]
                required_options = ["colors", "sizes", "variations"]
                for option in required_options:
                    if option not in options:
                        validation_errors.append(f"{blueprint_key}: Missing available_options.{option}")
        
        validation_passed = len(validation_errors) == 0
        message = f"Found {len(validation_errors)} validation errors" if validation_errors else "All validations passed"
        
        if validation_errors:
            print("Validation errors:")
            for error in validation_errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
        
        self.log_test("Product Config Validation", validation_passed, message)
        return validation_passed
    
    def test_mockup_config_validation(self) -> bool:
        """Test mockup configuration validation."""
        if not self.mockup_config:
            self.log_test("Mockup Config Validation", False, "Mockup config not loaded")
            return False
        
        validation_errors = []
        
        for blueprint_key, template in self.mockup_config["mockup_templates"].items():
            # Check required sections
            required_sections = ["template_config", "visual_settings", "color_mappings", "variation_modifications"]
            for section in required_sections:
                if section not in template:
                    validation_errors.append(f"{blueprint_key}: Missing {section}")
            
            # Check template config
            if "template_config" in template:
                template_config = template["template_config"]
                required_template = ["template_size", "design_area", "category"]
                for field in required_template:
                    if field not in template_config:
                        validation_errors.append(f"{blueprint_key}: Missing template_config.{field}")
            
            # Validate coordinate arrays
            if "template_config" in template and "design_area" in template["template_config"]:
                design_area = template["template_config"]["design_area"]
                if not isinstance(design_area, list) or len(design_area) != 4:
                    validation_errors.append(f"{blueprint_key}: Invalid design_area format")
        
        validation_passed = len(validation_errors) == 0
        message = f"Found {len(validation_errors)} validation errors" if validation_errors else "All validations passed"
        
        if validation_errors:
            print("Validation errors:")
            for error in validation_errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
        
        self.log_test("Mockup Config Validation", validation_passed, message)
        return validation_passed
    
    def test_mockup_generator_integration(self) -> bool:
        """Test integration with MockupGenerator class."""
        if not MOCKUP_GENERATOR_AVAILABLE:
            self.log_test("MockupGenerator Integration", False, "MockupGenerator not available")
            return False
        
        try:
            # Initialize MockupGenerator
            generator = MockupGenerator()
            
            # Get available blueprints from generator
            generator_blueprints = generator.list_available_blueprints()
            generator_keys = set(generator_blueprints.keys())
            
            # Get blueprint keys from our config
            config_keys = set(self.product_config["products"].keys()) if self.product_config else set()
            
            # Check if keys match
            keys_match = generator_keys == config_keys
            
            if keys_match:
                message = f"All {len(config_keys)} blueprint keys match between config and generator"
            else:
                missing_in_generator = config_keys - generator_keys
                missing_in_config = generator_keys - config_keys
                message = f"Mismatch - Missing in generator: {missing_in_generator}, Missing in config: {missing_in_config}"
            
            self.log_test("MockupGenerator Integration", keys_match, message)
            return keys_match
            
        except Exception as e:
            self.log_test("MockupGenerator Integration", False, f"Error: {e}")
            return False
    
    def test_data_consistency(self) -> bool:
        """Test data consistency between product and mockup configs."""
        if not self.product_config or not self.mockup_config:
            self.log_test("Data Consistency", False, "Config files not loaded")
            return False
        
        consistency_errors = []
        
        for blueprint_key in self.product_config["products"].keys():
            if blueprint_key not in self.mockup_config["mockup_templates"]:
                continue
            
            product = self.product_config["products"][blueprint_key]
            template = self.mockup_config["mockup_templates"][blueprint_key]
            
            # Check color consistency
            if "available_options" in product and "colors" in product["available_options"]:
                product_colors = set(product["available_options"]["colors"].keys())
                template_colors = set(template.get("color_mappings", {}).keys())
                
                if product_colors != template_colors:
                    consistency_errors.append(f"{blueprint_key}: Color mismatch - Product: {product_colors}, Template: {template_colors}")
            
            # Check variation consistency
            if "available_options" in product and "variations" in product["available_options"]:
                product_variations = set(product["available_options"]["variations"].keys())
                template_variations = set(template.get("variation_modifications", {}).keys())
                
                if product_variations != template_variations:
                    consistency_errors.append(f"{blueprint_key}: Variation mismatch - Product: {product_variations}, Template: {template_variations}")
        
        consistency_passed = len(consistency_errors) == 0
        message = f"Found {len(consistency_errors)} consistency errors" if consistency_errors else "All data consistent"
        
        if consistency_errors:
            print("Consistency errors:")
            for error in consistency_errors[:3]:  # Show first 3 errors
                print(f"  - {error}")
        
        self.log_test("Data Consistency", consistency_passed, message)
        return consistency_passed
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary."""
        print("=== SEA-E Configuration Integration Tests ===\n")
        
        # Run tests in order
        tests = [
            self.test_config_files_exist,
            self.test_json_parsing,
            self.test_required_structure,
            self.test_blueprint_key_consistency,
            self.test_product_config_validation,
            self.test_mockup_config_validation,
            self.test_data_consistency,
            self.test_mockup_generator_integration
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed_tests = total_tests - passed_tests
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "all_passed": failed_tests == 0,
            "results": self.test_results
        }
        
        print("=== Test Summary ===")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Overall Result: {'PASS' if summary['all_passed'] else 'FAIL'}")
        
        return summary


def main():
    """Main function to run the tests."""
    tester = ConfigIntegrationTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if summary["all_passed"] else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
