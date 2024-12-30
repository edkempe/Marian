"""Test factories for generating test data."""

import json
from datetime import datetime

import factory
import pytz
from factory.faker import Faker
from factory.fuzzy import FuzzyChoice

from models.email import Email
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel
from shared_lib.constants import VALID_SENTIMENTS
from tests.test_constants import (
    TEST_ANALYSIS_CATEGORY,
    TEST_MIN_PRIORITY,
    TEST_ANALYSIS_SUMMARY,
    TEST_EMAIL_BCC,
    TEST_EMAIL_BODY,
    TEST_EMAIL_CC,
    TEST_EMAIL_RECIPIENT,
    TEST_EMAIL_SENDER,
    TEST_EMAIL_SUBJECT,
    TEST_GMAIL_API_RESPONSE,
    TEST_LABEL_NAME,
    TEST_LABEL_TYPE,
)


class BaseFactory(factory.Factory):
    """Base factory with common utilities."""
    
    @factory.lazy_attribute
    def created_at(self):
        """Generate current UTC timestamp."""
        return datetime.now(pytz.utc)
        
    @factory.lazy_attribute
    def updated_at(self):
        """Generate current UTC timestamp."""
        return datetime.now(pytz.utc)


class EmailFactory(BaseFactory):
    """Factory for creating Email objects."""

    class Meta:
        model = Email

    id = factory.Sequence(lambda n: f"test_email_{n}")
    threadId = factory.Sequence(lambda n: f"thread_{n}")
    subject = TEST_EMAIL_SUBJECT
    body = TEST_EMAIL_BODY
    from_ = TEST_EMAIL_SENDER
    to = TEST_EMAIL_RECIPIENT
    date = factory.LazyFunction(lambda: datetime.now(pytz.utc))
    cc = TEST_EMAIL_CC
    bcc = TEST_EMAIL_BCC
    full_api_response = factory.LazyFunction(lambda: json.dumps(TEST_GMAIL_API_RESPONSE))


class EmailAnalysisFactory(BaseFactory):
    """Factory for creating EmailAnalysis objects."""

    class Meta:
        model = EmailAnalysis

    id = factory.Sequence(lambda n: f"analysis_{n}")
    summary = TEST_ANALYSIS_SUMMARY
    category = factory.LazyFunction(lambda: json.dumps(TEST_ANALYSIS_CATEGORY))
    priority_score = TEST_MIN_PRIORITY
    sentiment = FuzzyChoice(VALID_SENTIMENTS)
    email = factory.SubFactory(EmailFactory)
    email_id = factory.SelfAttribute("email.id")


class GmailLabelFactory(BaseFactory):
    """Factory for creating GmailLabel objects."""

    class Meta:
        model = GmailLabel

    id = factory.Sequence(lambda n: f"Label_{n}")
    name = TEST_LABEL_NAME
    type = TEST_LABEL_TYPE
    is_active = Faker("boolean", chance_of_getting_true=90)  # 90% chance of being active
    first_seen_at = factory.SelfAttribute("created_at")
    last_seen_at = factory.SelfAttribute("updated_at")
