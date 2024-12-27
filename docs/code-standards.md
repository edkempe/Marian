# Code Standards and Best Practices

> **Documentation Role**: This is a supporting document for Development AI (Windsurf.ai) workflow, providing implementation standards. See `ai-architecture.md` for the complete documentation hierarchy.

## Critical Guidelines

1. **Code Removal Policy**
   - **NEVER** remove functionality or information/documentation without explicit permission
   - This applies to:
     - Test cases and test functionality
     - Documentation and comments
     - Helper functions and utilities
     - Logging and debugging code
     - Error handling
   - Duplicate important information in documentation rather than removing it
   - If you think something should be removed, always ask for explicit permission first
   - Document the reason and get approval before removing any code

2. **Code Addition Policy**
   - **NEVER** add new functionality without explicit approval
   - This applies to:
     - New files or modules
     - External libraries and dependencies
     - New features or functionality
     - Code reformatting or restructuring
     - Changes to build or deployment processes
   - Always propose and get approval before:
     - Adding new dependencies
     - Creating new files
     - Reformatting existing code
     - Adding new features
     - Changing project structure
   - Document the reason and expected impact of additions

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

## SQLAlchemy Model Standards

1. **Import Standards**
   ```python
   # Always use absolute imports for models
   from models.email import Email  # Good
   from .email import Email        # Avoid
   from ..models.email import Email  # Avoid
   ```

2. **Model Relationships**
   ```python
   # Always use fully qualified paths in relationships
   email = relationship("models.email.Email", backref="analysis")  # Good
   email = relationship("Email", backref="analysis")              # Avoid
   ```

3. **Model Organization**
   ```python
   class EmailAnalysis(Base):
       """Clear docstring explaining model purpose and structure."""
       __tablename__ = 'email_analysis'
       
       # Group fields by purpose with clear headers
       # Identification fields
       id = Column(Integer, primary_key=True)
       
       # Content fields
       title = Column(String)
       body = Column(Text)
       
       # Metadata fields
       created_at = Column(DateTime)
       updated_at = Column(DateTime)
       
       # Relationships (always with full paths)
       email = relationship("models.email.Email", backref="analysis")
   ```

4. **Type Hints**
   ```python
   # Use SQLAlchemy 2.0 type hints for clarity
   class Email(Base):
       id: Mapped[int] = Column(Integer, primary_key=True)
       subject: Mapped[str] = Column(Text)
       optional_field: Mapped[Optional[str]] = Column(Text, nullable=True)
   ```

5. **Common Issues and Solutions**
   - **Multiple Classes Found**: Use fully qualified paths in relationships
   - **Import Cycles**: Use string references in relationships
   - **Type Conflicts**: Use explicit SQLAlchemy types and type hints
   - **Session Management**: Always use context managers for sessions

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

## Chat Interaction Logging

### Critical Requirements

Chat interaction logging is a **critical system requirement**. All interactions between users and the AI must be reliably captured and preserved. This is non-negotiable for:

1. **Accountability**: Every interaction must be traceable and reviewable
2. **Training Data**: Interactions form the basis for future system improvements
3. **Debugging**: Chat logs are essential for identifying and fixing issues
4. **Compliance**: Maintaining a complete interaction history for audit purposes

### Implementation Standards

1. **Dual Logging System**:
   - System events, errors: Standard logging via `logging_util.py`
   - Chat interactions: Structured JSONL format in `data/chat_logs.jsonl`

2. **JSONL Format Requirements**:
   ```json
   {
     "timestamp": "ISO-8601 UTC",
     "session_id": "unique-session-id",
     "user_input": "raw user input",
     "system_response": "raw system response",
     "model": "model identifier",
     "status": "success|error",
     "error_details": "if applicable",
     "metadata": {}
   }
   ```

3. **Reliability Requirements**:
   - Atomic writes to prevent corruption
   - Immediate flush after each interaction
   - Automatic rotation of log files
   - Regular backups of chat logs

4. **Error Handling**:
   - Failed logs must trigger immediate alerts
   - Fallback logging mechanisms must be in place
   - No chat interaction should proceed without logging

### Monitoring and Maintenance

1. Regular log file health checks
2. Automated backup verification
3. Log rotation and cleanup policies
4. Storage capacity monitoring

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
