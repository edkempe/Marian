# 23. README-Driven Documentation

Date: 2025-01-01

## Status

Proposed

## Revision History
1.0.0 (2025-01-01) @dev
- Initial version
- Established README hierarchy
- Defined README requirements
- Added validation rules

1.1.0 (2025-01-01) @dev
- Clarified README authority model
- Aligned with documentation hierarchy
- Updated validation rules

## Context

README files serve multiple critical roles in our system:
1. Entry points for understanding components
2. Navigation aids for the codebase
3. Quick reference for developers
4. Documentation indices

However, we lack:
1. Clear standards for README content
2. Defined hierarchy between READMEs
3. Validation of README completeness
4. Integration with our documentation system

## Decision

We will implement a README-driven documentation approach that complements our documentation hierarchy ([ADR-0010](0010-documentation-standards-organization.md)):

### 1. README Authority Model

READMEs have a unique role in the documentation hierarchy:

1. **Parallel Authority Structure**
   - READMEs exist alongside the main documentation hierarchy
   - They serve as navigation and entry points
   - They reference authoritative documents
   - They have component-level authority

2. **Authority Scope**
   - Limited to their component/directory
   - Must defer to ADRs for architecture
   - Must defer to Standards for practices
   - Authoritative for component usage

3. **Cross-Cutting Concerns**
   - READMEs appear at all levels
   - Each README has clear scope
   - Authority limited to scope
   - References define authority

### 2. README Types and Authority

```
Documentation Hierarchy │ README Authority    │ Scope
─────────────────────────────────────────────────────
ADRs (Level 1)        │ Root README         │ Project-wide navigation
                      │                     │ Architecture overview
                      │                     │ Getting started
─────────────────────────────────────────────────────
Standards (Level 2)   │ Component READMEs   │ Component interfaces
                      │                     │ Usage patterns
                      │                     │ Local development
─────────────────────────────────────────────────────
Implementation (L3)   │ Implementation      │ Technical details
                      │ READMEs             │ Implementation notes
─────────────────────────────────────────────────────
Code (Level 4)        │ Code READMEs        │ Code organization
                      │                     │ Module usage
```

### 3. README Locations and Roles

```
/
├── README.md                 # Project overview & navigation
│   └── docs/                
│       ├── README.md        # Documentation guide
│       ├── adr/             
│       │   └── README.md    # ADR index & process
│       └── guides/          
│           └── README.md    # Guide index & usage
├── src/                     
│   └── README.md           # Code organization
└── tests/                   
    └── README.md           # Testing guide
```

### 4. Required Sections

```markdown
# Component Name

## Overview
- Purpose
- Key features
- Status

## Quick Start
- Prerequisites
- Installation
- Basic usage

## Architecture
- Key components
- Data flow
- Dependencies

## Documentation
- Setup guides
- API reference
- Examples

## Development
- Local setup
- Testing
- Contributing

## Related
- ADRs
- Design docs
- External docs
```

### 5. README Authority

1. **Project Root README**
   - Authoritative for:
     - Project overview
     - Architecture summary
     - Getting started
     - License and legal

2. **Component READMEs**
   - Authoritative for:
     - Component interfaces
     - Usage patterns
     - Configuration
     - Local development

3. **Specialized READMEs**
   - Authoritative for:
     - Implementation details
     - Technical specifications
     - Contribution workflows

### 6. Validation Rules

1. **Existence**
   - Required README locations
   - Minimum content length
   - Required sections

2. **Content**
   - Up-to-date examples
   - Valid links
   - Correct formatting

3. **Cross-References**
   - Links to ADRs
   - Component references
   - External documentation

## Consequences

### Positive
1. Clear entry points for all components
2. Consistent documentation structure
3. Easy to find information
4. Self-documenting codebase
5. Better onboarding experience

### Negative
1. More files to maintain
2. Need for regular updates
3. Potential for duplication
4. Validation overhead

### Mitigation
1. Automated README validation
2. Regular documentation audits
3. Clear update procedures
4. Template-driven creation

## Technical Details

### Validation Script
```python
def validate_readme(path: Path) -> List[Issue]:
    """Validate a README file against our standards."""
    issues = []
    
    # Check required sections
    required_sections = {
        "Overview", "Quick Start", "Architecture",
        "Documentation", "Development", "Related"
    }
    
    content = path.read_text()
    sections = extract_sections(content)
    
    # Validate sections
    missing = required_sections - sections.keys()
    if missing:
        issues.append(
            Issue(f"Missing sections: {missing}")
        )
    
    # Validate links
    broken_links = find_broken_links(content)
    if broken_links:
        issues.append(
            Issue(f"Broken links: {broken_links}")
        )
    
    return issues
```

### README Template
```markdown
# Component Name

## Overview
[Purpose and key features in 2-3 sentences]

## Quick Start
\`\`\`bash
# Installation
pip install component

# Basic usage
from component import Feature
\`\`\`

## Architecture
[Component diagram or key abstractions]

## Documentation
- [Setup Guide](docs/setup.md)
- [API Reference](docs/api.md)
- [Examples](docs/examples.md)

## Development
- [Contributing](CONTRIBUTING.md)
- [Testing Guide](TESTING.md)

## Related
- [ADR-XXXX](../adr/XXXX-title.md)
```

## Related Decisions
- [ADR-0010](0010-documentation-standards-organization.md): Documentation standards
- [ADR-0016](0016-minimalist-adr-template.md): Template standards
- [ADR-0000](0000-subsystem-architecture.md): System architecture

## Notes
- Regular audits of README completeness
- Automated validation in CI pipeline
- Template updates as needed

## References
- [ADR-0010](0010-documentation-standards-organization.md): Documentation Hierarchy
- [README Driven Development](https://tom.preston-werner.com/2010/08/23/readme-driven-development.html)
- [Standard Readme](https://github.com/RichardLitt/standard-readme)
- [Keep a Changelog](https://keepachangelog.com/)
