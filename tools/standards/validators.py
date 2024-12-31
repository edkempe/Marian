"""Documentation validation utilities.

This module provides functions for validating documentation against the
standards defined in constants.py. It combines validation logic from
the original doc_validator.py and test_process_quality.py.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .constants import STANDARDS

def is_new_doc(path: Path, cutoff_date: str = "2024-01-01") -> bool:
    """Check if document is new (created after cutoff)."""
    doc_date = datetime.fromtimestamp(path.stat().st_ctime)
    cutoff = datetime.strptime(cutoff_date, "%Y-%m-%d")
    return doc_date > cutoff

def get_doc_type(path: Path) -> str:
    """Get document type based on path."""
    if "adr" in path.parts:
        return "adr"
    elif "session_logs" in path.parts:
        return "session_logs"
    elif path.name == "README.md":
        return "readme"
    return "standard"

def get_max_lines(path: Path) -> int:
    """Get maximum lines allowed for document."""
    return (STANDARDS.MAX_NEW_DOC_LINES if is_new_doc(path) 
            else STANDARDS.MAX_EXISTING_DOC_LINES)

def validate_session_log(content: str) -> List[str]:
    """Validate session log format."""
    errors = []
    
    # Check required sections and subsections
    for section, subsections in STANDARDS.SESSION_LOG_SECTIONS.items():
        if section not in content:
            errors.append(f"[ERROR] Missing section: {section}")
        else:
            for subsection in subsections:
                if subsection not in content:
                    errors.append(f"[ERROR] Missing subsection: {subsection} in {section}")
    
    # Check timestamp format
    if not re.search(STANDARDS.PATTERNS["timestamp"], content):
        errors.append("[ERROR] Missing or invalid timestamps")
        
    return errors

def validate_doc(path: Path, strict: bool = False) -> List[str]:
    """Validate a document against standards."""
    errors = []
    content = path.read_text()
    lines = content.splitlines()
    doc_type = get_doc_type(path)
    max_lines = get_max_lines(path)
    
    # Check length
    if len(lines) > max_lines:
        if len(lines) > STANDARDS.MAX_EXISTING_DOC_LINES:
            errors.append(f"[ERROR] Exceeds maximum {STANDARDS.MAX_EXISTING_DOC_LINES} lines")
        elif is_new_doc(path) and len(lines) > STANDARDS.MAX_NEW_DOC_LINES:
            errors.append(f"[ERROR] New document exceeds {STANDARDS.MAX_NEW_DOC_LINES} lines")
        elif len(lines) > STANDARDS.WARN_DOC_LINES:
            errors.append(f"[WARN] Document approaching length limit ({len(lines)} lines)")
    
    # Check required sections
    if doc_type in STANDARDS.REQUIRED_SECTIONS:
        for section in STANDARDS.REQUIRED_SECTIONS[doc_type]:
            if section not in content:
                errors.append(f"[ERROR] Missing section: {section}")
    
    # Type-specific checks
    if doc_type == "session_logs":
        if not re.match(STANDARDS.PATTERNS["session_log"], path.name):
            errors.append("[ERROR] Invalid session log filename")
        errors.extend(validate_session_log(content))
    elif doc_type == "standard":
        if not re.search(STANDARDS.PATTERNS["version"], content):
            errors.append("[ERROR] Missing version number")
        if not re.search(STANDARDS.PATTERNS["status"], content):
            errors.append("[ERROR] Missing status")
    
    return errors

def validate_all(docs_dir: str = "docs", strict: bool = False) -> Dict[str, List[str]]:
    """Validate all documentation in directory."""
    issues = {}
    warnings = {}
    docs_path = Path(docs_dir)
    
    for doc in docs_path.rglob("*.md"):
        if errors := validate_doc(doc, strict):
            if any(e.startswith("[ERROR]") for e in errors):
                issues[str(doc)] = errors
            else:
                warnings[str(doc)] = errors
    
    # In strict mode, warnings are errors
    if strict:
        issues.update(warnings)
        
    return issues
