# 13. Minimalist CI/CD Pipeline

Date: 2024-12-31

## Status

Proposed

## Revision History
1.0.0 (2024-12-31) @dev
- Initial version with GitHub Actions
- Added pre-commit hooks
- Added deployment script

## Context

As a solo developer with AI assistance, we need a CI/CD pipeline that:
1. Automates routine tasks
2. Maintains quality without overhead
3. Deploys reliably
4. Leverages AI capabilities

## Decision

We will use GitHub Actions for a minimal CI/CD pipeline:

### 1. CI Pipeline
Single workflow for testing and validation:

```yaml
# .github/workflows/ci.yml
name: Python CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install
    - name: Run linting
      run: poetry run pylint src/ tests/ models/ shared_lib/
    - name: Run tests
      run: poetry run pytest -v
```

### 2. Pre-commit Hooks
Local quality checks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: local
    hooks:
      - id: pylint
        name: pylint
        entry: poetry run pylint
        language: system
        types: [python]
        args: [src, tests, models, shared_lib]
```

### 3. Deployment
Simple deployment script:

```python
# scripts/deploy.py
"""Deployment script for Jexi.

Usage:
    python scripts/deploy.py [--env=prod]
"""
import subprocess
from pathlib import Path

def deploy(env: str = "prod"):
    """Deploy the application."""
    # 1. Run tests
    subprocess.run(["pytest"], check=True)
    
    # 2. Build application
    subprocess.run(["poetry", "build"], check=True)
    
    # 3. Deploy (example using rsync)
    subprocess.run([
        "rsync", "-avz",
        "--exclude=*.pyc",
        "--exclude=__pycache__",
        ".",
        f"user@server:/opt/jexi-{env}"
    ], check=True)
```

### 4. Environment Management
Use `.env` files with templates:

```bash
# .env.template
DATABASE_URL=postgresql://user:pass@localhost:5432/db
API_KEY=your_api_key_here
DEBUG=false
```

## Consequences

### Positive
1. Automated quality checks
2. Simple deployment process
3. Version controlled configuration
4. Easy to maintain alone

### Negative
1. Limited deployment options
2. No blue/green deployments
3. Basic monitoring only

### Mitigation
1. Use AI for deployment verification
2. Maintain deployment checklist
3. Add monitoring as needed

## References
- [GitHub Actions](https://docs.github.com/en/actions)
- [Pre-commit](https://pre-commit.com/)
- [Poetry](https://python-poetry.org/docs/)
