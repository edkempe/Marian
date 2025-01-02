"""Configuration package.

This package provides a centralized location for all configuration settings.
It follows the 12-Factor App methodology for configuration management:
https://12factor.net/config

Usage:
    from config import settings, env_settings

    db_url = settings.database_settings.URL
    is_production = env_settings.ENV.is_production
"""

from config.environment import env_settings
from config.settings import (
    api_settings,
    database_settings,
    email_settings,
    logging_settings,
    security_settings,
)

__all__ = [
    'env_settings',
    'api_settings',
    'database_settings',
    'email_settings',
    'logging_settings',
    'security_settings',
]
