# ADR 001: Layered Architecture Design

**Version:** 1.0.0  
**Status:** Authoritative (2024-12-28)

## Context
The Marian project needs a clear architectural structure that:
1. Enforces separation of concerns
2. Prevents circular dependencies
3. Makes the codebase maintainable and testable
4. Establishes clear ownership of domain models and business logic

## Decision
We will use a layered architecture with the following structure:

### 1. Foundation Layer (shared_lib/)
- Core utilities, constants, and infrastructure
- Cannot import from other layers
- Must be self-contained
- Contains both configuration constants (paths, settings) and domain constants (enums, rules)
- Examples: database utilities, logging, domain enums

### 2. Domain Layer (models/)
- Source of truth for domain entities and business rules
- Can import from shared_lib and other models
- Contains SQLAlchemy models and core business rules
- Models are authoritative - they define what is valid in our domain
- Examples: Email, EmailAnalysis, AssetCatalog models

### 3. Service Layer (services/)
- Business logic and use cases
- Can import from models and shared_lib
- Orchestrates domain models to implement features
- Examples: EmailAnalysisService, AssetCatalogService

### 4. Script Layer (scripts/)
- Application entry points
- Can import from services, models, and shared_lib
- Cannot import from other scripts
- Each script is standalone - shared code belongs in a library layer
- Examples: analyze_emails.py, generate_report.py

## Constants Management
We maintain two types of constants:

1. Configuration Constants (shared_lib/constants.py)
   - Application settings
   - Directory paths
   - Database configurations
   - API settings
   - Logging configurations

2. Domain Constants (shared_lib/constants.py)
   - Enums defining valid domain values
   - Business rule constraints
   - Domain-specific validation rules
   - Used across all layers

All constants live in shared_lib to ensure:
- Single source of truth
- Consistent usage across layers
- No circular dependencies
- Easy maintenance

## Architectural Rules
1. No circular dependencies between any modules
2. shared_lib can only import from shared_lib
3. models can import from models and shared_lib
4. services can import from models and shared_lib
5. scripts can import from services, models, and shared_lib but not other scripts

## Consequences

### Positive
1. Clear separation of concerns with defined responsibilities
2. Domain models are authoritative source of truth
3. Business logic is centralized in services
4. Prevents tangled dependencies
5. Makes testing easier with clear boundaries
6. Scripts remain simple entry points
7. Constants are managed consistently in shared_lib

### Negative
1. More initial setup required
2. May need to move code between layers as requirements evolve
3. Some duplication might occur to maintain layer separation

## Validation
The architecture is enforced through:
1. test_dependencies.py which checks for layer violations
2. Continuous integration tests
3. Code review process

## Notes
- Models being authoritative means they define what operations are valid
- If code needs to be shared between scripts, it belongs in a library layer
- Service layer keeps business logic separate from models while having access to domain rules
- All constants (both configuration and domain) live in shared_lib for consistency

## Version History
- 1.0.0 (2024-12-28): Initial architecture design
  - Defined layered architecture with shared_lib, models, services, and scripts
  - Established layer boundaries and dependency rules
  - Moved all constants (configuration and domain) to shared_lib
