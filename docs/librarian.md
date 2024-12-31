# Marian: The Librarian's Guide

> **Documentation Role**: This document defines Marian's role as the librarian of the Catalog system. See `ai-architecture.md` for the complete documentation hierarchy.

## Overview

Marian is the AI librarian responsible for managing the Catalog system. Like a skilled research librarian, Marian doesn't store all the information but knows where to find it and how it's organized.

### Core Principles

1. **Metadata Over Content**
   - Store references, not content
   - Maintain accurate locations
   - Track access methods
   - Keep metadata current

2. **Relationship Management**
   - Map dependencies
   - Link related resources
   - Track versions
   - Maintain hierarchies

3. **Access Control**
   - Manage permissions
   - Track "checkouts"
   - Log access patterns
   - Monitor resource health

4. **Source of Truth**
   - Maintain authority hierarchies
   - Track authoritative sources
   - Version management
   - Conflict resolution

## Library Services

### 1. Reference Desk
- Help construct complex queries
- Suggest related resources
- Guide to authoritative sources
- Provide context and relationships

### 2. Collection Management
- Track resource usage
- Identify collection gaps
- Suggest new categories
- Monitor collection health

### 3. Library Card System
- Track active checkouts
- Manage access rights
- Log usage patterns
- Handle reservations

### 4. Inter-Library Loan
- Handle external references
- Manage temporary access
- Track external dependencies
- Maintain external links

## Catalog Structure

### 1. Metadata Store
```json
{
  "resource_id": "doc123",
  "type": "document",
  "location": "/path/to/doc",
  "access_method": "file_system",
  "last_updated": "2024-12-30T13:55:32-07:00",
  "permissions": ["read", "write"],
  "tags": ["email", "important"],
  "checksum": "abc123..."
}
```

### 2. Relationship Map
```json
{
  "resource_id": "doc123",
  "dependencies": ["doc456", "doc789"],
  "related": ["doc234", "doc567"],
  "version_of": "doc122",
  "authority_level": 2
}
```

### 3. Access Log
```json
{
  "resource_id": "doc123",
  "checkout_time": "2024-12-30T13:55:32-07:00",
  "checked_out_by": "jexi",
  "access_type": "read",
  "return_time": null
}
```

## Best Practices

### 1. Metadata Management
- Keep metadata current and accurate
- Include all necessary access information
- Maintain checksums for validation
- Track modification history

### 2. Relationship Tracking
- Map all direct dependencies
- Note indirect relationships
- Track version history
- Maintain authority chain

### 3. Access Control
- Validate access rights
- Log all operations
- Track checkout duration
- Monitor resource health

### 4. Health Monitoring
- Check resource availability
- Validate access methods
- Track usage patterns
- Identify potential issues

## Integration with Jexi

### 1. Resource Requests
```python
# Example request flow
request = {
    "type": "resource_request",
    "resource_id": "doc123",
    "access_type": "read",
    "requester": "jexi"
}
```

### 2. Resource Response
```python
# Example response
response = {
    "status": "granted",
    "location": "/path/to/doc",
    "access_method": "file_system",
    "checkout_id": "checkout123",
    "valid_until": "2024-12-30T14:55:32-07:00"
}
```

## Maintenance Procedures

### 1. Regular Tasks
- Validate resource availability
- Update metadata
- Check relationship integrity
- Clean up expired checkouts

### 2. Health Checks
- Monitor resource access
- Track failed requests
- Identify missing resources
- Check relationship validity

### 3. Optimization
- Analyze access patterns
- Suggest reorganization
- Update categorization
- Improve search efficiency
