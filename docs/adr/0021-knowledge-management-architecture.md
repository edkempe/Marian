# ADR 0021: Knowledge Management Architecture

## Status

Accepted

## Context

The Jexi system needs to manage various types of knowledge and information:
1. Email content and metadata
2. User preferences and settings
3. System configuration and rules
4. Learned patterns and behaviors

We need an architecture that can:
- Maintain clear ownership of information
- Track relationships between pieces of knowledge
- Support versioning and history
- Handle different types of storage
- Maintain consistency and accuracy

## Decision

We will implement a layered knowledge management architecture based on the library metaphor:

### 1. Knowledge Hierarchy

```
Catalog (Metadata Layer)
├── Sources
│   ├── Email
│   ├── Configuration
│   └── User Preferences
├── Relationships
│   ├── Dependencies
│   ├── References
│   └── Versions
└── Access Patterns
    ├── Frequently Used
    ├── Recently Added
    └── Priority Level
```

### 2. Component Responsibilities

#### Catalog System
- Maintains metadata about all information
- Tracks relationships and dependencies
- Manages access patterns and usage
- Does not store actual content

#### Storage System
- Handles physical storage of content
- Implements different storage strategies
- Manages backup and recovery
- Optimizes access patterns

#### Access Control
- Manages permissions and access
- Implements security policies
- Tracks usage and auditing
- Handles authentication

### 3. Information Flow

1. **Storage Flow**
   ```python
   class KnowledgeManager:
       def store_information(self, info: Information):
           # 1. Generate metadata
           metadata = self.create_metadata(info)
           
           # 2. Store in catalog
           ref = self.catalog.add_metadata(metadata)
           
           # 3. Store content
           self.storage.store(ref, info.content)
           
           # 4. Update relationships
           self.catalog.update_relationships(ref)
   ```

2. **Retrieval Flow**
   ```python
   class KnowledgeManager:
       def retrieve_information(self, query: Query):
           # 1. Search catalog
           refs = self.catalog.find_references(query)
           
           # 2. Check access
           allowed_refs = self.access.filter(refs)
           
           # 3. Retrieve content
           return self.storage.retrieve_many(allowed_refs)
   ```

## Consequences

### Positive
1. **Clear Structure**: Well-defined layers and responsibilities
2. **Flexibility**: Can change storage without affecting catalog
3. **Security**: Centralized access control
4. **Scalability**: Independent scaling of components
5. **Maintainability**: Clear boundaries and interfaces

### Negative
1. **Complexity**: Multiple layers to manage
2. **Performance**: Multiple steps for access
3. **Consistency**: Need to maintain across layers

### Mitigation
1. Caching frequently accessed data
2. Batch operations for efficiency
3. Regular consistency checks

## Technical Details

### Metadata Structure
```python
@dataclass
class Metadata:
    id: str
    type: ContentType
    created: datetime
    modified: datetime
    source: Source
    access_level: AccessLevel
    relationships: List[Relationship]
    storage_info: StorageInfo
```

### Storage Strategy
```python
class StorageStrategy(Protocol):
    def store(self, ref: Reference, content: Content) -> None: ...
    def retrieve(self, ref: Reference) -> Content: ...
    def delete(self, ref: Reference) -> None: ...
    def exists(self, ref: Reference) -> bool: ...
```

## Related Decisions
- [ADR-0020](0020-ai-system-architecture.md): Overall AI architecture
- [ADR-0019](0019-api-first-schema-design.md): Database schema design

## Notes
- Regular audits of metadata consistency
- Monitor storage usage patterns
- Review access patterns periodically

## References
- [Knowledge Management Systems](https://en.wikipedia.org/wiki/Knowledge_management)
- [Information Architecture](https://en.wikipedia.org/wiki/Information_architecture)
- [Content Management Patterns](https://en.wikipedia.org/wiki/Content_management)
