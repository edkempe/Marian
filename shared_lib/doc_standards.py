"""Documentation standards and constants."""

from typing import Dict, List
from pathlib import Path
import re
from datetime import datetime

# File size limits (in lines)
MAX_NEW_DOC_LINES = 500  # Strict limit for new docs
MAX_EXISTING_DOC_LINES = 2000  # Lenient limit for existing docs
WARN_DOC_LINES = 750  # Warning threshold

# Required sections by document type
REQUIRED_SECTIONS = {
    "session_logs": [
        "Session Overview",
        "Progress Log",
        "Next Steps",
        "Questions/Blockers"
    ],
    "adr": [
        "Status",
        "Context",
        "Decision",
        "Consequences"
    ],
    "standard": [
        "Quick Reference",
        "Version",
        "Status"
    ]
}

# Session log format
SESSION_LOG_SECTIONS = {
    "Session Overview": [
        "Start:",
        "Focus:"
    ],
    "Progress Log": [],  # Dynamic based on timestamps
    "Next Steps": [],  # Dynamic based on content
    "Questions/Blockers": []  # Dynamic based on content
}

# File patterns
SESSION_LOG_PATTERN = r"session_log_\d{4}-\d{2}-\d{2}\.md$"
TIMESTAMP_PATTERN = r"\d{2}:\d{2}\s+MST"
VERSION_PATTERN = r"\*\*Version:\*\*\s+\d+\.\d+\.\d+"
STATUS_PATTERN = r"\*\*Status:\*\*\s+\w+"
BACKLOG_ITEM_PATTERN = r"^\d+\.\s+[^:]+:\s+.{1,50}$"

def is_new_doc(path: Path, cutoff_date: str = "2024-01-01") -> bool:
    """Check if document is new (created after cutoff)."""
    return path.stat().st_ctime > Path(cutoff_date).stat().st_ctime

def get_doc_type(path: Path) -> str:
    """Get document type based on path."""
    if "session_logs" in str(path):
        return "session_logs"
    elif "adr" in str(path):
        return "adr"
    return "standard"

def get_max_lines(path: Path) -> int:
    """Get maximum lines allowed for document."""
    return MAX_NEW_DOC_LINES if is_new_doc(path) else MAX_EXISTING_DOC_LINES

def validate_session_log_format(content: str) -> List[str]:
    """Validate session log format.
    
    Args:
        content: Content of session log file
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Check overview section
    for required in SESSION_LOG_SECTIONS["Session Overview"]:
        if not any(line.startswith(f"- {required}") for line in content.splitlines()):
            errors.append(f"[ERROR] Missing {required} in Session Overview")
            
    # Check timestamps
    timestamps = re.findall(TIMESTAMP_PATTERN, content)
    if not timestamps:
        errors.append("[ERROR] No timestamped entries found")
    else:
        # Check timestamp order
        prev_time = None
        for time_str in timestamps:
            current_time = datetime.strptime(time_str, "%H:%M MST")
            if prev_time and current_time < prev_time:
                errors.append("[ERROR] Timestamps not in chronological order")
            prev_time = current_time
            
    # Check backlog items
    if "## Backlog Items" in content:
        items = re.findall(r"^\d+\..+$", content, re.MULTILINE)
        for item in items:
            if len(item.split("\n")) > 2:
                errors.append("[ERROR] Backlog item exceeds 2 lines")
            if len(item) > 100:  # 50 words ≈ 100 chars
                errors.append("[ERROR] Backlog item exceeds 50 words")
                
    return errors
