"""Documentation standards and constants.

This module serves as the single source of truth for all documentation
standards used throughout the project.
"""

from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path

@dataclass(frozen=True)
class DocumentationStandards:
    """Single source of truth for documentation standards."""
    
    # File size limits (in lines)
    MAX_NEW_DOC_LINES: int = 500
    MAX_EXISTING_DOC_LINES: int = 2000
    WARN_DOC_LINES: int = 750
    
    # Required sections by document type
    REQUIRED_SECTIONS: Dict[str, List[str]] = {
        "adr": [
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
        ],
        "api": [
            "Description",
            "Parameters",
            "Returns",
            "Examples"
        ],
        "test": [
            "Purpose",
            "Test Cases",
            "Expected Results"
        ]
    }

    # Documentation file patterns
    DOC_PATTERNS: List[str] = [
        "*.md",
        "*.rst",
        "*.txt",
        "**/docs/**/*",
        "**/README*"
    ]

    # Required docstring sections
    REQUIRED_DOCSTRING_SECTIONS: List[str] = [
        "Args",
        "Returns",
        "Raises"
    ]

    # Style guidelines
    MAX_LINE_LENGTH: int = 80
    MIN_DOCSTRING_LENGTH: int = 10
    MAX_DOCSTRING_LENGTH: int = 1000

    # Validation rules
    HEADING_PATTERN: str = r"^#{1,6}\s+.+$"
    CODE_BLOCK_PATTERN: str = r"```[a-z]*\n[\s\S]*?\n```"
    LINK_PATTERN: str = r"\[([^\]]+)\]\(([^)]+)\)"

# Singleton instance
STANDARDS = DocumentationStandards()
