"""Service for managing code and document assets in the catalog."""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from models.asset_catalog import (
    AssetCatalogItem,
    AssetCatalogTag,
    AssetDependency,
    AssetType,
)
from models.catalog import Tag
from shared_lib.database_session_util import get_catalog_session


class AssetCatalogService:
    """Service for managing code and document assets."""

    def __init__(self):
        """Initialize the asset catalog service."""
        pass

    def add_asset(
        self,
        title: str,
        file_path: str,
        asset_type: str,
        description: str = "",
        language: str = None,
        dependencies: List[str] = None,
        metadata: Dict[str, Any] = None,
        tags: List[str] = None,
    ) -> AssetCatalogItem:
        """Add a new asset to the catalog."""
        with get_catalog_session() as session:
            # Normalize file path
            file_path = os.path.normpath(file_path)

            # Check if asset already exists
            existing = (
                session.query(AssetCatalogItem)
                .filter_by(file_path=file_path, deleted=False)
                .first()
            )
            if existing:
                raise ValueError(f"Asset with file path '{file_path}' already exists")

            # Create the asset
            asset = AssetCatalogItem(
                title=title,
                file_path=file_path,
                asset_type=asset_type,
                description=description,
                language=language,
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            session.add(asset)
            session.flush()  # Get the asset ID

            # Add dependencies if provided
            if dependencies:
                for dep in dependencies:
                    dependency = AssetDependency(
                        source_id=asset.id, target_id=dep, dependency_type="imports"
                    )
                    session.add(dependency)

            # Add tags if provided
            if tags:
                for tag_name in tags:
                    # Check if tag exists
                    tag = session.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        session.add(tag)
                        session.flush()

                    # Create asset-tag association
                    asset_tag = AssetCatalogTag(asset_id=asset.id, tag_id=tag.id)
                    session.add(asset_tag)

            session.commit()
            return asset

    def update_asset(
        self,
        asset_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        language: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[AssetCatalogItem]:
        """Update an existing asset."""
        with get_catalog_session() as session:
            asset = (
                session.query(AssetCatalogItem)
                .filter_by(id=asset_id, deleted=False)
                .first()
            )
            if not asset:
                raise ValueError(f"Asset with ID {asset_id} not found")

            # Update basic fields
            if title:
                asset.title = title
            if description:
                asset.description = description
            if language:
                asset.language = language
            if metadata:
                asset.metadata.update(metadata)

            asset.updated_at = datetime.utcnow()

            # Update dependencies if provided
            if dependencies is not None:
                # Remove existing dependencies
                session.query(AssetDependency).filter(
                    AssetDependency.source_id == asset_id
                ).delete()

                # Add new dependencies
                for dep in dependencies:
                    dependency = AssetDependency(
                        source_id=asset_id, target_id=dep, dependency_type="imports"
                    )
                    session.add(dependency)

            # Update tags if provided
            if tags is not None:
                # Remove existing tags
                session.query(AssetCatalogTag).filter(
                    AssetCatalogTag.asset_id == asset_id
                ).delete()

                # Add new tags
                for tag_name in tags:
                    tag = session.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        session.add(tag)
                        session.flush()

                    asset_tag = AssetCatalogTag(asset_id=asset_id, tag_id=tag.id)
                    session.add(asset_tag)

            session.commit()
            return asset

    def delete_asset(self, asset_id: int):
        """Soft delete an asset."""
        with get_catalog_session() as session:
            asset = (
                session.query(AssetCatalogItem)
                .filter_by(id=asset_id, deleted=False)
                .first()
            )
            if not asset:
                raise ValueError(f"Asset with ID {asset_id} not found")

            asset.deleted = True
            asset.status = "deleted"
            session.commit()

    def add_dependency(
        self,
        source_id: int,
        target_id: int,
        dependency_type: str,
        metadata: Dict[str, Any] = None,
    ) -> AssetDependency:
        """Add a dependency between two assets."""
        with get_catalog_session() as session:
            # Verify assets exist
            source = (
                session.query(AssetCatalogItem)
                .filter_by(id=source_id, deleted=False)
                .first()
            )
            target = (
                session.query(AssetCatalogItem)
                .filter_by(id=target_id, deleted=False)
                .first()
            )

            if not source or not target:
                raise ValueError("Source or target asset not found")

            # Create dependency
            dependency = AssetDependency(
                source_id=source_id,
                target_id=target_id,
                dependency_type=dependency_type,
                metadata=metadata or {},
            )
            session.add(dependency)
            session.commit()
            return dependency

    def search_assets(
        self,
        query: str = None,
        asset_type: str = None,
        language: str = None,
        file_path: str = None,
        tags: List[str] = None,
    ) -> List[AssetCatalogItem]:
        """Search for assets in the catalog."""
        with get_catalog_session() as session:
            filters = []

            if query:
                filters.append(
                    or_(
                        AssetCatalogItem.title.ilike(f"%{query}%"),
                        AssetCatalogItem.description.ilike(f"%{query}%"),
                    )
                )

            if asset_type:
                filters.append(AssetCatalogItem.asset_type == asset_type)

            if language:
                filters.append(AssetCatalogItem.language == language)

            if file_path:
                filters.append(
                    AssetCatalogItem.file_path == os.path.normpath(file_path)
                )

            if tags:
                for tag in tags:
                    filters.append(
                        AssetCatalogItem.tags.any(AssetCatalogTag.name == tag)
                    )

            query = session.query(AssetCatalogItem)
            if filters:
                query = query.filter(and_(*filters))

            return query.all()

    def get_asset_dependencies(
        self, asset_id: int, include_indirect: bool = False
    ) -> List[Tuple[AssetCatalogItem, str]]:
        """Get dependencies of an asset."""
        with get_catalog_session() as session:
            deps = (
                session.query(AssetCatalogItem, AssetDependency.dependency_type)
                .join(
                    AssetDependency,
                    and_(
                        AssetDependency.target_id == AssetCatalogItem.id,
                        AssetDependency.source_id == asset_id,
                    ),
                )
                .filter(AssetCatalogItem.deleted == False)
                .all()
            )

            if include_indirect:
                seen = {asset_id}
                to_check = [d[0].id for d in deps]

                while to_check:
                    current_id = to_check.pop(0)
                    if current_id not in seen:
                        seen.add(current_id)
                        indirect_deps = (
                            session.query(
                                AssetCatalogItem, AssetDependency.dependency_type
                            )
                            .join(
                                AssetDependency,
                                and_(
                                    AssetDependency.target_id == AssetCatalogItem.id,
                                    AssetDependency.source_id == current_id,
                                ),
                            )
                            .filter(AssetCatalogItem.deleted == False)
                            .all()
                        )
                        deps.extend(indirect_deps)
                        to_check.extend(d[0].id for d in indirect_deps)

            return deps

    def get_asset_dependents(
        self, asset_id: int, include_indirect: bool = False
    ) -> List[Tuple[AssetCatalogItem, str]]:
        """Get dependents of an asset."""
        with get_catalog_session() as session:
            deps = (
                session.query(AssetCatalogItem, AssetDependency.dependency_type)
                .join(
                    AssetDependency,
                    and_(
                        AssetDependency.source_id == AssetCatalogItem.id,
                        AssetDependency.target_id == asset_id,
                    ),
                )
                .filter(AssetCatalogItem.deleted == False)
                .all()
            )

            if include_indirect:
                seen = {asset_id}
                to_check = [d[0].id for d in deps]

                while to_check:
                    current_id = to_check.pop(0)
                    if current_id not in seen:
                        seen.add(current_id)
                        indirect_deps = (
                            session.query(
                                AssetCatalogItem, AssetDependency.dependency_type
                            )
                            .join(
                                AssetDependency,
                                and_(
                                    AssetDependency.source_id == AssetCatalogItem.id,
                                    AssetDependency.target_id == current_id,
                                ),
                            )
                            .filter(AssetCatalogItem.deleted == False)
                            .all()
                        )
                        deps.extend(indirect_deps)
                        to_check.extend(d[0].id for d in indirect_deps)

            return deps
