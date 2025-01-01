"""Model package initialization."""

from models.base import Base
from models.email import EmailMessage
from models.email_analysis import EmailAnalysis
from models.catalog import CatalogEntry

__all__ = [
    "Base",
    "EmailMessage",
    "EmailAnalysis",
    "CatalogEntry",
]
