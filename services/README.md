# Jexi Services

**Version:** 1.0.0
**Status:** Authoritative

> Business logic and application services for the Jexi project.

## Overview
- **Purpose**: Implement business operations
- **Stability**: Stable
- **Maintenance**: Active
- **Python**: >= 3.12

## Directory Structure
```
/services/
├── README.md              # This file
├── email_service.py       # Email processing service
├── analysis_service.py    # Content analysis service
├── gmail_service.py       # Gmail API service
├── catalog_service.py     # Marian's catalog management service
├── librarian_service.py   # Marian's core functionality
├── monitoring_service.py  # System monitoring
└── migration_service.py   # Database migrations
```

## Core Components
1. **Email Service**
   - Purpose: Process and analyze emails
   - When to use: Email operations
   - Location: `email_service.py`

2. **Catalog Service**
   - Purpose: Manage email catalogs
   - When to use: Catalog operations
   - Location: `catalog_service.py`

3. **Analysis Service**
   - Purpose: Analyze content
   - When to use: Content analysis operations
   - Location: `analysis_service.py`

4. **Gmail Service**
   - Purpose: Interact with Gmail API
   - When to use: Gmail operations
   - Location: `gmail_service.py`

5. **Librarian Service**
   - Purpose: Marian's core functionality
   - When to use: Marian operations
   - Location: `librarian_service.py`

6. **Monitoring Service**
   - Purpose: Monitor system
   - When to use: System monitoring operations
   - Location: `monitoring_service.py`

7. **Migration Service**
   - Purpose: Perform database migrations
   - When to use: Database migration operations
   - Location: `migration_service.py`

## Version History
- 1.0.0 (2024-12-28): Initial service structure
  - Created email and catalog services
  - Added service interfaces
  - Established service boundaries
