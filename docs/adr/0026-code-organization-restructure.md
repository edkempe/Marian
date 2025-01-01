# 26. Code Organization Restructure

Date: 2025-01-01

## Status

Proposed

## Context

Our current code organization has several issues:

1. **Inconsistent Directory Structure**
- Multiple utility locations (`utils/`, `tools/`, `shared_lib/`)
- Source code split between `src/` and root
- Unclear separation between scripts and applications
- Multiple configuration locations

2. **Architectural Violations**
- Scripts in both `scripts/` and `src/`
- No clear service layer
- Mixed responsibilities in `shared_lib/`
- Unclear domain boundaries

3. **Configuration Sprawl**
- Environment variables in multiple files
- Scattered config files
- Unconsolidated constants

4. **Testing Misalignment**
- Test structure doesn't mirror source
- Unclear fixture organization
- Mixed test types

## Decision

We will reorganize the codebase following Python best practices and clean architecture principles:

### 1. Core Directory Structure
```
jexi/
├── src/                    # All source code
│   ├── api/               # API interfaces
│   │   ├── rest/         # REST endpoints
│   │   └── graphql/      # GraphQL schemas
│   ├── core/             # Core business logic
│   │   ├── entities/     # Business entities
│   │   └── interfaces/   # Abstract interfaces
│   ├── models/           # Domain models
│   │   ├── email/       # Email-related models
│   │   └── catalog/     # Catalog-related models
│   ├── services/         # Business services
│   │   ├── analysis/    # Analysis services
│   │   └── storage/     # Storage services
│   └── utils/            # Utilities
│       ├── db/          # Database utilities
│       └── logging/     # Logging utilities
├── scripts/              # Entry point scripts
│   ├── analysis/        # Analysis scripts
│   └── maintenance/     # Maintenance scripts
├── config/               # All configuration
│   ├── settings/        # App settings
│   │   ├── base.py     # Base settings
│   │   ├── dev.py      # Development settings
│   │   └── prod.py     # Production settings
│   └── constants/       # Business constants
│       ├── paths.py    # Path constants
│       └── rules.py    # Business rules
├── tests/               # Tests mirror src/
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── fixtures/       # Test fixtures
└── tools/               # Development tools
    ├── linting/        # Linting configs
    └── scripts/        # Dev scripts
```

### 2. Key Principles

1. **Single Source of Truth**
   - All source code in `src/`
   - All configuration in `config/`
   - Clear separation of settings and constants

2. **Clear Dependencies**
   - Core domain models independent
   - Services depend on models
   - APIs depend on services
   - No circular dependencies

3. **Configuration Hierarchy**
   - Environment variables for secrets
   - Settings files for app config
   - Constants for business rules

4. **Testing Structure**
   - Tests mirror source structure
   - Clear separation of test types
   - Hierarchical fixtures

### 3. Implementation Rules

1. **Imports**
```python
# Allowed
from src.core.entities import Entity
from src.models.email import EmailModel
from src.services.analysis import AnalysisService

# Not Allowed
from scripts import utility
from src import models
import * from anywhere
```

2. **Dependencies**
```
core -> No dependencies
models -> core
services -> models, core
api -> services, models, core
scripts -> any
```

3. **Configuration**
```python
# Settings (config/settings/base.py)
DATABASE_URL = os.getenv('DATABASE_URL')

# Constants (config/constants/rules.py)
MAX_RETRY_ATTEMPTS = 3
EMAIL_TYPES = ['personal', 'work']
```

## Consequences

### Positive
1. Clear organization and responsibilities
2. Easier maintenance and testing
3. Better dependency management
4. Simplified onboarding
5. Improved AI assistance

### Negative
1. Significant migration effort
2. Temporary code instability
3. Need to update all imports
4. Learning curve for new structure

### Mitigation
1. Phased migration approach
2. Comprehensive testing
3. Clear documentation
4. Automated import updates

## Related Decisions
- [ADR-0001](0001-layered-architecture.md): Base architecture
- [ADR-0009](0009-constants-consolidation.md): Constants management
- [ADR-0025](0025-documentation-industry-alignment.md): Documentation

## Notes
- Migration will be phased
- Each phase must maintain functionality
- Tests must pass at each step
