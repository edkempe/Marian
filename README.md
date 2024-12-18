# Marian Project

## Overview
An AI-powered email analysis and management system that uses advanced language models to process, categorize, and extract insights from emails.

## File Naming Convention
- Processors: `processor_<type>.py` (e.g., processor_email.py)
- Utilities: `util_<purpose>.py` (e.g., util_db.py)
- Schemas: `schema_<type>.sql` (e.g., schema_prompt.sql)
- Tests: `test_<module>.py` (e.g., test_processor_email.py)

## Prompt Naming Convention
Format: `<domain>.<task>.<subtask>.v<version>`
Example: `email.analysis.triage.v1.0.0`

## Setup Instructions
1. Clone the repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
