"""
Shared library for Marian project containing common utilities and integrations.
"""

# External API integrations
from .anthropic_lib import parse_claude_response

# Database utilities
from .database_session_util import (
    get_analysis_session,
    get_catalog_session,
    get_email_session,
)
from .gmail_lib import GmailAPI

# Core utilities
from .logging_util import setup_logging

__all__ = [
    # External APIs
    "parse_claude_response",
    "GmailAPI",
    # Database
    "get_email_session",
    "get_analysis_session",
    "get_catalog_session",
    # Core
    "setup_logging",
]
