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
    4. "Here's the array: [...]"
    """
    # Clean the text first
    cleaned_text = clean_json_text(text)
    
    # Try to find JSON object or array
    try:
        # Find the first { or [
        obj_start = cleaned_text.find('{')
        arr_start = cleaned_text.find('[')
        
        # Determine which comes first (if any)
        if obj_start == -1 and arr_start == -1:
            return "", "No JSON object or array found in response"
            
        # If both exist, use the first one
        if obj_start != -1 and arr_start != -1:
            start = min(obj_start, arr_start)
            is_array = arr_start == start
        else:
            start = obj_start if obj_start != -1 else arr_start
            is_array = arr_start == start
            
        # Track nested braces/brackets to find the matching closing one
        depth = 0
        in_string = False
        escape_next = False
        open_char = '[' if is_array else '{'
        close_char = ']' if is_array else '}'
        
        for i, char in enumerate(cleaned_text[start:], start):
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
                
            if not in_string:
                if char == open_char:
                    depth += 1
                elif char == close_char:
                    depth -= 1
                    if depth == 0:
                        # Found the matching closing character
                        json_str = cleaned_text[start:i+1]
                        try:
                            # Verify it's valid JSON
                            json.loads(json_str)
                            return json_str, None
                        except json.JSONDecodeError as e:
                            return "", f"Invalid JSON: {str(e)}"
        
        return "", f"No closing {close_char} found for JSON {'array' if is_array else 'object'}"
        
    except Exception as e:
        return "", f"Error extracting JSON: {str(e)}"

def parse_claude_response(response_text: str, error_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Parse a Claude API response that may contain JSON with leading/trailing text.
    
    Args:
        response_text: The raw response text from Claude
        error_context: Optional dictionary of context info for error logging
        
    Returns:
        Parsed JSON as dict if successful, None if parsing failed
    """
    try:
        # If response_text is a Message object, get its content
        if hasattr(response_text, 'content'):
            response_text = response_text.content
            
        # Clean the text first
        cleaned_text = clean_json_text(response_text)
        
        # Find JSON object in text
        json_str, error_msg = extract_json(cleaned_text)
        if not json_str:
            if error_context:
                logger.error(
                    f"Failed to extract JSON: {error_msg}",
                    extra={
                        **(error_context or {}),
                        'raw_response': response_text,
                        'cleaned_text': cleaned_text
                    }
                )
            return None
        
        # Parse the cleaned JSON
        try:
            # Try to parse as is
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Try to fix common formatting issues
                fixed_json = json_str.strip()
                if fixed_json.startswith('"') and fixed_json.endswith('"'):
                    fixed_json = fixed_json[1:-1]  # Remove quotes
                if fixed_json.startswith('`') and fixed_json.endswith('`'):
                    fixed_json = fixed_json[1:-1]  # Remove backticks
                fixed_json = fixed_json.replace('\\"', '"')  # Fix escaped quotes
                fixed_json = fixed_json.replace('\\n', '\n')  # Fix escaped newlines
                return json.loads(fixed_json)
        except json.JSONDecodeError as e:
            if error_context:
                logger.error(
                    f"Failed to parse JSON: {str(e)}",
                    extra={
                        **(error_context or {}),
                        'extracted_json': json_str,
                        'raw_response': response_text,
                        'cleaned_text': cleaned_text
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
