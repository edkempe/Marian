"""Minimal test suite for critical functionality."""

from typing import Dict

import pytest
from models.email_analysis import EmailAnalysis

from tests.factories import EmailFactory
from tests.test_constants import (
    TEST_EMAIL_SUBJECT,
    TEST_IMPORTANT_EMAIL_BODY,
    TEST_ANALYSIS_CATEGORY,
    TEST_MIN_PRIORITY,
)
from tests.test_utils import assert_email_analysis_response, assert_email_analysis_results


def test_email_analysis(test_mode_analyzer, verify_api_connection) -> None:
    """Test email analysis with real API calls.
    
    This test verifies that:
    1. The analyzer can process an email
    2. The response has the expected structure
    3. The response contains valid values for priority and category
    
    Args:
        test_mode_analyzer: EmailAnalyzer fixture in test mode
        verify_api_connection: Fixture to verify API connection
    """
    # Create test email data
    test_email: Dict[str, str] = {
        "subject": TEST_EMAIL_SUBJECT,
        "body": TEST_IMPORTANT_EMAIL_BODY,
    }
    
    # Analyze email
    analysis: EmailAnalysis = test_mode_analyzer.analyze_email(test_email)
    
    # Verify analysis results
    assert_email_analysis_response(analysis)
    assert_email_analysis_results(
        analysis=analysis,
        expected_min_priority=TEST_MIN_PRIORITY,
        expected_categories=TEST_ANALYSIS_CATEGORY,
    )
