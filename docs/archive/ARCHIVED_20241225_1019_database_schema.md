# Database Schema Documentation

## Data Model as Single Source of Truth

The data model defined in this document serves as the **single source of truth** for the entire application. All other components must align with and validate against this model:

- Database schema must exactly reflect these definitions
- Code models must be generated from or validated against this schema
- API endpoints must respect these data constraints
- Tests must verify conformance to this model

### Validation Requirements
1. Schema changes must be proposed against this document first
2. Code changes must demonstrate compliance with the model
3. Tests must verify both schema and data conformance
4. Migration plans must ensure data model integrity

## Core Design Principles

### ID Types
- All IDs are stored as TEXT to maintain direct correspondence with Gmail's API
- This includes both message IDs and thread IDs
- Benefits:
  1. Direct mapping to Gmail's API without translation
  2. Easier debugging and traceability
  3. No need for mapping tables
  4. Eliminates ID mismatch errors
  5. Simplifies data import/export

### Date/Time Handling
- All dates stored in ISO 8601 format
- UTC timezone used for consistency
- Original email timezone preserved in raw_data

## Database Structure

### Main Database (db_email_store.db)

#### emails
Primary table for storing raw email data from Gmail.

| Column           | Type    | Constraints           | Description                          |
|-----------------|---------|----------------------|--------------------------------------|
| id              | TEXT    | PK, NOT NULL         | Gmail message ID                     |
| thread_id       | TEXT    | NOT NULL             | Gmail thread ID                      |
| subject         | TEXT    | DEFAULT 'No Subject' | Email subject                        |
| sender          | TEXT    | NOT NULL             | Sender email address                 |
| date            | TEXT    | NOT NULL             | Email date in ISO format             |
| body            | TEXT    | DEFAULT ''           | Email content                        |
| labels          | TEXT    | DEFAULT '[]'         | Gmail labels as JSON array           |
| raw_data        | TEXT    | NOT NULL             | Complete raw email data as JSON      |
| created_at      | TEXT    | NOT NULL             | Record creation timestamp            |
| updated_at      | TEXT    | NOT NULL             | Last update timestamp               |

#### email_analysis
Stores AI analysis results for each email.

| Column           | Type    | Constraints           | Description                          |
|-----------------|---------|----------------------|--------------------------------------|
| email_id        | TEXT    | PK, FK(emails.id)    | Reference to email                   |
| analysis_date   | TEXT    | NOT NULL             | Analysis timestamp in ISO format     |
| prompt_version  | TEXT    | NOT NULL             | Version of analysis prompt used      |
| summary         | TEXT    | NOT NULL             | Brief email summary                  |
| categories      | TEXT    | NOT NULL             | Categories as JSON array             |
| priority        | INTEGER | NOT NULL             | Priority score (1-5)                 |
| priority_reason | TEXT    | NOT NULL             | Explanation for priority             |
| action_needed   | INTEGER | NOT NULL             | Boolean as INTEGER (0/1)             |
| action_type     | TEXT    | DEFAULT NULL         | Type of action as JSON               |
| action_deadline | TEXT    | DEFAULT NULL         | Deadline in ISO format               |
| key_points      | TEXT    | NOT NULL             | Key points as JSON array             |
| people          | TEXT    | DEFAULT '[]'         | People mentioned as JSON array       |
| created_at      | TEXT    | NOT NULL             | Record creation timestamp            |
| updated_at      | TEXT    | NOT NULL             | Last update timestamp               |

### Catalog Database (db_catalog.db)

#### catalog_entries
Stores organized information entries.

| Column           | Type    | Constraints           | Description                          |
|-----------------|---------|----------------------|--------------------------------------|
| id              | TEXT    | PK, NOT NULL         | Unique entry ID                      |
| email_id        | TEXT    | FK(emails.id)        | Source email if applicable           |
| title           | TEXT    | NOT NULL             | Entry title                          |
| content         | TEXT    | NOT NULL             | Entry content                        |
| category        | TEXT    | NOT NULL             | Primary category                     |
| tags            | TEXT    | DEFAULT '[]'         | Tags as JSON array                   |
| metadata        | TEXT    | DEFAULT '{}'         | Additional metadata as JSON          |
| created_at      | TEXT    | NOT NULL             | Record creation timestamp            |
| updated_at      | TEXT    | NOT NULL             | Last update timestamp               |

## Implementation Notes

### JSON Fields
- All JSON fields must be valid JSON or NULL
- Empty arrays stored as '[]'
- Empty objects stored as '{}'
- Schema validation performed at application level

### Timestamps
- All timestamps stored in ISO 8601 format
- Application responsible for timezone conversion
- UTC used for internal storage

### Constraints
- Foreign key constraints enforced
- NOT NULL constraints on critical fields
- Default values provided where appropriate

### Indexes
- Primary keys automatically indexed
- Foreign keys indexed for join performance
- Additional indexes on frequently queried fields
