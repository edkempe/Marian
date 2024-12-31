"""Documentation standards and constants.

This module serves as the single source of truth for all documentation
standards used throughout the project. It combines standards from:
1. Previous shared_lib/doc_standards.py
2. Documentation sections in test_process_quality.py
3. Industry best practices
"""

from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path
import re
from datetime import datetime

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
        "session_logs": [
            "Session Overview",
            "Progress Log",
            "Next Steps",
            "Questions/Blockers"
        ],
        "standard": [
            "Quick Reference",
            "Version",
            "Status"
        ],
        "readme": [
            "Installation",
            "Usage",
            "API",
            "Contributing",
            "License"
        ]
    }
    
    # Session log sections with required subsections
    SESSION_LOG_SECTIONS: Dict[str, List[str]] = {
        "Session Overview": [
            "Start:",
            "Focus:"
        ],
        "Progress Log": [],  # Dynamic based on timestamps
        "Next Steps": [],    # Dynamic based on content
        "Questions/Blockers": []  # Dynamic based on content
    }
    
    # Patterns for validation
    PATTERNS: Dict[str, str] = {
        "session_log": r"session_log_\d{4}-\d{2}-\d{2}\.md$",
        "timestamp": r"\d{2}:\d{2}\s+MST",
        "version": r"\*\*Version:\*\*\s+\d+\.\d+\.\d+",
        "status": r"\*\*Status:\*\*\s+\w+",
        "backlog_item": r"^\d+\.\s+[^:]+:\s+.{1,50}$"
    }
    
    # Code documentation requirements
    CODE_DOCUMENTATION: Dict[str, str] = {
        "Module": "Module purpose and contents",
        "Class": "Class responsibility and usage",
        "Method": "Parameters, return values, and behavior",
        "Example": "Usage examples"
    }

# Singleton instance
STANDARDS = DocumentationStandards()
