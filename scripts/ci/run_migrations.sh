#!/bin/bash
set -e

# Script to run database migrations in CI environment
# Usage: ./scripts/ci/run_migrations.sh [--check]

# Set up environment
export PYTHONPATH="$PYTHONPATH:$(pwd)"
export ENV="test"

# Parse arguments
CHECK_ONLY=0
if [ "$1" = "--check" ]; then
    CHECK_ONLY=1
fi

# Function to handle errors
handle_error() {
    echo "Error: $1"
    exit 1
}

# Validate schema changes
echo "Validating schema changes..."
./scripts/manage_migrations.py validate || handle_error "Schema validation failed"

# Check for pending migrations
echo "Checking for pending migrations..."
PENDING=$(./scripts/manage_migrations.py pending)
HAS_PENDING=$?

if [ $CHECK_ONLY -eq 1 ]; then
    if [ $HAS_PENDING -eq 1 ]; then
        handle_error "Pending migrations found. Please apply migrations locally and commit them."
    else
        echo "No pending migrations found."
        exit 0
    fi
fi

# Apply migrations if we have any
if [ $HAS_PENDING -eq 1 ]; then
    echo "Applying migrations..."
    ./scripts/manage_migrations.py apply || handle_error "Failed to apply migrations"
    echo "Migrations applied successfully."
else
    echo "No migrations to apply."
fi

exit 0
