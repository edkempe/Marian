"""Documentation standards validator."""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared_lib.doc_standards import (
    MAX_NEW_DOC_LINES,
    MAX_EXISTING_DOC_LINES,
    WARN_DOC_LINES,
    REQUIRED_SECTIONS,
    SESSION_LOG_PATTERN,
    TIMESTAMP_PATTERN,
    VERSION_PATTERN,
    STATUS_PATTERN,
    is_new_doc,
    get_doc_type,
    get_max_lines
)

class DocValidator:
    """Validates documentation against standards."""
    
    def __init__(self, docs_dir: str = "docs", strict: bool = False):
        self.docs_dir = Path(docs_dir)
        self.strict = strict  # Strict mode for CI, lenient for pre-commit
        
    def validate_all(self) -> Dict[str, List[str]]:
        """Validate all documentation."""
        issues = {}
        warnings = {}
        
        for doc in self.docs_dir.rglob("*.md"):
            doc_type = get_doc_type(doc)
            max_lines = get_max_lines(doc)
            
            if errors := self.validate_doc(doc, doc_type, max_lines):
                if any(e.startswith("[ERROR]") for e in errors):
                    issues[str(doc)] = errors
                else:
                    warnings[str(doc)] = errors
                    
        # In strict mode, warnings are errors
        if self.strict:
            issues.update(warnings)
            
        return issues
    
    def validate_doc(self, path: Path, doc_type: str, max_lines: int) -> List[str]:
        """Validate a document."""
        errors = []
        content = path.read_text()
        lines = content.splitlines()
        
        # Check length
        if len(lines) > max_lines:
            if len(lines) > MAX_EXISTING_DOC_LINES:
                errors.append(f"[ERROR] Exceeds maximum {MAX_EXISTING_DOC_LINES} lines")
            elif is_new_doc(path) and len(lines) > MAX_NEW_DOC_LINES:
                errors.append(f"[ERROR] New document exceeds {MAX_NEW_DOC_LINES} lines")
            elif len(lines) > WARN_DOC_LINES:
                errors.append(f"[WARN] Document approaching length limit ({len(lines)} lines)")
                
        # Check required sections
        for section in REQUIRED_SECTIONS[doc_type]:
            if section not in content:
                errors.append(f"[ERROR] Missing section: {section}")
                
        # Type-specific checks
        if doc_type == "session_logs":
            if not re.match(SESSION_LOG_PATTERN, path.name):
                errors.append("[ERROR] Invalid session log filename")
            if not re.search(TIMESTAMP_PATTERN, content):
                errors.append("[ERROR] Missing timestamped entries")
        elif doc_type == "standard":
            if not re.search(VERSION_PATTERN, content):
                errors.append("[ERROR] Missing version number")
            if not re.search(STATUS_PATTERN, content):
                errors.append("[ERROR] Missing status")
                
        return errors

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Strict validation mode")
    args = parser.parse_args()
    
    validator = DocValidator(strict=args.strict)
    issues = validator.validate_all()
    
    if issues:
        print("Documentation Issues Found:")
        for doc, errors in issues.items():
            print(f"\n{doc}:")
            for error in errors:
                print(f"  - {error}")
        exit(1 if args.strict else 0)  # Only fail in strict mode
    else:
        print("All documentation validates successfully!")
        exit(0)
