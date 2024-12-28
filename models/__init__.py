"""Models package initialization.

This module provides convenient access to all models while maintaining proper import paths.
Always use absolute imports (from models.email import Email) rather than relative imports
to prevent SQLAlchemy model resolution issues.
"""

from models.base import Base
from models.email import Email
from models.email_analysis import EmailAnalysis, EmailAnalysisResponse
from models.catalog import Catalog
from models.asset_catalog import AssetCatalog
from models.gmail_label import GmailLabel
from models.mixins import TimestampMixin

__all__ = [
    'Base',
    'Email',
    'EmailAnalysis',
    'EmailAnalysisResponse',
    'Catalog',
    'AssetCatalog',
    'GmailLabel',
    'TimestampMixin'
]
