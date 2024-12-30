"""Database seeding utilities.

This module provides utilities for seeding databases with test data.
It supports:
1. Loading seed data from YAML files
2. Generating fake data using Faker
3. Maintaining referential integrity
4. Environment-specific seeding
"""

import logging
import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml
from faker import Faker
from sqlalchemy.orm import Session

from models.email import Email
from models.email_analysis import EmailAnalysis
from models.gmail_label import GmailLabel
from shared_lib.database_session_util import (
    get_email_session,
    get_analysis_session,
)

logger = logging.getLogger(__name__)
fake = Faker()

class DatabaseSeeder:
    """Database seeder class."""

    def __init__(self, env: str = "development"):
        """Initialize seeder.
        
        Args:
            env: Environment name (development, test, etc.)
        """
        self.env = env
        self.email_session = get_email_session()
        self.analysis_session = get_analysis_session()
        
    def _load_seed_data(self, name: str) -> Dict[str, Any]:
        """Load seed data from YAML file.
        
        Args:
            name: Name of seed data file (without .yaml extension)
            
        Returns:
            Dictionary containing seed data
        """
        seed_dir = Path("config/seeds")
        seed_file = seed_dir / f"{name}.{self.env}.yaml"
        
        if not seed_file.exists():
            seed_file = seed_dir / f"{name}.yaml"
            
        if not seed_file.exists():
            raise FileNotFoundError(f"No seed file found for {name}")
            
        with open(seed_file) as f:
            return yaml.safe_load(f)
            
    def _generate_fake_email(self) -> Dict[str, Any]:
        """Generate fake email data."""
        # Generate realistic email content
        subject_templates = [
            "Re: {topic} Update",
            "Meeting: {topic} Discussion",
            "Question about {topic}",
            "Important: {topic} Changes",
            "{topic} Review Needed",
        ]
        
        topics = [
            "Project Timeline",
            "Database Migration",
            "Code Review",
            "API Integration",
            "User Feedback",
            "Performance Issues",
            "Security Update",
            "Documentation",
            "Testing Strategy",
            "Release Planning",
        ]
        
        body_templates = [
            """
            Hi {recipient_name},
            
            I wanted to follow up on the {topic}. Here are the key points:
            
            1. {point1}
            2. {point2}
            3. {point3}
            
            Let me know if you have any questions.
            
            Best regards,
            {sender_name}
            """,
            """
            {recipient_name},
            
            Quick update on {topic}:
            - {point1}
            - {point2}
            
            Can we discuss this in our next meeting?
            
            Thanks,
            {sender_name}
            """,
            """
            Team,
            
            Here's the latest on our {topic}:
            
            Current Status:
            {point1}
            
            Next Steps:
            {point2}
            
            Action Items:
            {point3}
            
            Please review and provide feedback.
            
            Best,
            {sender_name}
            """,
        ]
        
        points = [
            "Completed initial implementation",
            "Testing in progress",
            "Documentation needs update",
            "Found potential issues",
            "Ready for review",
            "Needs more discussion",
            "Blocked by dependencies",
            "Moving forward as planned",
            "Requires team input",
            "Successfully deployed",
        ]
        
        # Generate sender and recipient names
        sender_name = fake.name()
        recipient_name = fake.name()
        
        # Generate email content
        topic = fake.random_element(topics)
        subject = fake.random_element(subject_templates).format(topic=topic)
        
        body = fake.random_element(body_templates).format(
            recipient_name=recipient_name,
            sender_name=sender_name,
            topic=topic,
            point1=fake.random_element(points),
            point2=fake.random_element(points),
            point3=fake.random_element(points),
        )
        
        # Generate realistic API response
        api_response = {
            "id": fake.uuid4(),
            "threadId": fake.uuid4(),
            "labelIds": [
                "INBOX",
                "IMPORTANT" if fake.boolean() else None,
                "CATEGORY_PERSONAL" if fake.boolean() else "CATEGORY_WORK",
            ],
            "snippet": body[:100] + "...",
            "payload": {
                "mimeType": "text/plain",
                "headers": [
                    {
                        "name": "From",
                        "value": f"{sender_name} <{fake.email()}>"
                    },
                    {
                        "name": "To",
                        "value": f"{recipient_name} <{fake.email()}>"
                    },
                    {
                        "name": "Subject",
                        "value": subject
                    },
                    {
                        "name": "Date",
                        "value": fake.date_time_this_year(tzinfo=timezone.utc).isoformat()
                    },
                ],
                "body": {
                    "data": body,
                    "size": len(body),
                },
            },
            "sizeEstimate": len(body),
        }
        
        return {
            "thread_id": api_response["threadId"],
            "message_id": api_response["id"],
            "subject": subject,
            "body": body,
            "snippet": api_response["snippet"],
            "from_address": f"{sender_name} <{fake.email()}>",
            "to_address": f"{recipient_name} <{fake.email()}>",
            "cc_address": f"{fake.name()} <{fake.email()}>" if fake.boolean() else None,
            "bcc_address": f"{fake.name()} <{fake.email()}>" if fake.boolean() else None,
            "has_attachments": fake.boolean(chance_of_getting_true=30),
            "is_read": fake.boolean(chance_of_getting_true=70),
            "is_important": fake.boolean(chance_of_getting_true=20),
            "received_at": fake.date_time_this_year(tzinfo=timezone.utc),
            "api_response": json.dumps(api_response),
        }
        
    def _generate_fake_analysis(self, email_id: str) -> Dict[str, Any]:
        """Generate fake email analysis data."""
        # Define realistic categories and their associated keywords
        categories = {
            "work": [
                "project", "meeting", "deadline", "report", "client",
                "presentation", "budget", "timeline", "milestone",
            ],
            "personal": [
                "family", "vacation", "weekend", "dinner", "party",
                "holiday", "birthday", "travel", "friend",
            ],
            "finance": [
                "invoice", "payment", "budget", "expense", "cost",
                "quote", "price", "billing", "account",
            ],
            "social": [
                "event", "meetup", "gathering", "party", "celebration",
                "invitation", "rsvp", "social", "community",
            ],
            "support": [
                "issue", "problem", "help", "question", "assistance",
                "error", "bug", "fix", "solution",
            ],
        }
        
        # Generate category based on email content
        email = self.email_session.query(Email).filter_by(id=email_id).first()
        if email:
            content = f"{email.subject} {email.body}".lower()
            category_scores = {
                cat: sum(1 for word in keywords if word in content)
                for cat, keywords in categories.items()
            }
            category = max(category_scores.items(), key=lambda x: x[1])[0]
        else:
            category = fake.random_element(list(categories.keys()))
        
        # Generate sentiment based on category and keywords
        positive_words = [
            "great", "excellent", "amazing", "wonderful", "successful",
            "thank", "appreciate", "good", "happy", "pleased",
        ]
        negative_words = [
            "issue", "problem", "error", "fail", "bad",
            "wrong", "delay", "bug", "sorry", "unfortunately",
        ]
        
        if email:
            content = f"{email.subject} {email.body}".lower()
            positive_score = sum(1 for word in positive_words if word in content)
            negative_score = sum(1 for word in negative_words if word in content)
            
            if positive_score > negative_score:
                sentiment = "positive"
            elif negative_score > positive_score:
                sentiment = "negative"
            elif positive_score == negative_score and (positive_score + negative_score) > 0:
                sentiment = "mixed"
            else:
                sentiment = "neutral"
        else:
            sentiment = fake.random_element(["positive", "negative", "neutral", "mixed"])
        
        # Generate priority based on sentiment and category
        priority_weights = {
            ("work", "negative"): 90,      # High priority for work issues
            ("work", "positive"): 60,      # Medium priority for work updates
            ("finance", "negative"): 80,   # High priority for financial issues
            ("finance", "positive"): 70,   # Medium-high for financial updates
            ("support", "negative"): 85,   # High priority for support issues
            ("support", "positive"): 50,   # Medium priority for support updates
            ("personal", "negative"): 40,  # Lower priority for personal issues
            ("personal", "positive"): 20,  # Low priority for personal updates
            ("social", "negative"): 30,    # Lower priority for social issues
            ("social", "positive"): 10,    # Low priority for social updates
        }
        
        priority_score = priority_weights.get(
            (category, sentiment),
            fake.random_int(min=0, max=100)
        )
        
        if priority_score >= 70:
            priority = "high"
        elif priority_score >= 40:
            priority = "medium"
        else:
            priority = "low"
        
        # Generate summary based on email content
        if email:
            summary = f"{sentiment.title()} {category} email: {email.snippet}"
        else:
            summary = f"{sentiment.title()} {category} email with {priority} priority"
        
        return {
            "email_id": email_id,
            "sentiment": sentiment,
            "category": category,
            "summary": summary,
            "priority": priority,
            "analyzed_at": fake.date_time_between(
                start_date="-1h",
                end_date="now",
                tzinfo=timezone.utc
            ),
        }

    def _generate_fake_label(self) -> Dict[str, Any]:
        """Generate fake Gmail label data."""
        # Define realistic label templates
        system_labels = [
            ("INBOX", "show", "labelShow", True),
            ("SENT", "show", "labelShow", True),
            ("DRAFT", "show", "labelShow", True),
            ("SPAM", "show", "labelHide", True),
            ("TRASH", "show", "labelHide", True),
            ("IMPORTANT", "show", "labelShow", True),
            ("STARRED", "show", "labelShow", True),
            ("UNREAD", "show", "labelHide", True),
        ]
        
        user_label_templates = [
            "Project/{name}",
            "Client/{name}",
            "Team/{name}",
            "Priority/{level}",
            "Status/{status}",
            "Department/{name}",
            "Category/{name}",
        ]
        
        names = [
            "Development",
            "Marketing",
            "Sales",
            "Support",
            "HR",
            "Finance",
            "Operations",
            "Research",
        ]
        
        levels = ["High", "Medium", "Low"]
        statuses = ["Active", "Pending", "Completed", "Archived"]
        
        if fake.boolean(chance_of_getting_true=30):  # 30% chance of system label
            name, msg_vis, label_vis, is_system = fake.random_element(system_labels)
        else:
            template = fake.random_element(user_label_templates)
            if "{name}" in template:
                name = template.format(name=fake.random_element(names))
            elif "{level}" in template:
                name = template.format(level=fake.random_element(levels))
            elif "{status}" in template:
                name = template.format(status=fake.random_element(statuses))
            else:
                name = template
                
            msg_vis = fake.random_element(["show", "hide"])
            label_vis = fake.random_element(["labelShow", "labelHide"])
            is_system = False
        
        return {
            "label_id": fake.uuid4(),
            "name": name,
            "type": "system" if is_system else "user",
            "message_list_visibility": msg_vis,
            "label_list_visibility": label_vis,
            "is_system": is_system,
        }

    def seed_emails(self, count: int = 10, seed_file: Optional[str] = None) -> List[Email]:
        """Seed email data.
        
        Args:
            count: Number of emails to generate if using fake data
            seed_file: Optional seed file name
            
        Returns:
            List of created Email objects
        """
        emails = []
        
        if seed_file:
            data = self._load_seed_data(seed_file)
            for email_data in data["emails"]:
                email = Email(**email_data)
                self.email_session.add(email)
                emails.append(email)
        else:
            for _ in range(count):
                email = Email(**self._generate_fake_email())
                self.email_session.add(email)
                emails.append(email)
                
        self.email_session.commit()
        return emails

    def seed_analysis(
        self,
        emails: Optional[List[Email]] = None,
        count: int = 10,
        seed_file: Optional[str] = None
    ) -> List[EmailAnalysis]:
        """Seed email analysis data.
        
        Args:
            emails: Optional list of emails to analyze
            count: Number of analyses to generate if using fake data
            seed_file: Optional seed file name
            
        Returns:
            List of created EmailAnalysis objects
        """
        analyses = []
        
        if seed_file:
            data = self._load_seed_data(seed_file)
            for analysis_data in data["analyses"]:
                analysis = EmailAnalysis(**analysis_data)
                self.analysis_session.add(analysis)
                analyses.append(analysis)
        else:
            if not emails:
                emails = self.seed_emails(count)
                
            for email in emails:
                analysis = EmailAnalysis(**self._generate_fake_analysis(email.id))
                self.analysis_session.add(analysis)
                analyses.append(analysis)
                
        self.analysis_session.commit()
        return analyses

    def seed_labels(
        self,
        count: int = 5,
        seed_file: Optional[str] = None
    ) -> List[GmailLabel]:
        """Seed Gmail label data.
        
        Args:
            count: Number of labels to generate if using fake data
            seed_file: Optional seed file name
            
        Returns:
            List of created GmailLabel objects
        """
        labels = []
        
        if seed_file:
            data = self._load_seed_data(seed_file)
            for label_data in data["labels"]:
                label = GmailLabel(**label_data)
                self.email_session.add(label)
                labels.append(label)
        else:
            for _ in range(count):
                label = GmailLabel(**self._generate_fake_label())
                self.email_session.add(label)
                labels.append(label)
                
        self.email_session.commit()
        return labels

    def seed_all(
        self,
        email_count: int = 10,
        label_count: int = 5,
        seed_file: Optional[str] = None
    ) -> Dict[str, List[Any]]:
        """Seed all data.
        
        Args:
            email_count: Number of emails to generate if using fake data
            label_count: Number of labels to generate if using fake data
            seed_file: Optional seed file name
            
        Returns:
            Dictionary containing all created objects
        """
        emails = self.seed_emails(email_count, seed_file)
        analyses = self.seed_analysis(emails, seed_file=seed_file)
        labels = self.seed_labels(label_count, seed_file)
        
        return {
            "emails": emails,
            "analyses": analyses,
            "labels": labels
        }

    def cleanup(self) -> None:
        """Clean up all seeded data."""
        try:
            # Delete in reverse order of dependencies
            self.analysis_session.query(EmailAnalysis).delete()
            self.email_session.query(GmailLabel).delete()
            self.email_session.query(Email).delete()
            
            self.analysis_session.commit()
            self.email_session.commit()
            
        except Exception as e:
            logger.error(f"Failed to cleanup seeded data: {str(e)}")
            self.analysis_session.rollback()
            self.email_session.rollback()
            raise
