"""Documentation standards package.

This package provides a centralized location for all documentation standards,
validation rules, and utilities used throughout the project's development tools.

Usage:
    from tools.standards import DocumentationStandards
    from tools.standards.validators import validate_doc, validate_all
"""

from .constants import DocumentationStandards
from .validators import validate_doc, validate_all

__all__ = ['DocumentationStandards', 'validate_doc', 'validate_all']
