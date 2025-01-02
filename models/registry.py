"""Model registry."""

from sqlalchemy.orm import registry

from models.base import Base
from models.email_message import EmailMessage
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel
from models.catalog_item import CatalogItem
from models.tag import Tag
from models.item_relationship import ItemRelationship

# Create registry
mapper_registry = registry()

# Configure registry with all models
mapper_registry.configure()

# Export Base for use in tests
__all__ = ["Base"]
