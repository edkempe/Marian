"""Marian package initialization."""

from .app_api_client import APIClient
from .app_catalog import CatalogChat
from .app_email_analyzer import EmailAnalyzer
from .app_email_reports import EmailAnalytics
from .app_email_self_log import EmailSelfAnalyzer
from .app_get_mail import GmailAPI, fetch_emails, list_labels, process_email

__all__ = [
    "CatalogChat",
    "EmailAnalyzer",
    "EmailAnalytics",
    "EmailSelfAnalyzer",
    "GmailAPI",
    "fetch_emails",
    "process_email",
    "list_labels",
    "APIClient",
]
