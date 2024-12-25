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
