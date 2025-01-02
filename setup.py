"""
Jexi - AI-powered Email Processing System

Components:
1. Jexi Core: Email processing and analysis
   - Gmail integration
   - Content analysis
   - Email organization

2. Marian: Catalog management system
   - Knowledge organization
   - Asset categorization
   - Library operations
"""

from setuptools import setup, find_packages

setup(
    name="jexi",
    version="1.0.0",
    description="AI-powered email processing and analysis system",
    long_description=__doc__,
    author="Eddie Kempe",
    packages=find_packages(),
    package_data={"": ["*.json", "*.yaml", "*.yml"]},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib',
        'anthropic',
        'sqlalchemy',
        'alembic',
        'pytest',
        'pytest-cov'
    ],
    python_requires=">=3.8",
)
