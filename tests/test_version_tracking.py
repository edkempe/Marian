#!/usr/bin/env python3
"""Tests for version tracking functionality."""
import pytest
import os
from ..shared_lib.broken_test_util import EmailProcessor, load_test_fixtures
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@pytest.fixture
def setup_test_data():
    """Set up test data."""
    return load_test_fixtures()

def test_email_processing(setup_test_data):
    """Test email processing with hardcoded prompt"""
    # Initialize processor
    api_key = setup_test_data
    processor = EmailProcessor(api_key=api_key)
    
    # Get current prompt info
    prompt = processor.analysis_prompt
    logging.info(f"Using prompt: {prompt['prompt_name']}")
    
    # Process some test emails (if any)
    unprocessed = processor.get_unprocessed_emails()
    if unprocessed:
        logging.info(f"Found {len(unprocessed)} unprocessed emails")
        for email in unprocessed[:5]:  # Process up to 5 emails
            if processor.process_email(email):
                logging.info(f"Successfully processed email: {email[1]}")  # email[1] is subject
            else:
                logging.error(f"Failed to process email: {email[1]}")
    else:
        logging.info("No unprocessed emails found")

if __name__ == "__main__":
    pytest.main([__file__])
