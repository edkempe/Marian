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
    
    # Required documentation files
    REQUIRED_DOCS: Dict[str, List[str]] = field(default_factory=lambda: {
        "Overview": ["Purpose", "Features"],
        "Installation": ["Requirements", "Setup"],
        "Usage": ["Basic", "Advanced"],
        "Development": ["Testing", "Contributing"],
        "py": [
            "Module docstring",
            "Class docstrings",
            "Function docstrings",
            "Type hints",
        ],
        "sql": [
            "File description",
            "Table descriptions",
            "Column descriptions",
            "Index descriptions",
        ],
        "js": [
            "File description",
            "Function descriptions",
            "Parameter descriptions",
            "Return value descriptions",
        ],
        "html": [
            "File description",
            "Component descriptions",
            "Template variables",
            "Dependencies",
        ],
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
    
    # Code documentation standards
    CODE_DOCUMENTATION: Dict[str, List[str]] = field(default_factory=lambda: {
        "classes": ["__init__", "methods", "attributes"],
        "functions": ["parameters", "returns", "raises", "examples"],
        "modules": ["description", "classes", "functions", "dependencies"],
        "tests": ["purpose", "setup", "assertions", "cleanup"]
    })

    def get_doc_type(self, path: Path) -> str:
        """Get the document type based on the file path.
        
        Args:
            path: Path to the document
            
        Returns:
            Document type (adr, readme, api, etc.)
        """
        filename = path.name.lower()
        ext = path.suffix.lower()
        
        if "adr" in filename:
            return "adr"
        elif filename == "readme.md":
            return "readme"
        elif "api" in filename:
            return "api"
        elif filename.startswith("test_"):
            return "test"
        elif "session" in filename and "log" in filename:
            return "session_log"
        elif ext == ".py":
            return "python"
        elif ext == ".sql":
            return "sql"
        elif ext == ".js":
            return "javascript"
        elif ext == ".html":
            return "html"
        else:
            return "unknown"

    def validate_code_doc(self, path: Path) -> List[str]:
        """Validate code documentation against standards.
        
        Args:
            path: Path to the code file
            
        Returns:
            List of validation errors, empty if valid
        """
        errors = []
        ext = path.suffix.lower()
        
        if ext == ".py":
            # Check Python docstrings
            with open(path, "r") as f:
                content = f.read()
            
            # Check module docstring
            if not re.match(r'""".*?"""', content, re.DOTALL):
                errors.append("Missing module docstring")
            
            # Check class docstrings
            classes = re.finditer(r"class\s+(\w+)\s*[:\(]", content)
            for class_match in classes:
                class_name = class_match.group(1)
                if not re.search(rf"class\s+{class_name}\s*[:\(].*?\s+\"\"\".*?\"\"\"", 
                               content[class_match.start():], re.DOTALL):
                    errors.append(f"Missing docstring for class {class_name}")
            
            # Check function docstrings
            functions = re.finditer(r"def\s+(\w+)\s*\(", content)
            for func_match in functions:
                func_name = func_match.group(1)
                if not re.search(rf"def\s+{func_name}\s*\(.*?\s+\"\"\".*?\"\"\"",
                               content[func_match.start():], re.DOTALL):
                    errors.append(f"Missing docstring for function {func_name}")
        
        return errors

    def validate_doc(self, path: Path) -> List[str]:
        """Validate a document against standards.
        
        Args:
            path: Path to the document
            doc_type: Type of document (adr, readme, api, etc.)
            
        Returns:
            List of validation errors, empty if valid
        """
        errors = []
        doc_type = self.get_doc_type(path)
        
        # Validate file extension
        if path.suffix.lower() not in [".md", ".rst", ".txt"]:
            errors.append(f"Invalid file extension: {path.suffix}")
        
        # Read document content
        try:
            content = path.read_text()
        except Exception as e:
            errors.append(f"Failed to read document: {e}")
            return errors
        
        # Check required sections
        if doc_type in self.REQUIRED_SECTIONS:
            for section in self.REQUIRED_SECTIONS[doc_type]:
                if not re.search(rf"^#+\s+{section}", content, re.MULTILINE | re.IGNORECASE):
                    errors.append(f"Missing required section: {section}")
        
        # Check section fields
        for section, fields in self.SECTION_FIELDS.items():
            section_match = re.search(rf"^#+\s+{section}(.*?)(?=^#+\s+|\Z)", 
                                   content, re.MULTILINE | re.DOTALL)
            if section_match:
                section_content = section_match.group(1)
                for field in fields:
                    if not re.search(rf"\b{field}\b", section_content, re.IGNORECASE):
                        errors.append(f"Missing field '{field}' in section '{section}'")
        
        return errors

# Singleton instance - THE source of truth
STANDARDS = DocumentationStandards()

# Export required sections and docs for backward compatibility
REQUIRED_SECTIONS = STANDARDS.REQUIRED_SECTIONS
SECTION_FIELDS = STANDARDS.SECTION_FIELDS
VALID_STATUSES = STANDARDS.VALID_STATUSES
FILE_PATTERNS = STANDARDS.FILE_PATTERNS
REQUIRED_DOCS = STANDARDS.REQUIRED_DOCS
CODE_DOCUMENTATION = STANDARDS.CODE_DOCUMENTATION
validate_doc = STANDARDS.validate_doc
get_doc_type = STANDARDS.get_doc_type
validate_code_doc = STANDARDS.validate_code_doc
