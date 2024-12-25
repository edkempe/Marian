#!/bin/bash

# Set variables
DB_NAME="email_store.db"
BACKUP_DIR="backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="email_db_backup_$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform backup
echo "Starting backup of $DB_NAME..."
sqlite3 "$DB_NAME" .dump > "$BACKUP_DIR/$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_DIR/$BACKUP_FILE"
else
    echo "Backup failed!"
    exit 1
fi

# Compress the backup file
gzip "$BACKUP_DIR/$BACKUP_FILE"
echo "Backup compressed: $BACKUP_DIR/$BACKUP_FILE.gz"

# Optional: Remove backups older than 30 days
find "$BACKUP_DIR" -name "email_db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup process completed."
