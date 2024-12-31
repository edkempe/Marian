"""File operation constants."""

# File Size Limits
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

# File Types
ALLOWED_EXTENSIONS = {
    "txt",
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "csv",
}

# File Paths
UPLOAD_FOLDER = "uploads"
TEMP_FOLDER = "temp"
BACKUP_FOLDER = "backup"
