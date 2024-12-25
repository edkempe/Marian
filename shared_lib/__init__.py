"""
Shared library for Marian project containing common utilities and integrations.
"""

# External API integrations
from .anthropic_lib import parse_claude_response
from .gmail_lib import GmailAPI

# Database utilities
from .database_util import get_session
from .db_init_util import init_db
from .db_email_util import get_email_session

# Core utilities
from .network_util import check_long_urls
from .performance_util import cache, rate_limit, circuit_breaker, retry_operation, measure_time
from .schema_util import verify_schema, verify_code_usage
from .security_util import authenticate, validate_token, hash_password
from .logging_util import configure_logging

__all__ = [
    # External APIs
    'parse_claude_response',
    'GmailAPI',
    
    # Database
    'get_session',
    'init_db',
    'get_email_session',
    
    # Core utilities
    'check_long_urls',
    'cache',
    'rate_limit',
    'circuit_breaker',
    'retry_operation',
    'measure_time',
    'verify_schema',
    'verify_code_usage',
    'authenticate',
    'validate_token',
    'hash_password',
    'configure_logging',
]
