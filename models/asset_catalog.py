"""Models for code and document asset catalogs."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import (
    String, Integer, Text, Boolean, JSON, ForeignKey, UniqueConstraint,
    event, and_, or_, Index, text, DateTime
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship, Session, validates
)
from models.base import Base
from models.catalog import CatalogItem, Tag, CatalogTag
from models.domain_constants import (
    AssetType, ItemStatus, RelationType, CONSTRAINTS, 
    DEFAULTS, STATE_TRANSITIONS, RELATIONSHIP_RULES
)

class AssetCatalogItem(Base):
    """Model for code and document assets in the catalog."""
    __tablename__ = "asset_catalog_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text(2000), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default='draft')
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    archived_date: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_date: Mapped[int] = mapped_column(Integer, nullable=False)
    modified_date: Mapped[int] = mapped_column(Integer, nullable=False)
    item_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="asset_catalog_tags",
        back_populates="asset_items"
    )
    
    dependencies: Mapped[List["AssetDependency"]] = relationship(
        "AssetDependency",
        foreign_keys="[AssetDependency.source_id]",
        back_populates="source_item",
        cascade="all, delete-orphan"
    )
    
    dependents: Mapped[List["AssetDependency"]] = relationship(
        "AssetDependency",
        foreign_keys="[AssetDependency.target_id]",
        back_populates="target_item",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        """Return string representation."""
        return f"<AssetCatalogItem(id={self.id}, title='{self.title}', status='{self.status}')>"

class AssetCatalogTag(Base):
    """Association model for asset catalog items and tags."""
    __tablename__ = "asset_catalog_tags"

    asset_id: Mapped[int] = mapped_column(ForeignKey("asset_catalog_items.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)

    def __init__(self, asset_id: int, tag_id: int):
        self.asset_id = asset_id
        self.tag_id = tag_id

    def __repr__(self):
        """Return string representation."""
        return f"<AssetCatalogTag(asset_id={self.asset_id}, tag_id={self.tag_id})>"

class AssetDependency(Base):
    """Model for dependencies between asset catalog items."""
    __tablename__ = "asset_dependencies"

    source_id: Mapped[int] = mapped_column(ForeignKey("asset_catalog_items.id"), primary_key=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("asset_catalog_items.id"), primary_key=True)
    dependency_type: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    dependency_metadata: Mapped[Optional[str]] = mapped_column("metadata", Text, nullable=True)

    # Relationships
    source_item: Mapped["AssetCatalogItem"] = relationship(
        "AssetCatalogItem",
        foreign_keys=[source_id],
        back_populates="dependencies"
    )
    target_item: Mapped["AssetCatalogItem"] = relationship(
        "AssetCatalogItem",
        foreign_keys=[target_id],
        back_populates="dependents"
    )

    def __repr__(self):
        """Return string representation."""
        return f"<AssetDependency(source={self.source_id}, target={self.target_id}, type='{self.dependency_type}')>"

# Add Tag relationship to asset items
Tag.asset_items = relationship(
    "AssetCatalogItem",
    secondary="asset_catalog_tags",
    back_populates="tags"
)
