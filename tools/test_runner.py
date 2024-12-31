"""Test runner tool for the project.

This tool handles test execution with proper environment setup,
avoiding conflicts with the main application configuration.
"""

import os
import sys
from pathlib import Path
import pytest
from typing import List, Optional
from config.test_settings import test_settings

def run_tests(test_paths: List[str], verbose: bool = True) -> int:
    """Run tests with proper environment setup.
    
    Args:
        test_paths: List of test paths to run
        verbose: Whether to show verbose output
    
    Returns:
        int: Exit code (0 for success)
    """
    # Add project root to Python path
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Set test environment variables
    os.environ.update({
        "ENV": test_settings.ENV,
        "DEBUG": str(test_settings.DEBUG).lower(),
        "DATABASE_URL": test_settings.DATABASE_URL,
        "API_KEY": test_settings.API_KEY,
        "TEST_MODE": str(test_settings.TEST_MODE).lower()
    })
    
    # Build pytest arguments
    args = []
    if verbose:
        args.append("-v")
    args.extend(test_paths)
    
    # Run tests
    return pytest.main(args)

if __name__ == "__main__":
    # Get test paths from command line
    test_paths = sys.argv[1:] if len(sys.argv) > 1 else ["tests"]
    
    # Run tests
    exit_code = run_tests(test_paths)
    sys.exit(exit_code)
