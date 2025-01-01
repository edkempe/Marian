"""Documentation standards for the Marian project.

This module is the SINGLE SOURCE OF TRUTH for all documentation standards.
Both tests and pre-commit hooks must use these standards.

Key Principles:
1. All standards are defined here
2. Case-insensitive validation
3. No external dependencies
4. Used by both tests and pre-commit hooks
"""

from dataclasses import dataclass, field
import re
from typing import Dict, List, Set
from pathlib import Path

@dataclass(frozen=True)
class DocumentationStandards:
    """Single source of truth for documentation standards."""
    
    # File size limits (in lines)
    MAX_NEW_DOC_LINES: int = 500
    MAX_EXISTING_DOC_LINES: int = 2000
    WARN_DOC_LINES: int = 750
    
    # Required sections by document type
    REQUIRED_SECTIONS: Dict[str, List[str]] = field(default_factory=lambda: {
        "adr": [
            "Revision History",
            "Status",
            "Context",
            "Decision",
            "Consequences"
        ],
        "readme": [
            "Revision History",
            "Overview",
            "Installation",
            "Usage",
            "Contributing"
        ],
        "api": [
            "Revision History",
            "Description",
            "Parameters",
            "Returns",
            "Examples"
        ],
        "test": [
            "Revision History",
            "Purpose",
            "Test Cases",
            "Expected Results",
            "Dependencies"
        ],
        "session_log": [
            "Session Summary",
            "Key Changes",
            "Next Steps",
            "Notes"
        ],
        "README": [
            "Overview",
            "Installation",
            "Usage",
            "Development",
            "Contributing",
        ],
        "API": [
            "Description",
            "Parameters",
            "Returns",
            "Raises",
            "Examples",
        ],
        "Module": [
            "Description",
            "Classes",
            "Functions",
            "Dependencies",
        ],
        "Class": [
            "Description",
            "Attributes",
            "Methods",
            "Examples",
        ],
        "Function": [
            "Description",
            "Parameters",
            "Returns",
            "Raises",
            "Examples",
        ],
    })
    
    # Required fields for each section
    SECTION_FIELDS: Dict[str, List[str]] = field(default_factory=lambda: {
        "Revision History": ["Date", "Author", "Changes"],
        "Status": ["Current Status", "Last Review Date"],
        "Context": ["Problem", "Requirements"],
        "Decision": ["Solution", "Implementation"],
        "Consequences": ["Benefits", "Drawbacks"],
        "Overview": ["Purpose", "Features"],
        "Installation": ["Requirements", "Steps"],
        "Usage": ["Examples", "Configuration"],
        "Contributing": ["Guidelines", "Process"],
        "Description": ["Purpose", "Features"],
        "Parameters": ["Name", "Type", "Description"],
        "Returns": ["Type", "Description"],
        "Raises": ["Exception", "Condition"],
        "Examples": ["Code", "Output"],
        "Test Cases": ["Input", "Expected Output"],
        "Dependencies": ["Name", "Version"],
    })
    
    # Valid statuses for documents
    VALID_STATUSES: Set[str] = field(default_factory=lambda: {
        "Draft",
        "Review",
        "Approved",
        "Deprecated",
        "Archived"
    })
    
    # File naming patterns
    FILE_PATTERNS: Dict[str, str] = field(default_factory=lambda: {
        "adr": r"^\d{4}-[a-z0-9-]+\.md$",
        "readme": r"^README\.md$",
        "api": r"^api-[a-z0-9-]+\.md$",
        "test": r"^test-[a-z0-9-]+\.md$",
        "session_log": r"^session-[a-z0-9-]+\.md$"
    })
    
    # Section order (for consistent formatting)
    SECTION_ORDER: Dict[str, List[str]] = field(default_factory=lambda: {
        "adr": [
            "Revision History",
            "Status",
            "Context",
            "Decision",
            "Consequences"
        ],
        "readme": [
            "Overview",
            "Installation",
            "Usage",
            "Contributing"
        ]
    })
    
    # Minimum content requirements
    MIN_SECTION_LENGTH: int = 50
    MAX_SECTION_LENGTH: int = 1000
    MIN_TOTAL_LENGTH: int = 200
    MAX_TOTAL_LENGTH: int = 5000
    
    # Documentation directories
    DOC_DIRS: Set[str] = field(default_factory=lambda: {
        "docs",
        "docs/adr",
        "docs/api",
        "docs/examples",
        "docs/guides",
        "docs/session_logs"
    })


# Singleton instance - THE source of truth
STANDARDS = DocumentationStandards()

# Export required sections and docs for backward compatibility
REQUIRED_SECTIONS = STANDARDS.REQUIRED_SECTIONS
SECTION_FIELDS = STANDARDS.SECTION_FIELDS
VALID_STATUSES = STANDARDS.VALID_STATUSES
FILE_PATTERNS = STANDARDS.FILE_PATTERNS
