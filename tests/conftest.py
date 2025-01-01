"""Test configuration and fixtures."""

import os
import shutil
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.registry import Base
from config.test_settings import test_settings
from shared_lib.database_session_util import (
    Session,
    EmailSessionFactory,
    AnalysisSessionFactory,
    CatalogSessionFactory,
)


@pytest.fixture(scope="session")
def test_data_dir():
    """Create and manage test data directory."""
    test_dir = test_settings.TEST_DATA_DIR
    test_dir.mkdir(parents=True, exist_ok=True)
    
    yield test_dir
    
    # Clean up test directory after all tests
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture(scope="session")
def test_dbs(test_data_dir):
    """Initialize test databases."""
    engines = {
        "default": create_engine(test_settings.DATABASE_URLS["default"]),
        "email": create_engine(test_settings.DATABASE_URLS["email"]),
        "analysis": create_engine(test_settings.DATABASE_URLS["analysis"]),
        "catalog": create_engine(test_settings.DATABASE_URLS["catalog"])
    }
    
    # Create all tables
    for engine in engines.values():
        Base.metadata.create_all(engine)
    
    yield engines
    
    # Clean up databases
    for engine in engines.values():
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_dbs):
    """Create a database session for testing."""
    session = Session()
    
    yield session
    
    # Rollback any changes
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def email_session(test_dbs):
    """Create an email database session for testing."""
    session = EmailSessionFactory()
    
    yield session
    
    # Rollback any changes
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def analysis_session(test_dbs):
    """Create an analysis database session for testing."""
    session = AnalysisSessionFactory()
    
    yield session
    
    # Rollback any changes
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def catalog_session(test_dbs):
    """Create a catalog database session for testing."""
    session = CatalogSessionFactory()
    
    yield session
    
    # Rollback any changes
    session.rollback()
    session.close()
