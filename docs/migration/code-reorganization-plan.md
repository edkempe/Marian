# Code Reorganization Migration Plan

## Overview
This document outlines the step-by-step plan for reorganizing the codebase according to [ADR-0026](../adr/0026-code-organization-restructure.md).

## Phase 1: Preparation (Week 1)

### 1.1 Create New Structure
```bash
mkdir -p src/{api/{rest,graphql},core/{entities,interfaces},services/{analysis,storage},utils/{db,logging}}
mkdir -p config/{settings,constants}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p scripts/{analysis,maintenance}
mkdir -p tools/{linting,scripts}
```

### 1.2 Create Base Files
```bash
# Configuration
touch config/settings/{base,dev,prod}.py
touch config/constants/{paths,rules}.py

# Core structure markers
touch src/{api,core,services,utils}/__init__.py
```

### 1.3 Setup Import Structure
```python
# src/__init__.py
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
```

## Phase 2: Configuration Migration (Week 1)

### 2.1 Settings Consolidation
1. Migrate environment variables
   - Audit all .env files
   - Create comprehensive .env.example
   - Update documentation

2. Create settings hierarchy
   ```python
   # config/settings/base.py
   from pathlib import Path
   
   ROOT_DIR = Path(__file__).parent.parent.parent
   
   # Common settings
   DEBUG = False
   LOGGING_LEVEL = 'INFO'
   ```

### 2.2 Constants Migration
1. Implement ADR-0009
2. Move all constants to config/constants/
3. Update all imports

## Phase 3: Core Components (Week 2)

### 3.1 Domain Models
1. Move models/ to src/models/
2. Organize by domain
   ```
   src/models/
   ├── email/
   ├── catalog/
   └── shared/
   ```

### 3.2 Core Business Logic
1. Create core entities
2. Define interfaces
3. Implement base classes

### 3.3 Services Layer
1. Create service classes
2. Implement dependency injection
3. Move business logic from scripts

## Phase 4: Utils and Tools (Week 2)

### 4.1 Utility Consolidation
1. Audit utils/, tools/, shared_lib/
2. Categorize utilities
3. Migrate to new structure
4. Update imports

### 4.2 Development Tools
1. Move development scripts to tools/
2. Update tool configurations
3. Document tool usage

## Phase 5: Scripts and Entry Points (Week 3)

### 5.1 Script Migration
1. Categorize current scripts
2. Create new script structure
3. Update imports and paths
4. Add script documentation

### 5.2 Entry Point Updates
1. Update main entry points
2. Verify CLI functionality
3. Update script documentation

## Phase 6: Testing (Week 3)

### 6.1 Test Restructure
1. Create new test hierarchy
2. Migrate existing tests
3. Update test imports
4. Organize fixtures

### 6.2 Test Coverage
1. Identify coverage gaps
2. Add missing tests
3. Verify all features

## Phase 7: Documentation and Cleanup (Week 4)

### 7.1 Documentation Updates
1. Update README files
2. Update API documentation
3. Update development guides
4. Create architecture diagrams

### 7.2 Final Cleanup
1. Remove old directories
2. Verify all imports
3. Run full test suite
4. Update CI/CD configs

## Validation Checklist

### For Each Phase
- [ ] All tests pass
- [ ] No broken imports
- [ ] Documentation updated
- [ ] Code review completed
- [ ] Performance verified

### Final Validation
- [ ] All features working
- [ ] No deprecated paths
- [ ] Complete documentation
- [ ] Clean git history

## Rollback Plan

### For Each Phase
1. Git tag before changes
2. Backup of critical files
3. Documented reversion steps
4. Test environment validation

### Emergency Rollback
```bash
# Tag current state
git tag -a pre_migration_phase_X -m "Pre-migration state"

# If needed, rollback
git reset --hard pre_migration_phase_X
```

## Success Criteria
1. All tests passing
2. No broken imports
3. All features working
4. Improved code organization
5. Clear documentation
6. Better maintainability

## Timeline
- Week 1: Phases 1-2
- Week 2: Phases 3-4
- Week 3: Phases 5-6
- Week 4: Phase 7

## Resources Needed
1. Development environment
2. Test environment
3. CI/CD pipeline
4. Code review capacity
5. Testing time

## Risk Management

### High-Risk Areas
1. Import dependencies
2. Configuration changes
3. Script functionality
4. Test coverage

### Mitigation Strategies
1. Phased approach
2. Comprehensive testing
3. Regular backups
4. Clear documentation
5. Review checkpoints
