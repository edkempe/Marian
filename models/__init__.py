"""Model package initialization."""

from models.base import Base
from models.email import EmailMessage
from models.analysis import EmailAnalysis
from models.catalog import CatalogItem
from models.label import GmailLabel
from models.tags import Tag
from models.relationships import ItemRelationship

__all__ = [
    "Base",
    "EmailMessage",
    "EmailAnalysis",
    "CatalogItem",
    "GmailLabel",
    "Tag",
    "ItemRelationship",
]
