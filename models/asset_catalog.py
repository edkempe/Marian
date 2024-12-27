"""Models for code and document asset catalogs."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import (
    String, Integer, Text, Boolean, JSON, ForeignKey, UniqueConstraint,
    event, and_, or_
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from models.base import Base
from models.catalog import CatalogItem, Tag, CatalogTag

class AssetType:
    """Asset types for the catalog."""
    CODE = 'code'
    DOCUMENT = 'document'
    TEST = 'test'
    CONFIG = 'config'
    SCRIPT = 'script'

class AssetCatalogItem(Base):
    """Model for code and document assets in the catalog."""
    __tablename__ = "asset_catalog_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    asset_type: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    language: Mapped[Optional[str]] = mapped_column(String)
    dependencies: Mapped[Optional[List[str]]] = mapped_column(JSON)
    asset_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default='active',
        server_default='active'
    )
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_date: Mapped[int] = mapped_column(
        Integer,
        default=lambda: int(datetime.utcnow().timestamp()),
        nullable=False
    )
    modified_date: Mapped[int] = mapped_column(
        Integer,
        default=lambda: int(datetime.utcnow().timestamp()),
        nullable=False,
        onupdate=lambda: int(datetime.utcnow().timestamp())
    )

    # Relationships
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="asset_catalog_tags",
        back_populates="asset_items"
    )

    # Dependencies and dependents
    dependencies_rel: Mapped[List["AssetDependency"]] = relationship(
        "AssetDependency",
        foreign_keys="[AssetDependency.source_id]",
        back_populates="source_item",
        cascade="all, delete-orphan"
    )
    dependents_rel: Mapped[List["AssetDependency"]] = relationship(
        "AssetDependency",
        foreign_keys="[AssetDependency.target_id]",
        back_populates="target_item",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<AssetCatalogItem(id={self.id}, title='{self.title}', type='{self.asset_type}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the asset catalog item to a dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'asset_type': self.asset_type,
            'file_path': self.file_path,
            'language': self.language,
            'dependencies': self.dependencies,
            'asset_metadata': self.asset_metadata,
            'status': self.status,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'tags': [tag.name for tag in self.tags],
            'dependencies_count': len(self.dependencies_rel),
            'dependents_count': len(self.dependents_rel)
        }

class AssetCatalogTag(Base):
    """Association model for asset catalog items and tags."""
    __tablename__ = "asset_catalog_tags"

    asset_id: Mapped[int] = mapped_column(ForeignKey("asset_catalog_items.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)

    def __init__(self, asset_id: int, tag_id: int):
        self.asset_id = asset_id
        self.tag_id = tag_id

    @classmethod
    def create(cls, session: Session, asset_id: int, tag_id: int) -> "AssetCatalogTag":
        """Create a new asset catalog tag with validation."""
        # Check if asset and tag exist and are not deleted
        asset = session.query(AssetCatalogItem).filter_by(id=asset_id, deleted=False).first()
        tag = session.query(Tag).filter_by(id=tag_id, deleted=False).first()

        if not asset or not tag:
            raise ValueError("Asset or tag not found or is deleted")

        tag = cls(asset_id=asset_id, tag_id=tag_id)
        session.add(tag)
        return tag

class AssetDependency(Base):
    """Model for dependencies between asset catalog items."""
    __tablename__ = "asset_dependencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("asset_catalog_items.id"), nullable=False)
    target_id: Mapped[int] = mapped_column(ForeignKey("asset_catalog_items.id"), nullable=False)
    dependency_type: Mapped[str] = mapped_column(String, nullable=False)
    dependency_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_date: Mapped[int] = mapped_column(
        Integer,
        default=lambda: int(datetime.utcnow().timestamp()),
        nullable=False
    )

    # Relationships
    source_item: Mapped["AssetCatalogItem"] = relationship(
        "AssetCatalogItem",
        foreign_keys=[source_id],
        back_populates="dependencies_rel"
    )
    target_item: Mapped["AssetCatalogItem"] = relationship(
        "AssetCatalogItem",
        foreign_keys=[target_id],
        back_populates="dependents_rel"
    )

    __table_args__ = (
        UniqueConstraint('source_id', 'target_id', 'dependency_type',
                        name='unique_asset_dependency'),
    )

    def __repr__(self):
        return f"<AssetDependency(id={self.id}, source={self.source_id}, target={self.target_id})>"

# Add Tag relationship to asset items
Tag.asset_items = relationship(
    "AssetCatalogItem",
    secondary="asset_catalog_tags",
    back_populates="tags"
)
