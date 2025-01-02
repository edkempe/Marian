# 16. Minimalist ADR Template

Date: 2024-12-31

## Status

Proposed

## Revision History
1.0.0 (2024-12-31) @dev
- Initial template

## Context

As a solo developer with AI assistance, we need ADRs that are:
1. Easy to understand
2. Quick to write
3. Focused on essential decisions
4. AI-friendly for future reference
5. Track changes over time

## Decision

We will use this minimalist template for all ADRs:

```markdown
# N. Title (One Line, Problem-Focused)

Date: YYYY-MM-DD

## Status
[Proposed, Accepted, Deprecated, Superseded]

## Revision History
1.0.0 (YYYY-MM-DD) @author
- Initial version

1.1.0 (YYYY-MM-DD) @author
- Added feature X
- Updated section Y

## Context
- What problem are we solving?
- Why is it important?
- What constraints exist?
(3-5 bullet points max)

## Decision
- What is the solution?
- Show ONE clear example
- Keep it focused
(Code example should be minimal and clear)

## Consequences
### Positive
- 2-3 key benefits
- Focus on solo development
- AI collaboration benefits

### Negative
- 1-2 main drawbacks
- Be honest about limitations

### Mitigation
- 1-2 practical steps
- Focus on what you can do now

## References
- 1-2 key resources
- Prefer official docs
```

### Example Usage

```markdown
# 7. Simple Database Migrations

Date: 2024-12-31

## Status
Accepted

## Revision History
1.0.0 (2024-12-31) @dev
- Initial version with basic Alembic setup

1.1.0 (2024-12-31) @dev
- Added async support
- Simplified configuration

## Context
- Need to track database changes
- Working alone with AI help
- Must be simple to maintain

## Decision
Use Alembic with minimal config:

```python
# migrations/env.py
from alembic import context
from models import Base

target_metadata = Base.metadata
```

## Consequences
### Positive
- Easy to understand
- AI can help generate migrations
- Clear history

### Negative
- Limited rollback options

### Mitigation
- Keep migrations small
- Test thoroughly before applying

## References
- Alembic docs
```

## Consequences

### Positive
1. Consistent, minimal ADRs
2. Faster to write and review
3. Better for AI assistance
4. Clear focus on solo development
5. Simple revision tracking

### Negative
1. May need expansion for team growth
2. Less detailed than traditional ADRs

### Mitigation
1. Add detail when needed
2. Let AI suggest expansions
3. Use semantic versioning for clarity

## References
- [Lightweight ADRs](https://adr.github.io/madr/)
- [ADR Tools](https://github.com/npryce/adr-tools)
- [Semantic Versioning](https://semver.org/)
