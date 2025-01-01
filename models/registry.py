"""Model registry for SQLAlchemy."""

from sqlalchemy.orm import registry

from models.base import Base
from models.email import EmailMessage
from models.email_analysis import EmailAnalysis
from models.catalog import CatalogEntry


# Create registry and map all models
mapper_registry = registry()
mapper_registry.configure()

# Export Base for use in tests
__all__ = ["Base"]
