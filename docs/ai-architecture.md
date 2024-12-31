# Jexi AI Architecture

This document explains the AI systems in the Jexi project and establishes the documentation hierarchy for AI-related content.

## Overview

The system uses multiple AI components working together in a library-based architecture:

1. **Runtime AI**
   - **Jexi**: The primary assistant that interacts with users
     - Processes and analyzes emails
     - Can request and "check out" information through Marian
     - Uses the catalog but doesn't manage it
     
   - **Marian**: The librarian who manages the Catalog
     - Maintains metadata about all information sources
     - Knows where everything is located and how it relates
     - Maintains the source of truth hierarchy
     - Doesn't store content, only references to it
     
   - **Catalog**: The knowledge management system
     - Like a library's card catalog
     - Stores metadata, locations, and relationships
     - Contains references/pointers to actual content
     - Maps the knowledge landscape
     - Tracks hierarchies and dependencies

2. **Development AI**
   - **Cascade**: The development assistant
     - Helps implement new features
     - Reviews and refactors code
     - Manages testing and documentation

## Component Details

### Runtime AI

#### Jexi (The Primary Assistant)
> Jexi is the main AI assistant that interacts with users and processes their information.

Responsibilities:
- Email processing and analysis
- User interaction and task management
- Can request information through Marian
- "Checks out" content when needed
- Uses the catalog but doesn't manage it

Access Patterns:
- Requests information through Marian
- Gets guided to authoritative sources
- Maintains active "checkouts"
- Reports usage patterns back to Catalog

#### Marian (The Librarian)
> Marian is the librarian who manages the Catalog system, like a skilled research librarian who knows where everything is and how it's organized.

Responsibilities:
- Maintains the Catalog (metadata and relationships)
- Guides users to authoritative sources
- Manages the source of truth hierarchy
- Tracks resource locations and access methods
- Suggests related resources
- Monitors collection health

Features:
1. **Reference Desk**
   - Helps construct complex queries
   - Suggests related resources
   - Guides to authoritative sources

2. **Collection Management**
   - Tracks resource usage
   - Identifies gaps in the catalog
   - Suggests new categorizations

3. **Library Card System**
   - Tracks what's currently "checked out"
   - Manages access permissions
   - Logs usage patterns

4. **Inter-Library Loan**
   - Handles external resource references
   - Manages temporary access
   - Tracks external dependencies

#### The Catalog
> The Catalog is like a library's card catalog system - it doesn't contain the books, it tells you where to find them.

Components:
1. **Metadata Store**
   - Resource locations and access methods
   - Tags and categories
   - Last updated timestamps
   - Access permissions

2. **Relationship Mapper**
   - Dependencies between resources
   - Related content links
   - Version relationships
   - Authority hierarchies

3. **Access Tracker**
   - Current "checkouts"
   - Usage history
   - Access patterns
   - Permission logs

4. **Health Monitor**
   - Resource availability
   - Link validity
   - Usage statistics
   - Gap analysis

### Development AI

#### Cascade
> Cascade is the development assistant that helps build and maintain the system.

Responsibilities:
- Code implementation
- Testing and validation
- Documentation management
- Code review and refactoring

## Documentation Hierarchy

### Core Documentation
1. `ai-architecture.md`: This file - system architecture
2. `librarian.md`: Marian's behavior and operations
3. `catalog-spec.md`: Catalog system specification

### Implementation Guides
1. `catalog-schema.md`: Metadata schema specification
2. `access-patterns.md`: How to request and use resources
3. `truth-hierarchy.md`: Source of truth management

### Best Practices
1. `metadata-guide.md`: How to structure metadata
2. `relationship-guide.md`: How to define relationships
3. `access-guide.md`: Resource access patterns

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
