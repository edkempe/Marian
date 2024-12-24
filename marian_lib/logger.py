"""Logging configuration for the Marian system."""
import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

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
    """Formatter that includes test status in the log entry."""
    def format(self, record):
        # Add is_test attribute if not present
        if not hasattr(record, 'is_test'):
            record.is_test = False
        return super().format(record)

def setup_logger(name, log_dir='logs', is_test=False):
    """Set up a logger with both file and console handlers.
    
    Args:
        name: Logger name (e.g., 'catalog', 'api', 'database')
        log_dir: Directory to store log files
        is_test: Whether this logger is being used for tests
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
        
    # Add test filter
    test_filter = TestFilter(is_test)
    logger.addFilter(test_filter)
    
    # File handler with rotation
    log_file = log_path / f"{name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatters and add it to the handlers
    file_formatter = TestFormatter(
        '%(asctime)s [%(levelname)s] %(name)s - %(message)s'
    )
    console_formatter = TestFormatter(
        '[%(levelname)s] %(message)s'
    )
    
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Performance logging
def log_performance(logger, operation, start_time):
    """Log performance metrics for an operation."""
    duration = datetime.now() - start_time
    logger.debug(f"Performance: {operation} took {duration.total_seconds():.3f} seconds")

# System state logging
def log_system_state(logger, **kwargs):
    """Log system state information."""
    state_info = [f"{k}={v}" for k, v in kwargs.items()]
    logger.info(f"System State: {', '.join(state_info)}")

# Security logging
def log_security_event(logger, event_type, details):
    """Log security-related events."""
    logger.warning(f"Security Event - {event_type}: {details}")

def is_test_entry(line):
    """Check if a log line is a test entry."""
    return '[TEST]' in line
