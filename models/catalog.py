"""SQLAlchemy models for the Marian Catalog system.

This module defines the data models for catalog items, tags, and their relationships.
Following the latest schema from migrations V1-V3, with proper SQLAlchemy relationships
and case-insensitive constraints.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Integer, String, Text, Boolean, ForeignKey, JSON, 
    CheckConstraint, Index, text, event
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship, Session, 
    validates, object_session
)
from sqlalchemy.sql import func
from models.base import Base
from models.domain_constants import (
    ItemStatus, RelationType, CONSTRAINTS, 
    DEFAULTS, STATE_TRANSITIONS
)

class CatalogItem(Base):
    """Model for catalog items in the system."""
    __tablename__ = "catalog_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(
        String(CONSTRAINTS['title_max_length']), 
        nullable=False, 
        unique=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text(CONSTRAINTS['description_max_length'])
    )
    content: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String)
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
    item_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="catalog_tags",
        back_populates="items"
    )

    __table_args__ = (
        Index('idx_catalog_items_title', text('title COLLATE NOCASE')),
        Index('idx_catalog_items_status', 'status'),
        Index('idx_catalog_items_deleted', 'deleted'),
    )

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

    @validates('title')
    def validate_title(self, key, value):
        """Validate title length and uniqueness."""
        if len(value) < CONSTRAINTS['title_min_length']:
            raise ValueError(
                f"Title must be at least {CONSTRAINTS['title_min_length']} characters"
            )
        return value

    def __repr__(self):
        return f"<CatalogItem(id={self.id}, title='{self.title}', status='{self.status}')>"

class Tag(Base):
    """Model for tags that can be applied to catalog items."""
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(CONSTRAINTS['tag_max_length']), 
        nullable=False, 
        unique=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text)
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
    items: Mapped[List["CatalogItem"]] = relationship(
        "CatalogItem",
        secondary="catalog_tags",
        back_populates="tags"
    )

    __table_args__ = (
        Index('idx_tags_name', text('name COLLATE NOCASE')),
        Index('idx_tags_deleted', 'deleted'),
    )

    @validates('name')
    def validate_name(self, key, value):
        """Validate tag name length."""
        if len(value) < CONSTRAINTS['tag_min_length']:
            raise ValueError(
                f"Tag name must be at least {CONSTRAINTS['tag_min_length']} characters"
            )
        return value

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"

class CatalogTag(Base):
    """Association model for the many-to-many relationship between CatalogItems and Tags."""
    __tablename__ = "catalog_tags"

    catalog_id: Mapped[int] = mapped_column(ForeignKey("catalog_items.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)

    def __init__(self, catalog_id: int, tag_id: int):
        self.catalog_id = catalog_id
        self.tag_id = tag_id

    @validates('catalog_id', 'tag_id')
    def validate_ids(self, key, value):
        """Validate that neither item nor tag is archived."""
        session = object_session(self)
        if session is None:
            return value

        if key == 'catalog_id':
            item = session.query(CatalogItem).get(value)
            if item and item.status == ItemStatus.ARCHIVED:
                raise ValueError("Cannot tag an archived item")
        elif key == 'tag_id':
            tag = session.query(Tag).get(value)
            if tag and tag.deleted:
                raise ValueError("Cannot use a deleted tag")
        return value

    @classmethod
    def create(cls, session: Session, catalog_id: int, tag_id: int) -> "CatalogTag":
        """Create a new catalog tag with validation."""
        tag = cls(catalog_id=catalog_id, tag_id=tag_id)
        session.add(tag)
        return tag

    def __repr__(self):
        return f"<CatalogTag(catalog_id={self.catalog_id}, tag_id={self.tag_id})>"

class ItemRelationship(Base):
    """Model for relationships between catalog items."""
    __tablename__ = "item_relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("catalog_items.id"), nullable=False)
    target_id: Mapped[int] = mapped_column(ForeignKey("catalog_items.id"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[int] = mapped_column(
        Integer,
        default=lambda: int(datetime.utcnow().timestamp()),
        nullable=False
    )
    relationship_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    source_item: Mapped["CatalogItem"] = relationship(
        "CatalogItem",
        foreign_keys=[source_id],
        backref="outgoing_relationships"
    )
    target_item: Mapped["CatalogItem"] = relationship(
        "CatalogItem",
        foreign_keys=[target_id],
        backref="incoming_relationships"
    )

    __table_args__ = (
        Index('idx_relationships_source', 'source_id'),
        Index('idx_relationships_target', 'target_id'),
        Index('idx_relationships_type', 'relationship_type'),
    )

    @validates('relationship_type')
    def validate_relationship_type(self, key, value):
        """Validate relationship type."""
        if value not in [r.value for r in RelationType]:
            raise ValueError(f"Invalid relationship type: {value}")
        return value

    @validates('source_id', 'target_id')
    def validate_ids(self, key, value):
        """Validate that neither source nor target is archived."""
        session = object_session(self)
        if session is None:
            return value

        item = session.query(CatalogItem).get(value)
        if item and item.status == ItemStatus.ARCHIVED:
            raise ValueError(
                f"Cannot create relationship with archived item (id={value})"
            )
        return value

    def __repr__(self):
        return f"<ItemRelationship(id={self.id}, type='{self.relationship_type}')>"

# Event listeners for case-insensitive uniqueness
@event.listens_for(CatalogItem, 'before_insert')
@event.listens_for(CatalogItem, 'before_update')
def catalog_item_before_save(mapper, connection, target):
    """Ensure case-insensitive uniqueness for catalog item titles."""
    if target.title is None:
        return
        
    stmt = text(
        "SELECT 1 FROM catalog_items WHERE lower(title) = lower(:title) "
        "AND id != :id"
    )
    existing = connection.execute(
        stmt, 
        {"title": target.title, "id": target.id or -1}
    ).first()
    
    if existing:
        raise ValueError(f"Title '{target.title}' already exists (case-insensitive)")

@event.listens_for(Tag, 'before_insert')
@event.listens_for(Tag, 'before_update')
def tag_before_save(mapper, connection, target):
    """Ensure case-insensitive uniqueness for tag names."""
    if target.name is None:
        return
        
    stmt = text(
        "SELECT 1 FROM tags WHERE lower(name) = lower(:name) "
        "AND id != :id"
    )
    existing = connection.execute(
        stmt, 
        {"name": target.name, "id": target.id or -1}
    ).first()
    
    if existing:
        raise ValueError(f"Tag name '{target.name}' already exists (case-insensitive)")
