# 12. Minimalist Versioning Strategy

Date: 2024-12-31

## Status

Proposed

## Revision History
1.0.0 (2024-12-31) @dev
- Initial version with two-branch strategy
- Added semantic versioning rules
- Added release process

## Context

As a solo developer with AI assistance, we need a simple versioning strategy that:
1. Maintains clarity for both human and AI
2. Avoids complex branching strategies
3. Makes releases straightforward
4. Preserves history for AI context

## Decision

We will use a minimalist Git workflow with semantic versioning:

### 1. Branch Strategy
Only two branches:
- `main`: Always deployable
- `dev`: Work in progress

```bash
# Start new work
git checkout -b dev main

# When ready to deploy
git checkout main
git merge dev
git tag v1.0.0
```

### 2. Commit Messages
Structure commits for AI readability:

```
<type>: <summary>

<details>

Co-authored-by: AI Assistant <ai@codeium.com>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code improvement
- `test`: Test addition/fix

### 3. Version Numbers
Use semantic versioning (MAJOR.MINOR.PATCH):

```python
# In pyproject.toml
[tool.poetry]
version = "1.0.0"  # Breaking.Feature.Fix
```

### 4. Release Process
Simple checklist for releases:

1. Update version:
   ```python
   # version.py
   __version__ = "1.0.0"
   ```

2. Update changelog:
   ```markdown
   # CHANGELOG.md
   ## [1.0.0] - 2024-12-31
   ### Added
   - Feature X
   ### Fixed
   - Bug Y
   ```

3. Tag and push:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

### 5. Version Control
- Keep `.gitignore` comprehensive
- Commit dependencies (pyproject.toml)
- Never commit secrets or env files

## Consequences

### Positive
1. Simple to maintain alone
2. Clear history for AI context
3. Easy to understand state
4. Minimal process overhead

### Negative
1. Less suitable for team scaling
2. Limited parallel development
3. No formal review process

### Mitigation
1. Use AI for code review
2. Maintain clear documentation
3. Automate version bumping

## References
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
