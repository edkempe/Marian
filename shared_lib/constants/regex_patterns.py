"""Regular expression patterns."""

from dataclasses import dataclass, field
from typing import Dict

@dataclass(frozen=True)
class RegexPatternConstants:
    """Regular expression pattern constants."""

    # Email patterns
    EMAIL: Dict[str, str] = field(default_factory=lambda: {
        "address": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "subject": r"^Subject:\s*(.*)$",
        "date": r"^Date:\s*(.*)$",
        "from": r"^From:\s*(.*)$",
        "to": r"^To:\s*(.*)$",
        "cc": r"^Cc:\s*(.*)$",
        "bcc": r"^Bcc:\s*(.*)$",
        "attachment": r"^Content-Disposition:\s*attachment;\s*filename=\"?([^\"]+)\"?",
    })

    # File patterns
    FILE: Dict[str, str] = field(default_factory=lambda: {
        "extension": r"\.([^.]+)$",
        "filename": r"^[^/\\]+$",
        "path": r"^(?:[^/\\]+[/\\])*[^/\\]+$",
        "url": r"^(https?://[^\s<>\"]+|www\.[^\s<>\"]+)",
    })

    # Code patterns
    CODE: Dict[str, str] = field(default_factory=lambda: {
        "function": r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
        "class": r"^class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[:\(]",
        "import": r"^(?:from\s+([^\s]+)\s+)?import\s+([^\s]+)",
        "variable": r"^[a-zA-Z_][a-zA-Z0-9_]*\s*=",
    })

    # Date patterns
    DATE: Dict[str, str] = field(default_factory=lambda: {
        "iso": r"\d{4}-\d{2}-\d{2}",
        "iso_time": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?",
        "us_date": r"\d{1,2}/\d{1,2}/\d{4}",
        "eu_date": r"\d{1,2}\.\d{1,2}\.\d{4}",
    })

    def __getitem__(self, key: str) -> Dict[str, str]:
        """Make the class subscriptable."""
        return getattr(self, key)

# Singleton instance
REGEX_PATTERNS = RegexPatternConstants()
