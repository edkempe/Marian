"""Logging configuration for the Marian project.

This module sets up structured logging with rotating file handler and consistent formatting.
It also provides Prometheus metrics for monitoring.
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import structlog
from prometheus_client import Counter, Histogram, start_http_server

from constants import LOGGING_CONFIG

# Prometheus metrics
EMAIL_ANALYSIS_COUNTER = Counter(
    'email_analysis_total',
    'Total number of email analyses performed',
    ['status']
)

API_ERROR_COUNTER = Counter(
    'api_error_total',
    'Total number of API errors',
    ['type']
)

VALIDATION_ERROR_COUNTER = Counter(
    'validation_error_total',
    'Total number of validation errors',
    ['field']
)

ANALYSIS_DURATION = Histogram(
    'email_analysis_duration_seconds',
    'Time taken to analyze emails',
    ['operation']
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

structured_logger = structlog.get_logger()

class TestFilter(logging.Filter):
    """Filter to mark or filter test log entries."""
    def __init__(self, is_test=False):
        self.is_test = is_test
        
    def filter(self, record):
        # Mark the record as test or non-test
        record.is_test = self.is_test
        # Add test marker to message if it's a test
        if self.is_test and not record.msg.startswith('[TEST] '):
            record.msg = f'[TEST] {record.msg}'
        return True

class TestFormatter(logging.Formatter):
    """Custom formatter for test logs."""
    def format(self, record):
        if hasattr(record, 'is_test') and record.is_test:
            record.msg = f'[TEST] {record.msg}'
        return super().format(record)

def setup_logging(name: str, log_dir: str = 'logs', is_test: bool = False) -> logging.Logger:
    """Set up logging with both file and console handlers.
    
    Args:
        name: The name of the logger, typically __name__
        log_dir: Directory to store log files
        is_test: Whether this logger is being used for tests
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_CONFIG['LOG_LEVEL'])
    
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create rotating file handler
    log_file = os.path.join(log_dir, LOGGING_CONFIG['LOG_FILE'])
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOGGING_CONFIG['MAX_BYTES'],
        backupCount=LOGGING_CONFIG['BACKUP_COUNT']
    )
    file_handler.setLevel(LOGGING_CONFIG['LOG_LEVEL'])
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOGGING_CONFIG['LOG_LEVEL'])
    
    # Create formatter
    formatter = logging.Formatter(LOGGING_CONFIG['LOG_FORMAT'])
    
    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_error(logger: logging.Logger, event: str, error: Exception, **kwargs: Any) -> None:
    """Log an error with consistent structure.
    
    Args:
        logger: Logger instance
        event: Name of the event where error occurred
        error: Exception object
        **kwargs: Additional context to include in log
    """
    error_data = {
        'event': event,
        'error_type': type(error).__name__,
        'error_message': str(error),
        **kwargs
    }
    logger.error(json.dumps(error_data))

def log_api_response(logger: logging.Logger, event: str, response: Dict[str, Any], **kwargs: Any) -> None:
    """Log an API response with consistent structure.
    
    Args:
        logger: Logger instance
        event: Name of the event (e.g., 'claude_analysis')
        response: API response data
        **kwargs: Additional context to include in log
    """
    response_data = {
        'event': event,
        'response': response,
        **kwargs
    }
    logger.info(json.dumps(response_data))

def log_db_operation(logger: logging.Logger, event: str, operation: str, table: str, **kwargs: Any) -> None:
    """Log database operations with consistent structure.
    
    Args:
        logger: Logger instance
        event: Name of the event
        operation: Type of operation (insert, update, delete, etc.)
        table: Name of the table being operated on
        **kwargs: Additional context to include in log
    """
    operation_data = {
        'event': event,
        'operation': operation,
        'table': table,
        **kwargs
    }
    logger.info(json.dumps(operation_data))

def log_performance(logger: logging.Logger, operation: str, start_time: datetime) -> None:
    """Log performance metrics for an operation.
    
    Args:
        logger: Logger instance
        operation: Name of the operation being measured
        start_time: Start time of the operation
    """
    duration = datetime.now() - start_time
    duration_seconds = duration.total_seconds()
    ANALYSIS_DURATION.labels(operation=operation).observe(duration_seconds)
    logger.info(f"Performance: {operation} took {duration_seconds:.2f} seconds")

def log_system_state(logger: logging.Logger, **kwargs: Any) -> None:
    """Log system state information.
    
    Args:
        logger: Logger instance
        **kwargs: System state information to log
    """
    state_data = {
        'event': 'system_state',
        **kwargs
    }
    logger.info(json.dumps(state_data))

def log_security_event(logger: logging.Logger, event_type: str, details: Dict[str, Any]) -> None:
    """Log security-related events.
    
    Args:
        logger: Logger instance
        event_type: Type of security event
        details: Event details
    """
    security_data = {
        'event': 'security',
        'type': event_type,
        'details': details
    }
    logger.info(json.dumps(security_data))

def is_test_entry(line: str) -> bool:
    """Check if a log line is a test entry.
    
    Args:
        line: Log line to check
        
    Returns:
        True if the line is a test entry
    """
    return '[TEST]' in line

def start_metrics_server(port: int = 8000) -> None:
    """Start the Prometheus metrics server.
    
    Args:
        port: Port to run the metrics server on
    """
    start_http_server(port)

def log_api_error(error_type: str, details: Dict[str, Any]) -> None:
    """Log an API error and increment the counter.
    
    Args:
        error_type: Type of API error
        details: Error details
    """
    API_ERROR_COUNTER.labels(type=error_type).inc()
    structured_logger.error("api_error", error_type=error_type, **details)

def log_validation_error(field: str, details: Dict[str, Any]) -> None:
    """Log a validation error and increment the counter.
    
    Args:
        field: Field that failed validation
        details: Error details
    """
    VALIDATION_ERROR_COUNTER.labels(field=field).inc()
    structured_logger.error("validation_error", field=field, **details)
