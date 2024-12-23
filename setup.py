from setuptools import setup, find_packages

setup(
    name="marian",
    version="0.1",
    packages=find_packages(include=['*']),
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
