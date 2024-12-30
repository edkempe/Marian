# API to Model Mappings

Version: 1.0.0
Status: Authoritative

This document tracks the external APIs used by our models and how their responses map to our database schema.

## Gmail API

API Version: v1
Documentation: https://developers.google.com/gmail/api/reference/rest/v1/users.messages

### Email Model (users.messages endpoint)

API Field                      | Model Field       | Type          | Notes
------------------------------|-------------------|---------------|------------------------
id                           | id                | String(100)   | Message ID
payload.headers[subject]     | subject          | String(500)   | Email subject
snippet                      | body             | Text          | Email preview
payload.headers[from]        | sender           | String(200)   | Sender email
payload.headers[to]          | to_address       | String(200)   | Recipient email
payload.headers[date]        | received_date    | DateTime      | RFC 2822 format
labelIds                     | labels           | String(500)   | Comma-separated
threadId                     | thread_id        | String(100)   | Thread ID
payload.parts[].attachmentId | has_attachments  | Boolean       | True if any attachments
payload.headers[cc]          | cc_address       | Text          | CC recipients
payload.headers[bcc]         | bcc_address      | Text          | BCC recipients
raw response                 | full_api_response| Text          | Complete API response

### Gmail Labels (users.labels endpoint)

API Field | Model Field    | Type       | Notes
----------|---------------|------------|------------------
id        | id           | String(100) | Label ID
name      | name         | String(100) | Display name
type      | type         | String(50)  | "system" or "user"
-         | is_active    | Boolean     | Label visibility
-         | first_seen_at| DateTime    | First appearance
-         | last_seen_at | DateTime    | Last seen
-         | deleted_at   | DateTime    | Removal date

### Gmail User Profile (users.getProfile endpoint)

API Field     | Model Field     | Type       | Notes
--------------|----------------|------------|------------------
emailAddress  | email         | String(200) | User's email
messagesTotal | total_messages| Integer     | Message count
threadsTotal  | total_threads | Integer     | Thread count
historyId     | history_id    | String(20)  | Current history ID

### Gmail Drafts (users.drafts endpoint)

API Field    | Model Field    | Type       | Notes
-------------|---------------|------------|------------------
id           | draft_id      | String(100)| Draft ID
message.id   | message_id    | String(100)| Message ID if sent
message      | content       | Text       | Draft content
created      | created_date  | DateTime   | Creation time
updated      | updated_date  | DateTime   | Last modified

## Anthropic API (Claude)

API Version: v0.18.1
Documentation: https://docs.anthropic.com/claude/reference/

### Email Analysis (messages.create endpoint)

API Field                      | Model Field      | Type        | Notes
------------------------------|------------------|-------------|------------------
response.content[summary]      | summary         | Text        | Analysis summary
response.content[categories]   | category        | List[str]   | Email categories
response.content[priority_score]| priority_score  | Integer     | Priority (1-5)
response.content[action_needed] | action_needed   | Boolean     | Action required
response.content[action_type]  | action_type     | List[str]   | Types of actions
response.content[action_deadline]| action_deadline | DateTime    | Action due date
response.content[key_points]   | key_points      | List[str]   | Main points
response.content[people_mentioned]| people_mentioned| List[str]   | People in email
response.content[project]      | project         | String(100) | Project name
response.content[topic]        | topic           | String(100) | Email topic
response.content[sentiment]    | sentiment       | String(50)  | Email sentiment
response.content[confidence]   | confidence_score| Float       | Analysis confidence

### Semantic Search (messages.create endpoint)

API Field                      | Model Field      | Type        | Notes
------------------------------|------------------|-------------|------------------
response.content[matches]      | matches         | List[Dict]  | Matching items
response.content[scores]       | similarity_scores| List[Float] | Match scores (0-1)
response.content[reasoning]    | match_reasoning  | Text        | Match explanation
response.content[confidence]   | confidence_score| Float       | Overall confidence

### API Configuration

Parameter    | Value                  | Notes
-------------|------------------------|------------------
model        | claude-3-haiku-20240307| Current version
max_tokens   | 1000                  | Response limit
temperature  | 0                     | Deterministic

## Asset Catalog API

API Version: v1
Documentation: [Internal API Documentation]

### Asset Catalog Items

API Field | Model Field    | Type       | Notes
----------|---------------|------------|------------------
id        | id           | Integer    | Auto-incrementing
title     | title        | String(255)| Asset title
description| description | Text(2000) | Asset description
content   | content      | Text       | Asset content
source    | source       | String     | Source identifier
status    | status       | String     | Default: 'draft'
deleted   | deleted      | Boolean    | Soft delete flag
archivedAt| archived_date| Integer    | Unix timestamp
createdAt | created_date | Integer    | Unix timestamp
modifiedAt| modified_date| Integer    | Unix timestamp
metadata  | item_info    | JSON       | Additional metadata

### Asset Dependencies

API Field | Model Field    | Type       | Notes
----------|---------------|------------|------------------
sourceId  | source_id     | Integer    | Source asset ID
targetId  | target_id     | Integer    | Target asset ID
type      | dependency_type| String(50) | Type of dependency
metadata  | metadata      | Text       | Additional metadata

## Notes

1. All timestamps stored as Unix timestamps
2. Text fields have no practical length limit
3. String fields have explicit length limits
4. JSON responses are parsed and validated before storage
5. Default values match API defaults where applicable
6. Anthropic API responses are parsed from structured JSON in response content
