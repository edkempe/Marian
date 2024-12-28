# Shared Library

**Version:** 1.0.0  
**Status:** Authoritative

> Core utilities and shared functionality for the Marian project.

## Overview
- **Purpose**: Provide common utilities
- **Stability**: Stable
- **Maintenance**: Active
- **Python**: >= 3.12

## Directory Structure
```
/shared_lib/
├── README.md              # This file
├── constants.py           # Project constants
├── database.py           # Database utilities
└── gmail_lib.py          # Gmail API utilities
```

## Core Components
1. **Constants**
   - Purpose: Project-wide constants
   - When to use: Accessing shared values
   - Location: `constants.py`

2. **Database Utilities**
   - Purpose: Database connection and helpers
   - When to use: Database operations
   - Location: `database.py`

## Version History
- 1.0.0 (2024-12-28): Initial library structure
  - Created core utilities
  - Added constants management
  - Established database helpers
