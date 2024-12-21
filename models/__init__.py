"""Models package for Marian project."""

from .base import Base
from .email import Email, EmailMetadata
from .email_analysis import EmailAnalysis, EmailAnalysisResponse

__all__ = [
    'Base',
    'Email',
    'EmailMetadata',
    'EmailAnalysis',
    'EmailAnalysisResponse'
]
