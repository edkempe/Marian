"""Tests for scalability utilities."""

import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from utils.util_scalability import (
    cache,
    circuit_breaker,
    measure_time,
    rate_limit,
    redis_client,
    retry_operation,
)


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("utils.util_scalability.redis_client") as mock:
        mock.get.return_value = None
        yield mock


def test_cache_decorator(mock_redis):
    """Test cache decorator functionality."""
    mock_redis.get.return_value = None

    @cache(ttl=60)
    def expensive_operation(x):
        return x * 2

    # First call should cache
    result1 = expensive_operation(5)
    assert result1 == 10
    mock_redis.setex.assert_called_once()

    # Second call should use cache
    mock_redis.get.return_value = "10"
    result2 = expensive_operation(5)
    assert int(result2) == 10  # Compare as integers


def test_rate_limit_decorator(mock_redis):
    """Test rate limit decorator functionality."""
    mock_redis.pipeline.return_value = mock_redis
    mock_redis.execute.return_value = [100]  # Return count after increment
    mock_redis.get.return_value = "99"  # Just below limit

    @rate_limit(limit=100, window=3600)
    def limited_operation():
        return "success"

    # Should succeed when under limit
    assert limited_operation() == "success"

    # Should fail when over limit
    mock_redis.get.return_value = "100"
    with pytest.raises(Exception, match="Rate limit exceeded"):
        limited_operation()


def test_circuit_breaker_decorator(mock_redis):
    """Test circuit breaker decorator functionality."""
    failure_count = 0
    last_failure_time = None

    def get_side_effect(key):
        nonlocal failure_count, last_failure_time
        if key.endswith(":failures"):
            return str(failure_count)
        elif key.endswith(":last_failure"):
            return str(last_failure_time) if last_failure_time else "0"
        return "0"

    mock_redis.get.side_effect = get_side_effect
    mock_redis.pipeline.return_value = mock_redis
    mock_redis.execute.return_value = None

    @circuit_breaker(failure_threshold=2, reset_timeout=60)
    def failing_operation():
        raise ValueError("Operation failed")

    # First call should raise the original error
    with pytest.raises(ValueError, match="Operation failed"):
        try:
            failing_operation()
        finally:
            failure_count = 1
            last_failure_time = time.time()

    # Second call should raise circuit breaker error
    with pytest.raises(ValueError, match="Operation failed"):
        try:
            failing_operation()
        finally:
            failure_count = 2
            last_failure_time = time.time()

    # Third call should detect open circuit
    with pytest.raises(Exception, match="Circuit breaker is open"):
        failing_operation()


def test_measure_time_decorator():
    """Test time measurement decorator."""

    @measure_time("test_operation")
    def slow_operation():
        time.sleep(0.1)
        return "done"

    result = slow_operation()
    assert result == "done"


def test_retry_operation():
    """Test retry operation."""
    mock_func = Mock(side_effect=[ValueError, ValueError, "success"])

    result = retry_operation(mock_func)
    assert result == "success"
    assert mock_func.call_count == 3


def test_retry_operation_max_attempts():
    """Test retry operation max attempts."""
    mock_func = Mock(side_effect=ValueError("Test error"))

    with pytest.raises(Exception):
        retry_operation(mock_func)
    assert mock_func.call_count == 3


def test_cache_ttl(mock_redis):
    """Test cache TTL setting."""
    mock_redis.get.return_value = None  # Ensure cache miss

    @cache(ttl=30)
    def cached_operation():
        return "result"

    cached_operation()
    mock_redis.setex.assert_called_once()
    args = mock_redis.setex.call_args[0]
    assert args[1] == 30  # Check TTL value
    assert args[2] == "result"  # Check cached value


def test_rate_limit_window(mock_redis):
    """Test rate limit window setting."""
    mock_redis.pipeline.return_value = mock_redis
    mock_redis.execute.return_value = [1]

    @rate_limit(limit=10, window=60)
    def limited_operation():
        return "success"

    limited_operation()
    mock_redis.expire.assert_called_once_with("rate_limit:limited_operation", 60)
