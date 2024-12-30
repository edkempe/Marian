"""Utility functions for the Marian project."""

import re
from typing import Any, Dict, List, Optional, Tuple

from shared_lib.constants import REGEX_PATTERNS, SentimentTypes


def normalize_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize the response data to handle variations between models.
    
    Args:
        response_data: Raw response data from the model
        
    Returns:
        Normalized response data
    """
    normalized = {}
    
    # Handle summary - ensure it's a string
    normalized["summary"] = str(response_data.get("summary", "")).strip()
    
    # Handle categories - ensure it's a list of strings
    categories = response_data.get("category", [])
    if isinstance(categories, str):
        categories = [categories]
    normalized["category"] = [str(cat).strip() for cat in categories]
    
    # Handle priority score - ensure it's an int between 1-5
    try:
        score = int(response_data.get("priority_score", 1))
        normalized["priority_score"] = max(1, min(5, score))
    except (ValueError, TypeError):
        normalized["priority_score"] = 1
        
    # Handle priority reason
    normalized["priority_reason"] = str(response_data.get("priority_reason", "")).strip()
    
    # Handle action needed - ensure it's a boolean
    normalized["action_needed"] = bool(response_data.get("action_needed", False))
    
    # Handle action type - ensure it's a list of strings
    action_types = response_data.get("action_type", [])
    if isinstance(action_types, str):
        action_types = [action_types]
    normalized["action_type"] = [str(act).strip() for act in action_types]
    
    # Handle action deadline - ensure it's a valid date or special value
    deadline = str(response_data.get("action_deadline", "")).strip()
    if deadline.lower() == "asap":
        normalized["action_deadline"] = "ASAP"
    elif re.match(REGEX_PATTERNS["ISO_DATE"], deadline):
        normalized["action_deadline"] = deadline
    else:
        normalized["action_deadline"] = None
        
    # Handle key points - ensure it's a list of strings
    key_points = response_data.get("key_points", [])
    if isinstance(key_points, str):
        key_points = [key_points]
    normalized["key_points"] = [str(point).strip() for point in key_points]
    
    # Handle people mentioned - ensure it's a list of strings
    people = response_data.get("people_mentioned", [])
    if isinstance(people, str):
        people = [people]
    normalized["people_mentioned"] = [str(person).strip() for person in people]
    
    # Handle project and topic
    normalized["project"] = str(response_data.get("project", "")).strip()
    normalized["topic"] = str(response_data.get("topic", "")).strip()
    
    # Handle sentiment - ensure it's one of the valid values
    sentiment = str(response_data.get("sentiment", "neutral")).lower().strip()
    if sentiment not in SentimentTypes.values():
        sentiment = "neutral"
    normalized["sentiment"] = sentiment
    
    # Handle confidence score - ensure it's a float between 0 and 1
    try:
        score = float(response_data.get("confidence_score", 0.8))
        normalized["confidence_score"] = max(0.0, min(1.0, score))
    except (ValueError, TypeError):
        normalized["confidence_score"] = 0.8
        
    return normalized


def extract_urls(text: str) -> Tuple[List[str], List[str]]:
    """Extract URLs from text and create display versions.
    
    Args:
        text: Text to extract URLs from
        
    Returns:
        Tuple of (original URLs, display URLs)
    """
    urls = re.findall(REGEX_PATTERNS["URL"], text)
    
    display_urls = []
    for url in urls:
        if len(url) > 50:
            display_urls.append(f"{url[:25]}...{url[-22:]}")
        else:
            display_urls.append(url)
            
    return urls, display_urls


def sanitize_email_content(content: str) -> str:
    """Sanitize email content by removing sensitive information.
    
    Args:
        content: Email content to sanitize
        
    Returns:
        Sanitized content
    """
    # Remove email addresses
    content = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', content)
    
    # Remove phone numbers
    content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', content)
    
    # Remove URLs
    content = re.sub(REGEX_PATTERNS["URL"], '[URL]', content)
    
    # Remove credit card numbers
    content = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', content)
    
    return content
