"""Utility functions for the Marian project."""

from .util_check_urls import check_long_urls
from .util_db_init import init_db as initialize_database
from .logging_config import setup_logging, log_error, log_api_response, log_db_operation
from .util_scalability import cache, rate_limit, circuit_breaker, retry_operation, measure_time
from .util_schema_verify import verify_schema, verify_code_usage
from .util_security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    encrypt_data,
    decrypt_data,
    sanitize_email_content,
    validate_api_key,
    check_permissions
)
from .util_test_data import generate_test_data, load_test_fixtures, EmailProcessor

__all__ = [
    'check_long_urls',
    'initialize_database',
    'setup_logging',
    'log_error',
    'log_api_response',
    'log_db_operation',
    'cache',
    'rate_limit',
    'circuit_breaker',
    'retry_operation',
    'measure_time',
    'verify_schema',
    'verify_code_usage',
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'verify_token',
    'encrypt_data',
    'decrypt_data',
    'sanitize_email_content',
    'validate_api_key',
    'check_permissions',
    'generate_test_data',
    'load_test_fixtures',
    'EmailProcessor'
]
