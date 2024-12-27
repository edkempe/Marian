# Archive Guide

## Purpose
The archive folder stores historical content that is no longer active but may be valuable for future reference. This includes old code versions, superseded documentation, and past design decisions.

## Location
- `/archive` - Single location at project root for all archived content
- Flat structure (no subfolders) for simplicity
- Clear naming convention identifies content type

## Naming Convention
Format: `ARCHIVED_YYYYMMDD_HHMM_filename.ext`

Examples:
- `ARCHIVED_20241225_1111_database_schema.md`
- `ARCHIVED_20241225_1111_test_email.py`
- `ARCHIVED_20241225_1111_ADR001_SQLAlchemy_Models.md`

## What to Archive
- Superseded documentation
- Old code versions
- Past design decisions
- Test files no longer needed
- Any content that:
  1. Is no longer active
  2. May have future reference value
  3. Contains important historical context

## What NOT to Archive
- Backups of current files (use `/backup`)
- Temporary files (delete these)
- Generated files (regenerate when needed)
- Database files (use `/backup`)

## Archive vs Backup
- **Archive**: Historical reference
  - Old versions
  - Superseded content
  - Past decisions
  - Located in `/archive`

- **Backup**: Disaster recovery
  - Current file copies
  - Active database snapshots
  - System configurations
  - Located in `/backup`
  - Follow 3-2-1 backup strategy

## Process
1. Identify content to archive
2. Rename following convention
3. Move to `/archive`
4. Update any references
5. Document the archival in session notes
