"""Testing-related constants."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Set

@dataclass(frozen=True)
class TestingConstants:
    """Testing-related constants."""
    
    # Test Data
    TEST_USER: Dict[str, Any] = field(default_factory=lambda: {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
    })
    
    # Test Timeouts
    TEST_TIMEOUT: int = 5  # seconds
    INTEGRATION_TEST_TIMEOUT: int = 30  # seconds
    
    # Test Database
    TEST_DATABASE: Dict[str, Any] = field(default_factory=lambda: {
        "name": "test_db",
        "host": "localhost",
        "port": 5432,
    })
    
    # Test Environment
    TEST_ENV: Dict[str, str] = field(default_factory=lambda: {
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "DEBUG",
        "DISABLE_AUTH": "true",
        "MOCK_EXTERNAL_SERVICES": "true",
    })
    
    # Test Files
    TEST_FILES: Dict[str, str] = field(default_factory=lambda: {
        "small": "test_data/small.txt",
        "medium": "test_data/medium.pdf",
        "large": "test_data/large.docx",
    })
    
    # Test API
    TEST_API: Dict[str, str] = field(default_factory=lambda: {
        "base_url": "http://localhost:8000",
        "test_token": "test_token_123",
        "mock_responses": "test_data/mock_responses.json",
    })
    
    # Required Versioning
    REQUIRED_VERSIONING: Dict[str, str] = field(default_factory=lambda: {
        "python": ">=3.8",
        "pytest": ">=6.0.0",
        "sqlalchemy": ">=1.4.0",
    })
    
    # Excluded Directories
    EXCLUDED_DIRS: Set[str] = field(default_factory=lambda: {
        ".git",
        ".pytest_cache",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        "build",
        "dist",
    })
    
    # Test Configuration
    TEST_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "batch_size": 10,
        "max_retries": 3,
        "timeout": 30,
        "cache_ttl": 3600,
    })
    
    def __getitem__(self, key: str) -> Any:
        """Make the class subscriptable."""
        return getattr(self, key)

# Singleton instance
TESTING_CONFIG = TestingConstants()
