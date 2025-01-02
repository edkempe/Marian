"""Date and time utilities for the Jexi project."""

from datetime import datetime
from typing import Optional

def format_iso_date(date: datetime) -> str:
    """Format date in ISO format."""
    return date.isoformat()

def parse_iso_date(date_str: str) -> Optional[datetime]:
    """Parse ISO format date string."""
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None
