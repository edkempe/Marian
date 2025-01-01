# 10. Documentation Standards Organization

Date: 2024-12-31
Updated: 2025-01-01

## Status

Accepted

## Revision History
1.0.0 (2024-12-31) @dev
- Initial version with standards consolidation
- Moved all standards to tools/doc_standards.py
- Added validation rules

1.1.0 (2025-01-01) @dev
- Added documentation hierarchy of authority
- Aligned with existing documentation structure

## Context

Documentation standards and validation were split across multiple locations:

1. `shared_lib/doc_standards.py`: Constants and validation rules
2. `tools/doc_validator.py`: Pre-commit hook for validation
3. `tests/test_process_quality.py`: Duplicate standards and validation

This created several issues:
1. Documentation validation depended on shared_lib, pulling in unnecessary dependencies
2. Pre-commit hooks failed due to missing dependencies
3. Standards were duplicated between validation and testing code
4. No single source of truth for documentation requirements
5. Risk of standards diverging between tests and pre-commit hooks
6. Unclear hierarchy of authority between different types of documentation

## Decision

### 1. Documentation Hierarchy

We establish the following hierarchy of authority for documentation:

1. **Architecture Decision Records (ADRs)**
   - Highest authority for all architectural decisions
   - Must be followed by all other documentation
   - Changes require formal review process
   - Located in `/docs/adr/`
   - Examples:
     - System architecture
     - AI components
     - Database design
     - Schema management

2. **Standards & Guidelines**
   - Project-wide standards and guidelines
   - Must implement ADR decisions
   - Changes require team review
   - Key files:
     - `/docs/code-standards.md`
     - `/docs/doc-standards.md`
     - `/docs/ai-guidelines.md`

3. **Implementation Documentation**
   - How-to guides, setup instructions, and workflows
   - Must follow ADRs and standards
   - Regular updates allowed
   - Key files:
     - `/docs/guides/`
     - `/docs/setup.md`
     - `/docs/testing-guide.md`
     - `/docs/troubleshooting.md`

4. **Code Documentation**
   - Comments, docstrings, and inline docs
   - Must align with all above
   - Can be updated with code
   - Located with code

### 2. README Authority Model

READMEs have a parallel authority structure (see [ADR-0023](0023-readme-driven-documentation.md)):

1. **Authority Scope**
   - Each README has authority within its component/directory
   - Must defer to ADRs for architectural decisions
   - Must defer to Standards for coding practices
   - Authoritative for component usage and organization

2. **Cross-Cutting Nature**
   - READMEs exist at all documentation levels
   - Authority is limited to their scope
   - They serve as navigation aids
   - They reference authoritative documents

3. **README Types**
   - Root README: Project-wide navigation
   - Component READMEs: Interface documentation
   - Implementation READMEs: Technical details
   - Code READMEs: Module organization

### 2. Standards Consolidation

We will consolidate all documentation standards into tools/doc_standards.py:

```python
# Documentation hierarchy tracked in one place
DOC_HIERARCHY = {
    "adrs": {
        "path": "docs/adr",
        "authority_level": 1,
        "review_required": True,
        "reviewers": ["arch_team"]
    },
    "readmes": {
        "path": ["README.md", "docs/README.md"],
        "authority_level": 2,
        "review_required": False,
        "reviewers": ["dev_team"]
    },
    "standards": {
        "path": "docs/standards",
        "authority_level": 3,
        "review_required": True,
        "reviewers": ["tech_leads"]
    },
    "implementation": {
        "path": "docs/guides",
        "authority_level": 4,
        "review_required": False,
        "reviewers": ["dev_team"]
    },
    "code": {
        "path": "**/*.py",
        "authority_level": 5,
        "review_required": False,
        "reviewers": ["code_owners"]
    }
}

# Required files for each level
REQUIRED_DOCS = {
    "adrs": ["README.md", "template.md"],
    "readmes": ["README.md"],
    "standards": ["code-standards.md", "doc-standards.md", "ai-guidelines.md"],
    "implementation": ["setup.md", "testing-guide.md", "troubleshooting.md"],
    "code": ["README.md"]
}

# Required sections by doc type
REQUIRED_SECTIONS = {
    "adrs": ["status", "context", "decision", "consequences"],
    "readmes": ["overview", "getting-started", "usage"],
    "standards": ["overview", "rules", "examples", "validation"],
    "implementation": ["prerequisites", "steps", "examples", "troubleshooting"],
    "code": ["description", "usage", "examples"]
}

def validate_doc(path: Path, doc_type: str, max_lines: int) -> List[str]:
    """Validate a document against standards."""
    errors = []
    content = path.read_text().lower()
    
    # Check authority level
    doc_level = DOC_HIERARCHY[doc_type]["authority_level"]
    for ref in find_references(content):
        ref_level = get_doc_level(ref)
        if ref_level < doc_level:
            errors.append(f"[ERROR] Cannot override {ref} (level {ref_level})")
    
    # Check required sections
    for section in REQUIRED_SECTIONS[doc_type]:
        if section not in content:
            errors.append(f"[ERROR] Missing section: {section}")
    
    return errors
```

## Consequences

### Positive
1. Clear hierarchy matching our actual documentation structure
2. Single source of truth for all documentation standards
3. Automated validation of documentation relationships
4. Clear review requirements for each level
5. Easy to maintain and update standards
6. Better test coverage of validation code

### Negative
1. More complex validation logic
2. Need to update existing documentation
3. More formal review process required

### Mitigation
1. Automated tools to help with validation
2. Gradual migration of existing docs
3. Clear templates for each level

## Related ADRs
- [ADR-0000](0000-subsystem-architecture.md): Foundation for all documentation
- [ADR-0016](0016-minimalist-adr-template.md): ADR template standard
- [ADR-0023](0023-readme-driven-documentation.md): README-driven documentation

## References
- [Python Pre-commit Hooks](https://pre-commit.com/)
- [Python Documentation Standards](https://www.python.org/dev/peps/pep-0257/)
- [DRY (Don't Repeat Yourself)](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
- [Diátaxis Documentation Framework](https://diataxis.fr/)
