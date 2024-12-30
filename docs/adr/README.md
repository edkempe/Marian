# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for the Marian project.

## What are ADRs?

ADRs are documents that capture important architectural decisions made in a project. Each ADR describes:

1. The context (what is the issue)
2. The decision (what we're doing about it)
3. The consequences (what happens as a result)

## ADR File Naming Convention

Files are named using the following format:
`NNNN-title-with-dashes.md` where:
- NNNN is a four-digit number (0001-9999)
- Numbers are assigned chronologically
- Title is brief but descriptive
- Words are separated by hyphens
- Extension is markdown

## Directory Structure

```
.
├── README.md                           # This file
├── 0001-layered-architecture.md        # Core architecture design
├── 0002-minimal-security-testing.md    # Security testing approach
└── 0003-test-database-strategy.md      # Database testing strategy
```

## Creating New ADRs

When creating a new ADR:
1. Copy the template from `template.md`
2. Name it with the next available number
3. Fill in all sections
4. Add it to the directory structure above
5. Link it in the main project documentation

## Status

ADRs can have the following statuses:
- Proposed: Under discussion
- Accepted: Approved and in use
- Deprecated: No longer in use
- Superseded: Replaced by a newer decision
