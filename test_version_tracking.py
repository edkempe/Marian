#!/usr/bin/env python3
import os
from test_anthropic_email import EmailProcessor, get_api_key
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_email_processing():
    """Test email processing with hardcoded prompt"""
    # Initialize processor
    api_key = get_api_key()
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
    test_email_processing()
