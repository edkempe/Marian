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
    
    # Test settings
    TEST: Dict[str, Union[str, int, float]]
    
    # Semantic analysis settings
    SEMANTIC: Dict[str, Union[str, int, float]]
    SEMANTIC_PROMPT: str
    
    # Search and pagination settings
    MAX_ITEMS_PER_PAGE: int
    DEFAULT_SEARCH_LIMIT: int
    MIN_SEARCH_CHARS: int
    MAX_SEARCH_TERMS: int
    RELEVANCE_THRESHOLD: float
    MAX_RELATED_ITEMS: int
    
    # Prompts for Claude AI
    PROMPTS: Dict[str, str]
    
    # Table names
    TABLES: Dict[str, str]
    
    # Column names
    COLUMNS: Dict[str, Dict[str, str]]
    
    # Relationship types
    RELATIONSHIP_TYPES: List[str]
    
    # Valid status values
    VALID_STATUSES: List[str]
    
    # Indexes
    INDEXES: Dict[str, List[str]]
    
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
    'CHAT_LOG': 'chat_history.log',
    
    # API settings
    'SEMANTIC_MODEL': 'claude-3-opus-20240229',
    'TEST_MODEL': 'claude-3-haiku-20240307',
    'MAX_TOKENS': 4096,
    'TEMPERATURE': 0.7,
    
    # Test settings
    'test': {
        'model': 'claude-3-haiku-20240307',
        'threshold': 0.7,
        'max_tokens': 1000
    },
    
    # Semantic analysis settings
    'semantic': {
        'threshold': 0.85,
        'min_score': 0.5,
        'max_results': 10,
        'model': 'claude-3-haiku-20240307',  # Use Haiku for faster catalog operations
        'max_tokens': 1000,  # Sufficient for catalog comparisons
        'temperature': 0,    # Deterministic results for consistency
        'similarity_types': [
            'exact match',
            'synonym',
            'broader term',
            'narrower term',
            'related concept'
        ]
    },
    'SEMANTIC_PROMPT': 'You are a helpful assistant analyzing catalog items.',
    
    # Search and pagination settings
    'MAX_ITEMS_PER_PAGE': 20,
    'DEFAULT_SEARCH_LIMIT': 10,
    'MIN_SEARCH_CHARS': 3,
    'MAX_SEARCH_TERMS': 5,
    'RELEVANCE_THRESHOLD': 0.75,
    'MAX_RELATED_ITEMS': 5,
    
    # Prompts for Claude AI
    'PROMPTS': {
        'QUERY_ANALYSIS': """You are a catalog query analyzer. Your task is to extract structured information from natural language queries.
        Return a JSON object with the following fields:
        - intent: The primary intent (search, add, update, delete, list)
        - entities: Named entities mentioned in the query
        - filters: Any filters like date ranges or tags
        - search_terms: Key terms for searching
        
        Keep your response focused and concise.""",
        
        'RELEVANCE_RANKING': """You are a catalog item ranker. Your task is to score the relevance of items to a query.
        Return a JSON array of floating point scores between 0 and 1, where 1 is most relevant.
        Consider:
        - Semantic similarity between query and item content
        - Presence of query terms in title/content
        - Overall context and meaning
        
        Keep scores relative and well-distributed."""
    },
    
    # Table names
    'TABLES': {
        'CATALOG_ITEMS': 'catalog_items',
        'TAGS': 'tags',
        'CATALOG_TAGS': 'catalog_tags',
        'ITEM_RELATIONSHIPS': 'item_relationships'
    },
    
    # Column names
    'COLUMNS': {
        'CATALOG_ITEMS': {
            'ID': 'id',
            'TITLE': 'title',
            'DESCRIPTION': 'description',
            'CONTENT': 'content',
            'SOURCE': 'source',
            'STATUS': 'status',
            'DELETED': 'deleted',
            'ARCHIVED_DATE': 'archived_date',
            'CREATED_DATE': 'created_date',
            'MODIFIED_DATE': 'modified_date',
            'CREATED_BY': 'created_by',
            'UPDATED_BY': 'updated_by',
            'ITEM_METADATA': 'item_metadata'
        },
        'TAGS': {
            'ID': 'id',
            'NAME': 'name',
            'DESCRIPTION': 'description',
            'DELETED': 'deleted',
            'ARCHIVED_DATE': 'archived_date',
            'CREATED_DATE': 'created_date',
            'MODIFIED_DATE': 'modified_date'
        },
        'CATALOG_TAGS': {
            'CATALOG_ID': 'catalog_id',
            'TAG_ID': 'tag_id'
        },
        'ITEM_RELATIONSHIPS': {
            'ID': 'id',
            'SOURCE_ID': 'source_id',
            'TARGET_ID': 'target_id',
            'RELATIONSHIP_TYPE': 'relationship_type',
            'CREATED_DATE': 'created_date',
            'RELATIONSHIP_METADATA': 'relationship_metadata'
        }
    },
    
    # Relationship types
    'RELATIONSHIP_TYPES': [
        'related_to',
        'parent_of',
        'child_of',
        'referenced_by',
        'references'
    ],
    
    # Valid status values
    'VALID_STATUSES': [
        'draft',
        'published',
        'archived'
    ],
    
    # Indexes
    'INDEXES': {
        'CATALOG_ITEMS': [
            'idx_catalog_items_title',
            'idx_catalog_items_status',
            'idx_catalog_items_created_date',
            'idx_catalog_items_modified_date',
            'idx_catalog_items_deleted'
        ],
        'TAGS': [
            'idx_tags_name',
            'idx_tags_deleted'
        ]
    },
    
    # Logging settings
    'LOG_FILE': 'catalog.log',
    'LOG_MAX_BYTES': 10485760,  # 10MB
    'LOG_BACKUP_COUNT': 5,
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'LOG_LEVEL': 'INFO',
    
    # Error messages
    'ERROR_MESSAGES': {
        'semantic_error': 'Error in semantic analysis: {error}',
        'database_error': 'Error accessing database: {error}',
        'duplicate_error': 'Item with similar title already exists: {title}',
        'tag_error': 'Error managing tags: {error}',
        'archive_error': 'Error archiving item: {error}',
        'validation_error': 'Validation error: {error}'
    }
}
