# 7. External Tool Integration Policy

Date: 2024-12-31

## Status

Accepted

## Context

The project relies on various external tools and services for development, testing, and runtime operations:

1. Development Environment:
   - Code editing and AI assistance
   - Build and deployment tools
   - Version control and CI/CD

2. Runtime Dependencies:
   - System-level utilities
   - External APIs and services
   - Performance optimization tools

3. Testing and Quality:
   - Test runners and frameworks
   - Code quality tools
   - Security scanning

## Decision

We will document and standardize our use of external tools across several categories:

### 1. Development Environment

| Tool | Purpose | Installation | Benefits |
|------|----------|-------------|-----------|
| Windsurf.ai | IDE & AI Copilot | Web-based | - Advanced AI pair programming<br>- Integrated development environment<br>- Context-aware assistance |
| Git | Version Control | `brew install git` | - Distributed version control<br>- Branch management<br>- Collaboration |
| pre-commit | Git hooks | `pip install pre-commit` | - Automated code formatting<br>- Quality checks<br>- Consistent commits |
| pyenv | Python Version Management | `brew install pyenv` | - Multiple Python versions<br>- Project-specific Python versions<br>- Automatic version switching |

### 2. Build and Testing Tools

| Tool | Purpose | Installation | Benefits |
|------|----------|-------------|-----------|
| Poetry | Dependency & Task Management | `curl -sSL https://install.python-poetry.org | python3 -` | - Dependency management<br>- Virtual environment handling<br>- Task running<br>- Lock file for reproducible builds |
| pytest | Test framework | `pip install pytest` | - Comprehensive testing<br>- Plugin ecosystem<br>- Clear test organization |
| bandit | Security testing | `pip install bandit` | - Security vulnerability scanning<br>- Best practice enforcement |
| rmlint | Duplicate detection | `brew install rmlint` | - 2400x faster than custom code<br>- Handles edge cases<br>- Built-in caching |

### 3. Runtime Dependencies

| Tool | Purpose | Installation | Benefits |
|------|----------|-------------|-----------|
| SQLite | Database | Built into Python | - Lightweight<br>- Zero configuration<br>- Reliable |
| alembic | DB migrations | `pip install alembic` | - Version control for schema<br>- Automated migrations<br>- Rollback support |

### 4. External Services

| Service | Purpose | Configuration | Benefits |
|---------|----------|--------------|-----------|
| Gmail API | Email integration | OAuth 2.0 | - Reliable email access<br>- Rich feature set |
| Anthropic API | AI processing | API key | - Advanced language processing<br>- Reliable performance |

## Tool Decisions

### Chosen Tools

1. **Database Access**:
   - **Chosen**: SQLAlchemy with Alembic
   - **Rejected**: Direct SQLite imports
   - **Rationale**: SQLAlchemy provides ORM, migration support, and better abstraction
   - **Migration Plan**: Replace direct SQLite usage with SQLAlchemy throughout codebase

2. **Duplicate Detection**:
   - **Chosen**: rmlint
   - **Rejected**: Custom Python implementation
   - **Rationale**: 2400x performance improvement, better edge case handling
   - **Migration**: Completed, removed custom cache implementation

3. **Testing Framework**:
   - **Chosen**: pytest with plugins
   - **Rejected**: unittest
   - **Rationale**: Better fixtures, parameterization, and plugin ecosystem

4. **Version Control**:
   - **Chosen**: Git with pre-commit hooks
   - **Rejected**: Manual version control
   - **Rationale**: Industry standard, better collaboration

5. **Development Environment**:
   - **Chosen**: Windsurf.ai
   - **Alternatives**: VS Code, PyCharm
   - **Rationale**: Integrated AI assistance, modern features

6. **Dependency and Task Management**:
   - **Chosen**: Poetry
   - **Rejected**: Make, pip with requirements.txt
   - **Rationale**: Poetry provides modern dependency management, virtual environment handling, and task running capabilities in one tool
   - **Migration Plan**: Replace manual dependency management with Poetry, migrate task running from Make to Poetry scripts

### Evaluation Criteria

When evaluating tools, we consider:
1. Performance impact (>10x improvement)
2. Maintenance burden
3. Community support and documentation
4. Security implications
5. Integration complexity

### Future Considerations

1. **Containerization**:
   - Currently evaluating Docker for development consistency
   - Would simplify tool installation and version management

2. **CI/CD Tools**:
   - Evaluating GitHub Actions vs. Jenkins
   - Need to ensure all external tools are available in CI environment

## Integration Requirements

1. **Documentation**:
   - List in README.md
   - Include installation instructions
   - Document configuration steps
   - Explain version requirements

2. **Error Handling**:
   - Graceful degradation
   - Clear error messages
   - Alternative paths when available

3. **Security**:
   - Credential management
   - Access control
   - Regular updates
   - Vulnerability scanning

4. **Testing**:
   - Integration tests
   - Mocking capabilities
   - CI/CD compatibility

## Consequences

### Positive

- Leverages battle-tested solutions
- Reduces maintenance burden
- Improves development efficiency
- Better security through standard tools

### Negative

- External dependencies
- Version management complexity
- Learning curve for new tools
- Potential licensing issues

### Mitigations

1. **Dependency Management**:
   - Lock file versions
   - Regular updates
   - Compatibility testing

2. **Knowledge Transfer**:
   - Tool documentation
   - Usage examples
   - Training resources

3. **Security**:
   - Regular audits
   - Update monitoring
   - Security scanning

## References

- [Windsurf.ai Documentation](https://windsurf.ai/)
- [rmlint Documentation](https://rmlint.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Anthropic API Documentation](https://docs.anthropic.com/claude/)
- [Poetry Documentation](https://python-poetry.org/docs/)
