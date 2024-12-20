"""Security utilities for email analysis system."""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Data encryption
encryption_key = os.getenv("ENCRYPTION_KEY", "").encode()
if not encryption_key:
    encryption_key = Fernet.generate_key()
fernet = Fernet(encryption_key)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data."""
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    return fernet.decrypt(encrypted_data.encode()).decode()

def sanitize_email_content(content: str) -> str:
    """Remove sensitive information from email content."""
    # TODO: Implement content sanitization
    # This could include:
    # - Removing credit card numbers
    # - Removing social security numbers
    # - Removing API keys and passwords
    return content
