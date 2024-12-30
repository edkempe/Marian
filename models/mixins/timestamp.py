"""Timestamp mixin for adding created_at and updated_at fields to models.

This mixin provides consistent timestamp tracking across models. For complete documentation
on database design decisions and schema details, see docs/database_design.md.

Usage:
    from models.mixins import TimestampMixin

    class MyModel(Base, TimestampMixin):
        __tablename__ = 'my_model'
        # ... other columns ...

Note: This mixin is the source of truth for timestamp columns. Any changes should be
made here first, then migrated to the database.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import Mapped, declarative_mixin


@declarative_mixin
class TimestampMixin:
    """Mixin that adds created_at and updated_at columns to a model.

    Key Fields:
    - created_at: When the record was created (UTC)
    - updated_at: When the record was last updated (UTC)

    Note: Both fields are non-nullable and default to UTC now.
    The updated_at field automatically updates on record changes.
    """

    created_at: Mapped[datetime] = Column(
        DateTime,
        default=func.now(),  # Use database timestamp
        nullable=False,
        doc="When this record was created (UTC)",
    )

    updated_at: Mapped[datetime] = Column(
        DateTime,
        default=func.now(),  # Use database timestamp
        onupdate=func.now(),  # Auto-update on changes
        nullable=False,
        doc="When this record was last updated (UTC)",
    )
