# Marian Reports Directory

**Version:** 1.0.0  
**Status:** Authoritative source for report locations and standards

## Overview

This directory contains generated reports and analysis outputs from various parts of the Marian system. These reports are automatically generated and should not be manually edited.

## Directory Structure

- `/testing/` - Test analysis reports and quality metrics
  - Documentation quality reports
  - Import analysis
  - Test coverage
  - Code duplication analysis
- `/analysis/` - Email analysis outputs (gitignored)
- `/metrics/` - System performance metrics (gitignored)

## Report Guidelines

1. **Report Generation**
   - Reports are automatically generated
   - Do not edit reports manually
   - Reports should be regenerated as needed

2. **Version Control**
   - Most reports are gitignored
   - Only README files and templates are tracked
   - Generated files should not be committed

3. **Viewing Reports**
   - HTML reports should be viewed in a browser
   - Markdown reports can be viewed in any text editor
   - Reports are self-contained with embedded styles

## Report Types

### Test Reports
- Documentation quality and versioning
- Import analysis (unused imports, style issues)
- File duplicates and similarities
- Test coverage metrics

### Analysis Reports
- Email processing statistics
- Label distribution analysis
- Content classification results

### Metric Reports
- System performance metrics
- API usage statistics
- Processing time analysis

## Version History
- 1.0.0: Initial documentation of report directory structure and standards
