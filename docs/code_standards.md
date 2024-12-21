# Code Standards and Best Practices

## Documentation Standards

1. **Class Documentation**
   - Every class must have a docstring explaining its purpose
   - Document known issues and their solutions
   - Include model requirements and configuration details
   - Example:
   ```python
   class EmailAnalyzer:
       """Analyzes emails using Claude-3-Haiku with improved error handling and validation.
       
       This analyzer uses the Claude-3-Haiku model exclusively for consistent performance and cost efficiency.
       Do not change to other models without thorough testing and approval.
       
       Known Issues:
       1. Claude API Response Formatting:
          - The API may prefix responses with text like "Here is the JSON response:"
          - This causes json.loads() to fail with "Expecting value: line 1 column 2 (char 1)"
          - Solution: Use _extract_json() to clean the response
       
       Model Requirements:
       - Always use claude-3-haiku-20240307
       - Keep max_tokens_to_sample at 1000 for consistent response sizes
       - Use temperature=0 for deterministic outputs
       """
   ```

2. **Constants and Configuration**
   - Store all constants in `config/constants.py`
   - Document each constant's purpose and valid values
   - Use type hints for all constants
   - Example:
   ```python
   API_CONFIG = {
       'ANTHROPIC_MODEL': 'claude-3-haiku-20240307',  # Current stable model
       'MAX_TOKENS': 1000,  # Keep consistent for response size
       'TEMPERATURE': 0.0,  # Use 0 for deterministic outputs
   }
   ```

3. **Error Handling**
   - Document all known error cases
   - Provide solutions or workarounds
   - Include example error messages
   - Example:
   ```python
   def _extract_json(self, text: str) -> str:
       """Extract JSON object from text, removing any leading or trailing non-JSON content.
       
       Known Issues:
       1. Leading Text: API may add "Here's the JSON:" before the actual JSON
       2. Trailing Text: API may add "Hope this helps!" after the JSON
       3. Multiple JSON Objects: Need to identify the correct one
       
       Args:
           text: Text containing a JSON object, possibly with extra content
           
       Returns:
           Cleaned JSON string
           
       Example:
           Input: "Here is the JSON: {...} Hope this helps!"
           Output: "{...}"
       """
   ```

## Code Organization

1. **File Structure**
   ```
   marian/
   ├── app_*.py          # Main application files
   ├── config/           # Configuration files
   ├── models/           # Database models
   ├── utils/            # Utility functions
   ├── docs/            # Documentation
   └── tests/           # Test files
   ```

2. **Import Order**
   ```python
   # Standard library
   import os
   import json
   
   # Third-party libraries
   import anthropic
   from sqlalchemy import text
   
   # Local imports
   from models.email import Email
   from utils.logging import logger
   ```

3. **Class Organization**
   - Public methods first
   - Private methods last
   - Constants at class level
   - Clear separation between sections

## Best Practices

1. **API Handling**
   - Always use _extract_json() for Claude responses
   - Validate JSON before parsing
   - Handle missing fields gracefully
   - Log all API errors with context

2. **Database Operations**
   - Use SQLAlchemy sessions
   - Implement proper error handling
   - Use transactions appropriately
   - Log database operations

3. **Logging**
   - Use structured logging
   - Include relevant context
   - Use appropriate log levels
   - Log all errors with stack traces

4. **Testing**
   - Write unit tests for all functions
   - Mock external APIs
   - Test error cases
   - Use consistent test data
