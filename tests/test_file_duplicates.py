"""Tests to detect duplicate or similar files in the codebase."""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pytest

from shared_lib.constants import CACHE_DIR, TESTING_CONFIG
from shared_lib.file_constants import (
    ALLOWED_DUPLICATES,
    UNIQUE_CONTENT_FILES,
)
from shared_lib.path_util import get_project_root

# Directories to scan for duplicates
SCAN_DIRS = [
    "src",
    "models",
    "shared_lib",
    "services",
    "tools",
    "config",
    "scripts",
    "migrations",
    "alembic",
]

# Output file for rmlint results
RMLINT_OUTPUT = os.path.join(CACHE_DIR, "duplicates.json")

def find_duplicates(directory: str) -> Dict[str, List[str]]:
    """Find duplicate files using rmlint."""
    duplicates = {}
    
    # Build paths to scan
    scan_paths = [os.path.join(directory, d) for d in SCAN_DIRS if os.path.exists(os.path.join(directory, d))]
    if not scan_paths:
        return {}
        
    try:
        # Run rmlint with JSON output
        cmd = [
            "rmlint",
            "--types=duplicates",
            "--config=sh:handler=json",
            "--config=sh:write-json=" + RMLINT_OUTPUT,
            "--hidden",  # Include hidden files
            "--no-hardlinked",  # Don't consider hardlinks as duplicates
            "--no-followsymlinks",  # Don't follow symlinks
            "--no-crossdev",  # Don't cross device boundaries
            "--keep-hardlinked",  # Keep all hardlinked files
            "--merge-directories",  # Merge directories with same content
            "--progress",  # Show progress
            *scan_paths  # Add all paths to scan
        ]
        
        print(f"Running rmlint on {len(scan_paths)} directories...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error running rmlint: {result.stderr}")
            return {}
            
        # Read results
        if os.path.exists(RMLINT_OUTPUT):
            with open(RMLINT_OUTPUT, 'r') as f:
                data = json.load(f)
                
            # Process results
            for file_group in data.get('duplicates', []):
                if not file_group.get('is_original', False):  # Skip original files
                    continue
                    
                original = file_group.get('path')
                duplicate_paths = [d.get('path') for d in file_group.get('duplicate_paths', [])]
                
                if original and duplicate_paths:
                    # Filter out allowed duplicates
                    filtered_paths = [p for p in duplicate_paths 
                                   if os.path.basename(p) not in ALLOWED_DUPLICATES]
                    if filtered_paths:
                        duplicates[original] = filtered_paths
        
        return duplicates
        
    except FileNotFoundError:
        print("Error: rmlint not found. Please install rmlint first:")
        print("  brew install rmlint")
        return {}
    except Exception as e:
        print(f"Error while finding duplicates: {e}")
        return {}


@pytest.fixture(scope="session")
def check_rmlint():
    """Check if rmlint is installed."""
    try:
        subprocess.run(["rmlint", "--version"], capture_output=True)
    except FileNotFoundError:
        pytest.skip("rmlint not installed. Install with: brew install rmlint")


def test_no_duplicate_files(check_rmlint):
    """Test that there are no unwanted duplicate files in the codebase."""
    project_root = get_project_root()
    duplicates = find_duplicates(project_root)
    
    if duplicates:
        # Format duplicate information for error message
        duplicate_info = []
        for original, copies in duplicates.items():
            duplicate_info.append(f"\nOriginal: {original}")
            for copy in copies:
                duplicate_info.append(f"  Duplicate: {copy}")
        
        pytest.fail("Found duplicate files:\n" + "\n".join(duplicate_info))
