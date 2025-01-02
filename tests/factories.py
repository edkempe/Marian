"""Test factories for creating model instances."""

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDateTime, FuzzyText
from datetime import datetime, timedelta
from faker import Faker

from models.email import EmailMessage
from models.email_analysis import EmailAnalysis
from models.catalog import CatalogEntry
from models.gmail_label import GmailLabel

ENUMS = {
    "SENTIMENT_VALUES": ["positive", "negative", "neutral"],
    "CLAUDE_MODELS": ["v1", "v2"]
}

fake = Faker()


class EmailFactory(factory.Factory):
    """Factory for creating EmailMessage instances."""

    class Meta:
        model = EmailMessage

    message_id = factory.Sequence(lambda n: f"msg_{n}")
    thread_id = factory.Sequence(lambda n: f"thread_{n}")
    subject = fake.sentence()
    from_address = fake.email()
    to_addresses = factory.LazyFunction(lambda: [fake.email()])
    cc_addresses = factory.LazyFunction(lambda: [])
    bcc_addresses = factory.LazyFunction(lambda: [])
    body_text = fake.paragraph()
    body_html = factory.LazyAttribute(lambda obj: f"<html><body>{obj.body_text}</body></html>")
    received_date = factory.LazyFunction(lambda: datetime.utcnow())
    sent_date = factory.LazyFunction(lambda: datetime.utcnow() - timedelta(minutes=5))


class EmailAnalysisFactory(factory.Factory):
    """Factory for creating EmailAnalysis instances."""

    class Meta:
        model = EmailAnalysis

    analysis_id = factory.Sequence(lambda n: f"analysis_{n}")
    email = factory.SubFactory(EmailFactory)
    summary = fake.paragraph()
    sentiment = FuzzyChoice(ENUMS["SENTIMENT_VALUES"])
    categories = factory.LazyFunction(lambda: ["work", "important"])
    key_points = factory.LazyFunction(lambda: ["Point 1", "Point 2"])
    action_items = factory.LazyFunction(
        lambda: [
            {
                "description": "Action 1",
                "due_date": datetime.utcnow().isoformat(),
                "priority": "high",
                "assignee": fake.email()
            },
            {
                "description": "Action 2",
                "priority": "medium"
            }
        ]
    )
    priority_score = FuzzyChoice([1, 2, 3, 4, 5])
    confidence_score = factory.Faker('pyfloat', min_value=0.0, max_value=1.0)
    model_version = FuzzyChoice(ENUMS["CLAUDE_MODELS"])
    analysis_metadata = factory.LazyFunction(lambda: {"source": "email", "version": "1.0"})
    created_at = factory.LazyFunction(lambda: datetime.utcnow())
    updated_at = factory.LazyFunction(lambda: datetime.utcnow())


class CatalogEntryFactory(factory.Factory):
    """Factory for creating CatalogEntry instances."""

    class Meta:
        model = CatalogEntry

    email = factory.SubFactory(EmailFactory)
    title = fake.sentence()
    description = fake.paragraph()
    tags = factory.LazyFunction(lambda: ["tag1", "tag2"])
    extra_metadata = factory.LazyFunction(lambda: {"key": "value"})
    created_at = factory.LazyFunction(lambda: datetime.utcnow())
    updated_at = factory.LazyFunction(lambda: datetime.utcnow())


class GmailLabelFactory(factory.Factory):
    """Factory for creating GmailLabel instances.
    
    Based on Gmail API Label resource:
    https://developers.google.com/gmail/api/reference/rest/v1/users.labels#Label
    """

    class Meta:
        model = GmailLabel

    id = factory.Sequence(lambda n: f"Label_{n}")
    name = fake.word()
    type = FuzzyChoice(["system", "user"])
    message_list_visibility = FuzzyChoice(["show", "hide"])
    label_list_visibility = FuzzyChoice(["labelShow", "labelShowIfUnread", "labelHide"])
    
    # Color fields (only for user labels)
    color = factory.LazyAttribute(lambda o: "#000000" if o.type == "user" else None)
    background_color = factory.LazyAttribute(lambda o: "#ffffff" if o.type == "user" else None)
    text_color = factory.LazyAttribute(lambda o: "#000000" if o.type == "user" else None)
    
    # Message and thread counts
    messages_total = factory.LazyFunction(lambda: 0)
    messages_unread = factory.LazyFunction(lambda: 0)
    threads_total = factory.LazyFunction(lambda: 0)
    threads_unread = factory.LazyFunction(lambda: 0)
    
    # Timestamps
    created_at = factory.LazyFunction(lambda: datetime.utcnow())
    updated_at = factory.LazyFunction(lambda: datetime.utcnow())
