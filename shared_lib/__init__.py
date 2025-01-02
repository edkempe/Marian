"""
Shared library for Marian project containing common utilities and integrations.
"""

# Core utilities
from .logging_util import setup_logging

# Lazy imports to avoid dependency issues
def get_email_session():
    from .database_session_util import get_email_session as _get_email_session
    return _get_email_session()

def get_analysis_session():
    from .database_session_util import get_analysis_session as _get_analysis_session
    return _get_analysis_session()

def get_catalog_session():
    from .database_session_util import get_catalog_session as _get_catalog_session
    return _get_catalog_session()

def parse_claude_response():
    from .anthropic_lib import parse_claude_response as _parse_claude_response
    return _parse_claude_response()

def get_gmail_api():
    from .gmail_lib import GmailAPI
    return GmailAPI()

__all__ = [
    # External APIs
    "parse_claude_response",
    "get_gmail_api",
    # Database
    "get_email_session",
    "get_analysis_session",
    "get_catalog_session",
    # Core
    "setup_logging",
]
