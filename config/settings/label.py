"""Label settings configuration."""

from enum import Enum
from typing import Optional

from pydantic import Field

from config.settings.base import Settings


class LabelType(str, Enum):
    """Gmail label type enumeration."""
    SYSTEM = "system"
    USER = "user"


class MessageListVisibility(str, Enum):
    """Gmail message list visibility enumeration."""
    SHOW = "show"
    HIDE = "hide"


class LabelListVisibility(str, Enum):
    """Gmail label list visibility enumeration."""
    SHOW = "labelShow"
    SHOW_IF_UNREAD = "labelShowIfUnread"
    HIDE = "labelHide"


class LabelSettings(Settings):
    """Label configuration with validation.
    
    Based on Gmail API Label resource:
    https://developers.google.com/gmail/api/reference/rest/v1/users.labels#Label
    """
    
    # Label properties
    NAME_MAX_LENGTH: int = Field(
        default=255,
        description="Maximum length for label names"
    )
    TYPE: LabelType = Field(
        default=LabelType.USER,
        description="Default label type"
    )
    MESSAGE_LIST_VISIBILITY: MessageListVisibility = Field(
        default=MessageListVisibility.SHOW,
        description="Default message list visibility"
    )
    LABEL_LIST_VISIBILITY: LabelListVisibility = Field(
        default=LabelListVisibility.SHOW,
        description="Default label list visibility"
    )
    
    # Color settings
    COLOR_MAX_LENGTH: int = Field(
        default=20,
        description="Maximum length for color hex codes"
    )
    DEFAULT_BACKGROUND_COLOR: Optional[str] = Field(
        default=None,
        description="Default background color (hex)"
    )
    DEFAULT_TEXT_COLOR: Optional[str] = Field(
        default=None,
        description="Default text color (hex)"
    )
    
    # Counter defaults
    DEFAULT_MESSAGES_TOTAL: int = Field(
        default=0,
        description="Default total messages count"
    )
    DEFAULT_MESSAGES_UNREAD: int = Field(
        default=0,
        description="Default unread messages count"
    )
    DEFAULT_THREADS_TOTAL: int = Field(
        default=0,
        description="Default total threads count"
    )
    DEFAULT_THREADS_UNREAD: int = Field(
        default=0,
        description="Default unread threads count"
    )


# Create settings instance
label_settings = LabelSettings()
