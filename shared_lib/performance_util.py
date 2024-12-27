"""Performance and scalability utilities for the email analysis system.

This module provides utilities for improving system performance and scalability:

1. Caching: Redis-based caching to reduce repeated computations
2. Rate Limiting: Protect APIs and resources from overuse
3. Circuit Breaking: Prevent cascade failures in distributed systems
4. Performance Metrics: Monitor system performance using Prometheus

Future Use:
- Will be integrated when implementing API rate limiting for external services
- Will add caching for frequently accessed email analyses
- Will add performance monitoring for long-running operations
- Will implement circuit breakers for external API calls

Dependencies:
- Redis server for caching and rate limiting
- Prometheus for metrics collection
"""
import os
from functools import wraps
from typing import Any, Callable, Optional
import time

import redis
from tenacity import retry, stop_after_attempt, wait_exponential
from prometheus_client import Counter, Histogram, CollectorRegistry

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

# Custom registry for metrics
registry = CollectorRegistry()

# Metrics
CACHE_HITS = Counter('cache_hits_total', 'Number of cache hits', registry=registry)
CACHE_MISSES = Counter('cache_misses_total', 'Number of cache misses', registry=registry)
RATE_LIMIT_BLOCKS = Counter('rate_limit_blocks_total', 'Number of rate limit blocks', registry=registry)
OPERATION_DURATION = Histogram(
    'operation_duration_seconds',
    'Time spent in operations',
    ['operation'],
    registry=registry
)

def cache(ttl: int = 3600) -> Callable:
    """Cache decorator using Redis."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result is not None:
                CACHE_HITS.inc()
                try:
                    # Try to convert string to int/float if possible
                    return int(cached_result)
                except ValueError:
                    try:
                        return float(cached_result)
                    except ValueError:
                        return cached_result
            
            # If not in cache, execute function
            CACHE_MISSES.inc()
            result = func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(cache_key, ttl, str(result))
            return result
        return wrapper
    return decorator

def rate_limit(
    limit: int = 100,
    window: int = 3600,
    key_prefix: str = "rate_limit"
) -> Callable:
    """Rate limiting decorator using Redis."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create rate limit key
            key = f"{key_prefix}:{func.__name__}"
            
            # Check current count
            current = redis_client.get(key)
            current_count = int(current) if current is not None else 0
            
            if current_count >= limit:
                RATE_LIMIT_BLOCKS.inc()
                raise Exception("Rate limit exceeded")
            
            # Increment counter
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            pipe.execute()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def circuit_breaker(
    failure_threshold: int = 5,
    reset_timeout: int = 60,
    key_prefix: str = "circuit_breaker"
) -> Callable:
    """Circuit breaker decorator using Redis."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create circuit breaker keys
            failures_key = f"{key_prefix}:{func.__name__}:failures"
            last_failure_key = f"{key_prefix}:{func.__name__}:last_failure"
            
            # Check if circuit is open
            failures = int(redis_client.get(failures_key) or 0)
            last_failure = float(redis_client.get(last_failure_key) or 0)
            
            if failures >= failure_threshold:
                if time.time() - last_failure < reset_timeout:
                    raise Exception("Circuit breaker is open")
                # Reset after timeout
                redis_client.delete(failures_key, last_failure_key)
            
            try:
                result = func(*args, **kwargs)
                # Reset failures on success
                redis_client.delete(failures_key, last_failure_key)
                return result
            except Exception as e:
                # Increment failure count
                pipe = redis_client.pipeline()
                pipe.incr(failures_key)
                pipe.set(last_failure_key, time.time())
                pipe.execute()
                raise e
        return wrapper
    return decorator

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def retry_operation(operation: Callable, *args: Any, **kwargs: Any) -> Any:
    """Retry an operation with exponential backoff."""
    return operation(*args, **kwargs)

def measure_time(operation_name: str) -> Callable:
    """Measure operation duration using Prometheus."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                OPERATION_DURATION.labels(operation=operation_name).observe(duration)
        return wrapper
    return decorator
