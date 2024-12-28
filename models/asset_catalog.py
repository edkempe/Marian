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
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="asset_catalog_tags",
        back_populates="asset_items"
    )

    def __repr__(self):
        """Return string representation."""
        return f"<AssetCatalogItem(id={self.id}, name='{self.name}', type='{self.asset_type}')>"

class AssetCatalogTag(Base):
    """Association model for asset catalog items and tags."""
    __tablename__ = "asset_catalog_tags"

    asset_id: Mapped[int] = mapped_column(ForeignKey("asset_catalog_items.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)

    def __init__(self, asset_id: int, tag_id: int):
        self.asset_id = asset_id
        self.tag_id = tag_id

    @validates('asset_id', 'tag_id')
    def validate_ids(self, key, value):
        """Validate that neither asset nor tag is archived."""
        session = object_session(self)
        if session is None:
            return value

        if key == 'asset_id':
            asset = session.query(AssetCatalogItem).get(value)
            if asset and asset.status == ItemStatus.ARCHIVED:
                raise ValueError("Cannot tag an archived asset")
        elif key == 'tag_id':
            tag = session.query(Tag).get(value)
            if tag and tag.deleted:
                raise ValueError("Cannot use a deleted tag")
        return value

    @classmethod
    def create(cls, session: Session, asset_id: int, tag_id: int) -> "AssetCatalogTag":
        """Create a new asset catalog tag with validation."""
        tag = cls(asset_id=asset_id, tag_id=tag_id)
        session.add(tag)
        return tag

    def __repr__(self):
        return f"<AssetCatalogTag(asset_id={self.asset_id}, tag_id={self.tag_id})>"

class AssetDependency(Base):
    """Model for dependencies between asset catalog items."""
    __tablename__ = "asset_dependencies"

    source_id: Mapped[int] = mapped_column(ForeignKey("asset_catalog_items.id"), primary_key=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("asset_catalog_items.id"), primary_key=True)
    dependency_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

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

    def __repr__(self):
        """Return string representation."""
        return f"<AssetDependency(source={self.source_id}, target={self.target_id}, type='{self.dependency_type}')>"

# Add Tag relationship to asset items
Tag.asset_items = relationship(
    "AssetCatalogItem",
    secondary="asset_catalog_tags",
    back_populates="tags"
)
