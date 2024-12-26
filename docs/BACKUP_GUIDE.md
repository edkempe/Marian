# Backup Guide

## Purpose
The backup system ensures data resilience through the 3-2-1 backup strategy:
- 3 copies of data
- 2 different storage types
- 1 copy offsite

## Location Structure
```
/backup/
└── YYYYMMDD/           # Date-based directories
    ├── *.bak          # General backups
    ├── *.db           # Database snapshots
    └── *.config       # Configuration backups
```

## Naming Convention
1. Date-based directories: `YYYYMMDD`
2. File extensions:
   - `.bak` - General backups
   - `.db` - Database snapshots
   - `.config` - Configuration files
   - `.db-shm`, `.db-wal` - SQLite auxiliary files

## What to Backup
1. Critical Data:
   - Database files
   - User configurations
   - System settings
   - Authentication tokens

2. Code Safeguards:
   - Pre-migration copies
   - Pre-update snapshots
   - Configuration files

3. System State:
   - Environment configurations
   - Dependencies
   - Runtime settings

## What NOT to Backup
- Archived files (use `/archive`)
- Temporary files
- Cache files
- Log files (use log rotation)
- Generated files (can be recreated)

## Backup Metadata
Each backup includes a metadata file in JSON format. See `docs/examples/backup_metadata_example.json` for a complete example.

Structure:
```json
{
  "daily": {
    "YYYYMMDD": {
      "created": "ISO-8601 timestamp",
      "expires": "ISO-8601 timestamp",
      "files": {
        "filename.ext": {
          "size": bytes,
          "hash": "sha256_hash",
          "original_path": "absolute/path/to/original"
        }
      },
      "status": "active|expired",
      "verified": boolean
    }
  }
}
```

## Backup vs Archive
- **Backup**: Disaster recovery
  - Current state
  - Active files
  - System configurations
  - Located in `/backup`
  - Follow 3-2-1 strategy

- **Archive**: Historical reference
  - Old versions
  - Superseded content
  - Past decisions
  - Located in `/archive`

## Process
1. Daily Backups:
   ```bash
   mkdir -p backup/YYYYMMDD
   cp file.ext backup/YYYYMMDD/file.ext.bak
   ```

2. Database Backups:
   - Pre-migration
   - Daily snapshots
   - Keep WAL files

3. Configuration Backups:
   - System settings
   - User preferences
   - Environment variables

4. Validation:
   - Check backup integrity
   - Verify completeness
   - Test restoration
   - Monitor storage usage

## Retention Policy
1. Daily Backups:
   - Keep 30 days rolling
   - Automated cleanup
   - Monitor storage usage

2. Pre-change Backups:
   - Keep until change verified
   - Document verification
   - Manual cleanup

3. Manual Backups:
   - Developer managed
   - Document purpose
   - Clear cleanup criteria

4. Database Snapshots:
   - Keep all pre-migration
   - Keep 30 days rolling
   - Include WAL files

## Success Criteria
- All critical data backed up
- 3-2-1 strategy followed
- Backups verified
- Restoration tested
- Storage monitored

## Dependencies
- Backup verification tools
- Storage monitoring
- Automated rotation
- Integrity checks
