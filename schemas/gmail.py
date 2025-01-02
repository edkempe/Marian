"""Gmail API request/response schemas."""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, constr, conint, confloat


class MessageHeader(BaseModel):
    """Gmail message header."""
    
    name: str = Field(..., description="Header name")
    value: str = Field(..., description="Header value")


class MessageBody(BaseModel):
    """Gmail message body."""
    
    attachment_id: Optional[str] = Field(None, description="ID of attachment if body is an attachment")
    size: int = Field(..., description="Size in bytes")
    data: Optional[str] = Field(None, description="Base64 encoded content")


class MessagePart(BaseModel):
    """Gmail message part."""
    
    part_id: Optional[str] = Field(None, description="Part identifier")
    mime_type: str = Field(..., description="MIME type")
    filename: Optional[str] = Field(None, description="Filename if attachment")
    headers: List[MessageHeader] = Field(default_factory=list, description="Headers")
    body: MessageBody = Field(..., description="Body content")
    parts: Optional[List["MessagePart"]] = Field(None, description="Child parts")


class MessagePayload(BaseModel):
    """Gmail message payload."""
    
    part_id: Optional[str] = Field(None, description="Part identifier")
    mime_type: str = Field(..., description="MIME type")
    filename: Optional[str] = Field(None, description="Filename if attachment")
    headers: List[MessageHeader] = Field(default_factory=list, description="Headers")
    body: MessageBody = Field(..., description="Body content")
    parts: Optional[List[MessagePart]] = Field(None, description="Message parts")


class Message(BaseModel):
    """Gmail message resource."""
    
    id: str = Field(..., description="The immutable ID of the message", max_length=100)
    thread_id: str = Field(..., description="The ID of the thread the message belongs to", max_length=100)
    label_ids: Optional[List[str]] = Field(None, description="List of IDs of labels applied to this message")
    snippet: Optional[str] = Field(None, description="A short part of the message text", max_length=1000)
    history_id: Optional[str] = Field(None, description="The ID of the last history record that modified this message", max_length=20)
    internal_date: Optional[datetime] = Field(None, description="The internal message creation timestamp")
    size_estimate: Optional[int] = Field(None, description="Estimated size in bytes")
    raw: Optional[str] = Field(None, description="MIME message content if requested")
    payload: Optional[MessagePayload] = Field(None, description="The parsed email structure")
    
    class Config:
        """Pydantic model configuration."""
        
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
