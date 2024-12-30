"""Tests for security functionality."""

import os
import time
from datetime import datetime, timedelta

import pytest
from jose import jwt

from shared_lib.security_util import (
    create_access_token,
    decrypt_data,
    encrypt_data,
    get_password_hash,
    sanitize_email_content,
    verify_password,
    verify_token,
)


@pytest.fixture
def setup_env():
    """Set up test environment variables."""
    os.environ["JWT_SECRET_KEY"] = "test_secret_key"
    os.environ["ENCRYPTION_KEY"] = "test_encryption_key_must_be_32_bytes!"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    yield
    del os.environ["JWT_SECRET_KEY"]
    del os.environ["ENCRYPTION_KEY"]
    del os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]


def test_password_hashing():
    """Test password hashing and verification."""
    password = "test_password123"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_jwt_token(setup_env):
    """Test JWT token creation and verification."""
    data = {"user_id": 123, "email": "test@example.com"}
    expires = timedelta(minutes=30)

    token = create_access_token(data, expires)
    payload = verify_token(token)

    assert payload is not None
    assert payload["user_id"] == data["user_id"]
    assert payload["email"] == data["email"]


def test_invalid_jwt_token(setup_env):
    """Test invalid JWT token verification."""
    invalid_token = "invalid.token.here"
    payload = verify_token(invalid_token)
    assert payload is None


def test_data_encryption(setup_env):
    """Test data encryption and decryption."""
    sensitive_data = "sensitive information 123"
    encrypted = encrypt_data(sensitive_data)
    decrypted = decrypt_data(encrypted)

    assert encrypted != sensitive_data
    assert decrypted == sensitive_data


def test_email_sanitization():
    """Test email content sanitization."""
    content = "Test email with sensitive info"
    sanitized = sanitize_email_content(content)

    # Basic test until sanitization is implemented
    assert isinstance(sanitized, str)
    assert len(sanitized) > 0


def test_token_expiration(setup_env):
    """Test token expiration."""
    data = {"user_id": 123}
    # Set expiration to 1 second and wait
    expires = timedelta(seconds=1)
    token = create_access_token(data, expires)
    time.sleep(2)  # Wait for token to expire
    payload = verify_token(token)
    assert payload is None


def test_different_passwords():
    """Test different password combinations."""
    password1 = get_password_hash("password123")
    password2 = get_password_hash("password123")

    # Same password should generate different hashes
    assert password1 != password2

    # But both should verify correctly
    assert verify_password("password123", password1)
    assert verify_password("password123", password2)
