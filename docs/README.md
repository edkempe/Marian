# Marian Documentation

## Directory Structure

### Active Documentation
- `/docs`
  - `README.md` - This guide
  - `database_design.md` - Database design decisions and schema
  - `code_standards.md` - Coding standards and practices
  - `troubleshooting.md` - Common issues and solutions
  - `testing_guide.md` - Testing practices and guidelines

### Session Logs
- `/docs/sessions`
  - Current session logs
  - Session templates
  - Session README

### Archives
- `/docs/archive`
  - Archived documentation
  - Old versions
  - Superseded files
  - Naming: `{filename}_{YYYYMMDD}.md`

## Documentation Principles

1. **Single Source of Truth**
   - Code is primary documentation
   - Active docs explain "why" not "how"
   - Tests show usage patterns

2. **Necessary and Sufficient**
   - No duplicate information
   - Reference don't repeat
   - Archive don't delete

3. **Living Documentation**
   - Update as code changes
   - Archive old versions
   - Keep history in archive