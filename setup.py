"""
Marian Email Analysis System - AI-powered email analysis and organization system
"""

from setuptools import setup, find_packages

setup(
    name="marian",
    version="1.0.0",
    description="AI-powered email analysis and organization system",
    author="Eddie Kempe",
    packages=find_packages(exclude=['tests*', 'archive*']),
    package_data={'': ['*.json', '*.yaml', '*.yml']},
    include_package_data=True,
    install_requires=[
        "sqlalchemy",
        "alembic",
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
    ],
    python_requires='>=3.8',
)
