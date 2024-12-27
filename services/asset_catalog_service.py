"""Service for managing code and document assets in the catalog."""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from models.asset_catalog import (
    AssetCatalogItem, AssetCatalogTag, AssetDependency, AssetType
)
from models.catalog import Tag
from shared_lib.database_session_util import get_analysis_session
from shared_lib.constants import CATALOG_CONFIG

class AssetCatalogService:
    """Service for managing code and document assets."""

    def __init__(self, session: Optional[Session] = None):
        """Initialize the asset catalog service."""
        self.session = session or get_analysis_session()

    def add_asset(
        self,
        title: str,
        file_path: str,
        asset_type: str,
        description: str = "",
        language: str = None,
        dependencies: List[str] = None,
        metadata: Dict[str, Any] = None,
        tags: List[str] = None
    ) -> AssetCatalogItem:
        """Add a new asset to the catalog.
        
        Args:
            title: Title of the asset
            file_path: Path to the asset file
            asset_type: Type of asset (code, document, test, config, script)
            description: Description of the asset
            language: Programming language or document type
            dependencies: List of file paths that this asset depends on
            metadata: Additional metadata about the asset
            tags: List of tags to apply to the asset
        
        Returns:
            The created asset catalog item
        """
        # Normalize file path
        file_path = os.path.normpath(file_path)

        # Check if asset already exists
        existing = self.session.query(AssetCatalogItem).filter_by(
            file_path=file_path,
            deleted=False
        ).first()
        if existing:
            raise ValueError(f"Asset with file path '{file_path}' already exists")

        # Create asset
        asset = AssetCatalogItem(
            title=title,
            file_path=file_path,
            asset_type=asset_type,
            description=description,
            language=language,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        self.session.add(asset)

        # Add tags
        if tags:
            for tag_name in tags:
                tag = self.session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    self.session.add(tag)
                AssetCatalogTag.create(self.session, asset.id, tag.id)

        self.session.commit()
        return asset

    def update_asset(
        self,
        asset_id: int,
        title: str = None,
        description: str = None,
        metadata: Dict[str, Any] = None,
        tags: List[str] = None
    ) -> AssetCatalogItem:
        """Update an existing asset.
        
        Args:
            asset_id: ID of the asset to update
            title: New title (optional)
            description: New description (optional)
            metadata: New metadata (optional)
            tags: New tags (optional)
        
        Returns:
            The updated asset
        """
        asset = self.session.query(AssetCatalogItem).filter_by(
            id=asset_id,
            deleted=False
        ).first()
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found")

        if title:
            asset.title = title
        if description:
            asset.description = description
        if metadata:
            asset.metadata.update(metadata)

        if tags is not None:
            # Remove existing tags
            self.session.query(AssetCatalogTag).filter_by(asset_id=asset_id).delete()
            
            # Add new tags
            for tag_name in tags:
                tag = self.session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    self.session.add(tag)
                AssetCatalogTag.create(self.session, asset.id, tag.id)

        self.session.commit()
        return asset

    def delete_asset(self, asset_id: int):
        """Soft delete an asset."""
        asset = self.session.query(AssetCatalogItem).filter_by(
            id=asset_id,
            deleted=False
        ).first()
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found")

        asset.deleted = True
        asset.status = 'deleted'
        self.session.commit()

    def add_dependency(
        self,
        source_id: int,
        target_id: int,
        dependency_type: str,
        metadata: Dict[str, Any] = None
    ) -> AssetDependency:
        """Add a dependency between two assets.
        
        Args:
            source_id: ID of the dependent asset
            target_id: ID of the asset being depended on
            dependency_type: Type of dependency (e.g., 'imports', 'uses', 'tests')
            metadata: Additional metadata about the dependency
        
        Returns:
            The created dependency
        """
        # Verify assets exist
        source = self.session.query(AssetCatalogItem).filter_by(
            id=source_id,
            deleted=False
        ).first()
        target = self.session.query(AssetCatalogItem).filter_by(
            id=target_id,
            deleted=False
        ).first()

        if not source or not target:
            raise ValueError("Source or target asset not found")

        # Create dependency
        dependency = AssetDependency(
            source_id=source_id,
            target_id=target_id,
            dependency_type=dependency_type,
            metadata=metadata or {}
        )
        self.session.add(dependency)
        self.session.commit()
        return dependency

    def search_assets(
        self,
        query: str = None,
        asset_type: str = None,
        tags: List[str] = None,
        language: str = None
    ) -> List[AssetCatalogItem]:
        """Search for assets based on various criteria.
        
        Args:
            query: Search query for title/description
            asset_type: Filter by asset type
            tags: Filter by tags
            language: Filter by programming language
        
        Returns:
            List of matching assets
        """
        q = self.session.query(AssetCatalogItem).filter_by(deleted=False)

        if query:
            q = q.filter(or_(
                AssetCatalogItem.title.ilike(f"%{query}%"),
                AssetCatalogItem.description.ilike(f"%{query}%")
            ))

        if asset_type:
            q = q.filter_by(asset_type=asset_type)

        if language:
            q = q.filter_by(language=language)

        if tags:
            for tag in tags:
                q = q.filter(AssetCatalogItem.tags.any(Tag.name == tag))

        return q.all()

    def get_asset_dependencies(
        self,
        asset_id: int,
        include_indirect: bool = False
    ) -> List[Tuple[AssetCatalogItem, str]]:
        """Get dependencies of an asset.
        
        Args:
            asset_id: ID of the asset
            include_indirect: Whether to include indirect dependencies
        
        Returns:
            List of (asset, dependency_type) tuples
        """
        deps = self.session.query(
            AssetCatalogItem,
            AssetDependency.dependency_type
        ).join(
            AssetDependency,
            and_(
                AssetDependency.target_id == AssetCatalogItem.id,
                AssetDependency.source_id == asset_id
            )
        ).filter(
            AssetCatalogItem.deleted == False
        ).all()

        if include_indirect:
            seen = {asset_id}
            to_check = [d[0].id for d in deps]
            
            while to_check:
                current_id = to_check.pop(0)
                if current_id not in seen:
                    seen.add(current_id)
                    indirect_deps = self.session.query(
                        AssetCatalogItem,
                        AssetDependency.dependency_type
                    ).join(
                        AssetDependency,
                        and_(
                            AssetDependency.target_id == AssetCatalogItem.id,
                            AssetDependency.source_id == current_id
                        )
                    ).filter(
                        AssetCatalogItem.deleted == False
                    ).all()
                    deps.extend(indirect_deps)
                    to_check.extend(d[0].id for d in indirect_deps)

        return deps

    def get_asset_dependents(
        self,
        asset_id: int,
        include_indirect: bool = False
    ) -> List[Tuple[AssetCatalogItem, str]]:
        """Get dependents of an asset.
        
        Args:
            asset_id: ID of the asset
            include_indirect: Whether to include indirect dependents
        
        Returns:
            List of (asset, dependency_type) tuples
        """
        deps = self.session.query(
            AssetCatalogItem,
            AssetDependency.dependency_type
        ).join(
            AssetDependency,
            and_(
                AssetDependency.source_id == AssetCatalogItem.id,
                AssetDependency.target_id == asset_id
            )
        ).filter(
            AssetCatalogItem.deleted == False
        ).all()

        if include_indirect:
            seen = {asset_id}
            to_check = [d[0].id for d in deps]
            
            while to_check:
                current_id = to_check.pop(0)
                if current_id not in seen:
                    seen.add(current_id)
                    indirect_deps = self.session.query(
                        AssetCatalogItem,
                        AssetDependency.dependency_type
                    ).join(
                        AssetDependency,
                        and_(
                            AssetDependency.source_id == AssetCatalogItem.id,
                            AssetDependency.target_id == current_id
                        )
                    ).filter(
                        AssetCatalogItem.deleted == False
                    ).all()
                    deps.extend(indirect_deps)
                    to_check.extend(d[0].id for d in indirect_deps)

        return deps
