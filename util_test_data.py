#!/usr/bin/env python3
from datetime import datetime, timedelta
from database.config import get_session
from model_email import Email

test_emails = [
    {
        "subject": "Project Update: Q4 Roadmap",
        "body": """Hi team,

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
        "sender": "john@company.com",
        "received_date": datetime.now() - timedelta(days=1),
        "labels": "important,project-updates",
        "thread_id": "thread_001",
        "has_attachments": False
    },
    {
        "subject": "Urgent: Server Performance Issues",
        "body": """Team,

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
        "sender": "sarah@company.com",
        "received_date": datetime.now() - timedelta(hours=2),
        "labels": "urgent,production-issues",
        "thread_id": "thread_002",
        "has_attachments": False
    },
    {
        "subject": "Team Lunch Next Week",
        "body": """Hello everyone!

To celebrate our successful Q3, we're organizing a team lunch next Wednesday at 12:30 PM.

Location: Bistro Garden
Address: 123 Main St.

Please let me know if you have any dietary restrictions.

Looking forward to seeing everyone!

Best,
Emma""",
        "sender": "emma@company.com",
        "received_date": datetime.now() - timedelta(days=2),
        "labels": "team-events,social",
        "thread_id": "thread_003",
        "has_attachments": False
    }
]

def add_test_emails():
    """Add test emails to the database."""
    with get_session() as session:
        for email_data in test_emails:
            email = Email(**email_data)
            session.add(email)
        session.commit()
        print(f"Added {len(test_emails)} test emails to the database.")

if __name__ == "__main__":
    add_test_emails()
