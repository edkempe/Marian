# 5. Schema Configuration Management

Date: 2025-01-01

## Status

Proposed

## Context

The application needs a reliable way to manage database schema configurations, including column sizes, default values, and validation rules. Currently, there are inconsistencies between different parts of the codebase:

1. Schema configurations exist in multiple places:
   - `config/schema.yaml`: YAML configuration file
   - `shared_lib/schema_constants.py`: Python constants
   - Various archived schema constant files
   - Hardcoded values in some models

2. There's no clear process for:
   - Maintaining consistency between these different sources
   - Validating schema changes
   - Generating code from the configuration
   - Enforcing the use of schema constants in models

3. This has led to:
   - Inconsistent column sizes across models
   - Duplicate and potentially conflicting definitions
   - Difficulty in maintaining and updating schema configurations
   - Risk of schema-related bugs

## Decision

We will implement a schema configuration management system with the following components:

1. **Single Source of Truth**
   - `config/schema.yaml` will be the sole source of truth for schema configuration
   - All schema-related constants will be generated from this file
   - The YAML format provides better readability and maintainability than code

2. **Schema Configuration Loading**
   - `shared_lib/config_loader.py` will handle loading and validating the YAML configuration
   - Uses Pydantic models for validation and type safety
   - Supports environment-specific configurations (e.g., `schema.test.yaml`)

3. **Code Generation**
   - New script `tools/generate_schema_constants.py` will generate:
     - Python constants from YAML config
     - Type hints and documentation
     - Validation code
   - Generated code will be marked as auto-generated to prevent manual edits

4. **Model Validation**
   - Models must use constants from the generated code
   - Static analysis tools will enforce this requirement
   - Runtime validation will catch any mismatches

5. **Migration Process**
   - Schema changes must be made in `schema.yaml`
   - Running `generate_schema_constants.py` creates/updates constants
   - Alembic migrations use the generated constants

## Consequences

### Positive

1. **Consistency**: Single source of truth eliminates inconsistencies
2. **Maintainability**: Schema changes are made in one place
3. **Type Safety**: Generated code provides type hints and validation
4. **Documentation**: Schema configuration is self-documenting
5. **Flexibility**: Easy to add new schema properties and validation rules
6. **Reliability**: Reduced risk of schema-related bugs

### Negative

1. **Additional Step**: Need to run code generation after schema changes
2. **Learning Curve**: Team needs to learn the new process
3. **Migration**: Existing code needs to be updated to use generated constants

### Neutral

1. **Build Process**: Code generation becomes part of the build process
2. **Version Control**: Generated files need to be committed
3. **Testing**: Need to test both configuration and generated code

## Implementation Plan

1. **Phase 1: Setup**
   - Create schema.yaml template
   - Implement config loading and validation
   - Create code generation script

2. **Phase 2: Migration**
   - Update existing models to use generated constants
   - Remove duplicate/archived schema files
   - Add validation to CI pipeline

3. **Phase 3: Documentation**
   - Update developer documentation
   - Add schema management guidelines
   - Create examples and templates

## References

- [ADR-0004: Schema Constants in Shared Lib](0004-schema-constants-in-shared-lib.md)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
