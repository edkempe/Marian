"""API request/response schemas."""

from .gmail import (
    Message,
    MessageBody,
    MessageHeader,
    MessagePart,
    MessagePayload
)
from .anthropic import (
    ActionItem,
    EmailAnalysis
)

__all__ = [
    # Gmail schemas
    "Message",
    "MessageBody",
    "MessageHeader",
    "MessagePart",
    "MessagePayload",
    
    # Anthropic schemas
    "ActionItem",
    "EmailAnalysis"
]
