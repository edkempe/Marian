"""Marian shared library.

This package contains shared functionality used across the Marian project:
- anthropic_helper: Anthropic API integration utilities
"""

from .anthropic_helper import (
    get_anthropic_client,
    test_anthropic_connection,
    mock_anthropic_client,
    mock_anthropic
)

__version__ = '0.1.0'
__all__ = [
    'get_anthropic_client',
    'test_anthropic_connection',
    'mock_anthropic_client',
    'mock_anthropic'
]
