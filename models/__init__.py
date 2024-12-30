"""Models package initialization.

This module provides convenient access to all models while maintaining proper import paths.
Always use absolute imports (from models.email import Email) rather than relative imports
to prevent SQLAlchemy model resolution issues.
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
from models.email_analysis import EmailAnalysis, EmailAnalysisResponse
from models.gmail_label import GmailLabel
from models.mixins import TimestampMixin

__all__ = [
    # Models
    "Base",
    "Email",
    "EmailAnalysis",
    "EmailAnalysisResponse",
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
