# API to Model Mappings

**Version:** 1.0.0  
**Status:** Authoritative

> Documentation of external APIs and their mappings to our database models.

This document tracks the external APIs used by our models and how their responses map to our database schema.

## Gmail API

**API Version:** v1
**Documentation:** https://developers.google.com/gmail/api/reference/rest/v1/users.messages

### Email Model

Maps to the `emails` table. Source: `users.messages` endpoint.

| API Field | Model Field | Type | Notes |
|-----------|-------------|------|-------|
| id | id | String(100) | Message ID |
| payload.headers[subject] | subject | String(500) | Email subject |
| snippet | body | Text | Email preview |
| payload.headers[from] | sender | String(200) | Sender email |
| payload.headers[to] | to_address | String(200) | Recipient email |
| payload.headers[date] | received_date | DateTime | RFC 2822 format |
| labelIds | labels | String(500) | Comma-separated |
| threadId | thread_id | String(100) | Thread ID |
| payload.parts[].body.attachmentId | has_attachments | Boolean | True if any attachments |
| payload.headers[cc] | cc_address | Text | CC recipients |
| payload.headers[bcc] | bcc_address | Text | BCC recipients |
| raw response | full_api_response | Text | Complete API response |

### Gmail Labels

Maps to the `gmail_labels` table. Source: `users.labels` endpoint.

| API Field | Model Field | Type | Notes |
|-----------|-------------|------|-------|
| id | id | String(100) | Label ID |
| name | name | String(100) | Display name |
| type | type | String(50) | "system" or "user" |
| - | is_active | Boolean | Tracks label visibility |
| - | first_seen_at | DateTime | When label first appeared |
| - | last_seen_at | DateTime | Last time label was seen |
| - | deleted_at | DateTime | When label was removed |

## Asset Catalog API

**API Version:** v1
**Documentation:** [Internal API Documentation]

### Asset Catalog Items

Maps to the `asset_catalog_items` table.

| API Field | Model Field | Type | Notes |
|-----------|-------------|------|-------|
| id | id | Integer | Auto-incrementing |
| title | title | String(255) | Asset title |
| description | description | Text(2000) | Asset description |
| content | content | Text | Asset content |
| source | source | String | Source identifier |
| status | status | String | Default: 'draft' |
| deleted | deleted | Boolean | Soft delete flag |
| archivedAt | archived_date | Integer | Unix timestamp |
| createdAt | created_date | Integer | Unix timestamp |
| modifiedAt | modified_date | Integer | Unix timestamp |
| metadata | item_info | JSON | Additional metadata |

### Asset Dependencies

Maps to the `asset_dependencies` table.

| API Field | Model Field | Type | Notes |
|-----------|-------------|------|-------|
| sourceId | source_id | Integer | Source asset ID |
| targetId | target_id | Integer | Target asset ID |
| type | dependency_type | String(50) | Type of dependency |
| metadata | metadata | Text | Additional metadata |

## Notes

1. All timestamps are stored as Unix timestamps (seconds since epoch)
2. Text fields have no practical limit but should be kept reasonable
3. String fields have explicit length limits to match API constraints
4. JSON fields should be validated before storage
5. Default values should match API defaults where applicable
