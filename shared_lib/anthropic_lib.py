"""Utilities for working with Anthropic's Claude API responses.

This module provides utilities for handling common tasks when working with the Anthropic Claude API,
such as extracting JSON from responses that may contain leading/trailing text.

Common Issues Handled:
1. Claude API Response Formatting:
   - The API may prefix responses with text like "Here is the JSON response:"
   - This causes json.loads() to fail with "Expecting value: line 1 column 2 (char 1)"
   
2. JSON Validation:
   - Sometimes the API response may be missing required fields
   - Always validate the JSON structure before processing
   - Use empty strings/arrays instead of null values
   
Example API Response Issues:
1. "Here is the JSON response: {...}"
2. "{...} Hope this helps!"
3. "I've analyzed the email. Here's the JSON: {...}"
"""

import json
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def extract_json(text: str) -> str:
    """Extract JSON from text that may have leading/trailing content.
    
    Args:
        text: Text that may contain JSON with leading/trailing content
        
    Returns:
        Cleaned JSON string or empty string if no valid JSON found
        
    Example inputs that will be handled:
    1. "Here is the JSON response: {...}"
    2. "{...} Hope this helps!"
    3. "I've analyzed the email. Here's the JSON: {...}"
    """
    # Find anything that looks like a JSON object/array
    json_pattern = r'\{(?:[^{}]|(?R))*\}|\[(?:[^\[\]]|(?R))*\]'
    matches = re.finditer(json_pattern, text)
    
    # Try each match until we find valid JSON
    for match in matches:
        try:
            # Verify it's valid JSON by parsing it
            json_str = match.group()
            json.loads(json_str)  # Test if it's valid JSON
            return json_str
        except json.JSONDecodeError:
            continue
            
    return ""  # No valid JSON found

def parse_claude_response(response_text: str, error_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Parse a Claude API response that may contain JSON with leading/trailing text.
    
    Args:
        response_text: The raw response text from Claude
        error_context: Optional dictionary of context info for error logging
        
    Returns:
        Parsed JSON as dict if successful, None if parsing failed
    """
    try:
        # Extract JSON from response
        json_str = extract_json(response_text)
        if not json_str:
            if error_context:
                logger.error(
                    "No valid JSON found in Claude response",
                    extra=error_context
                )
            return None
        
        # Parse the cleaned JSON
        return json.loads(json_str)
        
    except Exception as e:
        if error_context:
            logger.error(
                f"Error parsing Claude response: {str(e)}", 
                extra=error_context
            )
        return None
