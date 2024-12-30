"""Email model constants."""

class EmailSchema:
    """Schema constants for the Email model."""
    # Column sizes
    LABEL_SIZE = 500
    SUBJECT_SIZE = 500
    SENDER_SIZE = 200
    THREAD_SIZE = 100
    TO_SIZE = 200
    ID_SIZE = 100

    # Default values
    DEFAULT_SUBJECT = ""
    DEFAULT_API_RESPONSE = "{}"
    DEFAULT_HAS_ATTACHMENTS = False

    # Validation
    MAX_BODY_LENGTH = 1000000  # 1MB
    REQUIRED_FIELDS = ['id', 'threadId']
