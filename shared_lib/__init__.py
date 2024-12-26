"""
Shared library for Marian project containing common utilities and integrations.
"""

# External API integrations
from .anthropic_lib import parse_claude_response
from .gmail_lib import GmailAPI

# Database utilities
from .database_util import get_email_session

# Core utilities
from .logging_util import setup_logging

__all__ = [
    # External APIs
    'parse_claude_response',
    'GmailAPI',
    
    # Database
    'get_email_session',
    
    # Core utilities
    'setup_logging',
]
