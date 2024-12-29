# Marian Prototypes Backlog

This file tracks the status and plans for prototype code and experimental features.

## Active Prototypes

### proto_gmail_operations.py
- Status: Under Review
- Purpose: Gmail API operations testing
- Features:
  - Email composition and sending
  - Draft management
  - Label operations
- Next Steps:
  - Move successful operations to main app
  - Document useful patterns

### proto_google_keep.py
- Status: Active
- Purpose: Google Keep integration testing
- Features:
  - Note creation and retrieval
  - Label management
  - Content synchronization
- Next Steps:
  - Complete basic integration
  - Test with real Keep data

### proto_inspect_prompts.py
- Status: Active
- Purpose: Prompt performance monitoring and inspection
- Features:
  - Tabulated overview of prompts
  - Version history tracking
  - Usage statistics
- Next Steps:
  - Update to work with new prompt storage system
  - Add export/import functionality
  - Integrate with logging system

### proto_prompt_manager.py
- Status: Under Review
- Purpose: Prompt management system testing
- Features:
  - Version tracking
  - Performance monitoring
  - A/B testing framework
- Next Steps:
  - Evaluate for production use
  - Document successful patterns

### proto_read_gmail.py
- Status: Under Review
- Purpose: Gmail reading functionality testing
- Features:
  - Basic email retrieval
  - Content parsing
  - Metadata extraction
- Next Steps:
  - Compare with current implementation
  - Archive if redundant

## Future Features from Prototypes

### Prompt Version Management
- Source: proto_prompt_manager.py
- Features needed:
  - Version tracking schema
  - Management system
  - UI for version control
  - A/B testing framework
  - Performance metrics

### Gmail Operations Integration
- Source: proto_gmail_operations.py
- Features to add:
  - Email composition and sending
  - Draft management
  - Label operations
  - Batch processing

### Google Keep Integration
- Source: proto_google_keep.py
- Features planned:
  - Note synchronization
  - Label management
  - Content organization
  - Search integration

## Implementation Notes

### Email Processing Prototype
**Status**: Planning
**Priority**: High
**Workstream**: Email Processing
**Description**: Implement a working prototype for email retrieval and processing workflow.

#### Technical Details
1. Email Retrieval
   - Test Gmail API connection
   - Implement basic email fetching
   - Add metadata extraction
   - Test with sample data

2. Processing Pipeline
   - Design workflow stages
   - Add error handling
   - Implement retry logic
   - Test end-to-end flow

#### Success Criteria
- Emails successfully retrieved
- Basic processing works
- Error handling in place
- Documentation complete
