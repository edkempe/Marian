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
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

def clean_json_text(text: str) -> str:
    """Clean text that may contain JSON by removing common prefixes/suffixes.
    
    Args:
        text: Text that may contain JSON with leading/trailing content
        
    Returns:
        Cleaned text with common prefixes/suffixes removed
    """
    # Remove common prefixes
    prefixes = [
        r"^Here'?s? (?:is )?(?:the )?(?:JSON|json)(?: response)?:?\s*",
        r"^I'?ve analyzed the email\.?\s*(?:Here'?s? (?:the )?(?:JSON|json))?:?\s*",
        r"^Based on (?:the )?(?:analysis|email).*?(?:here'?s? (?:the )?(?:JSON|json))?:?\s*",
        r"^(?:The )?(?:JSON|json) (?:response|analysis) (?:is|follows):?\s*",
    ]
    
    # Remove common suffixes
    suffixes = [
        r"\s*(?:I )?[Hh]ope this helps!?\.?\s*$",
        r"\s*[Ll]et me know if you need anything else\.?\s*$",
        r"\s*[Dd]o you have any other questions\??\s*$",
        r"\s*[Ii]s there anything else you'?d like me to explain\??\s*$"
    ]
    
    # Apply cleaning
    for pattern in prefixes:
        text = re.sub(pattern, "", text)
    for pattern in suffixes:
        text = re.sub(pattern, "", text)
    
    return text.strip()

def extract_json(text: str) -> Tuple[str, Optional[str]]:
    """Extract JSON from text that may have leading/trailing content.
    
    Args:
        text: Text that may contain JSON with leading/trailing content
        
    Returns:
        Tuple of (json_str, error_msg):
            - json_str: Cleaned JSON string or empty string if no valid JSON found
            - error_msg: Error message if JSON extraction failed, None if successful
        
    Example inputs that will be handled:
    1. "Here is the JSON response: {...}"
    2. "{...} Hope this helps!"
    3. "I've analyzed the email. Here's the JSON: {...}"
    """
    # Clean the text first
    cleaned_text = clean_json_text(text)
    
    # Find anything that looks like a JSON object/array
    json_pattern = r'\{(?:[^{}]|(?R))*\}|\[(?:[^\[\]]|(?R))*\]'
    matches = list(re.finditer(json_pattern, cleaned_text))
    
    if not matches:
        return "", "No JSON object/array found in response"
    
    # Try each match until we find valid JSON
    errors = []
    for match in matches:
        try:
            # Verify it's valid JSON by parsing it
            json_str = match.group()
            json.loads(json_str)  # Test if it's valid JSON
            return json_str, None
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {str(e)}")
            continue
            
    return "", f"Failed to parse JSON: {'; '.join(errors)}"

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
        json_str, error_msg = extract_json(response_text)
        if not json_str:
            if error_context:
                logger.error(
                    f"Failed to extract JSON: {error_msg}",
                    extra={
                        **(error_context or {}),
                        'raw_response': response_text
                    }
                )
            return None
        
        # Parse the cleaned JSON
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            if error_context:
                logger.error(
                    f"Failed to parse JSON: {str(e)}",
                    extra={
                        **(error_context or {}),
                        'extracted_json': json_str,
                        'raw_response': response_text
                    }
                )
            return None
            
    except Exception as e:
        if error_context:
            logger.error(
                f"Unexpected error parsing Claude response: {str(e)}", 
                extra={
                    **(error_context or {}),
                    'raw_response': response_text
                }
            )
        return None
