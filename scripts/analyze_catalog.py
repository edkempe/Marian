#!/usr/bin/env python3
"""Analyze the contents of the asset catalog."""

import os
import sys
from collections import Counter

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.asset_catalog_service import AssetCatalogService
from shared_lib.database_session_util import get_catalog_session


def analyze_catalog():
    """Analyze and print statistics about the asset catalog."""
    with get_catalog_session() as session:
        service = AssetCatalogService(session)

        # Get all assets
        assets = service.search_assets()

        # Count by type
        type_counts = Counter(asset.asset_type for asset in assets)
        print("\nAsset counts by type:")
        for asset_type, count in type_counts.most_common():
            print(f"{asset_type}: {count}")

        # Count by language
        lang_counts = Counter(asset.language for asset in assets if asset.language)
        print("\nAsset counts by language:")
        for lang, count in lang_counts.most_common():
            print(f"{lang}: {count}")

        # Get tag statistics
        all_tags = []
        for asset in assets:
            all_tags.extend([tag.name for tag in asset.tags])
        tag_counts = Counter(all_tags)

        if tag_counts:
            print("\nMost common tags:")
            for tag, count in tag_counts.most_common(10):
                print(f"{tag}: {count}")

        # Analyze dependencies
        dependency_types = []
        for asset in assets:
            deps = service.get_asset_dependencies(asset.id)
            dependency_types.extend(dep_type for _, dep_type in deps)

        dep_type_counts = Counter(dependency_types)
        if dep_type_counts:
            print("\nDependency type counts:")
            for dep_type, count in dep_type_counts.most_common():
                print(f"{dep_type}: {count}")

        print(f"\nTotal number of assets: {len(assets)}")


if __name__ == "__main__":
    analyze_catalog()
