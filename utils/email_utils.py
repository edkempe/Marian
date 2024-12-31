"""Email processing utilities for the Jexi project."""

import re
from typing import List, Optional, Tuple

def parse_email_address(email: str) -> Optional[Tuple[str, str]]:
    """Parse email into (local_part, domain)."""
    pattern = r'^([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$'
    match = re.match(pattern, email)
    if match:
        return match.group(1), match.group(2)
    return None

def normalize_email(email: str) -> str:
    """Normalize email address (lowercase, remove whitespace)."""
    return email.strip().lower()

def extract_email_addresses(text: str) -> List[str]:
    """Extract email addresses from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)
