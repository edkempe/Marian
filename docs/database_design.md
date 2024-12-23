# Database Design Decisions

## Email and Thread IDs

### Decision
Use TEXT type for both message IDs and thread IDs in the database, preserving Gmail's original string identifiers.

### Context
Gmail's API returns string identifiers for both messages and threads. While using INTEGER as primary key is generally preferred for performance, we chose to use TEXT to maintain direct correspondence with Gmail's API.

### Consequences

#### Advantages
1. Direct mapping to Gmail's API without ID translation
2. Easier debugging by using the same IDs as Gmail
3. No need for mapping tables between our IDs and Gmail IDs
4. Eliminates potential for ID mismatch errors
5. Simplifies data import/export with Gmail's API

#### Disadvantages
1. Slightly larger storage requirements for indexes
2. Potentially slower joins due to string comparisons
3. Larger memory footprint for primary key indexes

### Implementation Notes
1. All IDs are stored as TEXT in SQLite/SQLAlchemy
2. Foreign key relationships use the TEXT IDs
3. Input validation should ensure IDs are non-empty strings
4. Error handling should account for string ID formats

### Migration
If needed, existing databases with integer IDs can be migrated to use Gmail's string IDs. The migration process would involve:
1. Creating new tables with TEXT IDs
2. Fetching Gmail IDs for existing messages
3. Migrating data to new tables
4. Updating foreign key relationships
5. Dropping old tables

### Schema

#### emails
Primary table for storing raw email data from Gmail.

| Column           | Type    | Constraints       | Description                          |
|-----------------|---------|------------------|--------------------------------------|
| id              | TEXT    | PK, NOT NULL     | Gmail message ID                     |
| thread_id       | TEXT    | NOT NULL         | Gmail thread ID                      |
| subject         | TEXT    | DEFAULT 'No Subject' | Email subject                    |
| sender          | TEXT    | NOT NULL         | Sender email address                 |
| date            | TEXT    | NOT NULL         | Email date in ISO format             |
| body            | TEXT    | DEFAULT ''       | Email content                        |
| labels          | TEXT    | DEFAULT ''       | Comma-separated Gmail label IDs      |
| has_attachments | BOOLEAN | NOT NULL, DEFAULT 0 | Whether email has attachments     |
| full_api_response| TEXT    | DEFAULT '{}'     | Complete Gmail API response as JSON |

#### email_analysis
Stores AI analysis results for each email.

| Column           | Type     | Constraints        | Description                     |
|-----------------|----------|-------------------|----------------------------------|
| email_id        | TEXT     | PK, FK(emails.id) | References Gmail message ID      |
| thread_id       | TEXT     | NOT NULL          | Gmail thread ID                  |
| analysis_date   | DATETIME | NOT NULL          | When analysis was performed      |
| analyzed_date   | DATETIME | NOT NULL          | When email was analyzed          |
| prompt_version  | TEXT     | NULL              | Version of analysis prompt       |
| summary         | TEXT     | NOT NULL          | Brief email summary              |
| category        | JSON     | NOT NULL          | Email categories                 |
| priority_score  | INTEGER  | NOT NULL          | Priority (1-5)                   |
| priority_reason | TEXT     | NOT NULL          | Reason for priority              |
| action_needed   | BOOLEAN  | NOT NULL          | Action required flag             |
| action_type     | JSON     | NOT NULL          | Type of action needed            |
| action_deadline | DATETIME | NULL              | Action deadline date             |
| key_points      | JSON     | NOT NULL          | Key points from email            |
| people_mentioned| JSON     | NOT NULL          | People mentioned in email        |
| links_found     | JSON     | NOT NULL          | Full URLs found in email         |
| links_display   | JSON     | NOT NULL          | Truncated URLs for display       |
| project         | TEXT     | NULL              | Associated project               |
| topic           | TEXT     | NULL              | Email topic                      |
| sentiment       | TEXT     | NULL              | Email sentiment                  |
| confidence_score| FLOAT    | NULL              | Analysis confidence (0.0-1.0)    |
| full_api_response| JSON     | NOT NULL          | Complete analysis response       |
| raw_analysis    | JSON     | NOT NULL          | Complete analysis response       |

### Legacy Tables

### email_triage
Legacy table for email triage (deprecated). This table is no longer used and its functionality has been merged into `email_analysis`.

| Column            | Type    | Description              | Notes                    |
|------------------|---------|--------------------------|--------------------------|
| email_id         | TEXT    | Primary key              |                         |
| priority         | TEXT    | Email priority           |                         |
| category         | TEXT    | Email category           |                         |
| summary          | TEXT    | Brief summary            |                         |
| action_items     | TEXT    | Required actions         |                         |
| sentiment        | TEXT    | Email sentiment          |                         |
| analysis_date    | TEXT    | Analysis timestamp       |                         |
| batch_id         | INTEGER | Processing batch ID      |                         |
| processing_status| TEXT    | Current status           | Indexed                 |
| error_message    | TEXT    | Error if failed          |                         |
| retry_count      | INTEGER | Number of retries        | Default 0               |

#### Migration Status
- Priority and category merged into `email_analysis`
- Summary and sentiment preserved in new schema
- Action items expanded into more detailed fields
- Processing status handled by task queue
- Batch processing not yet implemented in new system

### Historical Changes

### 2024-12-23
- Changed email_id in email_analysis from INTEGER to TEXT to match Gmail IDs
- Added thread_id and has_attachments to emails table
- Consolidated analysis into main database
- Deprecated separate analysis database
- Added validation for Gmail IDs

### 2024-12-21
- Added email_triage table for initial analysis workflow
- Created separate analysis database (now deprecated)

### Code Examples

#### Model Definition
```python
# models/email.py
class Email(Base):
    __tablename__ = 'emails'
    id: Mapped[str] = Column(Text, primary_key=True)  # Gmail message ID
    thread_id: Mapped[str] = Column(Text)  # Gmail thread ID

# models/email_analysis.py
class EmailAnalysis(Base):
    __tablename__ = 'email_analysis'
    email_id: Mapped[str] = Column(Text, ForeignKey('emails.id'), primary_key=True)
    thread_id: Mapped[str] = Column(Text, nullable=False)
```

#### Database Schema
```sql
CREATE TABLE emails (
    id TEXT PRIMARY KEY,  -- Gmail message ID
    thread_id TEXT,       -- Gmail thread ID
    -- other fields...
);

CREATE TABLE email_analysis (
    email_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    FOREIGN KEY(email_id) REFERENCES emails(id)
    -- other fields...
);
```

### Related Documents
- [Gmail API Message Resource](https://developers.google.com/gmail/api/reference/rest/v1/users.messages#Message)
- [Gmail API Thread Resource](https://developers.google.com/gmail/api/reference/rest/v1/users.threads#Thread)

### Future Work

### Planned Changes
1. Implement batch processing system
   - Track batch_id and processing_status
   - Handle retries and error states
   - Priority: Medium

2. Clean up legacy components
   - Remove email_triage table
   - Archive old analysis database
   - Update documentation
   - Priority: Low

3. Schema Improvements
   - Consider partitioning by date
   - Add indexes for common queries
   - Priority: Low
