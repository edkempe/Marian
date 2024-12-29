"""Utility for logging configuration and management.

This module provides a consistent logging setup across the application.
It configures logging with appropriate formatting and handlers.
"""

import json
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Any, Dict, Optional

def setup_logging(logger_name: str) -> logging.Logger:
    """Set up a logger with consistent configuration.
    
    Args:
        logger_name: Name for the logger
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(logger_name)
    
    if not logger.handlers:
        # Set up console handler
        console = logging.StreamHandler()
        console.setFormatter(JsonFormatter())
        logger.addHandler(console)
        
        # Set default level
        logger.setLevel(logging.INFO)
        
        # Don't propagate to root logger
        logger.propagate = False
    
    return logger

class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted string
        """
        # Extract the log message
        if isinstance(record.msg, str):
            message = record.msg
        else:
            message = str(record.msg)
            
        # Build the base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname.lower(),
            "event": message
        }
        
        # Add any extra fields
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in ["msg", "args", "exc_info", "exc_text", "levelname", 
                             "levelno", "pathname", "filename", "module", "stack_info",
                             "lineno", "funcName", "created", "msecs", "relativeCreated",
                             "thread", "threadName", "processName", "process", "message"]:
                    log_entry[key] = value
                    
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

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
