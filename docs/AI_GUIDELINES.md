# AI Assistant Guidelines

## Git Operations

### Committing Changes
1. **Always combine staging and commit in one step**
   - Use `git commit -am "type: description"` for modified files
     - `-a` stages all modified tracked files
     - `-m` specifies the commit message
     - `-am` combines both flags to stage and commit in one command
   - Only use separate `git add` for new (untracked) files
   - Never stage files without immediately committing them

2. **Follow conventional commit format**
   ```
   type: brief description

   - Detailed change 1
   - Detailed change 2
   ```
   Types:
   - feat: new feature
   - fix: bug fix
   - docs: documentation changes
   - style: formatting
   - refactor: code restructuring
   - test: adding tests
   - chore: maintenance tasks

3. **Keep commits focused**
   - One logical change per commit
   - Include all related changes (code, tests, docs)
   - Make sure commit message fully describes the change

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
