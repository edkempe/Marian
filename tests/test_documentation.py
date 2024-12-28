"""Test suite for documentation validation.

This module ensures that our documentation is consistent and complete:
1. All referenced documents and folders exist
2. All existing documents and folders are referenced somewhere
3. No broken links or references
"""

import os
import re
import pytest
from typing import Set, Dict, List, Tuple

def get_all_docs_and_folders() -> Tuple[Set[str], Set[str]]:
    """Get all documentation files and folders in the project.
    
    Returns:
        Tuple of (doc_paths, folder_paths) relative to project root
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    doc_paths = set()
    folder_paths = set()
    
    for root, dirs, files in os.walk(project_root):
        rel_root = os.path.relpath(root, project_root)
        if rel_root == '.':
            rel_root = ''
            
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') 
                  and d not in {'.git', '__pycache__', 'venv', 'env'}]
        
        # Add folder path
        if rel_root:
            folder_paths.add(rel_root)
        
        # Add documentation files
        for file in files:
            if file.lower().endswith(('.md', '.rst', '.txt')):
                doc_path = os.path.join(rel_root, file) if rel_root else file
                doc_paths.add(doc_path)
    
    return doc_paths, folder_paths

def extract_doc_references(file_path: str) -> Set[str]:
    """Extract references to other documents from a file.
    
    Looks for:
    - Markdown links: [text](path)
    - Direct path references: '/path/to/doc.md'
    - Include statements: {% include "path/to/doc" %}
    """
    references = set()
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find markdown links
    markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    references.update(ref for _, ref in markdown_links if not ref.startswith(('http', '#')))
    
    # Find quoted paths
    quoted_paths = re.findall(r'[\'"]([^\'"\s]+\.(md|rst|txt))[\'"]', content)
    references.update(path for path, _ in quoted_paths)
    
    # Find include statements
    includes = re.findall(r'{%\s*include\s*[\'"]([^\'"]+)[\'"]', content)
    references.update(includes)
    
    # Find direct path references
    path_refs = re.findall(r'(?<=[\'"\s])/[^\s\'"]+\.(md|rst|txt)', content)
    references.update(path_refs)
    
    return references

def get_all_doc_references() -> Dict[str, Set[str]]:
    """Get all document references from all documentation files.
    
    Returns:
        Dict mapping source files to sets of referenced paths
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    doc_paths, _ = get_all_docs_and_folders()
    
    references = {}
    for doc in doc_paths:
        abs_path = os.path.join(project_root, doc)
        try:
            refs = extract_doc_references(abs_path)
            if refs:
                references[doc] = refs
        except Exception as e:
            print(f"Warning: Error processing {doc}: {e}")
    
    return references

def normalize_path(base_path: str, ref_path: str) -> str:
    """Normalize a referenced path relative to the base path."""
    if ref_path.startswith('/'):
        return ref_path.lstrip('/')
    
    base_dir = os.path.dirname(base_path)
    return os.path.normpath(os.path.join(base_dir, ref_path))

def check_doc_references() -> Tuple[Dict[str, Set[str]], Set[str]]:
    """Check all documentation references.
    
    Returns:
        Tuple of (broken_refs, unreferenced_docs) where:
        - broken_refs: Dict mapping source docs to sets of broken references
        - unreferenced_docs: Set of existing docs that aren't referenced anywhere
    """
    existing_docs, existing_folders = get_all_docs_and_folders()
    all_references = get_all_doc_references()
    
    # Track broken and valid references
    broken_refs: Dict[str, Set[str]] = {}
    referenced_docs: Set[str] = set()
    
    # Check each reference
    for source, refs in all_references.items():
        invalid_refs = set()
        for ref in refs:
            normalized_ref = normalize_path(source, ref)
            if normalized_ref not in existing_docs:
                invalid_refs.add(ref)
            else:
                referenced_docs.add(normalized_ref)
        
        if invalid_refs:
            broken_refs[source] = invalid_refs
    
    # Find unreferenced docs (excluding README.md at root)
    unreferenced = existing_docs - referenced_docs - {'README.md'}
    
    return broken_refs, unreferenced

def print_documentation_report():
    """Generate documentation analysis report."""
    docs, folders = get_all_docs_and_folders()
    all_references = get_all_doc_references()
    broken_refs, unreferenced = check_doc_references()
    
    report_data = {
        'stats': {
            'doc_count': len(docs),
            'folder_count': len(folders),
            'ref_count': sum(len(refs) for refs in all_references.values())
        },
        'broken_refs': broken_refs,
        'unreferenced': unreferenced
    }
    
    from .reporting import ReportManager
    report_manager = ReportManager()
    report_manager.write_documentation_report(report_data)

def test_documentation_references():
    """Test that all documentation references are valid and all docs are referenced."""
    broken_refs, unreferenced = check_doc_references()
    
    # Format error messages
    errors = []
    
    if broken_refs:
        errors.append("\nBroken document references found:")
        for source, invalid_refs in broken_refs.items():
            errors.append(f"\nIn {source}:")
            for ref in sorted(invalid_refs):
                errors.append(f"  - {ref}")
    
    if unreferenced:
        errors.append("\nUnreferenced documentation files found:")
        for doc in sorted(unreferenced):
            errors.append(f"  - {doc}")
    
    if errors:
        errors.insert(0, "Documentation validation failed!")
        pytest.fail("\n".join(errors))

@pytest.fixture(scope="session", autouse=True)
def documentation_report():
    """Print documentation report after tests run."""
    yield
    print_documentation_report()

if __name__ == '__main__':
    pytest.main([__file__])