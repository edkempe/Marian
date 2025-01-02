# 20. API Schema Validation System

Date: 2025-01-01

## Status

Proposed

## Context

Following our API-First Schema Design (ADR-0019), we needed a concrete implementation to:

1. Store and version external API specifications
2. Validate our models against these specifications
3. Automate schema compatibility checks
4. Provide clear documentation of API mappings

While ADR-0019 established the principles and ADR-0004 covered configuration management, we needed to decide how to implement these in practice.

## Decision

We will implement a comprehensive API schema validation system with the following components:

### 1. API Specification Storage
- Store OpenAPI/Swagger specifications in YAML format
- Location: `api_specs/<api_name>/<version>/<resource>.yaml`
- Example: `api_specs/gmail/v1/label.yaml`
- Version control these specifications
- Include official API documentation links

### 2. Schema Validator
- Create `models/validators/api_schema.py`
- Use Pydantic for schema validation
- Cache loaded schemas for performance
- Implement type compatibility checking
- Support nullable fields and enums

### 3. Automated Validation
- Use SQLAlchemy events for automatic validation
- Validate on database creation
- Support pre-commit hooks
- Generate validation reports

### 4. Implementation Example
```python
# API Schema (api_specs/gmail/v1/label.yaml)
components:
  schemas:
    Label:
      type: object
      properties:
        name:
          type: string
          maxLength: 255

# Model Validation (models/gmail_label.py)
@event.listens_for(Base.metadata, 'after_create')
def validate_schemas(target, connection, **kw):
    api_validator.validate_model(GmailLabel, "gmail", "v1", "label")
```

## Consequences

### Positive
1. **Automated Compliance**: Ensures models stay in sync with APIs
2. **Version Control**: API specs are versioned with code
3. **Documentation**: Specs serve as authoritative documentation
4. **Type Safety**: Catches type mismatches early

### Negative
1. **Maintenance**: Must keep API specs updated
2. **Complexity**: Additional validation layer
3. **Build Time**: Validation adds overhead

### Mitigation
1. Use automated tools to fetch API specs
2. Cache validation results
3. Make validation optional in development

## Related Decisions
- [ADR-0019](0019-api-first-schema-design.md): API-First Schema Design
- [ADR-0004](0004-configuration-based-schema-definitions.md): Configuration System

## Notes
- Consider implementing automated API spec updates
- Add validation to CI/CD pipeline
- Create tools to generate API specs from documentation
