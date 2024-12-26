"""Utility for reliable logging of chat interactions.

This module provides robust logging of all chat interactions between users and the AI.
Chat logging is a critical system requirement - no interaction should proceed without
being properly logged.

The module uses a dual logging approach:
1. System events and errors are logged via standard logging
2. Chat interactions are stored in JSONL format for easy processing
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from shared_lib.logging_util import setup_logging

logger = setup_logging('chat_logger')

class ChatLogger:
    """Handles reliable logging of chat interactions."""
    
    def __init__(self, log_file: str):
        """Initialize the chat logger.
        
        Args:
            log_file: Path to the JSONL log file
        """
        self.log_file = log_file
        self.session_id = str(uuid.uuid4())
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Verify we can write to the log file
        try:
            if not os.path.exists(log_file):
                with open(log_file, 'w') as f:
                    f.write('')
            else:
                with open(log_file, 'a') as f:
                    f.write('')
        except Exception as e:
            logger.error(f"Failed to access chat log file: {str(e)}")
            raise RuntimeError("Chat logging is required but unavailable")
    
    def log_interaction(
        self,
        user_input: str,
        system_response: Any,
        model: str,
        status: str = "success",
        error_details: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """Log a single chat interaction.
        
        Args:
            user_input: The raw user input
            system_response: The system's response (will be converted to string)
            model: Identifier of the model used
            status: Status of the interaction ("success" or "error")
            error_details: Error information if status is "error"
            metadata: Additional metadata to log
            
        Raises:
            RuntimeError: If logging fails
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "user_input": user_input,
            "system_response": str(system_response),
            "model": model,
            "status": status,
            "error_details": error_details,
            "metadata": metadata or {}
        }
        
        try:
            # Atomic write by first writing to temp file
            temp_file = f"{self.log_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(log_entry, f)
                f.write('\n')
                f.flush()
                os.fsync(f.fileno())
            
            # Atomic move of temp file to append to log file
            with open(self.log_file, 'a') as f:
                with open(temp_file, 'r') as t:
                    f.write(t.read())
                f.flush()
                os.fsync(f.fileno())
            
            # Clean up temp file
            os.remove(temp_file)
            
            logger.info(
                "Chat interaction logged",
                extra={
                    "session_id": self.session_id,
                    "status": status,
                    "has_error": error_details is not None
                }
            )
        except Exception as e:
            error_msg = f"Failed to log chat interaction: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def rotate_logs(self, max_size_mb: int = 100) -> None:
        """Rotate log file if it exceeds max_size_mb.
        
        Args:
            max_size_mb: Maximum size in MB before rotation
        """
        try:
            if not os.path.exists(self.log_file):
                return
                
            size_mb = os.path.getsize(self.log_file) / (1024 * 1024)
            if size_mb < max_size_mb:
                return
                
            # Rotate file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_file = f"{self.log_file}.{timestamp}"
            os.rename(self.log_file, rotated_file)
            
            logger.info(
                f"Rotated chat log file",
                extra={
                    "old_file": self.log_file,
                    "new_file": rotated_file,
                    "size_mb": size_mb
                }
            )
        except Exception as e:
            logger.error(f"Failed to rotate chat logs: {str(e)}")
            # Don't raise error for rotation failure
