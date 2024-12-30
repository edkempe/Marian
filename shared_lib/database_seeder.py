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
        return {
            "thread_id": fake.uuid4(),
            "message_id": fake.uuid4(),
            "subject": fake.sentence(),
            "body": fake.text(),
            "snippet": fake.text()[:100],
            "from_address": fake.email(),
            "to_address": fake.email(),
            "cc_address": fake.email() if fake.boolean() else None,
            "bcc_address": fake.email() if fake.boolean() else None,
            "has_attachments": fake.boolean(),
            "is_read": fake.boolean(),
            "is_important": fake.boolean(),
            "received_at": fake.date_time_this_year(tzinfo=timezone.utc),
            "api_response": "{}"
        }
        
    def _generate_fake_analysis(self, email_id: str) -> Dict[str, Any]:
        """Generate fake email analysis data."""
        return {
            "email_id": email_id,
            "sentiment": fake.random_element(["positive", "negative", "neutral", "mixed"]),
            "category": fake.random_element(["work", "personal", "finance", "social"]),
            "summary": fake.text()[:200],
            "priority": fake.random_element(["high", "medium", "low"]),
            "analyzed_at": fake.date_time_this_year(tzinfo=timezone.utc)
        }
        
    def _generate_fake_label(self) -> Dict[str, Any]:
        """Generate fake Gmail label data."""
        return {
            "label_id": fake.uuid4(),
            "name": fake.word(),
            "type": fake.random_element(["system", "user"]),
            "message_list_visibility": fake.random_element(["show", "hide"]),
            "label_list_visibility": fake.random_element(["labelShow", "labelHide"]),
            "is_system": fake.boolean()
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
