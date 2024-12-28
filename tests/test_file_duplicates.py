"""Tests to detect duplicate or similar files in the codebase."""

import os
import hashlib
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from difflib import SequenceMatcher
import pytest
from shared_lib.constants import TESTING_CONFIG

# Files that should be unique by name
UNIQUE_FILENAMES = [
    'setup.py',
    '.gitignore',
    'pyproject.toml',
]

# Files that can have multiple instances but should have unique content
UNIQUE_CONTENT_FILES = [
    'README.md',    # Each README should be specific to its directory
]

# Files that can have multiple instances with identical content
ALLOWED_DUPLICATES = [
    '__init__.py',  # Python package markers
    '.gitkeep',     # Git directory markers
    'constants.py', # Allow domain-specific constants files
]

# Files that should be unique by content
UNIQUE_CONTENT_PATTERNS = [
    '*.py',  # All Python files should have unique content
    '*.sql', # All SQL files should be unique
    '*.md',  # All documentation files should be unique
    '*.txt', # All text files should be unique
    '*.json', # All JSON files should be unique
    '*.yaml', # All YAML files should be unique
    '*.yml',  # All YAML files should be unique
]

# Directories to ignore completely
IGNORED_DIRS = [
    '__pycache__',  # Python cache
    '.pytest_cache',  # Pytest cache
    'archive',  # Archived files
]

# Threshold for considering filenames similar (increased for test files)
SIMILARITY_THRESHOLD = 0.92  # Only flag extremely similar names

def should_ignore_file(filepath: str) -> bool:
    """Check if a file should be ignored in duplicate checks."""
    # Ignore files in specific directories
    for ignored_dir in IGNORED_DIRS:
        if ignored_dir in filepath:
            return True
        
    # Get the filename
    filename = os.path.basename(filepath)
    
    # Only ignore allowed duplicates for name checks, not content checks
    if filename in ALLOWED_DUPLICATES and filename not in UNIQUE_CONTENT_FILES:
        return True

    # Ignore test files when checking for similar names
    if filename.startswith('test_'):
        return True
        
    return False

def should_check_content(filepath: str) -> bool:
    """Check if a file's content should be checked for duplicates."""
    filename = os.path.basename(filepath)
    
    # Always check content of files in UNIQUE_CONTENT_FILES
    if filename in UNIQUE_CONTENT_FILES:
        return True
        
    # Skip content check for allowed duplicates
    if filename in ALLOWED_DUPLICATES:
        return False
        
    # Check content based on file patterns
    return any(
        filepath.endswith(pattern.replace('*', ''))
        for pattern in UNIQUE_CONTENT_PATTERNS
    )

def calculate_file_hash(filepath: str) -> str:
    """Calculate SHA-256 hash of file content."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read the file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_filename_similarity(name1: str, name2: str) -> float:
    """Calculate similarity ratio between two filenames."""
    return SequenceMatcher(None, name1, name2).ratio()

def find_files(base_dir: str, pattern: str = None) -> List[str]:
    """Find all files matching the pattern."""
    matches = []
    for root, _, filenames in os.walk(base_dir):
        # Skip excluded directories
        rel_path = os.path.relpath(root, base_dir)
        if any(rel_path.startswith(excluded) for excluded in TESTING_CONFIG['EXCLUDED_DIRS']):
            continue
        
        for filename in filenames:
            if pattern:
                if not any(filename.endswith(p.replace('*', '')) for p in pattern.split('|')):
                    continue
            matches.append(os.path.join(root, filename))
    return matches

def find_duplicate_files() -> Tuple[Dict[str, List[str]], Dict[str, List[str]], List[Tuple[str, str, float]]]:
    """Find duplicate and similar files in the codebase."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Track duplicates
    filename_duplicates = defaultdict(list)
    content_duplicates = defaultdict(list)
    similar_names = []
    
    # Find duplicates by filename
    for unique_file in UNIQUE_FILENAMES:
        matches = find_files(base_dir, unique_file)
        matches = [m for m in matches if not should_ignore_file(m)]
        if len(matches) > 1:
            filename_duplicates[unique_file] = matches
    
    # Find duplicates by content
    content_pattern = '|'.join(UNIQUE_CONTENT_PATTERNS)
    all_files = find_files(base_dir, content_pattern)
    
    # Group by content hash for files that should be checked
    content_files = [f for f in all_files if should_check_content(f)]
    for filepath in content_files:
        file_hash = calculate_file_hash(filepath)
        content_duplicates[file_hash].append(filepath)
    
    # Remove unique entries
    content_duplicates = {k: v for k, v in content_duplicates.items() if len(v) > 1}
    
    # Find similar filenames
    checked_pairs = set()
    for file1 in all_files:
        if should_ignore_file(file1):
            continue
            
        name1 = os.path.basename(file1)
        for file2 in all_files:
            if file1 == file2 or should_ignore_file(file2):
                continue
                
            name2 = os.path.basename(file2)
            pair_key = tuple(sorted([file1, file2]))
            
            if pair_key in checked_pairs:
                continue
                
            checked_pairs.add(pair_key)
            similarity = get_filename_similarity(name1, name2)
            
            if similarity >= SIMILARITY_THRESHOLD:
                similar_names.append((file1, file2, similarity))
    
    return dict(filename_duplicates), dict(content_duplicates), similar_names

