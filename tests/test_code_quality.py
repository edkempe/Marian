"""Test suite for code quality standards."""

import subprocess
from pathlib import Path
import pytest
import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Critical error types that should always fail the test
CRITICAL_ERRORS = {
    "E0001",  # Syntax error
    "E0100",  # __init__ method is a generator
    "E0101",  # Explicit return in __init__
    "E0104",  # Return outside function
    "E0105",  # Yield outside function
    "E0107",  # Use of nonexistent operator
    "E0213",  # Method has no argument
    "E0602",  # Undefined variable
    "E0702",  # Raising str (should raise Exception)
    "E0711",  # NotImplemented raised (should raise NotImplementedError)
    "E0712",  # Catching an exception which doesn't inherit from Exception
}

def run_pylint(paths: List[str]) -> Dict:
    """Run pylint on specified paths and return the results.
    
    Args:
        paths: List of paths to check
        
    Returns:
        Dict containing pylint output and score
    """
    project_root = Path(__file__).parent.parent
    
    try:
        # Run pylint with JSON reporter for structured output
        result = subprocess.run(
            [
                "poetry", "run", "pylint",
                "--output-format=json",
                *paths
            ],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        # Parse JSON output
        if result.stdout:
            messages = json.loads(result.stdout)
        else:
            messages = []
            
        return {
            "messages": messages,
            "return_code": result.returncode
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run pylint: {e}")
        return {
            "messages": [],
            "return_code": e.returncode
        }
    except Exception as e:
        logger.error(f"Error running pylint: {e}")
        raise

@pytest.mark.timeout(30)
def test_code_quality():
    """Verify code quality using Pylint.
    
    This test runs Pylint on our main code directories and fails if:
    1. There are any critical errors (syntax errors, undefined variables, etc.)
    2. There are more than 10 errors in any single file
    """
    # Directories to check
    paths = ["src", "tests", "models", "shared_lib"]
    
    # Run pylint
    result = run_pylint(paths)
    
    # Group messages by file
    files_with_errors = {}
    critical_errors = []
    
    if result["messages"]:
        for msg in result["messages"]:
            msg_id = msg.get("message-id", "").split(":", 1)[0]
            path = msg.get("path", "unknown")
            line = msg.get("line", "?")
            message = msg.get("message", "unknown")
            error_msg = f"{path}:{line} [{msg_id}] {message}"
            
            # Check for critical errors
            if msg_id in CRITICAL_ERRORS:
                critical_errors.append(error_msg)
            
            # Count errors per file
            if path not in files_with_errors:
                files_with_errors[path] = []
            files_with_errors[path].append(error_msg)
    
    # Files with too many errors
    problematic_files = {
        file: errors for file, errors in files_with_errors.items()
        if len(errors) > 10
    }
    
    # Assert quality standards
    assert not critical_errors, (
        "Critical code quality issues found:\n" + "\n".join(critical_errors)
    )
    
    assert not problematic_files, (
        "Files with excessive issues (>10 errors):\n" + 
        "\n".join(f"{file}:\n  " + "\n  ".join(errors) 
                 for file, errors in problematic_files.items())
    )
