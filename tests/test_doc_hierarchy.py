"""Test suite for documentation hierarchy and scope validation.

This module ensures that our documentation hierarchy is consistent:
1. Each document correctly identifies its role and status
2. Documents properly reference the authoritative sources
3. No conflicts in authority claims
4. Clear documentation hierarchy is maintained
"""

import os
import re
from typing import Dict, List, Set, Tuple
from pathlib import Path

# Documentation hierarchy
DOC_HIERARCHY = {
    'dev-checklist.md': {
        'role': 'Authoritative source for development session procedures',
        'status': 'Authoritative source for all development session procedures',
        'scope': ['development procedures', 'development session procedures'],
        'must_reference': []
    },
    'session_logs/README.md': {
        'role': 'Authoritative source for session log standards',
        'status': 'Authoritative source for session log standards and procedures',
        'scope': ['session log standards', 'session logging requirements'],
        'must_reference': ['dev-checklist.md']
    },
    'ai-guidelines.md': {
        'role': 'Supporting documentation for AI development procedures',
        'status': 'Supporting documentation for AI development procedures',
        'scope': ['AI development procedures', 'AI-specific guidelines'],
        'must_reference': ['dev-checklist.md', 'session_logs/README.md']
    },
    'session-workflow.md': {
        'role': 'Supporting documentation for development session procedures',
        'status': 'Supporting documentation for development session procedures',
        'scope': ['workflow examples', 'detailed workflow'],
        'must_reference': ['dev-checklist.md', 'session_logs/README.md']
    }
}

def extract_doc_metadata(file_path: str) -> Dict[str, str]:
    """Extract metadata from a documentation file.
    
    Looks for:
    - Status declaration
    - Role/scope statement
    - Authority claims
    - References to other documents
    
    Returns:
        Dict with metadata fields
    """
    metadata = {
        'status': None,
        'role': None,
        'scope': set(),
        'references': set()
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract status
        status_match = re.search(r'\*\*Status:\*\*\s*([^\n]+)', content)
        if status_match:
            metadata['status'] = status_match.group(1).strip()
        
        # Extract role/scope
        role_match = re.search(r'\*\*Documentation Role\*\*:?\s*([^\n]+)', content)
        if role_match:
            metadata['role'] = role_match.group(1).strip()
        
        # Extract references to other docs
        refs = re.findall(r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)', content)
        metadata['references'] = {ref[1] for ref in refs}
    except Exception as e:
        print(f"Warning: Error processing {file_path}: {e}")
    
    return metadata

def check_doc_hierarchy() -> Tuple[List[str], List[str], List[str]]:
    """Check documentation hierarchy for consistency.
    
    Returns:
        Tuple of:
        - List of incorrect status declarations
        - List of missing required references
        - List of authority conflicts
    """
    project_root = str(Path(__file__).parent.parent)
    status_issues = []
    reference_issues = []
    authority_issues = []
    
    for doc_path, expected in DOC_HIERARCHY.items():
        abs_path = os.path.join(project_root, 'docs', doc_path)
        if not os.path.exists(abs_path):
            print(f"Warning: Document not found: {abs_path}")
            continue
            
        metadata = extract_doc_metadata(abs_path)
        
        # Check status
        if metadata['status'] != expected['status']:
            status_issues.append(
                f"{doc_path}: Expected status '{expected['status']}', "
                f"found '{metadata['status']}'"
            )
        
        # Check required references
        missing_refs = set()
        for ref in expected['must_reference']:
            found = False
            for actual_ref in metadata['references']:
                if ref in actual_ref:  # More flexible matching
                    found = True
                    break
            if not found:
                missing_refs.add(ref)
        
        if missing_refs:
            reference_issues.append(
                f"{doc_path}: Missing references to {', '.join(missing_refs)}"
            )
        
        # Check for authority conflicts
        if metadata['role']:
            role = metadata['role'].lower()
            matches = [scope for scope in expected['scope'] if scope.lower() in role]
            if not matches:
                authority_issues.append(
                    f"{doc_path}: Role does not match expected scope. "
                    f"Expected one of: {', '.join(expected['scope'])}"
                )
    
    return status_issues, reference_issues, authority_issues

def main():
    """Run documentation hierarchy check and print results."""
    status_issues, reference_issues, authority_issues = check_doc_hierarchy()
    
    # Format error messages
    errors = []
    if status_issues:
        errors.append("Status Declaration Issues:\n" + "\n".join(f"- {issue}" for issue in status_issues))
    if reference_issues:
        errors.append("Missing References:\n" + "\n".join(f"- {issue}" for issue in reference_issues))
    if authority_issues:
        errors.append("Authority/Scope Issues:\n" + "\n".join(f"- {issue}" for issue in authority_issues))
    
    if errors:
        print("\nDocumentation Hierarchy Issues Found:\n")
        print("\n\n".join(errors))
        exit(1)
    else:
        print("\nDocumentation hierarchy is consistent!\n")
        exit(0)

if __name__ == '__main__':
    main()
