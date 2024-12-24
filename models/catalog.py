"""SQLAlchemy models for the Marian Catalog system.

This module defines the data models for catalog items, tags, and their relationships.
Following the latest schema from migrations V1-V3, with proper SQLAlchemy relationships
and case-insensitive constraints.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, JSON, CheckConstraint, Index, text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from models.base import Base

class CatalogItem(Base):
    """Model for catalog items in the system."""
    __tablename__ = "catalog_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String)  # Source of the item
    status: Mapped[str] = mapped_column(
        String, 
        nullable=False,
        default='draft',
        server_default='draft'
    )
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_date: Mapped[Optional[int]] = mapped_column(Integer)  # UTC Unix timestamp
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
    created_by: Mapped[Optional[str]] = mapped_column(String)
    updated_by: Mapped[Optional[str]] = mapped_column(String)
    item_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Relationships
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="catalog_tags",
        back_populates="items"
    )
    
    __table_args__ = (
        CheckConstraint(
            status.in_(['draft', 'published', 'archived']),
            name='valid_status'
        ),
        Index('idx_catalog_items_title', text('title COLLATE NOCASE')),
        Index('idx_catalog_items_status', 'status'),
        Index('idx_catalog_items_created_date', 'created_date'),
        Index('idx_catalog_items_modified_date', 'modified_date'),
        Index('idx_catalog_items_deleted', 'deleted'),
    )
    
    def __repr__(self) -> str:
        return f"<CatalogItem(id={self.id}, title='{self.title}', status='{self.status}', deleted={self.deleted})>"

class Tag(Base):
    """Model for tags that can be applied to catalog items."""
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_date: Mapped[Optional[int]] = mapped_column(Integer)  # UTC Unix timestamp
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
    
    # Relationships
    items: Mapped[List["CatalogItem"]] = relationship(
        "CatalogItem",
        secondary="catalog_tags",
        back_populates="tags"
    )
    
    __table_args__ = (
        Index('idx_tags_name', text('name COLLATE NOCASE')),
        Index('idx_tags_deleted', 'deleted'),
    )
    
    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}', deleted={self.deleted})>"

class CatalogTag(Base):
    """Association model for the many-to-many relationship between CatalogItems and Tags."""
    __tablename__ = "catalog_tags"
    
    catalog_id: Mapped[int] = mapped_column(ForeignKey("catalog_items.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    
    def __repr__(self) -> str:
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
    relationship_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Relationships
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
    
    def __repr__(self) -> str:
        return f"<ItemRelationship(source_id={self.source_id}, type='{self.relationship_type}', target_id={self.target_id})>"

# Event listeners for case-insensitive uniqueness
@event.listens_for(CatalogItem, 'before_insert')
@event.listens_for(CatalogItem, 'before_update')
def catalog_item_before_save(mapper, connection, target):
    """Ensure case-insensitive uniqueness for catalog item titles."""
    if target.title:
        target.title = target.title.strip()
        # Check for case-insensitive duplicates
        stmt = text("SELECT 1 FROM catalog_items WHERE title = :title COLLATE NOCASE AND id != :id")
        params = {"title": target.title, "id": target.id or -1}
        result = connection.execute(stmt, params).scalar()
        if result:
            raise ValueError(f"A catalog item with title '{target.title}' (case-insensitive) already exists")

@event.listens_for(Tag, 'before_insert')
@event.listens_for(Tag, 'before_update')
def tag_before_save(mapper, connection, target):
    """Ensure case-insensitive uniqueness for tag names."""
    if target.name:
        target.name = target.name.strip()
        # Check for case-insensitive duplicates
        stmt = text("SELECT 1 FROM tags WHERE name = :name COLLATE NOCASE AND id != :id")
        params = {"name": target.name, "id": target.id or -1}
        result = connection.execute(stmt, params).scalar()
        if result:
            raise ValueError(f"A tag with name '{target.name}' (case-insensitive) already exists")
