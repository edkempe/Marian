"""Test utilities and fixtures."""

from typing import Dict, Optional, Union

import pytest

from models.email import EmailMessage
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel
from shared_lib.constants import VALID_SENTIMENTS
from src.app_email_analyzer import EmailAnalysisResponse
from tests.factories import EmailAnalysisFactory, EmailFactory, GmailLabelFactory


def create_test_email(
    id: Optional[str] = None,
    thread_id: Optional[str] = None,
    subject: Optional[str] = None,
    body: Optional[str] = None,
) -> EmailMessage:
    """Create a test email object using EmailFactory."""
    return EmailFactory(
        id=id,
        thread_id=thread_id,
        subject=subject,
        body=body,
    )


def create_test_analysis(
    email_id: Optional[str] = None,
    summary: Optional[str] = None,
    category: Optional[str] = None,
    priority_score: Optional[int] = None,
) -> EmailAnalysis:
    """Create a test email analysis object using EmailAnalysisFactory."""
    return EmailAnalysisFactory(
        email_id=email_id,
        summary=summary,
        category=category,
        priority_score=priority_score,
    )


def create_test_gmail_label(
    id: Optional[str] = None,
    name: Optional[str] = None,
    type: Optional[str] = None,
) -> GmailLabel:
    """Create a test Gmail label object using GmailLabelFactory."""
    return GmailLabelFactory(
        id=id,
        name=name,
        type=type,
    )


def assert_email_analysis_response(analysis: Union[Dict, EmailAnalysisResponse]) -> None:
    """Assert that an email analysis response has the expected structure."""
    if isinstance(analysis, EmailAnalysisResponse):
        assert analysis.summary is not None
        assert isinstance(analysis.summary, str)
        assert len(analysis.summary) > 0

        assert analysis.category is not None
        assert isinstance(analysis.category, list)
        assert len(analysis.category) > 0
        assert all(isinstance(cat, str) for cat in analysis.category)

        assert analysis.priority_score is not None
        assert isinstance(analysis.priority_score, int)
        assert 1 <= analysis.priority_score <= 10

        assert analysis.sentiment is not None
        assert analysis.sentiment.upper() in VALID_SENTIMENTS
    else:
        assert "summary" in analysis
        assert isinstance(analysis["summary"], str)
        assert len(analysis["summary"]) > 0

        assert "category" in analysis
        assert isinstance(analysis["category"], list)
        assert len(analysis["category"]) > 0
        assert all(isinstance(cat, str) for cat in analysis["category"])

        assert "priority_score" in analysis
        assert isinstance(analysis["priority_score"], int)
        assert 1 <= analysis["priority_score"] <= 10

        assert "sentiment" in analysis
        assert analysis["sentiment"].upper() in VALID_SENTIMENTS


def assert_email_analysis_results(analysis: EmailAnalysis, 
                                expected_min_priority: int,
                                expected_categories: list[str]) -> None:
    """Assert specific email analysis results.
    
    Args:
        analysis: The analysis response to verify
        expected_min_priority: Minimum expected priority score
        expected_categories: List of expected categories that should be present
    """
    # Verify priority score
    assert analysis.priority_score >= expected_min_priority, \
        f"Priority score {analysis.priority_score} is lower than minimum expected {expected_min_priority}"
    
    # Verify categories (case-insensitive)
    analysis_categories = [cat.upper() for cat in analysis.category]
    expected_categories = [cat.upper() for cat in expected_categories]
    matching_categories = [cat for cat in expected_categories if cat in analysis_categories]
    assert matching_categories, \
        f"None of the expected categories {expected_categories} found in analysis categories {analysis.category}"
