"""Documentation validator for pre-commit hooks.

This module provides validation functions for documentation files,
using the standards defined in doc_standards.py.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from tools.doc_standards import STANDARDS, validate_doc
from typing import List

def validate_files(files: List[str]) -> int:
    """Validate documentation files.
    
    Args:
        files: List of files to validate
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    exit_code = 0
    
    for file in files:
        path = Path(file)
        if not path.exists():
            print(f"[ERROR] File not found: {file}")
            exit_code = 1
            continue
            
        # Skip non-documentation files
        if not any(path.match(pattern) for pattern in STANDARDS.FILE_PATTERNS):
            continue
            
        # Determine doc type
        doc_type = "standard"
        if path.name == "README.md":
            doc_type = "readme"
        elif path.parent.name == "adr":
            doc_type = "adr"
        elif path.name.endswith(".md"):
            base = path.stem.lower()
            if base in STANDARDS.REQUIRED_SECTIONS:
                doc_type = base
                
        # Validate
        errors = validate_doc(path, doc_type)
        if errors:
            print(f"\nValidation errors in {file}:")
            for error in errors:
                print(f"  - {error}")
            exit_code = 1
            
    return exit_code

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: doc_validator.py <file1> [file2 ...]")
        sys.exit(1)
        
    sys.exit(validate_files(sys.argv[1:]))
