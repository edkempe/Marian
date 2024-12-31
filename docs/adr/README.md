# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for the Jexi project.

## What are ADRs?

ADRs are documents that capture important architectural decisions made in a project. Each ADR describes:

1. The context (what is the issue)
2. The decision (what we're doing about it)
3. The consequences (what happens as a result)

## ADR File Naming Convention

Files are named using the following format:
`NNNN-title-with-dashes.md` where:
- NNNN is a four-digit number (0000-9999)
- Numbers are assigned chronologically
- Title is brief but descriptive
- Words are separated by hyphens
- Extension is markdown

## Directory Structure

```
.
├── README.md                                        # This file
├── 0000-subsystem-architecture.md                   # Hub-and-spoke system design
├── 0001-layered-architecture.md                     # Core architecture design
├── 0002-minimal-security-testing.md                 # Security testing approach
├── 0003-test-database-strategy.md                   # Database testing strategy
├── 0004-configuration-based-schema-definitions.md   # Schema config system
├── 0004-schema-constants-in-shared-lib.md          # Schema constants (Under Review)
├── 0005-mocking-policy.md                          # Testing mock policy
└── 0006-subsystem-interface-protocol.md            # Subsystem communication protocol
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
- Under Review: Being evaluated
- Deprecated: No longer in use
- Superseded: Replaced by a newer decision

## Notes

- ADR 0000 defines the foundational hub-and-spoke architecture of Jexi, establishing how the main assistant coordinates with specialized subsystems. All other architectural decisions build upon this foundation.

- ADR 0004 currently has two implementations being evaluated:
  1. Configuration-based schema definitions using YAML
  2. Schema constants in shared library
  Both approaches are documented while under review.

- ADR 0006 builds directly on ADR 0000, defining how the hub-and-spoke components communicate.
