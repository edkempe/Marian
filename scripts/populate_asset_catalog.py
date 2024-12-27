"""Script to scan the project and populate the asset catalog."""

import os
import sys
import argparse
from typing import Dict, List, Set
import ast
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from services.asset_catalog_service import AssetCatalogService, AssetType
from models.base import Base
from shared_lib.database_session_util import get_analysis_session
from sqlalchemy import create_engine

def get_file_language(file_path: str) -> str:
    """Determine the language of a file based on its extension."""
    ext = os.path.splitext(file_path)[1].lower()
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.md': 'markdown',
        '.json': 'json',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.sql': 'sql',
        '.sh': 'shell',
        '.txt': 'text'
    }
    return language_map.get(ext, 'unknown')

def get_python_imports(file_path: str) -> Set[str]:
    """Extract Python imports from a file."""
    imports = set()
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for name in node.names:
                    if module:
                        imports.add(f"{module}.{name.name}")
                    else:
                        imports.add(name.name)
    except Exception as e:
        print(f"Warning: Could not parse imports from {file_path}: {e}")
    
    return imports

def get_file_metadata(file_path: str) -> Dict:
    """Get metadata for a file."""
    metadata = {
        'size': os.path.getsize(file_path),
        'last_modified': int(os.path.getmtime(file_path))
    }

    # For Python files, extract docstring
    if file_path.endswith('.py'):
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())
            if ast.get_docstring(tree):
                metadata['docstring'] = ast.get_docstring(tree)
        except Exception as e:
            print(f"Warning: Could not extract docstring from {file_path}: {e}")

    return metadata

def determine_asset_type(file_path: str) -> str:
    """Determine the type of asset based on its path and name."""
    path_parts = file_path.split(os.sep)
    filename = os.path.basename(file_path)

    if 'tests' in path_parts or filename.startswith('test_'):
        return AssetType.TEST
    elif 'docs' in path_parts or filename.endswith(('.md', '.rst', '.txt')):
        return AssetType.DOCUMENT
    elif 'config' in path_parts or filename in ['config.py', 'settings.py', 'constants.py']:
        return AssetType.CONFIG
    elif 'scripts' in path_parts or filename.endswith(('.sh', '.bash')):
        return AssetType.SCRIPT
    else:
        return AssetType.CODE

def scan_directory(
    directory: str,
    service: AssetCatalogService,
    exclude_dirs: List[str] = None,
    exclude_files: List[str] = None
) -> None:
    """Scan a directory and add its contents to the asset catalog."""
    exclude_dirs = set(exclude_dirs or [])
    exclude_files = set(exclude_files or [])

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]

        for file in files:
            if file in exclude_files or file.startswith('.'):
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, directory)

            # Skip certain file types
            if any(file.endswith(ext) for ext in ['.pyc', '.pyo', '.pyd', '.so']):
                continue

            try:
                # Get file information
                language = get_file_language(file_path)
                asset_type = determine_asset_type(file_path)
                metadata = get_file_metadata(file_path)

                # Create asset
                title = os.path.splitext(file)[0].replace('_', ' ').title()
                asset = service.add_asset(
                    title=title,
                    file_path=rel_path,
                    asset_type=asset_type,
                    language=language,
                    metadata=metadata
                )

                print(f"Added asset: {rel_path} ({asset_type})")

                # For Python files, add dependencies
                if language == 'python':
                    imports = get_python_imports(file_path)
                    for imp in imports:
                        # Try to find the imported module in our codebase
                        possible_paths = [
                            f"{imp.replace('.', '/')}.py",
                            f"{imp.split('.')[0]}.py"
                        ]
                        for path in possible_paths:
                            if os.path.exists(os.path.join(directory, path)):
                                try:
                                    target = service.search_assets(file_path=path)[0]
                                    service.add_dependency(
                                        source_id=asset.id,
                                        target_id=target.id,
                                        dependency_type='imports'
                                    )
                                    print(f"Added dependency: {rel_path} -> {path}")
                                except Exception as e:
                                    print(f"Warning: Could not add dependency {rel_path} -> {path}: {e}")

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

def main():
    """Main function to populate the asset catalog."""
    parser = argparse.ArgumentParser(description='Populate the asset catalog')
    parser.add_argument('--directory', '-d', default=project_root,
                       help='Directory to scan (default: project root)')
    parser.add_argument('--exclude-dirs', '-D', nargs='*', default=['venv', 'env', '__pycache__', 'node_modules'],
                       help='Directories to exclude')
    parser.add_argument('--exclude-files', '-F', nargs='*', default=[],
                       help='Files to exclude')
    args = parser.parse_args()

    # Initialize database
    engine = create_engine('sqlite:///data/asset_catalog.db')
    Base.metadata.create_all(engine)

    # Create service
    service = AssetCatalogService()

    # Scan directory
    scan_directory(
        args.directory,
        service,
        exclude_dirs=args.exclude_dirs,
        exclude_files=args.exclude_files
    )

if __name__ == '__main__':
    main()
