# Marian AI Architecture

This document explains the two distinct AI systems in the Marian project and establishes the documentation hierarchy for AI-related content.

## Documentation Hierarchy

### Core Source of Truth
1. **Code Implementation**
   - `models/catalog.py`: Definitive data model
   - `tests/`: Behavior specifications
2. **Documentation**
   - `README.md`: Project overview
   - `ai-architecture.md`: AI system boundaries

### Development AI (Windsurf.ai)
1. **Primary Documentation**
   - `dev-ai-workflow.md`: Development process and standards
2. **Supporting Documentation**
   - `code-standards.md`: Implementation guidelines
   - `testing-guide.md`: Test development practices
   - Session logs: Historical record

### Runtime AI (Anthropic)
1. **Primary Documentation**
   - `librarian.md`: Catalog operations and behavior
2. **Supporting Documentation**
   - `testing-guide.md`: Runtime AI testing
   - `design-decisions.md`: Architecture decisions

## 1. Development AI (Windsurf.ai)

The development environment uses Windsurf.ai as an AI copilot for code development and documentation.

### Primary Documentation
- `ai-guidelines.md`: Core development practices with AI
- `session-workflow.md`: Development session management

### Related Documentation
- `code-standards.md`: Code review practices (see "AI Review Guidelines" section)
- `testing-guide.md`: Test development approach (see "Test Generation" section)
- `backlog.md`: Development task planning (see "AI Assistance" section)

## 2. Runtime AI (Anthropic)

The Marian system uses Anthropic's AI for catalog operations and content analysis.

### Primary Documentation
- `librarian.md`: Core catalog AI behaviors
- `testing-guide.md`: Claude API testing approach

### Related Documentation
- `design-decisions.md`: AI architecture decisions (see "AI Integration" section)
- `backlog.md`: AI feature planning (see "Catalog Intelligence" section)

## Interaction Between Systems

While these are separate systems, they work together in several ways:

1. **Development Support**
   - Windsurf.ai helps develop and test Anthropic integrations
   - Development AI assists in prompt engineering for runtime AI
   - Test cases are developed with AI assistance

2. **Documentation Maintenance**
   - Development AI helps maintain runtime AI documentation
   - Changes to AI behavior are documented in both contexts
   - Version control tracks both development and runtime changes

3. **Quality Assurance**
   - Development AI reviews runtime AI implementations
   - Test coverage ensures reliable AI behavior
   - Documentation stays synchronized across both systems

## Best Practices

1. **Clear Separation**
   - Always specify which AI system you're referring to
   - Keep development and runtime concerns separate
   - Document overlaps explicitly

2. **Version Control**
   - Track changes to both AI systems
   - Document AI-related decisions in session logs
   - Maintain AI configuration history

3. **Testing Strategy**
   - Test runtime AI behavior systematically
   - Document test cases for AI interactions
   - Maintain test data for both systems

## References

This document serves as an index for AI-related content across the codebase. When updating any of the referenced documents, please maintain these cross-references for clarity.
