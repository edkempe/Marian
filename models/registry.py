"""Model registry for SQLAlchemy.

This module ensures all models are registered with SQLAlchemy before database operations.
Import this module before creating database engines or sessions.
"""

from models.asset_catalog import AssetCatalogItem, AssetCatalogTag, AssetDependency
from models.base import Base
from models.email import Email
from models.email_analysis import EmailAnalysis

# Import all models here to ensure they are registered with SQLAlchemy
__all__ = [
    "Base",
    "EmailAnalysis",
    "Email",
    "AssetCatalogItem",
    "AssetCatalogTag",
    "AssetDependency",
]
