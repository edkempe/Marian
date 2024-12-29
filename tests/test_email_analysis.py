"""Test suite for email analysis functionality."""

import pytest
from datetime import datetime, timedelta, timezone
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.email import Email
from models.email_analysis import EmailAnalysis
from shared_lib.database_session_util import get_email_session, get_analysis_session
from src.app_email_analyzer import EmailAnalyzer
from shared_lib.gmail_lib import GmailAPI
from src.app_get_mail import fetch_emails
from shared_lib.constants import API_CONFIG, DATABASE_CONFIG, EMAIL_CONFIG

@pytest.fixture(scope="session")
def email_analyzer():
    """Create and initialize EmailAnalyzer instance."""
    analyzer = EmailAnalyzer()
    return analyzer

@pytest.fixture(scope="session")
def gmail_api():
    """Create and initialize Gmail API instance."""
    gmail = GmailAPI()
    gmail.setup_label_database()
    gmail.sync_labels()
    return gmail

@pytest.fixture
def test_emails(gmail_api):
    """Fetch recent test emails from Gmail."""
    # Get emails from the last configured days
    start_date = datetime.now(timezone.utc) - timedelta(days=EMAIL_CONFIG['DAYS_TO_FETCH'])
    messages = fetch_emails(gmail_api.service, start_date=start_date)
    
    # Process first few messages up to batch size
    emails = []
    with get_email_session() as session:
        for msg in messages[:EMAIL_CONFIG['BATCH_SIZE']]:
            try:
                message = gmail_api.service.users().messages().get(
                    userId='me', id=msg['id']).execute()
                
                # Create Email object
                email = Email(
                    id=message['id'],
                    threadId=message['threadId'],
                    subject=next((h['value'] for h in message['payload']['headers'] 
                                if h['name'].lower() == 'subject'), '[No Subject]'),
                    body=message.get('snippet', ''),
                    from_=next((h['value'] for h in message['payload']['headers'] 
                                     if h['name'].lower() == 'from'), '[No Sender]'),
                    received_date=datetime.now(timezone.utc),
                    labels=','.join(message.get('labelIds', []))
                )
                emails.append(email)
                
                if len(emails) >= 2:  # Just get 2 emails for testing
                    break
                    
            except Exception as e:
                print(f"Error processing message: {str(e)}")
                continue
    
    return emails

def test_analyzer_initialization(email_analyzer):
    """Test EmailAnalyzer initialization and configuration."""
    assert email_analyzer.client is not None

def test_email_analysis(email_analyzer, test_emails):
    """Test analyzing a single email."""
    # Test with first email
    email = test_emails[0]
    analysis = email_analyzer.analyze_email({
        'id': email.id,
        'threadId': email.threadId,
        'subject': email.subject,
        'body': email.body,
        'date': email.received_date.isoformat(),
        'labels': email.labels
    })
    
    assert analysis is not None
    assert isinstance(analysis, EmailAnalysis)
    assert analysis.summary
    assert isinstance(analysis.category, list)
    assert isinstance(analysis.priority_score, int)
    assert 1 <= analysis.priority_score <= 5
    assert analysis.confidence_score >= 0.0
    assert analysis.confidence_score <= 1.0
    
    print(f"\nAnalysis results for email: {email.subject}")
    print(f"Summary: {analysis.summary}")
    print(f"Category: {analysis.category}")
    print(f"Priority: {analysis.priority_score}")
    print(f"Action needed: {analysis.action_needed}")
    if analysis.action_needed:
        print(f"Action type: {analysis.action_type}")
        print(f"Deadline: {analysis.action_deadline}")

def test_batch_analysis(email_analyzer, test_emails):
    """Test analyzing multiple emails."""
    analyses = []
    for email in test_emails:
        analysis = email_analyzer.analyze_email({
            'id': email.id,
            'threadId': email.threadId,
            'subject': email.subject,
            'body': email.body,
            'date': email.received_date.isoformat(),
            'labels': email.labels
        })
        if analysis:
            analyses.append(analysis)
    
    assert len(analyses) == len(test_emails)
    assert all(isinstance(a, EmailAnalysis) for a in analyses)
    
    # Print analysis results
    for i, (email, analysis) in enumerate(zip(test_emails, analyses)):
        print(f"\nEmail {i+1}: {email.subject}")
        print(f"Summary: {analysis.summary}")
        print(f"Priority: {analysis.priority_score}")
        print(f"Topics: {analysis.topic}")

def test_analysis_storage(email_analyzer, test_emails):
    """Test storing analysis results in database."""
    email = test_emails[0]
    analysis = email_analyzer.analyze_email({
        'id': email.id,
        'threadId': email.threadId,
        'subject': email.subject,
        'body': email.body,
        'date': email.received_date.isoformat(),
        'labels': email.labels
    })
    
    assert analysis is not None
    
    with get_analysis_session() as session:
        # Store analysis
        db_analysis = EmailAnalysis(
            email_id=email.id,
            threadId=email.threadId,
            summary=analysis.summary,
            category=','.join(analysis.category),
            priority_score=analysis.priority_score,
            priority_reason=analysis.priority_reason,
            action_needed=analysis.action_needed,
            action_type=','.join(analysis.action_type),
            action_deadline=analysis.action_deadline,
            key_points=','.join(analysis.key_points),
            people_mentioned=','.join(analysis.people_mentioned),
            project=analysis.project,
            topic=analysis.topic,
            sentiment=analysis.sentiment,
            confidence_score=analysis.confidence_score
        )
        session.add(db_analysis)
        session.commit()
        
        # Verify storage
        stored = session.query(EmailAnalysis).filter_by(email_id=email.id).first()
        assert stored is not None
        assert stored.summary == analysis.summary
        assert stored.priority_score == analysis.priority_score
        assert stored.action_needed == analysis.action_needed
        assert stored.confidence_score == analysis.confidence_score
        
        print(f"\nStored analysis for email: {email.subject}")
        print(f"Summary: {stored.summary}")
        print(f"Priority: {stored.priority_score}")
        print(f"Action needed: {stored.action_needed}")

if __name__ == '__main__':
    pytest.main([__file__])
