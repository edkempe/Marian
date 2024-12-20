#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.email import Email
from models.email_analysis import EmailAnalysis

# Create engine
engine = create_engine('sqlite:///email_store.db')
analysis_engine = create_engine('sqlite:///email_analysis.db')

# Create all tables
Base.metadata.create_all(engine)
Base.metadata.create_all(analysis_engine)

print("Database tables created successfully!")
