"""Base model for SQLAlchemy.

This module provides the base SQLAlchemy model class that all other models should inherit from.
To maintain consistency and avoid model resolution issues, follow these guidelines:

1. Always use absolute imports when importing models:
   from models.email import Email  # Good
   from .email import Email        # Avoid
   from ..models.email import Email  # Avoid

2. Always use fully qualified paths in relationships:
   relationship("models.email.Email", ...)  # Good
   relationship("Email", ...)               # Avoid

3. Keep model names unique across the application to prevent conflicts
"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass
