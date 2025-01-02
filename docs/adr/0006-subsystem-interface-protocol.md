# ADR 0006: Subsystem Interface Protocol

## Status
Proposed

## Context
Following ADR-0000's hub-and-spoke architecture, we need a standardized way for:
1. Subsystems to communicate with Jexi and each other
2. Users to interact with subsystems directly or through Jexi
3. Subsystems to register their capabilities and maintain state
4. Context to be preserved across subsystem interactions

## Decision

We will implement a protocol with these key components:

### 1. Subsystem Registration

Each subsystem must implement a standard registration interface:

```python
class SubsystemRegistration:
    name: str                # Unique identifier (e.g., "marian")
    display_name: str        # User-friendly name (e.g., "Marian the Librarian")
    capabilities: List[str]  # What the subsystem can do
    direct_access: bool      # Can users access directly?
    state_management: bool   # Does it maintain state?
```

### 2. Communication Protocol

Messages between components will use a standardized format:

```python
class Message:
    id: str                 # Unique message ID
    timestamp: datetime     # When the message was created
    source: str            # Who sent the message
    target: str            # Who should receive it
    type: MessageType      # Type of message
    content: dict          # The actual message content
    context: Context       # Conversation context
    metadata: dict         # Additional information
```

### 3. Context Management

Context objects track state across interactions:

```python
class Context:
    session_id: str        # Unique session identifier
    user_id: str          # Who is making the request
    conversation_id: str   # Current conversation thread
    state: dict           # Current state information
    history: List[str]    # Previous message IDs
    preferences: dict     # User preferences
```

### 4. Access Patterns

#### Direct Access
```
User -> Subsystem
1. User requests subsystem directly
2. Subsystem checks authorization
3. Subsystem handles request
4. Subsystem notifies Jexi (async)
```

#### Coordinated Access
```
User -> Jexi -> Subsystem
1. User requests through Jexi
2. Jexi identifies target subsystem
3. Jexi forwards request with context
4. Subsystem processes request
5. Jexi manages response
```

#### Multi-System Coordination
```
User -> Jexi -> [Subsystem A <-> Subsystem B]
1. Jexi identifies needed subsystems
2. Jexi creates coordination context
3. Subsystems collaborate through context
4. Jexi aggregates responses
```

### 5. State Management

Each subsystem can choose its state management approach:

1. **Stateless**
   - No state between requests
   - All context in messages
   - Simpler but less efficient

2. **Stateful**
   - Maintains session state
   - Caches common data
   - More efficient but complex

3. **Hybrid**
   - Core state in messages
   - Caches performance data
   - Balance of approaches

### 6. Authentication & Authorization

1. **Authentication**
   - Single sign-on across system
   - JWT-based tokens
   - Subsystem-specific credentials

2. **Authorization**
   - Role-based access control
   - Capability-based security
   - Fine-grained permissions

## Implementation

### 1. Base Classes

```python
class BaseSubsystem(ABC):
    @abstractmethod
    def register(self) -> SubsystemRegistration:
        """Register subsystem capabilities"""
        pass

    @abstractmethod
    async def handle_message(self, msg: Message) -> Message:
        """Process incoming message"""
        pass

    @abstractmethod
    async def get_status(self) -> SubsystemStatus:
        """Report current status"""
        pass
```

### 2. Message Bus

```python
class MessageBus:
    async def route_message(self, msg: Message):
        """Route message to target"""
        pass

    async def broadcast(self, msg: Message):
        """Send to all subsystems"""
        pass

    async def coordinate(self, msgs: List[Message]):
        """Coordinate multiple messages"""
        pass
```

## Consequences

### Positive
1. Standardized communication
2. Clear interfaces
3. Flexible state management
4. Scalable architecture
5. Easy to add new subsystems

### Negative
1. Additional complexity
2. Message overhead
3. Need to manage state
4. Protocol maintenance

### Neutral
1. Need to version protocol
2. Must document standards
3. Training requirements

## Implementation Guidelines

1. **Message Format**
   - Use Protocol Buffers or similar
   - Version all messages
   - Include validation

2. **State Management**
   - Clear state ownership
   - State synchronization
   - Conflict resolution

3. **Error Handling**
   - Graceful degradation
   - Clear error messages
   - Recovery procedures

4. **Performance**
   - Message batching
   - Connection pooling
   - Caching strategy

## References
- ADR-0000: Hub-and-Spoke Architecture
- [Protocol Buffers](https://developers.google.com/protocol-buffers)
- [gRPC](https://grpc.io/)
