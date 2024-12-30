# 4. Configuration-Based Schema Definitions

Date: 2024-12-29

## Status

Accepted

## Context

We had schema-related constants (column sizes, default values, validation rules) duplicated between the models layer and shared library layer. This created maintenance issues and potential inconsistencies. We needed a solution that would:

1. Provide a single source of truth for schema definitions
2. Support different environments (development, testing, production)
3. Follow Infrastructure as Code (IaC) principles
4. Be easily maintainable and extensible
5. Maintain proper separation of concerns

## Decision

We decided to implement a configuration-based approach using YAML files for schema definitions:

1. Create `config/schema.yaml` as the primary schema configuration file
2. Support environment-specific overrides (e.g., `schema.development.yaml`)
3. Use Pydantic for configuration validation and type safety
4. Implement a configuration loader in shared_lib
5. Update models to use the configuration system

Example configuration:
```yaml
email:
  columns:
    subject:
      size: 500
      type: string
      description: "Maximum size for email subject"
  defaults:
    subject: ""
    has_attachments: false
```

Example model usage:
```python
from shared_lib.config_loader import get_schema_config

config = get_schema_config().email

class Email(Base):
    subject = Column(
        String(config.columns["subject"].size),
        server_default=config.defaults.subject
    )
```

## Configuration Truth Hierarchy

The system follows a strict configuration precedence order, from highest to lowest priority:

1. Environment Variables (`.env` or system)
   ```bash
   # Overrides all other config locations
   export SCHEMA_CONFIG_PATH=/custom/path/schema.yaml
   export ENV=production
   ```

2. Environment-specific YAML (`/config/schema.{env}.yaml`)
   ```yaml
   # /config/schema.production.yaml
   email:
     columns:
       subject:
         size: 1000  # Production needs longer subjects
         type: string
         description: "Email subject line"
   ```

3. Default YAML (`/config/schema.yaml`)
   ```yaml
   # /config/schema.yaml
   email:
     columns:
       subject:
         size: 500  # Standard size
         type: string
         description: "Email subject line"
     defaults:
       has_attachments: false
   ```

4. Pydantic Models (`/shared_lib/config_loader.py`)
   ```python
   class ColumnConfig(BaseModel):
       size: int = Field(gt=0, default=100)
       type: str = Field(pattern="^(string|text)$")
       description: str = Field(min_length=1)
   ```

5. SQLAlchemy Models (`/models/email.py`, `/models/email_analysis.py`)
   ```python
   class Email(Base):
       subject = Column(String(100))  # Fallback if all else fails
   ```

Configuration flows down this hierarchy, with each level providing defaults that can be overridden by levels above it. This ensures both flexibility and safety.

## Consequences

### Positive

1. **Infrastructure as Code Benefits**:
   - Schema definitions are declarative and version-controlled
   - Supports different environments
   - Easy to review and validate
   - Aligns with DevOps practices

2. **Maintainability**:
   - Single source of truth for schema definitions
   - Easy to modify without code changes
   - Clear separation of configuration from code
   - Self-documenting through YAML structure

3. **Type Safety and Validation**:
   - Configuration is validated at startup
   - Type hints provide IDE support
   - Errors caught early in development

4. **Flexibility**:
   - Easy to add new schema properties
   - Supports environment-specific configurations
   - Can extend validation rules
   - Documentation built into configuration

### Negative

1. **Additional Complexity**:
   - Need to manage configuration files
   - Must handle configuration loading and validation
   - Potential for runtime errors if configuration is invalid

2. **Learning Curve**:
   - Developers need to understand configuration system
   - Need to maintain configuration documentation
   - May need to debug configuration issues

### Neutral

1. Need to decide on configuration file locations and naming conventions
2. May need to implement configuration caching for performance
3. Must manage configuration file versioning

## Notes

- Keep configuration files in version control
- Document configuration schema and validation rules
- Consider adding configuration validation to CI/CD pipeline
- Monitor configuration file size and complexity

## References

- [Infrastructure as Code](https://www.martinfowler.com/bliki/InfrastructureAsCode.html)
- [12-Factor App: Config](https://12factor.net/config)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [YAML Specification](https://yaml.org/spec/1.2/spec.html)
