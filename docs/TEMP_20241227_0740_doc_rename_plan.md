# Documentation Renaming Plan

## Phase 1: Core Documentation Renaming
1. Create new files with correct names:
   ```
   SETUP_GUIDE.md         -> setup.md
   TESTING_GUIDE.md       -> testing.md
   LIBRARIAN_GUIDE.md     -> librarian.md
   BACKUP_GUIDE.md        -> backup.md
   ARCHIVE_GUIDE.md       -> archiving.md
   AI_SESSION_GUIDE.md    -> ai-sessions.md
   GUIDELINES.md          -> contributing.md
   AI_GUIDELINES.md       -> ai-guidelines.md
   TROUBLESHOOTING.md     -> troubleshooting.md
   ```

2. Update all internal links in documentation
3. Update any references in code or scripts
4. Archive old files with timestamp prefix

## Phase 2: AI Documentation Review
1. Review content overlap between:
   - ai-sessions.md
   - ai-guidelines.md
   - contributing.md

2. Consolidate and reorganize content:
   - Move general AI interaction guidelines to contributing.md
   - Keep AI session-specific workflows in ai-sessions.md
   - Consider merging ai-guidelines.md into these files

3. Update cross-references between files

## Phase 3: Documentation Structure
1. Create new documentation sections if needed:
   - /docs/guides/ - For detailed how-to guides
   - /docs/reference/ - For reference documentation
   - /docs/decisions/ - For ADRs

2. Move files to appropriate sections
3. Update all links and references

## Implementation Steps
1. Create git branch: `docs/rename-standardization`
2. Create new files with correct names
3. Copy and update content
4. Update all cross-references
5. Archive old files
6. Review and consolidate AI documentation
7. Create PR for review

## Next Steps
- [ ] Review and approve renaming plan
- [ ] Schedule implementation work
- [ ] Create tracking issue for AI documentation consolidation
- [ ] Update documentation guidelines with new structure
