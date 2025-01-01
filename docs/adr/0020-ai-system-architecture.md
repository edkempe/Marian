# 20. AI System Architecture

Date: 2025-01-01

## Status

Accepted

## Revision History
1.0.0 (2025-01-01) @dev
- Initial version
- Migrated from ai-architecture.md
- Added explicit component boundaries
- Established clear hierarchy

## Context

The Jexi project uses multiple AI components that need to work together effectively while maintaining clear boundaries and responsibilities. Following [ADR-0000](0000-subsystem-architecture.md)'s hub-and-spoke design, we need to establish:

1. Clear roles and responsibilities for each AI component
2. How components communicate and share information
3. Separation between runtime and development AI systems
4. Knowledge management and information flow

## Decision

We will implement a library-based AI architecture that extends our core architecture ([ADR-0000](0000-subsystem-architecture.md)) with the following components:

### 1. Runtime AI Components

#### Jexi (Primary Assistant)
- Primary user interaction point
- Email processing and analysis
- Information retrieval through Marian
- Task management and coordination
- Does not directly manage knowledge catalog

#### Marian (The Librarian)
- Knowledge catalog management
- Metadata maintenance
- Information relationship tracking
- Source of truth hierarchy
- Reference management (not content storage)

#### Catalog (Knowledge Store)
- Metadata and relationship storage
- Location references and pointers
- Knowledge hierarchy tracking
- No direct content storage
- Like a library's card catalog system

### 2. Development AI Component

#### Cascade (Development Assistant)
- Code implementation support
- Code review and refactoring
- Development workflow assistance
- Separate from runtime systems

### 3. Component Interaction Rules

1. **Information Flow**
   - Jexi → Marian: Information requests
   - Marian → Catalog: Metadata operations
   - Catalog → Storage: Content references

2. **Responsibility Boundaries**
   - Each component has a single primary responsibility
   - No direct catalog access from Jexi
   - No content storage in Catalog
   - Development AI separate from runtime

3. **State Management**
   - Each component manages its own state
   - Shared state through defined interfaces
   - Clear ownership of data

## Consequences

### Positive
1. **Clear Boundaries**: Each component has defined responsibilities
2. **Scalability**: Components can be scaled independently
3. **Maintainability**: Easy to update individual components
4. **Flexibility**: Can replace components if needed
5. **Security**: Clear data access patterns

### Negative
1. **Complexity**: Multiple components to manage
2. **Overhead**: Communication between components
3. **State Management**: Need to handle distributed state

### Mitigation
1. Clear interface definitions
2. Comprehensive monitoring
3. Regular boundary reviews

## Technical Details

### Component Communication

```python
class JexiAssistant:
    def request_information(self, query: str) -> Information:
        # Always go through Marian
        return marian.find_information(query)

class MarianLibrarian:
    def find_information(self, query: str) -> Information:
        # Use catalog to locate information
        reference = catalog.find_reference(query)
        return storage.retrieve(reference)

class KnowledgeCatalog:
    def find_reference(self, query: str) -> Reference:
        # Only return references, never content
        return self.metadata_store.query(query)
```

### State Management Example

```python
class ComponentState:
    def __init__(self):
        self._state = {}
        self._locks = {}

    def update(self, key: str, value: Any):
        with self._locks.get(key, nullcontext()):
            self._state[key] = value
            self.notify_observers(key)
```

## Related Decisions
- [ADR-0000](0000-subsystem-architecture.md): Core system architecture that this extends
- [ADR-0021](0021-knowledge-management-architecture.md): Implements knowledge management
- [ADR-0022](0022-development-runtime-separation.md): Implements system separation
- [ADR-0002](0002-minimal-security-testing.md): Security requirements that influence separation
- [ADR-0010](0010-documentation-standards-organization.md): Documentation hierarchy this follows

## Notes
- This ADR serves as the foundation for AI-specific architectural decisions
- All AI-related changes must align with this architecture
- Regular audits needed to ensure compliance

## References
- [Library-based Architecture Pattern](https://en.wikipedia.org/wiki/Library_pattern)
- [Component-based Software Engineering](https://en.wikipedia.org/wiki/Component-based_software_engineering)
- [State Management Patterns](https://en.wikipedia.org/wiki/State_management)
