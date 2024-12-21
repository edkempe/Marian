"""Models package for Marian project."""

from .base import Base
from .email import Email
from .email_analysis import EmailAnalysis, EmailAnalysisResponse

__all__ = [
    'Base',
    'Email',
    'EmailAnalysis',
    'EmailAnalysisResponse'
]
