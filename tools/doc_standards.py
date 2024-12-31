"""Documentation standards for the Marian project.

This module is the SINGLE SOURCE OF TRUTH for all documentation standards.
Both tests and pre-commit hooks must use these standards.

Key Principles:
1. All standards are defined here
2. Case-insensitive validation
3. No external dependencies
4. Used by both tests and pre-commit hooks
"""

from dataclasses import dataclass
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
    REQUIRED_SECTIONS: Dict[str, List[str]] = {
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
            "Expected Results"
        ],
        "development": [
            "Revision History",
            "Overview",
            "Guidelines",
            "Examples"
        ],
        "deployment": [
            "Environment",
            "Configuration",
            "Procedure"
        ],
        "architecture": [
            "Overview",
            "Components",
            "Data Flow"
        ]
    }

    # Revision history validation
    REVISION_HEADER = r"^## Revision History\s*$"
    VERSION_LINE = r"^(\d+\.\d+\.\d+)\s+\((\d{4}-\d{2}-\d{2})\)\s+(@\w+)\s*$"
    CHANGE_LINE = r"^-\s+.+$"

    def validate_revision_history(self, content: str) -> List[str]:
        """Validate revision history format."""
        errors = []
        lines = content.split('\n')
        
        # Find revision history section
        revision_start = None
        for i, line in enumerate(lines):
            if re.match(self.REVISION_HEADER, line):
                revision_start = i
                break
        
        if revision_start is None:
            errors.append("Missing '## Revision History' section")
            return errors
        
        # Validate version entries
        i = revision_start + 1
        found_version = False
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Check for new section
            if line.startswith('##'):
                break
            
            # Validate version line
            version_match = re.match(self.VERSION_LINE, line)
            if version_match:
                found_version = True
                version, date, author = version_match.groups()
                
                # Validate semantic version
                if not self._validate_semver(version):
                    errors.append(f"Invalid semantic version: {version}")
                
                # Validate changes list
                changes_found = False
                i += 1
                while i < len(lines) and lines[i].strip():
                    if re.match(self.CHANGE_LINE, lines[i].strip()):
                        changes_found = True
                    elif not lines[i].strip():
                        break
                    else:
                        errors.append(
                            f"Invalid change format: {lines[i].strip()}"
                        )
                    i += 1
                
                if not changes_found:
                    errors.append(
                        f"No changes listed for version {version}"
                    )
            
            i += 1
        
        if not found_version:
            errors.append("No version entries found")
        
        return errors

    def _validate_semver(self, version: str) -> bool:
        """Validate semantic version format."""
        try:
            major, minor, patch = map(int, version.split('.'))
            return True
        except ValueError:
            return False

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

    # Required documentation files
    REQUIRED_DOCS: Set[str] = {
        "README.md",
        "CONTRIBUTING.md",
        "docs/development.md",
        "docs/deployment.md",
        "docs/testing.md",
        "docs/architecture.md"
    }

    # Style guidelines
    MAX_LINE_LENGTH: int = 80
    MIN_DOCSTRING_LENGTH: int = 10
    MAX_DOCSTRING_LENGTH: int = 1000

    # Validation rules
    HEADING_PATTERN: str = r"^#{1,6}\s+.+$"
    CODE_BLOCK_PATTERN: str = r"```[a-z]*\n[\s\S]*?\n```"
    LINK_PATTERN: str = r"\[([^\]]+)\]\(([^)]+)\)"

def validate_doc(path: Path, doc_type: str) -> List[str]:
    """Validate a document against standards.
    
    Args:
        path: Path to the document
        doc_type: Type of document (adr, readme, api, etc.)
        
    Returns:
        List of validation errors, empty if valid
    """
    errors = []
    content = path.read_text().lower()  # Case-insensitive validation
    
    standards = STANDARDS
    
    # Check required sections
    if doc_type in standards.REQUIRED_SECTIONS:
        for section in standards.REQUIRED_SECTIONS[doc_type]:
            if section.lower() not in content:
                errors.append(f"Missing required section: {section}")
    
    # Check line length
    lines = content.split("\n")
    if len(lines) > standards.MAX_EXISTING_DOC_LINES:
        errors.append(f"Document exceeds maximum length of {standards.MAX_EXISTING_DOC_LINES} lines")
    
    # Check revision history
    if doc_type in ["adr", "readme", "api", "test", "development"]:
        errors.extend(standards.validate_revision_history(content))
    
    return errors

# Singleton instance - THE source of truth
STANDARDS = DocumentationStandards()
