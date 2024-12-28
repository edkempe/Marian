# AI Guidelines and Session Management

> **Documentation Role**: This is the authoritative source for AI development session management. For session log standards and procedures, see `session_logs/README.md`.

## Core Principles
- Follow established guidelines and practices
- Keep changes focused and atomic
- Document all changes thoroughly
- Maintain consistent project structure
- Communicate clearly and concisely

## Session Management

### Before Starting a Session
- Review recent session logs
- Check backlog for priorities
- Understand current project state
- Set clear session objectives
- Verify environment and dependencies

### During a Session
- Follow coding and git guidelines
- Keep session log updated
- Document all decisions
- Track time on tasks
- Ask for clarification when needed

### After a Session
- Complete session summary
- Update backlog
- Document follow-up tasks
- Push session log and code changes
- Review all changes for consistency

### Session Documentation
For specific details on session logs, including:
- Naming conventions
- Required structure
- Templates
- Directory organization

See: `session_logs/README.md`

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
- Follow test-driven development practices
- Maintain backward compatibility when possible

## Library Organization

### File Organization
- All shared libraries and utilities in `shared_lib/` directory
- Keep directory structure flat unless needed
- Use clear, descriptive file names with appropriate suffixes:
  - `*_lib.py` for external integrations (e.g., `gmail_lib.py`)
  - `*_util.py` for utility functions (e.g., `security_util.py`)
- Avoid deep hierarchies or unnecessary abstractions
- Each file should have a single responsibility

### Import Guidelines
- Import from `shared_lib` directly:
  ```python
  from shared_lib.gmail_lib import GmailAPI
  from shared_lib.security_util import authenticate
  ```
- Use `__init__.py` to expose common functions/classes
- Group imports by type (standard, third-party, local)
- Use absolute imports for clarity

### Library Development
- Keep utility functions focused and single-purpose
- Document all public functions and classes
- Include usage examples in docstrings
- Write unit tests for all library code
- Avoid circular dependencies

## Documentation Standards

### File Organization
```
docs/
├── sessions/
│   ├── YYYY-MM-DD-HH-MM.md  # Current session
│   └── README.md            # Session log index
├── backlog.md              # Task tracking
└── *.md                    # Technical documentation
```

### Session Log Template
```markdown
# Session YYYY-MM-DD-HH-MM

## Focus
[Session objectives]

## Running Log
- HH:MM - Session started
- HH:MM - [Action/decision]

## Accomplished
[Work completed]

## Decisions
[Key decisions]

## Follow-up Tasks
[New backlog items]
```

### Task Template
```markdown
- [ ] Task Name (From: Session YYYY-MM-DD)
  - Context: [Background]
  - Priority: [Level]
  - Dependencies: [Requirements]
  - Added: YYYY-MM-DD
```

### Documentation Guidelines
- Keep README.md high-level and user-focused
- Put detailed technical information in specific guides
- Use lowercase with hyphens for filenames
- Follow consistent formatting within documents
- Include examples for complex concepts
- Keep documentation up to date with code changes

## Task Management

### Backlog Structure
```markdown
# Backlog

## Immediate Priority
- [ ] Task A (From: Session YYYY-MM-DD)
  - Context: [Direct follow-up from previous work]
  - Priority: [Immediate/High/Medium/Low]
  - Dependencies: [Other tasks/requirements]

## High Priority
- [ ] Task B
  - Context: [Background information]
  - Added: YYYY-MM-DD
```

### Task Management Guidelines
- Add new tasks with clear context
- Include session reference
- Specify priority level
- Note dependencies
- Update existing task priorities

## Communication Style
- Be concise and clear
- Explain rationale for changes
- Proactively suggest improvements
- Ask for clarification when needed
- Use markdown formatting consistently
- Reference specific files and functions with backticks
