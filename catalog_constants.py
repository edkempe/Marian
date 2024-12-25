"""Constants for the Marian Catalog System.

This module contains all configuration settings and constants used by the catalog
components of the Marian project. These settings are specific to catalog functionality
and are kept separate from other Marian components to avoid confusion.

Configuration Sections:
    - DATABASE: Database paths and connection settings
    - API: Claude API settings for semantic analysis
    - SEMANTIC: Settings for semantic matching and analysis
    - SEARCH: Search and pagination settings
    - TABLES: Database table names
    - RELATIONSHIPS: Valid relationship types
    - LOGGING: Log file settings and formats
    - ERROR_MESSAGES: Standard error message templates
"""

from typing import Dict, List, Union, TypedDict

class CatalogConfig(TypedDict):
    """Type hints for catalog configuration."""
    # Database settings
    DB_FILE: str
    DB_URL: str
    CHAT_LOG: str
    
    # API settings
    SEMANTIC_MODEL: str
    TEST_MODEL: str
    MAX_TOKENS: int
    TEMPERATURE: float
    
    # Semantic analysis settings
    SEMANTIC_THRESHOLD: float
    SEMANTIC_PROMPT: str
    
    # Search and pagination settings
    MAX_ITEMS_PER_PAGE: int
    DEFAULT_SEARCH_LIMIT: int
    MIN_SEARCH_CHARS: int
    MAX_SEARCH_TERMS: int
    RELEVANCE_THRESHOLD: float
    MAX_RELATED_ITEMS: int
    
    # Table names
    TABLES: Dict[str, str]
    
    # Relationship types
    RELATIONSHIP_TYPES: List[str]
    
    # Logging settings
    LOG_FILE: str
    LOG_MAX_BYTES: int
    LOG_BACKUP_COUNT: int
    LOG_FORMAT: str
    LOG_LEVEL: str
    
    # Error messages
    ERROR_MESSAGES: Dict[str, str]

# Catalog Configuration
CATALOG_CONFIG: CatalogConfig = {
    # Database Settings
    'DB_FILE': 'db_catalog.db',
    'DB_URL': 'sqlite:///db_catalog.db',
    'CHAT_LOG': 'chat_logs.jsonl',
    
    # API Settings
    'SEMANTIC_MODEL': 'claude-3-opus-20240229',  # Model for production use
    'TEST_MODEL': 'claude-3-haiku-20240307',     # Faster model for testing
    'MAX_TOKENS': 1000,
    'TEMPERATURE': 0.0,  # Zero temperature for consistent outputs
    
    # Semantic Analysis Settings
    'SEMANTIC_THRESHOLD': 0.7,  # Threshold for semantic similarity matches
    
    # Search and Pagination Settings
    'MAX_ITEMS_PER_PAGE': 50,
    'DEFAULT_SEARCH_LIMIT': 10,
    'MIN_SEARCH_CHARS': 3,
    'MAX_SEARCH_TERMS': 10,
    'RELEVANCE_THRESHOLD': 0.7,
    'MAX_RELATED_ITEMS': 5,
    
    # Table Names
    'TABLES': {
        'CATALOG': 'catalog_items',
        'TAGS': 'tags',
        'CATALOG_TAGS': 'catalog_tags',
        'CHAT_HISTORY': 'chat_history',
        'RELATIONSHIPS': 'item_relationships'
    },
    
    # Valid Relationship Types
    'RELATIONSHIP_TYPES': [
        'related_to',
        'parent_of',
        'child_of',
        'references',
        'referenced_by',
        'derived_from',
        'supersedes',
        'superseded_by',
    ],
    
    # Logging Settings
    'LOG_FILE': 'catalog.log',
    'LOG_MAX_BYTES': 10485760,  # 10MB
    'LOG_BACKUP_COUNT': 5,
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'LOG_LEVEL': 'INFO',
    
    # Semantic Analysis Prompt
    'SEMANTIC_PROMPT': '''Please analyze the semantic similarity between the following text and each item in the list. Consider not just word overlap but meaning and context.

For each item, determine if it is semantically similar to the text, considering:
1. Core meaning and intent
2. Subject matter and domain
3. Level of specificity
4. Context and usage

Return only items that are truly semantically similar (sharing the same core meaning/topic), not just superficially similar.

Text to compare: {text}

Items to check:
{items}

For each item that is semantically similar (sharing the same core topic/meaning), return it and its similarity score (0-1) in this format:
[("item text", similarity_score), ...]

Only include items with similarity >= {threshold}. Return an empty list if no items are similar enough.

Example responses:
- For "Python Tutorial" and ["Python Guide", "Snake Care"]:
  [("Python Guide", 0.85)]  # High similarity in programming context
- For "Python Snake" and ["Python Guide"]:
  []  # Different contexts (animal vs programming)''',
    
    # Error Messages
    'ERROR_MESSAGES': {
        'semantic_error': 'Error in semantic analysis: {error}',
        'database_error': 'Error accessing database: {error}',
        'validation_error': 'Error validating input: {error}',
        'archive_error': 'Error archiving item: {error}',
        'item_not_found': 'Item not found in catalog',
        'tag_not_found': 'Tag not found',
        'invalid_relationship': 'Invalid relationship type',
        'duplicate_item': 'Item already exists in catalog',
        'duplicate_tag': 'Tag already exists',
        'invalid_search': 'Invalid search query'
    }
}
