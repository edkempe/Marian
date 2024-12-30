"""Tests to detect duplicate or similar files in the codebase."""

import hashlib
import os
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pytest

from shared_lib.constants import TESTING_CONFIG
from shared_lib.file_constants import (
    ALLOWED_DUPLICATES,
    HTML_EXT,
    IGNORED_DIRS,
    MD_EXT,
    REPORTS_DIR,
    SIMILARITY_THRESHOLD,
    TESTING_DIR,
    UNIQUE_CONTENT_FILES,
    UNIQUE_FILENAMES,
)
from shared_lib.path_util import (
    get_absolute_path,
    get_project_root,
    join_paths,
    list_files,
    write_file,
)


def should_ignore_file(filepath: str) -> bool:
    """Check if a file should be ignored in duplicate checks."""
    return any(ignored in filepath for ignored in IGNORED_DIRS)


def get_file_hash(filepath: str) -> str:
    """Calculate SHA256 hash of file contents."""
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def find_duplicates(directory: str) -> Dict[str, List[str]]:
    """Find duplicate files by content hash."""
    hash_dict: Dict[str, List[str]] = defaultdict(list)

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename in ALLOWED_DUPLICATES and filename not in UNIQUE_CONTENT_FILES:
                continue

            filepath = os.path.join(root, filename)
            if should_ignore_file(filepath):
                continue

            file_hash = get_file_hash(filepath)
            hash_dict[file_hash].append(filepath)

    return {k: v for k, v in hash_dict.items() if len(v) > 1}


def find_similar_names(directory: str) -> List[Tuple[str, str, float]]:
    """Find files with similar names using string similarity."""
    similar_pairs = []
    all_files = []

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename in ALLOWED_DUPLICATES:
                continue

            filepath = os.path.join(root, filename)
            if should_ignore_file(filepath):
                continue

            all_files.append(filepath)

    for i, file1 in enumerate(all_files):
        for file2 in all_files[i + 1 :]:
            name1 = os.path.basename(file1)
            name2 = os.path.basename(file2)

            similarity = SequenceMatcher(None, name1, name2).ratio()
            if similarity >= SIMILARITY_THRESHOLD:
                similar_pairs.append((file1, file2, similarity))

    return similar_pairs


def generate_report(
    duplicates: Dict[str, List[str]], similar_names: List[Tuple[str, str, float]]
) -> None:
    """Generate markdown and HTML reports."""
    base_dir = get_project_root()
    md_path = join_paths(base_dir, REPORTS_DIR, TESTING_DIR, f"duplicate_files{MD_EXT}")
    html_path = join_paths(
        base_dir, REPORTS_DIR, TESTING_DIR, f"duplicate_files{HTML_EXT}"
    )

    md_content = "# Duplicate and Similar Files Report\n\n"

    if duplicates:
        md_content += "## Files with Identical Content\n\n"
        for _, files in duplicates.items():
            md_content += "* Duplicates:\n"
            for file in files:
                md_content += f"  * {file}\n"
            md_content += "\n"
    else:
        md_content += "No duplicate files found.\n\n"

    if similar_names:
        md_content += "## Files with Similar Names\n\n"
        for file1, file2, similarity in similar_names:
            md_content += f"* {similarity:.2%} similar:\n"
            md_content += f"  * {file1}\n"
            md_content += f"  * {file2}\n\n"
    else:
        md_content += "No files with similar names found.\n"

    write_file(md_path, md_content)

    html_content = f"""
    <html>
    <head>
        <title>Duplicate and Similar Files Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #333; }}
            .duplicate-group {{ margin: 10px 0; padding: 10px; background: #f5f5f5; }}
            .similar-group {{ margin: 10px 0; padding: 10px; background: #f0f0f0; }}
        </style>
    </head>
    <body>
        <h1>Duplicate and Similar Files Report</h1>

        <h2>Files with Identical Content</h2>
        {"".join(f'''
        <div class="duplicate-group">
            <strong>Duplicates:</strong><br/>
            {"<br/>".join(f"&bull; {file}" for file in files)}
        </div>
        ''' for _, files in duplicates.items()) if duplicates else "No duplicate files found."}

        <h2>Files with Similar Names</h2>
        {"".join(f'''
        <div class="similar-group">
            <strong>{similarity:.2%} similar:</strong><br/>
            &bull; {file1}<br/>
            &bull; {file2}
        </div>
        ''' for file1, file2, similarity in similar_names) if similar_names else "No files with similar names found."}
    </body>
    </html>
    """

    write_file(html_path, html_content)


def test_no_duplicate_files():
    """Test that there are no unwanted duplicate files."""
    base_dir = get_project_root()
    duplicates = find_duplicates(str(base_dir))
    similar_names = find_similar_names(str(base_dir))

    generate_report(duplicates, similar_names)

    assert not duplicates, "Found duplicate files"
    assert not similar_names, "Found files with similar names"
