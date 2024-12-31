# Revision History Standard

## Revision History
1.0.0 (2024-12-31) @dev
- Initial revision history standard
- Added format specification
- Added validation rules

## Overview
This document defines the standard format for tracking document revisions across the project.

## Format Specification

### Required Section
Every markdown document must include a `## Revision History` section after the title and before the main content:

```markdown
# Document Title

## Revision History
1.0.0 (2024-12-31) @dev
- Initial version
- Added feature X
- Added section Y
```

### Version Entry Format
Each version entry must follow this format:
```markdown
VERSION (DATE) @AUTHOR
- Change 1
- Change 2
- Change 3
```

Where:
- `VERSION`: Semantic version (X.Y.Z)
- `DATE`: ISO format (YYYY-MM-DD)
- `@AUTHOR`: Author tag starting with @
- Changes: Bullet points starting with -

### Semantic Versioning
Follow these rules for version numbers:
1. `MAJOR` (X): Breaking changes or complete rewrites
2. `MINOR` (Y): New content or non-breaking changes
3. `PATCH` (Z): Typos, formatting, or clarifications

### Change Descriptions
- Start with a verb (Added, Updated, Fixed, etc.)
- Be specific but concise
- Focus on what changed, not why
- List most important changes first

## Examples

### Good Examples
```markdown
1.0.0 (2024-12-31) @dev
- Initial document structure
- Added core sections
- Added examples

1.1.0 (2024-12-31) @dev
- Added validation rules
- Updated formatting guidelines
```

### Bad Examples
```markdown
1.0 (12/31/24) dev  # Wrong format
* First version     # Wrong bullet style
```

## Validation
Use the revision validator to check compliance:

```bash
python tools/revision_validator.py docs/
```

## Integration

### Pre-commit Hook
Add this validation to your pre-commit config:

```yaml
- repo: local
  hooks:
    - id: revision-history
      name: Revision History Validator
      entry: python tools/revision_validator.py
      language: python
      types: [markdown]
```

### GitHub Actions
Include validation in your CI pipeline:

```yaml
- name: Validate Documentation
  run: python tools/revision_validator.py docs/
```

## References
- [Semantic Versioning](https://semver.org/)
- [ISO Date Format](https://www.iso.org/iso-8601-date-and-time-format.html)
