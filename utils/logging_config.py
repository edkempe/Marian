"""Logging configuration for the Marian project.

This module sets up structured logging with rotating file handler and consistent formatting.
"""

import logging
import logging.handlers
import json
from pathlib import Path
from typing import Any, Dict

from config.constants import LOGGING_CONFIG

def setup_logging(name: str) -> logging.Logger:
    """Set up logging with both file and console handlers.
    
    Args:
        name: The name of the logger, typically __name__
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_CONFIG['LOG_LEVEL'])
    
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / LOGGING_CONFIG['LOG_FILE'],
        maxBytes=LOGGING_CONFIG['MAX_BYTES'],
        backupCount=LOGGING_CONFIG['BACKUP_COUNT']
    )
    file_handler.setFormatter(logging.Formatter(LOGGING_CONFIG['LOG_FORMAT']))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOGGING_CONFIG['LOG_FORMAT']))
    
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
        'error_type': error.__class__.__name__,
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
    log_data = {
        'event': event,
        'response': response,
        **kwargs
    }
    logger.info(json.dumps(log_data))

def log_db_operation(logger: logging.Logger, event: str, operation: str, table: str, **kwargs: Any) -> None:
    """Log database operations with consistent structure.
    
    Args:
        logger: Logger instance
        event: Name of the event
        operation: Type of operation (insert, update, delete, etc.)
        table: Name of the table being operated on
        **kwargs: Additional context to include in log
    """
    log_data = {
        'event': event,
        'operation': operation,
        'table': table,
        **kwargs
    }
    logger.info(json.dumps(log_data))
