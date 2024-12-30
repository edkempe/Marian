"""Script to check email database contents."""

from constants import DATABASE_CONFIG
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from models.email import Email


def check_database():
    """Check contents of email database."""
    engine = create_engine(DATABASE_CONFIG["EMAIL_DB_URL"])
    with Session(engine) as session:
        # Get total count
        total = session.query(func.count(Email.id)).scalar()
        print(f"\nTotal emails in database: {total}")

        # Get sample email with all fields
        email = session.query(Email).first()
        if email:
            print("\nSample email details:")
            print(f"ID: {email.id}")
            print(f"Thread ID: {email.thread_id}")
            print(f"Subject: {email.subject}")
            print(f"From: {email.from_address}")
            print(f"To: {email.to_address}")
            print(f"CC: {email.cc_address}")
            print(f"BCC: {email.bcc_address}")
            print(f"Date: {email.received_date}")
            print(f"Labels: {email.labels}")
            print(f"Has Attachments: {email.has_attachments}")
            print("\nFull API Response Preview (first 200 chars):")
            print(f"{email.full_api_response[:200]}...")

        # Get personal emails
        print("\nPersonal Emails:")
        personal_emails = (
            session.query(Email).filter(Email.labels.like("%CATEGORY_PERSONAL%")).all()
        )
        for email in personal_emails:
            print(f"\nSubject: {email.subject}")
            print(f"From: {email.from_address}")
            print(f"Date: {email.received_date}")
            print(f"Labels: {email.labels}")

        # Get emails with Label_167
        print("\nEmails with Label_167:")
        label_167_emails = (
            session.query(Email).filter(Email.labels.like("%Label_167%")).all()
        )
        for email in label_167_emails:
            print(f"\nSubject: {email.subject}")
            print(f"From: {email.from_address}")
            print(f"Labels: {email.labels}")

        # Get some statistics
        print("\nEmail Statistics:")
        emails_with_attachments = (
            session.query(func.count(Email.id))
            .filter(Email.has_attachments == True)
            .scalar()
        )
        print(f"Emails with attachments: {emails_with_attachments}")

        # Get label distribution
        print("\nMost common labels:")
        all_labels = session.query(Email.labels).all()
        label_count = {}
        for labels_str in all_labels:
            if labels_str[0]:  # Check if labels string exists
                for label in labels_str[0].split(","):
                    label_count[label] = label_count.get(label, 0) + 1

        for label, count in sorted(
            label_count.items(), key=lambda x: x[1], reverse=True
        )[:10]:
            print(f"{label}: {count}")


if __name__ == "__main__":
    check_database()
