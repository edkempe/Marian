"""Logging utility for Marian project."""
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from catalog_constants import CATALOG_CONFIG

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Set up a logger with consistent formatting and rotation.
    
    Args:
        name: Name of the logger
        log_file: Optional log file path. If not provided, uses default from config.
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:  # Only add handler if logger doesn't have one
        # Use provided log file or default from config
        log_file = log_file or CATALOG_CONFIG['LOG_FILE']
        
        # Create handlers
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=CATALOG_CONFIG['LOG_MAX_BYTES'],
            backupCount=CATALOG_CONFIG['LOG_BACKUP_COUNT']
        )
        console_handler = logging.StreamHandler()
        
        # Set format
        formatter = logging.Formatter(CATALOG_CONFIG['LOG_FORMAT'])
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Set level
        logger.setLevel(CATALOG_CONFIG['LOG_LEVEL'])
    
    return logger
