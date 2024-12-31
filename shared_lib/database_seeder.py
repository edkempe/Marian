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
from sqlalchemy import Table, MetaData, text, Column, Integer, String, Boolean, DateTime, ForeignKey, create_engine

from shared_lib.config_loader import get_schema_config
from shared_lib.constants import DATABASE_CONFIG
from shared_lib.database_session_util import get_engine_for_db_type


class DatabaseSeeder:
    """Database seeder class."""
    
    def __init__(self, env: str = "development"):
        """Initialize seeder.
        
        Args:
            env: Environment name (development, test, etc.)
        """
        self.env = env
        self.faker = Faker()
        self.schema_config = get_schema_config()
        
        # Create engines
        self.email_engine = get_engine_for_db_type("email")
        self.analysis_engine = get_engine_for_db_type("analysis")
        
        # Create MetaData instances
        self.email_metadata = MetaData()
        self.analysis_metadata = MetaData()
        
        # Create tables if they don't exist
        self._create_tables()
        
        # Reflect existing tables
        self.email_metadata.reflect(bind=self.email_engine)
        self.analysis_metadata.reflect(bind=self.analysis_engine)
        
    def _create_tables(self):
        """Create database tables if they don't exist."""
        # Email tables
        email_table = Table(
            "email",
            self.email_metadata,
            Column("id", Integer, primary_key=True),
            Column("subject", String, nullable=False),
            Column("sender", String, nullable=False),
            Column("recipient", String, nullable=False),
            Column("body", String, nullable=False),
            Column("timestamp", DateTime(timezone=True), nullable=False),
            Column("has_attachments", Boolean, default=False),
            Column("thread_id", String, nullable=False),
            Column("message_id", String, nullable=False, unique=True),
        )
        
        label_table = Table(
            "gmail_label",
            self.email_metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String, nullable=False),
            Column("type", String, nullable=False),
            Column("color", String),
            Column("visible", Boolean, default=True),
        )
        
        # Analysis tables
        analysis_table = Table(
            "analysis",
            self.analysis_metadata,
            Column("id", Integer, primary_key=True),
            Column("email_id", Integer, nullable=False),
            Column("sentiment", String, nullable=False),
            Column("priority", String, nullable=False),
            Column("summary", String),
            Column("analyzed_at", DateTime(timezone=True), nullable=False),
        )
        
        # Create tables
        self.email_metadata.create_all(self.email_engine)
        self.analysis_metadata.create_all(self.analysis_engine)
        
    def _load_seed_data(self, name: str) -> Dict[str, Any]:
        """Load seed data from YAML file."""
        seed_path = Path(f"config/seeds/{self.env}/{name}.yaml")
        if not seed_path.exists():
            seed_path = Path(f"config/seeds/{name}.yaml")
            
        if not seed_path.exists():
            raise FileNotFoundError(f"No seed file found for {name}")
            
        try:
            with open(seed_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Failed to parse seed file {name}: {str(e)}")
            
    def _generate_fake_email(self) -> Dict[str, Any]:
        """Generate fake email data."""
        return {
            "subject": self.faker.sentence(),
            "sender": self.faker.email(),
            "recipient": self.faker.email(),
            "body": self.faker.text(),
            "timestamp": datetime.now(timezone.utc),
            "has_attachments": self.faker.boolean(),
            "thread_id": self.faker.uuid4(),
            "message_id": self.faker.uuid4()
        }
        
    def _generate_fake_analysis(self, email_id: str) -> Dict[str, Any]:
        """Generate fake email analysis data."""
        return {
            "email_id": email_id,
            "sentiment": self.faker.random_element(
                self.schema_config.analysis.validation.valid_sentiments
            ),
            "priority": self.faker.random_element(
                self.schema_config.analysis.validation.valid_priorities
            ),
            "summary": self.faker.text(
                max_nb_chars=self.schema_config.analysis.validation.max_summary_length
            ),
            "analyzed_at": datetime.now(timezone.utc)
        }
        
    def _generate_fake_label(self) -> Dict[str, Any]:
        """Generate fake Gmail label data."""
        return {
            "name": self.faker.word(),
            "type": self.faker.random_element(
                self.schema_config.label.validation.valid_types
            ),
            "color": self.faker.hex_color(),
            "visible": self.faker.boolean()
        }
        
    def seed_emails(
        self,
        count: int = 10,
        seed_file: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Seed email data."""
        emails = []
        
        if seed_file:
            seed_data = self._load_seed_data(seed_file)
            emails.extend(seed_data.get("emails", []))
            
        while len(emails) < count:
            emails.append(self._generate_fake_email())
            
        # Insert into database and get IDs
        email_table = self.email_metadata.tables["email"]
        with self.email_engine.begin() as conn:
            for email in emails:
                result = conn.execute(
                    email_table.insert().returning(email_table.c.id),
                    email
                )
                email["id"] = result.scalar()
                
        return emails
        
    def seed_analysis(
        self,
        emails: Optional[List[Dict[str, Any]]] = None,
        count: int = 10,
        seed_file: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Seed email analysis data."""
        analyses = []
        
        if seed_file:
            seed_data = self._load_seed_data(seed_file)
            analyses.extend(seed_data.get("analyses", []))
            
        # Get email IDs if not provided
        if not emails:
            with self.email_engine.connect() as conn:
                result = conn.execute(text("SELECT id FROM email LIMIT :count"), {"count": count})
                emails = [{"id": row[0]} for row in result]
                
        # Generate analysis for each email
        for email in emails:
            if len(analyses) >= count:
                break
            analyses.append(self._generate_fake_analysis(email["id"]))
            
        # Insert into database
        analysis_table = self.analysis_metadata.tables["analysis"]
        with self.analysis_engine.begin() as conn:
            for analysis in analyses:
                conn.execute(
                    analysis_table.insert(),
                    analysis
                )
                
        return analyses
        
    def seed_labels(
        self,
        count: int = 5,
        seed_file: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Seed Gmail label data."""
        labels = []
        
        if seed_file:
            seed_data = self._load_seed_data(seed_file)
            labels.extend(seed_data.get("labels", []))
            
        while len(labels) < count:
            labels.append(self._generate_fake_label())
            
        # Insert into database
        label_table = self.email_metadata.tables["gmail_label"]
        with self.email_engine.begin() as conn:
            for label in labels:
                conn.execute(
                    label_table.insert(),
                    label
                )
                
        return labels
        
    def seed_all(
        self,
        email_count: int = 10,
        label_count: int = 5,
        seed_file: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Seed all data."""
        emails = self.seed_emails(email_count, seed_file)
        analyses = self.seed_analysis(emails, email_count, seed_file)
        labels = self.seed_labels(label_count, seed_file)
        
        return {
            "emails": emails,
            "analyses": analyses,
            "labels": labels
        }
        
    def cleanup(self):
        """Clean up all seeded data."""
        for engine in [self.email_engine, self.analysis_engine]:
            with engine.begin() as conn:
                meta = MetaData()
                meta.reflect(bind=engine)
                
                # Drop all tables except alembic_version
                for table in reversed(meta.sorted_tables):
                    if table.name != "alembic_version":
                        # Use parameterized query to prevent SQL injection
                        conn.execute(
                            text("DELETE FROM :table_name"),
                            {"table_name": table.name}
                        )
                        
                conn.commit()
