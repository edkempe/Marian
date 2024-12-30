"""Email analysis model constants."""

class AnalysisSchema:
    """Schema constants for the EmailAnalysis model."""
    # Column sizes
    SENTIMENT_SIZE = 50
    CATEGORY_SIZE = 100
    SUMMARY_SIZE = 1000

    # Default values
    DEFAULT_SENTIMENT = "neutral"
    DEFAULT_CATEGORY = "uncategorized"

    # Validation
    VALID_SENTIMENTS = {"positive", "negative", "neutral", "mixed"}
    VALID_PRIORITIES = {"high", "medium", "low"}
    MAX_SUMMARY_LENGTH = 1000
