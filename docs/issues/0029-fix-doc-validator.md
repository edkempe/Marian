# Issue 0029: Fix Documentation Validator Setup

## Status
Open (2025-01-02)

## Type
Bug

## Priority
High

## Description
The documentation validator pre-commit hook is broken after removing the `tools` directory. The validator was previously located at `tools/doc_validator.py` but was removed during the database consolidation cleanup.

## Impact
- Pre-commit hooks fail when trying to validate documentation
- Documentation changes require `--no-verify` flag to commit
- Reduced documentation quality assurance

## Required Changes
1. Move doc validator to appropriate location:
   - Create `scripts/validation/` directory
   - Move doc validator and standards to new location
   - Update pre-commit configuration

2. Update validator configuration:
   ```yaml
   - repo: local
     hooks:
       - id: doc-validator
         name: Documentation Validator
         entry: python scripts/validation/doc_validator.py
         language: system
         types: [markdown]
   ```

3. Restore validator functionality:
   - Copy validator code from git history
   - Update imports and paths
   - Add tests for validator

4. Update documentation:
   - Update development setup guide
   - Document new validator location
   - Add validator usage instructions

## Dependencies
- Pre-commit hook configuration
- Documentation standards
- Python validation tools

## Acceptance Criteria
1. Pre-commit hooks run successfully
2. Documentation validator works as before
3. All documentation follows standards
4. Clear setup instructions exist

## Related
- ADR 0007: External Tool Integration
- Issue 0028: Database Consolidation

## Notes
- Consider improving validator with new features
- May need to update other pre-commit hooks
- Document any changes to validation rules
