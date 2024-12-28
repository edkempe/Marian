# Jexi AI Architecture

This document explains the AI systems in the Jexi project and establishes the documentation hierarchy for AI-related content.

## Project Structure
- **Jexi**: The core AI assistant, powered by Anthropic
  - **Marian**: Jexi's librarian, who maintains the Catalog
    - **Catalog**: The knowledge database that Marian manages for Jexi

## AI Systems

### 1. Development AI (Cascade, "Cassy")
> Cascade (affectionately known as Cassy) is the Windsurf.ai copilot that assists with development. Think of Cassy as a skilled pair programmer who understands both code and documentation.

#### Primary Responsibilities
- Code development and review
- Documentation maintenance
- Test generation and validation
- Architecture decisions

#### Limitations
- Cannot access gitignored directories
- Cannot run unsafe commands automatically
- Must validate all generated code

### 2. Runtime AIs

#### Jexi (Core Assistant)
> Jexi is the core AI assistant, powered by Anthropic, that interacts with users and manages their digital life.

##### Primary Responsibilities
- User interaction
- Task management
- Information processing
- Decision support

#### Marian (The Librarian)
> Marian is Jexi's librarian, also powered by Anthropic, who specializes in maintaining and organizing the Catalog.

##### Primary Responsibilities
- Catalog entry management
- Content classification
- Relationship inference
- Query processing
- Source of truth management

##### Integration Points
- Maintains the Catalog for Jexi
- Answers Jexi's questions about information hierarchy
- Ensures data consistency and accuracy
- Manages sources of truth

## Documentation Hierarchy

### Core Source of Truth
1. **Code Implementation**
   - `models/catalog.py`: Definitive data model
   - `tests/`: Behavior specifications
2. **Documentation**
   - `README.md`: Project overview
   - `ai-architecture.md`: AI system boundaries

### Development AI (Cascade)
1. **Primary Documentation**
   - `README.md`: Project overview
   - `session-workflow.md`: Development workflow
2. **Supporting Documentation**
   - `contributing.md`: Development guidelines and standards
   - `code-standards.md`: Implementation guidelines
   - `testing-guide.md`: Test development practices
   - `troubleshooting.md`: Common issues
   - Session logs: Historical record

### Runtime AI (Jexi and Marian)
1. **Primary Documentation**
   - `core-assistant.md`: Jexi's behavior and operations
   - `librarian.md`: Marian's behavior and operations
2. **Supporting Documentation**
   - `ai-guidelines.md`: AI interaction guidelines
   - `design-decisions.md`: Architecture decisions
   - `backlog.md`: Project tasks and priorities

## Interaction Between Systems

While these are separate systems, they work together in several ways:

1. **Development Support**
   - Cascade helps develop and test Jexi and Marian integrations
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
