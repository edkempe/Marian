"""Sentiment type constants."""

from enum import Enum

class SentimentTypes(str, Enum):
    """Enumeration of valid sentiment types.
    
    This enum defines the valid sentiment types that can be used for email analysis.
    Each sentiment type is a string value that represents a particular emotional tone.
    """
    
    POSITIVE = "positive"  # Indicates a positive sentiment
    NEGATIVE = "negative"  # Indicates a negative sentiment
    NEUTRAL = "neutral"    # Indicates a neutral sentiment
    MIXED = "mixed"        # Indicates a mixed or ambiguous sentiment
