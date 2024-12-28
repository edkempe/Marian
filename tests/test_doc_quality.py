"""Tests for documentation quality and standards."""

import os
import re
from typing import Dict, List, Optional, Tuple
import pytest
import markdown
import jinja2
from shared_lib.constants import TESTING_CONFIG

# Key documents that must have versioning
REQUIRED_VERSIONING = TESTING_CONFIG['REQUIRED_VERSIONING']

# Directories to exclude from documentation checks
EXCLUDED_DIRS = TESTING_CONFIG['EXCLUDED_DIRS']

# Location for test reports
REPORTS_DIR = os.path.join('reports', 'testing')

# HTML template for reports
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
        }
        h1, h2 { 
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 0.3rem;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 0.5rem;
            text-align: left;
        }
        th {
            background-color: #f5f5f5;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        .stat-box {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 1rem;
            text-align: center;
        }
        .stat-number {
            font-size: 1.5rem;
            font-weight: bold;
            color: #0066cc;
        }
        .missing {
            color: #dc3545;
        }
    </style>
</head>
<body>
    {{ content }}
</body>
</html>
"""

def check_doc_versioning(file_path: str) -> Dict[str, Optional[str]]:
    """Check if a document has proper versioning.
    
    Returns:
        Dict with:
        - version: Version string if found, None if not
        - status: Status string if found, None if not
    """
    version_pattern = r'\*\*Version:\*\*\s*(\d+\.\d+\.\d+)'
    status_pattern = r'\*\*Status:\*\*\s*(Draft|Review|Authoritative|Deprecated)'
    
    result = {
        'version': None,
        'status': None
    }
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Check for version
            version_match = re.search(version_pattern, content)
            if version_match:
                result['version'] = version_match.group(1)
            
            # Check for status
            status_match = re.search(status_pattern, content)
            if status_match:
                result['status'] = status_match.group(1)
    except FileNotFoundError:
        pass
    
    return result

def get_all_docs(base_dir: str) -> List[str]:
    """Get all markdown documents in the project."""
    docs = []
    for root, _, files in os.walk(base_dir):
        # Skip excluded directories
        rel_path = os.path.relpath(root, base_dir)
        if any(rel_path.startswith(excluded) for excluded in EXCLUDED_DIRS):
            continue
            
        for file in files:
            if file.endswith('.md'):
                docs.append(os.path.relpath(
                    os.path.join(root, file), 
                    base_dir
                ))
    return docs

def test_required_doc_versioning():
    """Test that key documents have proper versioning."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Check each required document
    missing_version = []
    missing_status = []
    
    for doc in REQUIRED_VERSIONING:
        path = os.path.join(base_dir, doc)
        result = check_doc_versioning(path)
        
        if not result['version']:
            missing_version.append(doc)
        if not result['status']:
            missing_status.append(doc)
    
    assert not missing_version, \
        f"Documents missing version: {missing_version}"
    assert not missing_status, \
        f"Documents missing status: {missing_status}"

def generate_report_content() -> Tuple[List[Dict], List[str], List[str]]:
    """Generate report content data.
    
    Returns:
        Tuple of:
        - List of docs with complete versioning
        - List of docs missing versioning
        - List of docs missing status
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    docs = get_all_docs(base_dir)
    
    # Check each document
    missing_version = []
    missing_status = []
    has_both = []
    
    for doc in docs:
        path = os.path.join(base_dir, doc)
        result = check_doc_versioning(path)
        
        if not result['version'] and not result['status']:
            missing_version.append(doc)
        elif not result['version']:
            missing_status.append(doc)
        else:
            has_both.append({
                'path': doc,
                'version': result['version'],
                'status': result['status']
            })
    
    return has_both, missing_version, missing_status

def generate_markdown_report(has_both: List[Dict], 
                           missing_version: List[str],
                           missing_status: List[str]) -> str:
    """Generate markdown format report."""
    report = f"""# Documentation Versioning Report
Generated: {os.environ.get('CURRENT_TIME', 'Unknown')}

## Summary Statistics
- Total Documents: {len(has_both) + len(missing_version) + len(missing_status)}
- Documents with Complete Versioning: {len(has_both)}
- Documents Missing Version: {len(missing_version)}
- Documents Missing Status: {len(missing_status)}

## Documents with Complete Versioning
Total: {len(has_both)}

| Document | Version | Status |
|----------|---------|--------|
"""
    
    for doc in sorted(has_both, key=lambda x: x['path']):
        report += f"| {doc['path']} | {doc['version']} | {doc['status']} |\n"
    
    report += f"""
## Documents Missing Versioning
Total: {len(missing_version)}

The following documents are missing both version and status:
"""
    
    for doc in sorted(missing_version):
        report += f"- {doc}\n"
    
    report += f"""
## Documents Missing Status
Total: {len(missing_status)}

The following documents have a version but no status:
"""
    
    for doc in sorted(missing_status):
        report += f"- {doc}\n"
    
    return report

def generate_html_report(has_both: List[Dict],
                        missing_version: List[str],
                        missing_status: List[str]) -> str:
    """Generate HTML format report."""
    # Convert markdown to HTML
    md_content = generate_markdown_report(has_both, missing_version, missing_status)
    html_content = markdown.markdown(md_content, extensions=['tables'])
    
    # Apply template
    template = jinja2.Template(HTML_TEMPLATE)
    return template.render(
        title="Documentation Versioning Report",
        content=html_content
    )

def generate_versioning_report():
    """Generate reports of documents missing versioning."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Generate report content
    has_both, missing_version, missing_status = generate_report_content()
    
    # Generate markdown report
    md_report = generate_markdown_report(has_both, missing_version, missing_status)
    md_path = os.path.join(base_dir, REPORTS_DIR, 'doc_versioning.md')
    
    # Generate HTML report
    html_report = generate_html_report(has_both, missing_version, missing_status)
    html_path = os.path.join(base_dir, REPORTS_DIR, 'doc_versioning.html')
    
    # Write reports
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, 'w') as f:
        f.write(md_report)
    with open(html_path, 'w') as f:
        f.write(html_report)

if __name__ == '__main__':
    generate_versioning_report()
