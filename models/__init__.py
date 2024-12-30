"""Models package initialization.

This module imports and exposes the main models used in the application.
"""

from models.asset_catalog import AssetCatalogItem, AssetCatalogTag, AssetDependency
from models.base import Base
from models.catalog import CatalogItem, CatalogTag, ItemRelationship, Tag
from models.domain_constants import (
    CONSTRAINTS,
    DEFAULTS,
    RELATIONSHIP_RULES,
    STATE_TRANSITIONS,
    AssetType,
    ItemStatus,
    RelationType,
)
from models.email import Email
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel
from models.mixins import TimestampMixin

__all__ = [
    # Models
    "Base",
    "Email",
    "EmailAnalysis",
    "CatalogItem",
    "Tag",
    "CatalogTag",
    "ItemRelationship",
    "AssetCatalogItem",
    "AssetCatalogTag",
    "AssetDependency",
    "GmailLabel",
    "TimestampMixin",
    # Domain Constants
    "AssetType",
    "ItemStatus",
    "RelationType",
    "CONSTRAINTS",
    "DEFAULTS",
    "STATE_TRANSITIONS",
    "RELATIONSHIP_RULES",
]
