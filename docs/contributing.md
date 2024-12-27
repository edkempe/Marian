# Development Guidelines

**Version:** 1.0.0
**Status:** Authoritative source for development guidelines

## Critical Development Guidelines

### 1. Code Preservation Policy
- **NEVER** remove functionality or information/documentation without explicit permission
- This includes:
  - Test cases and functionality
  - Documentation and comments
  - Helper functions and utilities
  - Logging and debugging code
  - Error handling
- Duplicate important information rather than removing it
- Always get explicit approval before removing any code
- This guideline is critical and applies to all aspects of the project

### 2. Code Addition Policy
- **NEVER** add new functionality without explicit approval
- This includes:
  - New files or modules
  - External libraries and dependencies
  - New features or functionality
  - Code reformatting or restructuring
  - Changes to build or deployment processes
- Always propose and get approval before adding:
  - New dependencies
  - New files
  - Code reformatting
  - New features
  - Project structure changes
- Document the reason and impact of proposed additions
- This guideline is critical and applies to all aspects of the project

### 3. Testing Policy
- **NO MOCK TESTING** - All tests must use real integrations
- Tests interact with actual APIs, databases, and services
- Any changes to use mocks require explicit permission
- Test data volumes are limited to prevent timeouts
- Tests must be reliable and not dependent on mock behavior
- This policy ensures tests validate real-world behavior

### 4. Change Management Policy
- Keep detailed session logs of all development work
- Make changes small and incremental
- Ensure diffs are readable for review and approval
- Document reasoning behind each change
- Break large changes into smaller, reviewable chunks
- This policy ensures changes can be properly reviewed and tracked

## Code Modification Guidelines
- Modify code one line at a time so changes are easy to read in the diff
- Each change should be explained before making it
- Wait for confirmation before proceeding to next change

## Code Organization Guidelines
- Always search for existing code before creating new code or files
- Follow the Don't Repeat Yourself (DRY) principle:
  - Avoid duplicating code or functionality
  - Extract common patterns into reusable functions or classes
  - Use inheritance and composition to share behavior
  - Maintain single source of truth for business logic

## Documentation Standards

### File Naming Conventions
- Use lowercase with hyphens (kebab-case) for all documentation files
  - Good: `getting-started.md`, `api-documentation.md`
  - Avoid: `SETUP_GUIDE.md`, `API_REFERENCE.md`
- Avoid redundant suffixes like `_GUIDE` or `_MANUAL`
- Use standard names for common documentation:
  - `readme.md`: Project overview and getting started
  - `contributing.md`: Development guidelines and standards
  - `changelog.md`: Version history and changes
  - `license.md`: Project license
  - `api.md`: API documentation
  - `troubleshooting.md`: Common issues and solutions

### Documentation Organization
- Keep documentation in the `docs/` directory
- Use subdirectories for specific types of documentation:
  - `docs/sessions/`: AI pair programming session logs
  - `docs/decisions/`: Architecture Decision Records (ADRs)
  - `docs/api/`: Detailed API documentation
- Link related documentation files using relative links
- Keep paths short and descriptive

## Version History
- 1.0.0: Initial guidelines documentation covering code preservation, addition, testing, and change management policies
