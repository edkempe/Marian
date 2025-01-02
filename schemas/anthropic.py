"""Anthropic API request/response schemas."""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, constr, conint, confloat


class ActionItem(BaseModel):
    """Action item identified in an email."""
    
    description: str = Field(..., description="Description of the action item", max_length=500)
    due_date: Optional[datetime] = Field(None, description="When the action should be completed")
    priority: Optional[str] = Field(None, description="Priority level", pattern="^(high|medium|low)$")
    assignee: Optional[str] = Field(None, description="Email of person assigned to the action")
    status: Optional[str] = Field(None, description="Current status", pattern="^(pending|in_progress|completed)$")
    
    class Config:
        """Pydantic model configuration."""
        
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmailAnalysis(BaseModel):
    """Email analysis result."""
    
    id: str = Field(
        ...,
        description="The identifier of the analysis",
        pattern="^analysis_[A-Za-z0-9]+$",
        max_length=100
    )
    email_id: str = Field(..., description="Reference to the analyzed email", max_length=100)
    summary: str = Field(..., description="Brief summary of the email content", max_length=1000)
    sentiment: Optional[str] = Field(
        None,
        description="Detected sentiment of the email",
        pattern="^(positive|negative|neutral|mixed)$"
    )
    categories: Optional[List[str]] = Field(
        None,
        description="Detected categories for the email"
    )
    key_points: Optional[List[str]] = Field(
        None,
        description="Main points extracted from the email"
    )
    action_items: Optional[List[ActionItem]] = Field(
        None,
        description="Action items identified in the email"
    )
    priority_score: Optional[conint(ge=1, le=5)] = Field(
        None,
        description="Computed priority score (1-5)"
    )
    confidence_score: Optional[confloat(ge=0.0, le=1.0)] = Field(
        None,
        description="Confidence in the analysis (0.0-1.0)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional analysis metadata"
    )
    model_version: Optional[str] = Field(
        None,
        description="Version of Claude used for analysis",
        pattern="^claude-3-opus-[0-9]{8}$"
    )
    created_at: datetime = Field(..., description="When the analysis was created")
    updated_at: datetime = Field(..., description="When the analysis was last updated")
    
    class Config:
        """Pydantic model configuration."""
        
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
