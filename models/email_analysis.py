"""Email analysis model definitions."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import re

from sqlalchemy import Column, DateTime, Integer, String, JSON, ForeignKey, Float, ARRAY
from sqlalchemy.orm import relationship, validates

from models.base import Base
from models.validators.api_schema import api_validator
from shared_lib.schema_constants import COLUMN_SIZES, PATTERNS, VALUE_RANGES, ENUMS, AnalysisDefaults


class EmailAnalysis(Base):
    """Email analysis model.
    
    Based on Anthropic API Analysis resource.
    Note: We use analysis_metadata instead of metadata as the latter is reserved in SQLAlchemy.
    """
    
    __tablename__ = "email_analyses"
    
    # Core fields (exact field names from API, except metadata)
    id = Column(
        String(COLUMN_SIZES["ANALYSIS_ID"]),
        primary_key=True,
        comment="Anthropic API analysis ID"
    )
    email_id = Column(
        String(COLUMN_SIZES["MESSAGE_ID"]),
        ForeignKey("email_messages.id"),
        nullable=False,
        comment="Reference to analyzed email"
    )
    summary = Column(
        String(COLUMN_SIZES["SUMMARY"]),
        nullable=False,
        comment="Brief summary of email content"
    )
    sentiment = Column(
        String(20),  # Using enum values
        nullable=True,
        comment="Detected sentiment"
    )
    categories = Column(
        ARRAY(String(COLUMN_SIZES["CATEGORY"])),
        nullable=True,
        comment="Detected categories"
    )
    key_points = Column(
        ARRAY(String(COLUMN_SIZES["KEY_POINT"])),
        nullable=True,
        comment="Main points extracted"
    )
    action_items = Column(
        JSON,
        nullable=True,
        comment="Action items identified"
    )
    priority_score = Column(
        Integer,
        nullable=True,
        comment="Computed priority score (1-5)"
    )
    confidence_score = Column(
        Float,
        nullable=True,
        comment="Confidence in analysis (0.0-1.0)"
    )
    analysis_metadata = Column(  # Using analysis_metadata to avoid SQLAlchemy reserved word
        JSON,
        nullable=True,
        comment="Additional analysis metadata"
    )
    model_version = Column(
        String(COLUMN_SIZES["MODEL_VERSION"]),
        nullable=True,
        comment="Version of Claude used"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Analysis creation time"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Last update time"
    )
    
    # Relationships
    email = relationship("EmailMessage", back_populates="analysis")
    
    @validates("id")
    def validate_analysis_id(self, key: str, value: str) -> str:
        """Validate analysis ID format."""
        if not re.match(PATTERNS["ANALYSIS_ID"], value):
            raise ValueError(
                f"Invalid analysis ID format. Must match pattern: {PATTERNS['ANALYSIS_ID']}"
            )
        return value
    
    @validates("priority_score")
    def validate_priority_score(self, key: str, value: Optional[int]) -> Optional[int]:
        """Validate priority score range."""
        if value is not None:
            if not (VALUE_RANGES["PRIORITY_SCORE"]["min"] <= value <= VALUE_RANGES["PRIORITY_SCORE"]["max"]):
                raise ValueError(
                    f"Priority score must be between {VALUE_RANGES['PRIORITY_SCORE']['min']} "
                    f"and {VALUE_RANGES['PRIORITY_SCORE']['max']}"
                )
        return value
    
    @validates("confidence_score")
    def validate_confidence_score(self, key: str, value: Optional[float]) -> Optional[float]:
        """Validate confidence score range."""
        if value is not None:
            if not (VALUE_RANGES["CONFIDENCE_SCORE"]["min"] <= value <= VALUE_RANGES["CONFIDENCE_SCORE"]["max"]):
                raise ValueError(
                    f"Confidence score must be between {VALUE_RANGES['CONFIDENCE_SCORE']['min']} "
                    f"and {VALUE_RANGES['CONFIDENCE_SCORE']['max']}"
                )
        return value
    
    @validates("sentiment")
    def validate_sentiment(self, key: str, value: Optional[str]) -> Optional[str]:
        """Validate sentiment value."""
        if value is not None and value not in ENUMS["SENTIMENT"]:
            raise ValueError(f"Invalid sentiment value. Must be one of: {ENUMS['SENTIMENT']}")
        return value
    
    @validates("email_id")
    def validate_email_id(self, key: str, value: str) -> str:
        """Validate email ID format."""
        if not re.match(PATTERNS["MESSAGE_ID"], value):
            raise ValueError(
                f"Invalid email ID format. Must match pattern: {PATTERNS['MESSAGE_ID']}"
            )
        return value
    
    @validates("summary")
    def validate_summary(self, key: str, value: str) -> str:
        """Validate summary length."""
        if len(value) > COLUMN_SIZES["SUMMARY"]:
            raise ValueError(
                f"Summary is too long. Must be less than or equal to {COLUMN_SIZES['SUMMARY']} characters."
            )
        return value
    
    @validates("categories")
    def validate_categories(self, key: str, value: Optional[List[str]]) -> Optional[List[str]]:
        """Validate categories length."""
        if value is not None and len(value) > COLUMN_SIZES["CATEGORY"]:
            raise ValueError(
                f"Categories is too long. Must be less than or equal to {COLUMN_SIZES['CATEGORY']} items."
            )
        return value
    
    @validates("key_points")
    def validate_key_points(self, key: str, value: Optional[List[str]]) -> Optional[List[str]]:
        """Validate key points length."""
        if value is not None and len(value) > COLUMN_SIZES["KEY_POINT"]:
            raise ValueError(
                f"Key points is too long. Must be less than or equal to {COLUMN_SIZES['KEY_POINT']} items."
            )
        return value
    
    @validates("action_items")
    def validate_action_items(self, key: str, value: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
        """Validate action items length."""
        if value is not None and len(value) > COLUMN_SIZES["ACTION_ITEM"]:
            raise ValueError(
                f"Action items is too long. Must be less than or equal to {COLUMN_SIZES['ACTION_ITEM']} items."
            )
        return value
    
    @validates("model_version")
    def validate_model_version(self, key: str, value: Optional[str]) -> Optional[str]:
        """Validate model version length."""
        if value is not None and len(value) > COLUMN_SIZES["MODEL_VERSION"]:
            raise ValueError(
                f"Model version is too long. Must be less than or equal to {COLUMN_SIZES['MODEL_VERSION']} characters."
            )
        return value
    
    @validates("analysis_metadata")
    def validate_analysis_metadata(self, key: str, value: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate analysis metadata length."""
        if value is not None and len(value) > COLUMN_SIZES["METADATA"]:
            raise ValueError(
                f"Analysis metadata is too long. Must be less than or equal to {COLUMN_SIZES['METADATA']} items."
            )
        return value
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "EmailAnalysis":
        """Create model instance from Anthropic API response."""
        return cls(
            id=response["id"],
            email_id=response["email_id"],
            summary=response["summary"],
            sentiment=response.get("sentiment"),
            categories=response.get("categories", []),
            key_points=response.get("key_points", []),
            action_items=response.get("action_items", []),
            priority_score=response.get("priority_score"),
            confidence_score=response.get("confidence_score"),
            analysis_metadata=response.get("metadata", {}),  # Map metadata to analysis_metadata
            model_version=response.get("model_version")
        )
    
    def to_api_response(self) -> Dict[str, Any]:
        """Convert model instance to Anthropic API response format."""
        return {
            "id": self.id,
            "email_id": self.email_id,
            "summary": self.summary,
            "sentiment": self.sentiment,
            "categories": self.categories or [],
            "key_points": self.key_points or [],
            "action_items": self.action_items or [],
            "priority_score": self.priority_score,
            "confidence_score": self.confidence_score,
            "metadata": self.analysis_metadata or {},  # Map analysis_metadata back to metadata
            "model_version": self.model_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __init__(self, **kwargs):
        """Initialize with defaults from AnalysisDefaults."""
        defaults = AnalysisDefaults()
        for key, value in defaults.__dict__.items():
            if key == "metadata":  # Map metadata to analysis_metadata
                kwargs.setdefault("analysis_metadata", value)
            else:
                kwargs.setdefault(key, value)
        super().__init__(**kwargs)


@dataclass
class EmailAnalysisResponse:
    """Response model for email analysis API."""
    
    analysis_id: str
    email_id: str
    summary: str
    sentiment: Optional[str]
    categories: Optional[List[str]]
    key_points: Optional[List[str]]
    action_items: Optional[List[Dict[str, Any]]]
    priority_score: Optional[int]
    confidence_score: Optional[float]
    model_version: Optional[str]
    analysis_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, model: EmailAnalysis) -> "EmailAnalysisResponse":
        """Create response from model instance."""
        return cls(
            analysis_id=model.id,
            email_id=model.email_id,
            summary=model.summary,
            sentiment=model.sentiment,
            categories=model.categories,
            key_points=model.key_points,
            action_items=model.action_items,
            priority_score=model.priority_score,
            confidence_score=model.confidence_score,
            model_version=model.model_version,
            analysis_metadata=model.analysis_metadata,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
