#!/usr/bin/env python3
from datetime import datetime, timedelta, timezone
import os
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
- Engineering: Need estimates for Feature D implementation
- Product: Schedule user testing sessions for Feature A

Let me know if you have any questions or concerns.

Best regards,
John""",
        "from_address": "john@company.com",
        "to_address": "team@company.com",
        "received_date": datetime.now(timezone.utc) - timedelta(days=1),
        "labels": "important,project-updates",
        "thread_id": "thread_001",
        "has_attachments": False,
        "full_api_response": "{}"
    },
    {
        "id": "msg_002",
        "subject": "Urgent: Server Performance Issues",
        "content": """Team,

We're experiencing critical performance issues in the production environment:

- Response times have increased by 300%
- Several timeout errors reported by customers
- Database load is unusually high

I've started initial investigation and found some potential causes:
1. Recent code deployment might have introduced inefficient queries
2. Increased traffic from new feature launch
3. Possible memory leak in service X

Immediate actions needed:
1. Roll back latest deployment
2. Scale up database resources
3. Monitor system metrics closely

Please treat this as high priority.

Thanks,
Sarah""",
        "from_address": "sarah@company.com",
        "to_address": "team@company.com",
        "received_date": datetime.now(timezone.utc) - timedelta(hours=2),
        "labels": "urgent,production-issues",
        "thread_id": "thread_002",
        "has_attachments": False,
        "full_api_response": "{}"
    },
    {
        "id": "msg_003",
        "subject": "Team Lunch Next Week",
        "content": """Hello everyone!

To celebrate our successful Q3, we're organizing a team lunch next Wednesday at 12:30 PM.

Location: Bistro Garden
Address: 123 Main St.

Please let me know if you have any dietary restrictions.

Looking forward to seeing everyone!

Best,
Emma""",
        "from_address": "emma@company.com",
        "to_address": "team@company.com",
        "received_date": datetime.now(timezone.utc) - timedelta(days=2),
        "labels": "team-events,social",
        "thread_id": "thread_003",
        "has_attachments": False,
        "full_api_response": "{}"
    }
]

class EmailProcessor:
    """Test email processor for version tracking tests."""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.analysis_prompt = {
            'prompt_name': 'test_prompt',
            'version': '1.0',
            'description': 'Test prompt for email analysis'
        }
    
    def get_unprocessed_emails(self):
        """Get unprocessed test emails."""
        with get_email_session() as session:
            return [(1, email.subject) for email in session.query(Email).limit(5)]
    
    def process_email(self, email_tuple):
        """Process a test email."""
        email_id, subject = email_tuple
        return True  # Always succeed in test mode

def add_test_emails():
    """Add test emails to the database."""
    with get_email_session() as session:
        for email_data in test_emails:
            email = Email(**email_data)
            session.add(email)
        session.commit()
        print(f"Added {len(test_emails)} test emails to the database.")

def generate_test_data():
    """Generate test data for the application."""
    add_test_emails()

def load_test_fixtures():
    """Load test fixtures and return a test API key."""
    generate_test_data()
    return "test_api_key_12345"

if __name__ == "__main__":
    add_test_emails()
