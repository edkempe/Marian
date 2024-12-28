# Backup Directory

**Version:** 1.0.1  
**Status:** Authoritative

> Implements the 3-2-1 backup strategy: 3 copies of data, 2 different storage types, 1 copy offsite.

## Quick Reference
```bash
# Create daily backup directory
mkdir -p $(date +%Y%m%d)

# Backup database
cp database.db $(date +%Y%m%d)/database_$(date +%H%M).db

# List today's backups
ls -l $(date +%Y%m%d)/

# Verify backup integrity
sqlite3 $(date +%Y%m%d)/database_*.db "PRAGMA integrity_check;"
```

Common operations:
- Create daily backup directory
- Backup database files
- Verify backup integrity
- Clean old backups

## Overview
- **Purpose**: Data resilience and recovery
- **Stability**: Stable
- **Maintenance**: Active
- **Security**: High (Contains sensitive data)

---

## Directory Structure
```
/backup/
├── README.md                  # This file
└── YYYYMMDD/                 # Date-based directories
    ├── *.bak                # General backups
    ├── *.db                 # Database snapshots
    └── *.config             # Configuration backups
```

## Core Components

1. **Daily Backups**
   - Purpose: Regular data protection
   - When to use: Daily operations
   - Example:
     ```bash
     # Create daily backup
     ./scripts/backup_daily.sh
     ```

2. **Pre-Change Backups**
   - Purpose: Safety before changes
   - When to use: Before migrations/updates
   - Example:
     ```bash
     # Pre-migration backup
     ./scripts/backup_premigration.sh
     ```

---

## Backup Guidelines

### Content Types
1. **Critical Data**
   - Database files (.db)
   - User configurations (.config)
   - System settings (.bak)
   - Authentication tokens (.secret)

2. **System State**
   - Environment configurations
   - Dependencies
   - Runtime settings

### What NOT to Store
- Archived files (use `/archive`)
- Temporary files
- Cache files
- Version-controlled files
- AI assistance files (use `/docs`)

### Naming Convention
1. **Directories**
   - Format: `YYYYMMDD`
   - Example: `20241228`

2. **Files**
   - Format: `name_HHMM.ext`
   - Example: `database_1430.db`
   - Extensions:
     - `.bak`: General backups
     - `.db`: Database snapshots
     - `.config`: Configuration files

---

## Security and Maintenance

### Security Requirements
- Restricted access
- Encryption for offsite copies
- Regular security audits
- No sensitive data in filenames

### Maintenance Tasks
1. **Daily**
   - Create dated directory
   - Backup critical data
   - Verify integrity

2. **Weekly**
   - Clean old backups
   - Test restoration
   - Update offsite copy

3. **Monthly**
   - Full integrity check
   - Security audit
   - Storage optimization

---

## Related Documentation
- Parent: `../README.md` - Project root
- `../docs/backup.md` - Backup procedures
- `../archive/README.md` - Archive procedures

## Version History
- 1.0.1: Added quick reference, improved guidelines
- 1.0.0: Initial backup system setup
