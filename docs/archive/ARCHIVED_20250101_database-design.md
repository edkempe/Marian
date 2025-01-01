# [ARCHIVED] Database Design Documentation

> **ARCHIVED**: This document has been converted into Architecture Decision Records (ADRs). Please refer to:
> - [ADR-0019](../adr/0019-api-first-schema-design.md): API-First Schema Design
> - [ADR-0004](../adr/0004-configuration-based-schema-definitions.md): Schema Configuration
>
> This file is kept for historical reference only. All future updates should be made to the corresponding ADRs.

**Version:** 1.0.0
**Status:** Authoritative

## Design Principles

### 1. API-First Schema Design

Our database schema is designed to align with external APIs, following these principles:

1. **External APIs as Source of Truth**
   - Field types match API specifications
   - Field names preserve API conventions
   - Constraints reflect API limitations
   - Example: Gmail API uses string IDs, so our database does too

2. **Model-Driven Schema**
   - SQLAlchemy models define the schema
   - Models document API alignment
   - Additional fields follow API patterns
   - No schema changes without model updates

3. **Migration-Based Changes**
   - All schema changes require migrations
   - Migrations are tested before deployment
   - Backward compatibility is maintained
   - Type changes preserve data integrity

### 2. Schema Validation

We use automated testing to ensure schema consistency:

1. **Model-Database Alignment**
   - `test_schema.py` validates alignment
   - Runs before other tests
   - Catches drift early
   - Prevents silent mismatches

2. **Type Validation**
   - Field types match API specifications
   - Constraints are properly enforced
   - Foreign keys maintain referential integrity
   - Indexes support query patterns

3. **Migration Testing**
   - Migrations are tested in isolation
   - Data preservation is verified
   - Rollback procedures are tested
   - Performance impact is assessed

## Table Schemas

### Email Table (`emails`)

Stores email data from Gmail API.

**Fields:**
- `id` (VARCHAR(100)): Gmail message ID (source: Gmail API)
- `thread_id` (VARCHAR(100)): Gmail thread ID
- `subject` (VARCHAR(500)): Email subject
- `body` (TEXT): Email body
- `sender` (VARCHAR(200)): Sender email
- `to_address` (VARCHAR(200)): Recipient email
- `received_date` (DATETIME): Receipt timestamp (with timezone)
- `labels` (VARCHAR(500)): Gmail label IDs
- `has_attachments` (BOOLEAN): Attachment flag
- `cc_address` (TEXT): CC recipients
- `bcc_address` (TEXT): BCC recipients
- `full_api_response` (TEXT): Complete Gmail API response

**Constraints:**
- Primary Key: `id`
- Not Null: `id`
- Foreign Keys: Referenced by `email_analysis.email_id`

### Email Analysis Table (`email_analysis`)

Stores AI-generated email analysis.

**Fields:**
- `email_id` (VARCHAR(100)): Reference to email
- `analysis_date` (DATETIME): Analysis timestamp
- `summary` (TEXT): Email summary
- `category` (TEXT): Email category
- `priority_score` (INTEGER): Priority (1-5)
- `action_needed` (BOOLEAN): Action flag
- `sentiment` (TEXT): Email sentiment
- `confidence_score` (FLOAT): Analysis confidence

**Constraints:**
- Primary Key: `email_id`
- Foreign Key: `email_id` references `emails.id`
- Not Null: Most analysis fields

### Gmail Labels Table (`gmail_labels`)

Stores Gmail label metadata.

**Fields:**
- `id` (VARCHAR(100)): Gmail label ID
- `name` (VARCHAR(100)): Label name
- `type` (VARCHAR(50)): System/User label
- `is_active` (BOOLEAN): Active status
- `first_seen_at` (DATETIME): First occurrence
- `last_seen_at` (DATETIME): Last occurrence
- `deleted_at` (DATETIME): Deletion timestamp

**Constraints:**
- Primary Key: `id`
- Not Null: `id`, `name`, `type`

## Migrations

All schema changes are managed through migrations:

1. **Initial Schema** (`initial_schema.py`)
   - Base tables and relationships
   - Core field definitions
   - Primary keys and indexes

2. **CC/BCC Fields** (`add_cc_bcc_fields.py`)
   - Added CC/BCC address fields
   - Text type for multiple addresses
   - Default empty string

3. **Email and Label Fields** (`add_email_and_label_fields.py`)
   - Added recipient address
   - Added full API response
   - Added label tracking fields

4. **Email ID Type Fix** (`fix_email_id_type.py`)
   - Changed email ID to string
   - Matches Gmail API format
   - Updated foreign key relationships

## Best Practices

1. **Schema Changes**
   - Always start with API documentation
   - Update models before database
   - Use migrations for all changes
   - Test thoroughly before deployment

2. **Type Management**
   - Match API data types exactly
   - Use appropriate column types
   - Consider storage implications
   - Document type decisions

3. **Testing**
   - Run schema tests first
   - Verify data preservation
   - Test migrations both ways
   - Check constraint enforcement
