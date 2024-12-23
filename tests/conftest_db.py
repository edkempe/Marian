"""Test configuration and fixtures."""
import os
import pytest
import sqlite3
from datetime import datetime, timezone
import json

TEST_EMAIL_DB = 'test_email_store.db'
TEST_ANALYSIS_DB = 'test_analysis.db'

def setup_test_email_db():
    """Set up test email database with correct schema."""
    if os.path.exists(TEST_EMAIL_DB):
        os.remove(TEST_EMAIL_DB)
    
    conn = sqlite3.connect(TEST_EMAIL_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emails (
        id TEXT PRIMARY KEY,
        thread_id TEXT,
        subject TEXT,
        sender TEXT,
        date TEXT,  -- Store as ISO format string
        body TEXT,
        labels VARCHAR(150),
        has_attachments BOOLEAN DEFAULT 0 NOT NULL,
        full_api_response TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gmail_labels (
        id INTEGER PRIMARY KEY,
        label_id VARCHAR(30) NOT NULL UNIQUE,
        name TEXT NOT NULL,
        type TEXT,
        is_active BOOLEAN DEFAULT 1 NOT NULL,
        first_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at DATETIME
    )
    ''')
    
    conn.commit()
    return conn

def setup_test_analysis_db():
    """Set up test analysis database with correct schema."""
    if os.path.exists(TEST_ANALYSIS_DB):
        os.remove(TEST_ANALYSIS_DB)
    
    conn = sqlite3.connect(TEST_ANALYSIS_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS email_analysis (
        email_id TEXT PRIMARY KEY,
        thread_id TEXT NOT NULL,
        analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        analyzed_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        prompt_version TEXT,
        summary TEXT,
        category TEXT,
        priority_score INTEGER,
        priority_reason TEXT,
        action_needed BOOLEAN,
        action_type TEXT,
        action_deadline DATETIME,
        key_points TEXT,
        people_mentioned TEXT,
        links_found TEXT,
        links_display TEXT,
        project TEXT,
        topic TEXT,
        sentiment TEXT,
        confidence_score REAL,
        full_api_response TEXT,
        FOREIGN KEY(email_id) REFERENCES emails(id)
    )
    ''')
    
    conn.commit()
    return conn

def setup_test_dbs():
    """Set up both test databases."""
    email_conn = setup_test_email_db()
    analysis_conn = setup_test_analysis_db()
    return email_conn, analysis_conn

def insert_test_data(email_conn, analysis_conn):
    """Insert test data into both databases."""
    email_cursor = email_conn.cursor()
    analysis_cursor = analysis_conn.cursor()

    # Insert test emails
    test_emails = [
        ('18ab4cc9d45e2f1a', '18ab4cc9d45e2f1a', 'Test Email 1', 'sender1@test.com', 
         datetime.now(timezone.utc).isoformat(), 'Test content 1', 'INBOX,IMPORTANT', False,
         json.dumps({'raw': 'data1'})),
        ('18ab4cc9d45e2f1b', '18ab4cc9d45e2f1b', 'Test Email 2', 'sender2@test.com',
         datetime.now(timezone.utc).isoformat(), 'Test content 2', 'INBOX', True,
         json.dumps({'raw': 'data2'}))
    ]
    
    email_cursor.executemany('''
        INSERT INTO emails (id, thread_id, subject, sender, date, body, labels, has_attachments, full_api_response)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', test_emails)

    # Insert test analysis data
    test_analyses = [
        ('18ab4cc9d45e2f1a', '18ab4cc9d45e2f1a', datetime.now(timezone.utc), datetime.now(timezone.utc), 'v1',
         'Test summary 1', json.dumps(['category1']), 3, 'Test reason',
         True, json.dumps(['action1']), datetime.now(timezone.utc),
         json.dumps(['point1']), json.dumps(['person1']), 
         json.dumps(['link1']), json.dumps(['display1']),
         'project1', 'topic1', 'positive', 0.9,
         json.dumps({'raw': 'data1'})),
        ('18ab4cc9d45e2f1b', '18ab4cc9d45e2f1b', datetime.now(timezone.utc), datetime.now(timezone.utc), 'v1',
         'Test summary 2', json.dumps(['category2']), 2, 'Test reason 2',
         False, json.dumps([]), None,
         json.dumps(['point2']), json.dumps([]), 
         json.dumps([]), json.dumps([]),
         'project2', 'topic2', 'neutral', 0.8,
         json.dumps({'raw': 'data2'}))
    ]

    analysis_cursor.executemany('''
        INSERT INTO email_analysis (
            email_id, thread_id, analysis_date, analyzed_date, prompt_version,
            summary, category, priority_score, priority_reason,
            action_needed, action_type, action_deadline,
            key_points, people_mentioned, links_found, links_display,
            project, topic, sentiment, confidence_score, full_api_response
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', test_analyses)

    email_conn.commit()
    analysis_conn.commit()

@pytest.fixture
def setup_test_data_fixture():
    """Fixture to set up test data in databases."""
    email_conn, analysis_conn = setup_test_dbs()
    insert_test_data(email_conn, analysis_conn)
    
    yield
    
    # Cleanup
    email_conn.close()
    analysis_conn.close()
    if os.path.exists(TEST_EMAIL_DB):
        os.remove(TEST_EMAIL_DB)
    if os.path.exists(TEST_ANALYSIS_DB):
        os.remove(TEST_ANALYSIS_DB)
