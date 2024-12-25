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

## Backup Metadata
Each backup is tracked in `backup_metadata.json` with detailed information about its lifecycle, contents, and status.

### Structure
```json
{
  "daily": {
    "YYYYMMDD": {
      "created": "ISO-8601 timestamp",
      "expires": "ISO-8601 timestamp",
      "files": {
        "relative/path/to/file": {
          "size": "bytes",
          "hash": "sha256_hash",
          "has_wal": "boolean, for db files"
        }
      },
      "status": "active|expired|verified",
      "verified": "boolean"
    }
  },
  "pre_change": {
    "YYYYMMDD_HHMM_description": {
      "created": "ISO-8601 timestamp",
      "description": "Change description",
      "status": "pending_verification|verified|retired",
      "files": {
        "relative/path/to/file": {
          "size": "bytes",
          "hash": "sha256_hash"
        }
      },
      "change_ticket": "reference to change",
      "retention": "until_verified|days_N|permanent",
      "verified_by": "developer name",
      "verified_date": "ISO-8601 timestamp"
    }
  },
  "manual": {
    "YYYYMMDD_HHMM_description": {
      "created": "ISO-8601 timestamp",
      "creator": "developer name",
      "purpose": "backup purpose",
      "files": {
        "relative/path/to/file": {
          "size": "bytes",
          "hash": "sha256_hash"
        }
      },
      "retention": "days_N|permanent",
      "notes": "additional context"
    }
  }
}
```

### Fields
1. **Common Fields**
   - `created`: Creation timestamp
   - `files`: Inventory of backed up files
   - `size`: File size in bytes
   - `hash`: SHA-256 hash for integrity

2. **Daily Specific**
   - `expires`: Auto-calculated expiration
   - `status`: Current backup status
   - `verified`: Integrity check status

3. **Pre-change Specific**
   - `description`: Change being made
   - `change_ticket`: Reference to change
   - `status`: Verification status
   - `verified_by`: Who verified the change
   - `verified_date`: When verified

4. **Manual Specific**
   - `creator`: Who made the backup
   - `purpose`: Why it was created
   - `notes`: Additional context
   - `retention`: Custom retention policy

### Usage
1. **Automation**
   ```python
   # Check expiring backups
   expiring = [b for b in daily_backups 
               if b.expires < today + timedelta(days=7)]
   
   # Verify integrity
   for file in backup.files:
       assert hash(file) == file.hash
   
   # Calculate storage
   total_size = sum(f.size for b in backups for f in b.files)
   ```

2. **Monitoring**
   - Track backup completeness
   - Monitor storage usage
   - Alert on verification needs
   - Report on retention status

3. **Recovery**
   - Find latest valid backup
   - Verify file integrity
   - Track recovery steps
   - Document verification

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
