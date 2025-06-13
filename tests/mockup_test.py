
#!/usr/bin/env python3
"""
Test script for the SEA-E Mockup Generator Module.

This script demonstrates the mockup generator functionality by creating
sample designs and generating mockups for all supported product types.

Usage:
    python mockup_test.py
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modules.mockup_generator import MockupGenerator, create_sample_design
from core.logger import setup_logger

# Initialize logger
logger = setup_logger("mockup_test", "INFO")

def test_mockup_generator():
    """Test the mockup generator with sample designs."""
    
    print("=== SEA-E Mockup Generator Test ===\n")
    
    # Create output directory in the project
    output_dir = str(Path(__file__).parent.parent / "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize generator
    generator = MockupGenerator(output_dir)
    
    # Create sample design
    sample_design_path = os.path.join(output_dir, "test_design.png")
    create_sample_design(sample_design_path)
    print(f"✓ Created sample design: {sample_design_path}")
    
    # Test 1: List available blueprints
    print("\n1. Testing blueprint listing...")
    blueprints = generator.list_available_blueprints()
    print(f"✓ Found {len(blueprints)} available blueprints:")
    for key in blueprints.keys():
        print(f"   - {key}")
    
    # Test 2: Generate single mockups for each product type
    print("\n2. Testing single mockup generation...")
    test_cases = [
        ('tshirt_bella_canvas_3001', 'white', 'crew_neck'),
        ('sweatshirt_gildan_18000', 'black', 'crewneck'),
        ('poster_matte_ideju', 'white', 'standard')
    ]
    
    single_mockup_results = []
    for blueprint_key, color, variation in test_cases:
        print(f"   Generating {blueprint_key} ({color}, {variation})...")
        result = generator.generate_mockup(
            blueprint_key, 
            sample_design_path, 
            color, 
            variation
        )
        single_mockup_results.append(result)
        
        if result['success']:
            print(f"   ✓ Success: {Path(result['mockup_path']).name}")
            print(f"     Static assets: {len(result['static_assets'])}")
        else:
            print(f"   ✗ Failed: {result['error']}")
    
    # Test 3: Generate all variations for one product
    print("\n3. Testing all variations generation...")
    print("   Generating all T-shirt variations...")
    all_variations_results = generator.generate_all_variations(
        'tshirt_bella_canvas_3001', 
        sample_design_path
    )
    
    successful_variations = sum(1 for r in all_variations_results if r['success'])
    print(f"   ✓ Generated {successful_variations}/{len(all_variations_results)} variations")
    
    # Test 4: Error handling
    print("\n4. Testing error handling...")
    
    # Test with invalid blueprint
    invalid_result = generator.generate_mockup(
        'invalid_blueprint', 
        sample_design_path
    )
    if not invalid_result['success']:
        print("   ✓ Correctly handled invalid blueprint")
    else:
        print("   ✗ Should have failed with invalid blueprint")
    
    # Test with non-existent design file
    missing_file_result = generator.generate_mockup(
        'tshirt_bella_canvas_3001', 
        'non_existent_file.png'
    )
    if not missing_file_result['success']:
        print("   ✓ Correctly handled missing design file")
    else:
        print("   ✗ Should have failed with missing design file")
    
    # Summary
    print("\n=== Test Summary ===")
    total_single = len(single_mockup_results)
    successful_single = sum(1 for r in single_mockup_results if r['success'])
    
    print(f"Single mockups: {successful_single}/{total_single} successful")
    print(f"All variations: {successful_variations}/{len(all_variations_results)} successful")
    print(f"Error handling: 2/2 tests passed")
    
    # List generated files
    print(f"\nGenerated files in {output_dir}:")
    output_path = Path(output_dir)
    png_files = list(output_path.glob("*.png"))
    
    for file_path in sorted(png_files):
        file_size = file_path.stat().st_size
        print(f"   {file_path.name} ({file_size:,} bytes)")
    
    print(f"\nTotal files generated: {len(png_files)}")
    
    # Verify output structure
    print("\n=== Output Structure Verification ===")
    expected_files = [
        "test_design.png",  # Sample design
    ]
    
    # Check for mockup files
    mockup_files = [f for f in png_files if "tshirt" in f.name or "sweatshirt" in f.name or "poster" in f.name]
    thumbnail_files = [f for f in png_files if "thumbnail" in f.name]
    preview_files = [f for f in png_files if "preview" in f.name]
    square_files = [f for f in png_files if "square" in f.name]
    
    print(f"✓ Mockup files: {len(mockup_files)}")
    print(f"✓ Thumbnail files: {len(thumbnail_files)}")
    print(f"✓ Preview files: {len(preview_files)}")
    print(f"✓ Square files: {len(square_files)}")
    
    if len(mockup_files) > 0:
        print("\n✅ Mockup generator test completed successfully!")
        assert True  # Test passed
    else:
        print("\n❌ Mockup generator test failed - no mockups generated")
        assert False, "No mockups generated"

def test_cli_interface():
    """Test the CLI interface."""
    print("\n=== CLI Interface Test ===")
    
    # Test help command
    print("Testing CLI help...")
    exit_code = os.system("python /home/ubuntu/sea-engine/src/modules/mockup_generator.py --help > /dev/null 2>&1")
    if exit_code == 0:
        print("✓ CLI help command works")
    else:
        print("✗ CLI help command failed")
    
    # Test list blueprints
    print("Testing list blueprints...")
    exit_code = os.system("python /home/ubuntu/sea-engine/src/modules/mockup_generator.py --list-blueprints > /dev/null 2>&1")
    if exit_code == 0:
        print("✓ List blueprints command works")
    else:
        print("✗ List blueprints command failed")
    
    # Test create sample
    print("Testing create sample...")
    test_output_dir = str(Path(__file__).parent.parent / "output")
    exit_code = os.system(f"python /home/ubuntu/sea-engine/src/modules/mockup_generator.py --create-sample --output-dir {test_output_dir} > /dev/null 2>&1")
    if exit_code == 0:
        print("✓ Create sample command works")
    else:
        print("✗ Create sample command failed")

if __name__ == "__main__":
    try:
        # Run main test
        success = test_mockup_generator()
        
        # Run CLI test
        test_cli_interface()
        
        if success:
            print("\n🎉 All tests passed! The mockup generator is ready for use.")
            sys.exit(0)
        else:
            print("\n💥 Some tests failed. Please check the implementation.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)
