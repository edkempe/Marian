"""Script to scan the project and populate the asset catalog."""

import argparse
import ast
import os
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.base import Base
from services.asset_catalog_service import AssetCatalogService, AssetType
from shared_lib.database_session_util import get_analysis_session


def get_file_language(file_path: str) -> str:
    """Determine the language of a file based on its extension."""
    ext = os.path.splitext(file_path)[1].lower()
    language_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".html": "html",
        ".css": "css",
        ".md": "markdown",
        ".json": "json",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".sql": "sql",
        ".sh": "shell",
        ".txt": "text",
    }
    return language_map.get(ext, "unknown")


def get_python_imports(file_path: str) -> Set[str]:
    """Extract Python imports from a file."""
    imports = set()
    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
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
        "size": os.path.getsize(file_path),
        "last_modified": int(os.path.getmtime(file_path)),
    }

    # For Python files, extract docstring
    if file_path.endswith(".py"):
        try:
            with open(file_path, "r") as f:
                tree = ast.parse(f.read())
            if ast.get_docstring(tree):
                metadata["docstring"] = ast.get_docstring(tree)
        except Exception as e:
            print(f"Warning: Could not extract docstring from {file_path}: {e}")

    return metadata


def determine_asset_type(file_path: str) -> str:
    """Determine the type of asset based on its path and name."""
    path_parts = file_path.split(os.sep)
    filename = os.path.basename(file_path)

    if "tests" in path_parts or filename.startswith("test_"):
        return AssetType.TEST
    elif "docs" in path_parts or filename.endswith((".md", ".rst", ".txt")):
        return AssetType.DOCUMENT
    elif "config" in path_parts or filename in [
        "config.py",
        "settings.py",
        "constants.py",
    ]:
        return AssetType.CONFIG
    elif "scripts" in path_parts or filename.endswith((".sh", ".bash")):
        return AssetType.SCRIPT
    else:
        return AssetType.CODE


def scan_directory(
    directory: str,
    service: AssetCatalogService,
    exclude_dirs: List[str] = None,
    exclude_files: List[str] = None,
):
    """Scan a directory and add its contents to the asset catalog."""
    exclude_dirs = set(exclude_dirs or [])
    exclude_files = set(exclude_files or [])

    # Walk through all files in the directory
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file in exclude_files:
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, directory)

            try:
                # Get file metadata
                metadata = get_file_metadata(file_path)

                # Get file language
                language = get_file_language(file_path)

                # Get dependencies for Python files
                dependencies = []
                if language == "python":
                    try:
                        dependencies = list(get_python_imports(file_path))
                    except Exception as e:
                        print(f"Warning: Could not parse imports from {file_path}: {e}")

                # Determine asset type
                asset_type = determine_asset_type(rel_path)

                # Check if asset already exists
                existing_assets = service.search_assets(file_path=rel_path)
                if existing_assets:
                    # Update existing asset
                    asset = existing_assets[0]
                    asset.title = os.path.basename(file_path)
                    asset.description = metadata.get("docstring", "")
                    asset.language = language
                    asset.dependencies = dependencies
                    asset.asset_metadata = metadata
                    asset.asset_type = asset_type
                    asset.modified_date = int(datetime.utcnow().timestamp())
                    print(f"Updated asset: {rel_path} ({asset_type})")
                else:
                    # Create new asset
                    asset = service.add_asset(
                        title=os.path.basename(file_path),
                        file_path=rel_path,
                        asset_type=asset_type,
                        description=metadata.get("docstring", ""),
                        language=language,
                        dependencies=dependencies,
                        metadata=metadata,
                    )
                    print(f"Added asset: {rel_path} ({asset_type})")

                # Add dependencies
                if dependencies:
                    for dep in dependencies:
                        try:
                            # Find the dependency in the catalog
                            dep_assets = service.search_assets(file_path=f"{dep}.py")
                            if dep_assets:
                                service.add_dependency(
                                    source_id=asset.id,
                                    target_id=dep_assets[0].id,
                                    dependency_type="import",
                                )
                        except Exception as e:
                            print(
                                f"Warning: Could not add dependency {rel_path} -> {dep}.py: {e}"
                            )

            except Exception as e:
                print(f"Error processing {file_path}: {e}")


def main():
    """Main function to populate the asset catalog."""
    parser = argparse.ArgumentParser(description="Populate the asset catalog")
    parser.add_argument(
        "--directory",
        "-d",
        default=project_root,
        help="Directory to scan (default: project root)",
    )
    parser.add_argument(
        "--exclude-dirs",
        "-D",
        nargs="*",
        default=["venv", "env", "__pycache__", "node_modules"],
        help="Directories to exclude",
    )
    parser.add_argument(
        "--exclude-files", "-F", nargs="*", default=[], help="Files to exclude"
    )
    args = parser.parse_args()

    # Initialize database
    engine = create_engine("sqlite:///data/asset_catalog.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create service with session
        service = AssetCatalogService(session)

        # Scan directory
        scan_directory(
            args.directory,
            service,
            exclude_dirs=args.exclude_dirs,
            exclude_files=args.exclude_files,
        )

        # Commit changes
        session.commit()
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
