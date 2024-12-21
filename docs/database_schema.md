# Database Schema Documentation

## Overview
The project uses SQLite databases to store emails and their analysis results.

## Database Files
- `db_email_store.db`: Main database containing emails and analysis
- `db_email_analysis.db`: Separate database for analysis results (currently not used)

## Tables

### emails
Primary table for storing raw email data.

| Column    | Type    | Description                     | Notes                    |
|-----------|---------|--------------------------------|--------------------------|
| id        | TEXT    | Primary key, email ID          | Gmail message ID        |
| subject   | TEXT    | Email subject                  |                         |
| sender    | TEXT    | Sender email address           |                         |
| date      | TEXT    | Email received date            | Stored in ISO format    |
| body      | TEXT    | Email body content             |                         |
| labels    | TEXT    | Gmail labels                   | JSON array as string    |
| raw_data  | TEXT    | Raw email data                 | JSON string             |

### email_analysis
Stores AI analysis results for each email.

| Column           | Type         | Description                  | Notes                    |
|-----------------|--------------|------------------------------|--------------------------|
| email_id        | INTEGER      | Primary key, references email| Should be TEXT to match |
| analysis_date   | DATETIME     | When analysis was performed  |                         |
| analyzed_date   | DATETIME     | When email was analyzed      | Required                |
| prompt_version  | VARCHAR(50)  | Version of analysis prompt   | Required                |
| summary         | VARCHAR      | Brief email summary          | Required                |
| category        | JSON         | Email categories             | Required                |
| priority_score  | INTEGER      | Priority (1-5)              | Required                |
| priority_reason | VARCHAR      | Reason for priority          | Required                |
| action_needed   | BOOLEAN      | Action required flag         | Required                |
| action_type     | JSON         | Type of action needed        | Required                |
| action_deadline | VARCHAR      | Action deadline date         | Optional                |
| key_points      | JSON         | Key points from email        | Required                |
| people_mentioned| JSON         | People mentioned             | Required                |
| links_found     | JSON         | URLs found in email          | Required                |
| links_display   | JSON         | Display text for URLs        | Required                |
| project         | VARCHAR      | Related project              | Optional                |
| topic           | VARCHAR      | Email topic                  | Optional                |
| ref_docs        | VARCHAR      | Reference documents          | Optional                |
| sentiment       | VARCHAR      | Email sentiment              | Required                |
| confidence_score| FLOAT        | Analysis confidence          | Required                |
| raw_analysis    | JSON         | Raw analysis response        | Required                |

### email_triage
Legacy table for email triage (currently not used).

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

## Required Changes

1. Update `Email` model to match database:
   - Remove `thread_id` and `has_attachments`
   - Change `date` to `Text` type
   - Add `raw_data` field

2. Update `EmailAnalysis` model:
   - Change `email_id` to `String` type to match email IDs

3. Consider:
   - Creating model for `email_triage` if still needed
   - Migrating `email_triage` data to `email_analysis`
   - Dropping `email_triage` if deprecated
