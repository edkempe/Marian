"""Test factories for creating model instances."""

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDateTime, FuzzyText
from datetime import datetime, timedelta

from models.email import EmailMessage
from models.email_analysis import EmailAnalysis
from models.catalog import CatalogEntry
from models.gmail_label import GmailLabel


class EmailFactory(factory.Factory):
    """Factory for creating EmailMessage instances."""

    class Meta:
        model = EmailMessage

    message_id = factory.Sequence(lambda n: f"msg_{n}")
    thread_id = factory.Sequence(lambda n: f"thread_{n}")
    subject = factory.Faker("sentence")
    from_address = factory.Faker("email")
    to_addresses = factory.LazyFunction(lambda: [factory.Faker("email").generate({})])
    cc_addresses = factory.LazyFunction(lambda: [])
    bcc_addresses = factory.LazyFunction(lambda: [])
    body_text = factory.Faker("paragraph")
    body_html = factory.LazyAttribute(lambda obj: f"<html><body>{obj.body_text}</body></html>")
    received_date = factory.LazyFunction(lambda: datetime.utcnow())
    sent_date = factory.LazyFunction(lambda: datetime.utcnow() - timedelta(minutes=5))


class EmailAnalysisFactory(factory.Factory):
    """Factory for creating EmailAnalysis instances."""

    class Meta:
        model = EmailAnalysis

    email = factory.SubFactory(EmailFactory)
    sentiment = FuzzyChoice(["positive", "negative", "neutral"])
    categories = factory.LazyFunction(lambda: ["work", "important"])
    summary = factory.Faker("paragraph")
    key_points = factory.LazyFunction(lambda: ["Point 1", "Point 2"])
    action_items = factory.LazyFunction(lambda: ["Action 1", "Action 2"])
    created_at = factory.LazyFunction(lambda: datetime.utcnow())
    updated_at = factory.LazyFunction(lambda: datetime.utcnow())


class CatalogEntryFactory(factory.Factory):
    """Factory for creating CatalogEntry instances."""

    class Meta:
        model = CatalogEntry

    email = factory.SubFactory(EmailFactory)
    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    tags = factory.LazyFunction(lambda: ["tag1", "tag2"])
    extra_metadata = factory.LazyFunction(lambda: {"key": "value"})
    created_at = factory.LazyFunction(lambda: datetime.utcnow())
    updated_at = factory.LazyFunction(lambda: datetime.utcnow())


class GmailLabelFactory(factory.Factory):
    """Factory for creating GmailLabel instances."""

    class Meta:
        model = GmailLabel

    id = factory.Sequence(lambda n: f"Label_{n}")
    name = factory.Faker("word")
    type = FuzzyChoice(["system", "user"])
    message_list_visibility = "show"
    label_list_visibility = "labelShow"
    messages_total = factory.LazyFunction(lambda: 0)
    messages_unread = factory.LazyFunction(lambda: 0)
    color = factory.LazyFunction(lambda: {"textColor": "#000000", "backgroundColor": "#ffffff"})
