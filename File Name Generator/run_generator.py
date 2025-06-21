#!/usr/bin/env python3
"""
Simple runner for the Intelligent Filename Generator
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the filename generator."""
    print("🚀 Starting Intelligent Filename Generator...")
    print()
    
    # Change to the File Name Generator directory
    generator_dir = Path(__file__).parent
    
    try:
        # Run the generator
        result = subprocess.run([
            sys.executable, 
            "intelligent_filename_generator.py"
        ], cwd=generator_dir, check=True)
        
        print("\n✅ Filename generation completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Generator failed with exit code: {e.returncode}")
        return 1
    except Exception as e:
        print(f"\n❌ Error running generator: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
