# Configuration Archive

**Version:** 1.0.0  
**Status:** Authoritative  
**Template:** [../../docs/templates/ARCHIVING.md](../../docs/templates/ARCHIVING.md)

> Archive of superseded configuration files, maintaining configuration history while keeping active settings clear.

## Quick Reference
```bash
# Archive a config file
mv old_config.yaml ARCHIVED_$(date +%Y%m%d_%H%M)_old_config.yaml

# Find archived config by content
grep -r "setting_name" .

# List recent archives
ls -lt | head
```

## Overview
- **Purpose**: Store superseded configs
- **Stability**: Stable
- **Maintenance**: Active
- **Formats**: YAML, JSON, INI, etc.

---

## Directory Structure
```
/config/archive/
├── README.md                           # This file
├── ARCHIVED_YYYYMMDD_HHMM_*.yaml      # Archived YAML configs
├── ARCHIVED_YYYYMMDD_HHMM_*.json      # Archived JSON configs
└── ARCHIVED_YYYYMMDD_HHMM_*.{ext}     # Other config types
```

## Archive Guidelines

1. **What to Archive**
   - Old configuration files
   - Deprecated settings
   - Previous environments
   - Build configurations

2. **When to Archive**
   - Config format changes
   - Major version updates
   - Environment changes
   - Setting deprecation

3. **Archive Process**
   - Add ARCHIVED prefix with timestamp
   - Move to `/config/archive`
   - Update any references
   - Note archival in session log

4. **Archive Organization**
   - Flat directory structure
   - No subdirectories
   - Chronological by archive date

## Version History
- 1.0.0: Initial version - Configuration archive setup
