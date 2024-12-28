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
from models.domain_constants import (
    AssetType, ItemStatus, RelationType, CONSTRAINTS, 
    DEFAULTS, STATE_TRANSITIONS, RELATIONSHIP_RULES
)

class AssetCatalogItem(Base):
    """Model for code and document assets in the catalog."""
    __tablename__ = "asset_catalog_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(
        String(CONSTRAINTS['title_max_length']), 
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text(CONSTRAINTS['description_max_length'])
    )
    asset_type: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    language: Mapped[Optional[str]] = mapped_column(String)
    content: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String, 
        nullable=False,
        default=ItemStatus.DRAFT,
        server_default=ItemStatus.DRAFT
    )
    deleted: Mapped[bool] = mapped_column(
        Boolean, 
        default=DEFAULTS['deleted'], 
        nullable=False
    )
    archived_date: Mapped[Optional[int]] = mapped_column(Integer)
    created_date: Mapped[int] = mapped_column(
        Integer,
        default=lambda: int(datetime.utcnow().timestamp()),
        nullable=False
    )
    modified_date: Mapped[int] = mapped_column(
        Integer,
        default=lambda: int(datetime.utcnow().timestamp()),
        onupdate=lambda: int(datetime.utcnow().timestamp()),
        nullable=False
    )
    asset_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Relationships
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="asset_catalog_tags",
        back_populates="asset_items"
    )
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

    __table_args__ = (
        Index('idx_asset_catalog_items_title', text('title COLLATE NOCASE')),
        Index('idx_asset_catalog_items_file_path', text('file_path COLLATE NOCASE')),
        Index('idx_asset_catalog_items_type', 'asset_type'),
        Index('idx_asset_catalog_items_status', 'status'),
        Index('idx_asset_catalog_items_deleted', 'deleted'),
    )

    @validates('title')
    def validate_title(self, key, value):
        """Validate title length."""
        if len(value) < CONSTRAINTS['title_min_length']:
            raise ValueError(
                f"Title must be at least {CONSTRAINTS['title_min_length']} characters"
            )
        return value

    @validates('status')
    def validate_status(self, key, value):
        """Validate status transitions."""
        if not hasattr(self, 'status'):
            return value
            
        if value not in [s.value for s in ItemStatus]:
            raise ValueError(f"Invalid status: {value}")
            
        current = self.status
        if current and value not in [s.value for s in STATE_TRANSITIONS[ItemStatus(current)]]:
            raise ValueError(
                f"Invalid status transition from {current} to {value}"
            )
        
        return value

    @validates('asset_type')
    def validate_asset_type(self, key, value):
        """Validate asset type."""
        if value not in [t.value for t in AssetType]:
            raise ValueError(f"Invalid asset type: {value}")
        return value

    def __repr__(self):
        return f"<AssetCatalogItem(id={self.id}, title='{self.title}', type='{self.asset_type}')>"

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("asset_catalog_items.id"), nullable=False)
    target_id: Mapped[int] = mapped_column(ForeignKey("asset_catalog_items.id"), nullable=False)
    dependency_type: Mapped[str] = mapped_column(String, nullable=False)
    dependency_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_date: Mapped[int] = mapped_column(
        Integer,
        default=lambda: int(datetime.utcnow().timestamp()),
        nullable=False
    )

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
        Index('idx_asset_dependencies_source', 'source_id'),
        Index('idx_asset_dependencies_target', 'target_id'),
        Index('idx_asset_dependencies_type', 'dependency_type'),
    )

    @validates('dependency_type')
    def validate_dependency_type(self, key, value):
        """Validate dependency type."""
        if value not in [r.value for r in RelationType]:
            raise ValueError(f"Invalid dependency type: {value}")
        return value

    @validates('source_id', 'target_id')
    def validate_ids(self, key, value):
        """Validate that neither source nor target is archived."""
        session = object_session(self)
        if session is None:
            return value

        item = session.query(AssetCatalogItem).get(value)
        if item and item.status == ItemStatus.ARCHIVED:
            raise ValueError(
                f"Cannot create dependency with archived item (id={value})"
            )
        return value

    def __repr__(self):
        return f"<AssetDependency(id={self.id}, type='{self.dependency_type}')>"

# Add Tag relationship to asset items
Tag.asset_items = relationship(
    "AssetCatalogItem",
    secondary="asset_catalog_tags",
    back_populates="tags"
)
