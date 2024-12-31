"""Database seeding utilities.

This module provides utilities for seeding databases with test data.
It supports:
1. Loading seed data from YAML files
2. Generating fake data using Faker
3. Maintaining referential integrity
4. Environment-specific seeding
"""

import os
import logging
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

import yaml
from faker import Faker
from sqlalchemy import Table, MetaData, text, Column, Integer, String, Boolean, DateTime, ForeignKey, create_engine
from sqlalchemy.exc import OperationalError

from shared_lib.config_loader import get_schema_config
from shared_lib.constants import DATABASE_CONFIG
from shared_lib.database_session_util import get_engine_for_db_type


class DatabaseSeeder:
    """Database seeder class."""
    
    # Environment constants
    ENV_DEVELOPMENT = "development"
    ENV_TEST = "test"
    
    # Default seed counts
    DEFAULT_EMAIL_COUNT = 10
    DEFAULT_LABEL_COUNT = 5
    
    def __init__(self, env: str = ENV_DEVELOPMENT):
        """Initialize seeder.
        
        Args:
            env: Environment name (development, test, etc.)
        
        Raises:
            ValueError: If environment is invalid
            OperationalError: If database connection fails
        """
        if env not in [self.ENV_DEVELOPMENT, self.ENV_TEST]:
            raise ValueError(f"Invalid environment. Must be '{self.ENV_DEVELOPMENT}' or '{self.ENV_TEST}'")
            
        self.env = env
        self.faker = Faker()
        
        try:
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
            
        except Exception as e:
            logging.error(f"Failed to initialize database seeder: {str(e)}")
            raise OperationalError(f"Database initialization failed: {str(e)}")
            
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
        """Load seed data from YAML file.
        
        Args:
            name: Name of seed file or absolute path to seed file
            
        Returns:
            Dict containing seed data
            
        Raises:
            FileNotFoundError: If seed file not found
            Exception: If seed file parsing fails
        """
        # Check if name is an absolute path
        seed_path = Path(name)
        if not seed_path.is_absolute():
            # Try environment-specific path first
            seed_path = Path(f"config/seeds/{self.env}/{name}.yaml")
            if not seed_path.exists():
                seed_path = Path(f"config/seeds/{name}.yaml")
                
        if not seed_path.exists():
            raise FileNotFoundError(f"No seed file found for {name}")
            
        try:
            with open(seed_path) as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise Exception(f"Failed to parse seed file {name}: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to load seed file {name}: {str(e)}")

    def _generate_fake_email(self, invalid_data: bool = False) -> Dict[str, Any]:
        """Generate fake email data.
        
        Args:
            invalid_data: If True, generate invalid data for testing
        
        Returns:
            Dict containing email data
        """
        if invalid_data:
            return {
                "subject": "Test Subject"
                # Missing required fields for testing
            }
            
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
        
    def _generate_fake_analysis(self, email_id: int, invalid_data: bool = False) -> Dict[str, Any]:
        """Generate fake email analysis data.
        
        Args:
            email_id: ID of email to analyze
            invalid_data: If True, generate invalid data for testing
        
        Returns:
            Dict containing analysis data
        """
        if invalid_data:
            return {
                "email_id": "not_an_integer",  # Invalid type
                "sentiment": "invalid_sentiment",  # Invalid value
                "priority": "invalid_priority",  # Invalid value
                "summary": "Test summary",
                "analyzed_at": "not_a_datetime"  # Invalid type
            }
            
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
        
    def _generate_fake_label(self, invalid_data: bool = False) -> Dict[str, Any]:
        """Generate fake Gmail label data.
        
        Args:
            invalid_data: If True, generate invalid data for testing
        
        Returns:
            Dict containing label data
        """
        if invalid_data:
            return {
                "name": "Test Label",
                "type": "user",  # Valid type
                "color": "#FFFFFF",  # Valid color
                "visible": "not_a_boolean"  # Invalid type
            }
            
        return {
            "name": self.faker.word(),
            "type": self.faker.random_element(
                self.schema_config.label.validation.valid_types
            ),
            "color": self.faker.hex_color(),
            "visible": self.faker.boolean()
        }

    def _validate_schema(self, data: Dict[str, Any], table: Table) -> None:
        """Validate data against table schema.
        
        Args:
            data: Data to validate
            table: SQLAlchemy table to validate against
        
        Raises:
            ValueError: If data does not match schema
        """
        for column in table.columns:
            # Skip primary key columns as they are auto-generated
            if column.primary_key:
                continue
                
            # Check if required field is present
            if not column.nullable and column.name not in data:
                raise ValueError(f"Required field {column.name} missing from data")
                
            # Validate data type if value is present
            if column.name in data:
                value = data[column.name]
                
                # Check for null values
                if value is None and not column.nullable:
                    raise ValueError(f"Field {column.name} cannot be null")
                    
                # Type validation
                if value is not None:
                    try:
                        # Special handling for boolean type
                        if column.type.python_type == bool:
                            if isinstance(value, bool):
                                continue
                            if isinstance(value, int):
                                data[column.name] = bool(value)
                            elif isinstance(value, str) and value.lower() in ['true', 'false']:
                                data[column.name] = value.lower() == 'true'
                            else:
                                raise ValueError(f"Invalid type for {column.name}: expected BOOLEAN, got {type(value)}")
                        else:
                            # Convert value to Python type
                            python_type = column.type.python_type
                            if not isinstance(value, python_type):
                                # Try to convert
                                data[column.name] = python_type(value)
                    except (ValueError, TypeError):
                        raise ValueError(
                            f"Invalid type for {column.name}: expected {column.type}, got {type(value)}"
                        )
                        
                    # Length validation for string fields
                    if hasattr(column.type, "length") and column.type.length is not None:
                        if len(str(value)) > column.type.length:
                            raise ValueError(
                                f"Value for {column.name} exceeds maximum length of {column.type.length}"
                            )

    def seed_emails(
        self,
        count: int = 10,
        seed_file: Optional[str] = None,
        invalid_data: bool = False
    ) -> List[Dict[str, Any]]:
        """Seed email data.
        
        Args:
            count: Number of emails to generate
            seed_file: Optional path to seed file
            invalid_data: If True, generate invalid data for testing
        
        Returns:
            List of generated emails
        """
        emails = []
        
        if seed_file:
            seed_data = self._load_seed_data(seed_file)
            emails.extend(seed_data.get("emails", []))
            
        while len(emails) < count:
            emails.append(self._generate_fake_email(invalid_data))
            
        # Validate and insert into database
        email_table = self.email_metadata.tables["email"]
        validated_emails = []
        
        for email in emails:
            try:
                # Validate schema
                self._validate_schema(email, email_table)
                validated_emails.append(email)
            except ValueError as e:
                logging.warning(f"Skipping invalid email: {str(e)}")
                if invalid_data:
                    raise  # Re-raise for testing
                continue
                
        # Insert valid emails
        with self.email_engine.begin() as conn:
            for email in validated_emails:
                result = conn.execute(
                    email_table.insert().returning(email_table.c.id),
                    email
                )
                email["id"] = result.scalar()
                
        return validated_emails

    def seed_analysis(
        self,
        emails: Optional[List[Dict[str, Any]]] = None,
        count: int = 10,
        seed_file: Optional[str] = None,
        invalid_data: bool = False
    ) -> List[Dict[str, Any]]:
        """Seed email analysis data.
        
        Args:
            emails: Optional list of emails to analyze
            count: Number of analyses to generate
            seed_file: Optional path to seed file
            invalid_data: If True, generate invalid data for testing
        
        Returns:
            List of generated analyses
        """
        analyses = []
        
        if seed_file:
            seed_data = self._load_seed_data(seed_file)
            analyses.extend(seed_data.get("analyses", []))
            
        # Get email IDs if not provided
        if not emails:
            with self.email_engine.connect() as conn:
                result = conn.execute(text("SELECT id FROM email LIMIT :count"), {"count": count})
                emails = [{"id": row[0]} for row in result]
                
        # Generate and validate analysis for each email
        analysis_table = self.analysis_metadata.tables["analysis"]
        validated_analyses = []
        
        for email in emails:
            if len(validated_analyses) >= count:
                break
                
            analysis = self._generate_fake_analysis(email["id"], invalid_data)
            try:
                # Validate schema
                self._validate_schema(analysis, analysis_table)
                validated_analyses.append(analysis)
            except ValueError as e:
                logging.warning(f"Skipping invalid analysis: {str(e)}")
                if invalid_data:
                    raise  # Re-raise for testing
                continue
                
        # Insert valid analyses
        with self.analysis_engine.begin() as conn:
            for analysis in validated_analyses:
                conn.execute(
                    analysis_table.insert(),
                    analysis
                )
                
        return validated_analyses

    def seed_labels(
        self,
        count: int = 5,
        seed_file: Optional[str] = None,
        invalid_data: bool = False
    ) -> List[Dict[str, Any]]:
        """Seed Gmail label data.
        
        Args:
            count: Number of labels to generate
            seed_file: Optional path to seed file
            invalid_data: If True, generate invalid data for testing
        
        Returns:
            List of generated labels
        """
        labels = []
        
        if seed_file:
            seed_data = self._load_seed_data(seed_file)
            labels.extend(seed_data.get("labels", []))
            
        while len(labels) < count:
            labels.append(self._generate_fake_label(invalid_data))
            
        # Validate and insert into database
        label_table = self.email_metadata.tables["gmail_label"]
        validated_labels = []
        
        for label in labels:
            try:
                # Validate schema
                self._validate_schema(label, label_table)
                validated_labels.append(label)
            except ValueError as e:
                logging.warning(f"Skipping invalid label: {str(e)}")
                if invalid_data:
                    raise  # Re-raise for testing
                continue
                
        # Insert valid labels
        with self.email_engine.begin() as conn:
            for label in validated_labels:
                conn.execute(
                    label_table.insert(),
                    label
                )
                
        return validated_labels

    def seed_all(
        self,
        email_count: int = DEFAULT_EMAIL_COUNT,
        label_count: int = DEFAULT_LABEL_COUNT,
        seed_file: Optional[str] = None,
        invalid_data: bool = False
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Seed all data.
        
        Args:
            email_count: Number of emails to generate
            label_count: Number of labels to generate
            seed_file: Optional path to seed file
            invalid_data: If True, generate invalid data for testing
            
        Returns:
            Dict containing generated data
        """
        emails = self.seed_emails(email_count, seed_file, invalid_data)
        analyses = self.seed_analysis(emails, email_count, seed_file, invalid_data)
        labels = self.seed_labels(label_count, seed_file, invalid_data)
        
        return {
            "emails": emails,
            "analyses": analyses,
            "labels": labels
        }
        
    def _verify_cleanup(self, engine, metadata):
        """Verify that all tables are empty except alembic_version.
        
        Args:
            engine: SQLAlchemy engine
            metadata: SQLAlchemy metadata
            
        Raises:
            OperationalError: If verification fails
        """
        for table in metadata.sorted_tables:
            if table.name != "alembic_version":
                with engine.connect() as conn:
                    count = conn.execute(
                        text(f"SELECT COUNT(*) FROM {table.name}")
                    ).scalar()
                    if count > 0:
                        raise OperationalError(
                            f"Cleanup verification failed: {table.name} still has {count} rows"
                        )

    def cleanup(self):
        """Clean up all seeded data.
        
        This method deletes all data from the tables while preserving the alembic_version table.
        The tables are deleted in reverse order to handle foreign key constraints.
        
        Raises:
            OperationalError: If cleanup fails
        """
        try:
            # Clean up email database
            with self.email_engine.begin() as conn:
                try:
                    for table in reversed(self.email_metadata.sorted_tables):
                        if table.name != "alembic_version":
                            conn.execute(table.delete())
                except Exception as e:
                    conn.rollback()
                    raise OperationalError(f"Failed to clean up email database: {str(e)}")
                    
            # Clean up analysis database
            with self.analysis_engine.begin() as conn:
                try:
                    for table in reversed(self.analysis_metadata.sorted_tables):
                        if table.name != "alembic_version":
                            conn.execute(table.delete())
                except Exception as e:
                    conn.rollback()
                    raise OperationalError(f"Failed to clean up analysis database: {str(e)}")
                    
            # Verify cleanup was successful
            self._verify_cleanup(self.email_engine, self.email_metadata)
            self._verify_cleanup(self.analysis_engine, self.analysis_metadata)
                    
        except Exception as e:
            logging.error(f"Failed to clean up data: {str(e)}")
            raise OperationalError(f"Failed to clean up data: {str(e)}")
