# AI Assistant Guidelines

## Git Operations

### Committing Changes
- Use `git commit -am "message"` for modified files to combine add and commit in one step
- Only use separate `git add` when new files need to be tracked
- Follow conventional commit format:
  ```
  type: brief description

  - Detailed change 1
  - Detailed change 2
  ```
  where type is one of:
  - feat: new feature
  - fix: bug fix
  - docs: documentation changes
  - style: formatting, missing semi colons, etc
  - refactor: code restructuring
  - test: adding tests
  - chore: maintenance tasks

## Code Changes
- Always explain changes before making them
- Use appropriate tools for file operations
- Keep changes focused and atomic
- Update documentation to reflect changes

## Library Organization

### File Organization
- All shared libraries and utilities are stored in the `shared_lib/` directory
- Keep the directory structure flat unless there's a clear need for subfolders
- Use clear, descriptive file names with appropriate suffixes:
  - `*_lib.py` for external integrations and core libraries (e.g., `gmail_lib.py`)
  - `*_util.py` for utility functions and helpers (e.g., `security_util.py`)
- Avoid creating deep hierarchies or unnecessary abstractions
- Each file should have a single, clear responsibility

### Import Guidelines
- Import from `shared_lib` directly:
  ```python
  from shared_lib.gmail_lib import GmailAPI
  from shared_lib.security_util import authenticate
  ```
- Use the `__init__.py` file to expose commonly used functions and classes
- Group imports by type (standard library, third-party, local)
- Use absolute imports for clarity

### Library Development
- Keep utility functions focused and single-purpose
- Document all public functions and classes with docstrings
- Include usage examples in docstrings for complex functionality
- Write unit tests for all library code
- Avoid circular dependencies between library modules

## Documentation
- Keep README.md high-level and user-focused
- Put detailed technical information in specific guides
- Update session logs with all significant changes
- Follow the principle of DRY (Don't Repeat Yourself)

## Communication
- Be concise and clear
- Explain rationale for changes
- Proactively suggest improvements
- Ask for clarification when needed
