# Documentation Standards

**Version:** 1.0.0
**Status:** Authoritative
**Length Limit:** 500 lines per document

## Quick Reference

```bash
# Create today's session log
touch docs/session_logs/session_log_$(date +%Y-%m-%d).md

# Update documentation
code docs/doc-standards.md  # Read this first
```

## Core Principles

1. **Conciseness**
   - 500-line limit per document
   - Quick reference section at top
   - Link to related docs instead of duplicating

2. **Hierarchy**
   - README.md: Project overview
   - doc-standards.md: This document
   - session_logs/: Daily progress
   - adr/: Architecture decisions

3. **Session Logs**
   - One log per day: `session_log_YYYY-MM-DD.md`
   - Required sections:
     - Session Overview (time, focus)
     - Progress Log (timestamped entries)
     - Next Steps
     - Questions/Blockers

4. **Maintenance**
   - Review docs monthly
   - Archive unused content
   - Update quick reference
   - Check cross-references

## Document Types

1. **Authoritative**
   - Source of truth
   - Cannot be overridden
   - Examples: doc-standards.md, code-standards.md

2. **Supporting**
   - Implementation details
   - Can be updated frequently
   - Examples: session logs, READMEs

## Process

1. **Creating Documents**
   ```markdown
   # Document Title
   
   **Version:** 1.0.0
   **Status:** [Authoritative|Supporting]
   **Length Limit:** 500 lines
   
   ## Quick Reference
   ...
   ```

2. **Updating Documents**
   - Check doc-standards.md first
   - Update version number
   - Keep under length limit
   - Add quick reference if missing

## Session Log Format

1. **File Name**
   ```
   session_log_YYYY-MM-DD.md
   ```

2. **Required Sections**
   ```markdown
   # Session Log YYYY-MM-DD

   ## Session Overview
   - Start: HH:MM MST
   - Focus: Brief description of main goals

   ## Progress Log
   ### HH:MM MST - Topic
   - Bullet points of what was done
   - Include specific files/changes
   - Keep entries focused

   ## Next Steps
   1. Numbered list of tasks
   2. Be specific and actionable
   3. Include dependencies

   ## Backlog Items
   ```markdown
   1. Item Name: 50-word description max.
      Two lines maximum per item.
   ```

   ## Questions/Blockers
   1. List open questions
   2. List blocking issues
   3. Include dependencies
   ```

3. **Best Practices**
   - Timestamp each major update
   - Keep entries concise
   - Link to relevant files/PRs
   - Update throughout the day
   - Include specific file paths
   - Reference ticket numbers

4. **Example Entry**
   ```markdown
   ### 08:15 MST - Feature Implementation
   - Created `src/feature.py` with core logic
   - Updated `tests/test_feature.py` with:
     - Unit tests for edge cases
     - Integration test framework
   - Added feature flags in `config.json`
   ```

## Backlog Items

```markdown
1. Consolidate Historical Logs: Convert pre-2024 session-based logs to daily format. Archive original files.
   Priority: Low, Timeline: Q1 2024

2. Documentation Cleanup: Review all docs, enforce 500-line limit, add quick reference sections.
   Priority: High, Timeline: January 2024