def test_no_duplicate_files():
    """Test that there are no unintended duplicate files."""
    filename_dupes, content_dupes, similar_names = find_duplicate_files()
    
    # Format error messages
    errors = []
    
    if filename_dupes:
        errors.append("\nDuplicate filenames found:")
        for filename, locations in filename_dupes.items():
            errors.append(f"\n{filename} found in multiple locations:")
            for loc in locations:
                errors.append(f"  - {loc}")
    
    if content_dupes:
        errors.append("\nFiles with duplicate content found:")
        for _, locations in content_dupes.items():
            errors.append("\nThe following files have identical content:")
            for loc in locations:
                errors.append(f"  - {loc}")
    
    if similar_names:
        errors.append("\nFiles with similar names found:")
        for file1, file2, similarity in similar_names:
            errors.append(
                f"\n{os.path.basename(file1)} and {os.path.basename(file2)} "
                f"are {similarity:.1%} similar:"
            )
            errors.append(f"  - {file1}")
            errors.append(f"  - {file2}")
    
    assert not any([filename_dupes, content_dupes, similar_names]), \
        "\n".join(errors)

def generate_duplicate_report():
    """Generate a report of duplicate files."""
    filename_dupes, content_dupes, similar_names = find_duplicate_files()
    
    report = """# File Duplication Report
Generated: {}

## Summary
- Duplicate Filenames: {}
- Files with Duplicate Content: {}
- Similar Filenames: {}

## Duplicate Filenames
Files that should be unique but were found in multiple locations:

""".format(
        os.environ.get('CURRENT_TIME', 'Unknown'),
        len(filename_dupes),
        sum(len(v) for v in content_dupes.values()) // 2,
        len(similar_names)
    )
    
    if filename_dupes:
        for filename, locations in filename_dupes.items():
            report += f"\n### {filename}\n"
            for loc in locations:
                report += f"- {loc}\n"
    else:
        report += "No duplicate filenames found.\n"
    
    report += "\n## Duplicate Content\nFiles with identical content:\n"
    
    if content_dupes:
        for hash_val, locations in content_dupes.items():
            report += f"\n### Content Hash: {hash_val[:8]}\n"
            for loc in locations:
                report += f"- {loc}\n"
    else:
        report += "No files with duplicate content found.\n"
    
    report += "\n## Similar Filenames\nFiles with names that are very similar:\n"
    
    if similar_names:
        for file1, file2, similarity in similar_names:
            report += f"\n### {similarity:.1%} Similar\n"
            report += f"- {file1}\n"
            report += f"- {file2}\n"
    else:
        report += "No similar filenames found.\n"
    
    # Write reports
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Markdown report
    md_path = os.path.join(base_dir, 'reports', 'testing', 'file_duplicates.md')
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, 'w') as f:
        f.write(report)
    
    # HTML report
    from test_doc_quality import HTML_TEMPLATE
    import markdown
    import jinja2
    
    html_content = markdown.markdown(report, extensions=['tables'])
    template = jinja2.Template(HTML_TEMPLATE)
    html_report = template.render(
        title="File Duplication Report",
        content=html_content
    )
    
    html_path = os.path.join(base_dir, 'reports', 'testing', 'file_duplicates.html')
    with open(html_path, 'w') as f:
        f.write(html_report)

if __name__ == '__main__':
    generate_duplicate_report()
