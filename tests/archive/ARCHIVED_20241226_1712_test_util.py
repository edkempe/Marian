#!/usr/bin/env python3
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from models.email import Email
from shared_lib.database_session_util import get_email_session

test_emails = [
    {
        "id": "msg_001",
        "subject": "Project Update: Q4 Roadmap",
        "content": """Hi team,

I wanted to share a quick update on our Q4 roadmap progress. Here are the key points:

1. Feature A is on track for release next week
2. We're seeing some delays in Feature B due to technical challenges
3. Customer feedback for Feature C has been overwhelmingly positive

Action items:
- Team leads: Please review the updated timeline by EOW
- Engineering: Focus on resolving Feature B blockers
- Product: Schedule customer feedback sessions for Feature C

Let me know if you have any questions.

Best,
Project Manager""",
    },
    {
        "id": "msg_002",
        "subject": "Weekly Team Sync Notes",
        "content": """Team,

Here's a summary of today's sync meeting:

Updates:
- Backend team completed API v2 migration
- Frontend team started work on new dashboard
- DevOps implemented automated backup system

Next steps:
1. Complete code review for API changes
2. Begin user testing of dashboard prototype
3. Document backup procedures

Regards,
Team Lead""",
    },
]


class EmailProcessor:
    """Test email processor for version tracking tests."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.analysis_prompt = {
            "prompt_name": "test_prompt",
            "version": "1.0",
            "description": "Test prompt for email analysis",
        }

    def get_unprocessed_emails(self):
        """Get unprocessed test emails."""
        return [
            (email["id"], email["subject"], email["content"]) for email in test_emails
        ]

    def process_email(self, email_tuple):
        """Process a test email."""
        email_id, subject, content = email_tuple
        return {
            "email_id": email_id,
            "analysis": {
                "summary": "Test analysis",
                "key_points": ["Point 1", "Point 2"],
                "action_items": ["Action 1", "Action 2"],
            },
            "prompt_version": self.analysis_prompt["version"],
        }


def add_test_emails():
    """Add test emails to the database."""
    session = get_email_session()
    for email_data in test_emails:
        email = Email(
            message_id=email_data["id"],
            subject=email_data["subject"],
            content=email_data["content"],
            received_date=datetime.now(timezone.utc),
            processed=False,
        )
        session.add(email)
    session.commit()


def generate_test_data():
    """Generate test data for the application."""
    add_test_emails()


def load_test_fixtures():
    """Load test fixtures and return a test API key."""
    generate_test_data()
    return "test_api_key_12345"


if __name__ == "__main__":
    add_test_emails()
