"""Domain constants for the Marian project.

This module defines the core domain constants that shape the business rules and
model behavior. These constants are the authoritative source for all domain-specific
values and constraints.

Key Principles:
1. No dependencies on other project modules
2. Only contain domain-specific constants
3. Used to enforce business rules and constraints
4. Source of truth for valid values in the domain

Note:
    This is separate from shared_lib.constants which handles application configuration.
    These constants define the domain rules and constraints that shape our models.
"""

from enum import Enum, auto
from typing import List, Dict, Any

class AssetType(str, Enum):
    """Valid asset types in the domain.
    
    Using string enum ensures:
    1. Type safety
    2. Serialization compatibility
    3. String representation
    4. Value validation
    """
    CODE = 'code'
    DOCUMENT = 'document'
    TEST = 'test'
    CONFIG = 'config'
    SCRIPT = 'script'

class ItemStatus(str, Enum):
    """Valid status values for catalog items."""
    DRAFT = 'draft'
    REVIEW = 'review'
    APPROVED = 'approved'
    ARCHIVED = 'archived'

class RelationType(str, Enum):
    """Valid relationship types between items."""
    DEPENDS_ON = 'depends_on'
    RELATED_TO = 'related_to'
    SUPERSEDES = 'supersedes'
    IMPLEMENTS = 'implements'
    TESTS = 'tests'

# Domain-level constraints
CONSTRAINTS = {
    'title_min_length': 3,
    'title_max_length': 255,
    'description_max_length': 2000,
    'tag_min_length': 2,
    'tag_max_length': 50,
}

# Default values (these are part of the domain rules)
DEFAULTS = {
    'status': ItemStatus.DRAFT,
    'deleted': False,
    'language': None,
    'content': None,
    'description': None,
    'source': None,
    'metadata': None,
}

# Valid state transitions (part of domain rules)
STATE_TRANSITIONS = {
    ItemStatus.DRAFT: [ItemStatus.REVIEW, ItemStatus.ARCHIVED],
    ItemStatus.REVIEW: [ItemStatus.APPROVED, ItemStatus.DRAFT, ItemStatus.ARCHIVED],
    ItemStatus.APPROVED: [ItemStatus.ARCHIVED],
    ItemStatus.ARCHIVED: [ItemStatus.DRAFT],
}

# Relationship rules (which types are valid for which asset types)
RELATIONSHIP_RULES = {
    AssetType.CODE: {
        AssetType.CODE: [RelationType.DEPENDS_ON, RelationType.RELATED_TO, RelationType.SUPERSEDES],
        AssetType.TEST: [RelationType.TESTS],
        AssetType.DOCUMENT: [RelationType.IMPLEMENTS],
    },
    AssetType.TEST: {
        AssetType.CODE: [RelationType.TESTS],
        AssetType.TEST: [RelationType.RELATED_TO],
    },
    AssetType.DOCUMENT: {
        AssetType.CODE: [RelationType.IMPLEMENTS],
        AssetType.DOCUMENT: [RelationType.RELATED_TO, RelationType.SUPERSEDES],
    },
}
