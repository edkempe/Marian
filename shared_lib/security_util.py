"""Security utilities for email analysis system."""
import os
import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import base64

from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

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
    """Verify a password against its hash.
    
    Args:
        plain_password: The password to verify
        hashed_password: The hash to verify against
        
    Returns:
        bool: True if password matches hash, False otherwise
        
    Raises:
        ValueError: If inputs are invalid (empty/None)
        RuntimeError: If verification fails due to system error
    """
    if not plain_password or not hashed_password:
        logger.error("Empty password or hash provided")
        raise ValueError("Password and hash must not be empty")
        
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError as e:
        # Invalid hash format
        logger.error(f"Invalid password hash format: {str(e)}")
        raise ValueError(f"Invalid password hash format: {str(e)}")
    except Exception as e:
        # System-level errors (memory, etc)
        logger.error(f"System error during password verification: {str(e)}")
        raise RuntimeError(f"Password verification failed: {str(e)}")

def get_password_hash(password: str) -> str:
    """Generate password hash.
    
    Args:
        password: The password to hash
        
    Returns:
        str: The hashed password
        
    Raises:
        ValueError: If password is empty/None
        RuntimeError: If hashing fails due to system error
    """
    if not password:
        logger.error("Empty password provided")
        raise ValueError("Password must not be empty")
        
    try:
        return pwd_context.hash(password)
    except ValueError as e:
        # Invalid password format
        logger.error(f"Invalid password format: {str(e)}")
        raise ValueError(f"Invalid password format: {str(e)}")
    except Exception as e:
        # System-level errors (memory, etc)
        logger.error(f"System error during password hashing: {str(e)}")
        raise RuntimeError(f"Password hashing failed: {str(e)}")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta. If not provided,
                      defaults to ACCESS_TOKEN_EXPIRE_MINUTES
                      
    Returns:
        str: The encoded JWT token
        
    Raises:
        ValueError: If data is empty/None or SECRET_KEY not configured
        RuntimeError: If token creation fails due to system error
    """
    if not data:
        logger.error("Empty data provided for token creation")
        raise ValueError("Token data must not be empty")
        
    if not SECRET_KEY:
        logger.error("JWT_SECRET_KEY environment variable not set")
        raise ValueError("JWT_SECRET_KEY must be configured")
        
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except TypeError as e:
        # Data contains non-serializable types
        logger.error(f"Invalid token data format: {str(e)}")
        raise ValueError(f"Token data must be JSON serializable: {str(e)}")
    except Exception as e:
        # System-level errors
        logger.error(f"System error during token creation: {str(e)}")
        raise RuntimeError(f"Token creation failed: {str(e)}")

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        Optional[Dict[str, Any]]: The decoded token payload if valid,
                                 None if token is expired or invalid
        
    Raises:
        ValueError: If token is empty/None or SECRET_KEY not configured
        RuntimeError: If verification fails due to system error
    """
    if not token:
        logger.error("Empty token provided")
        raise ValueError("Token must not be empty")
        
    if not SECRET_KEY:
        logger.error("JWT_SECRET_KEY environment variable not set")
        raise ValueError("JWT_SECRET_KEY must be configured")
        
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        # Token is expired or invalid
        logger.warning(f"Invalid or expired token: {str(e)}")
        return None
    except Exception as e:
        # System-level errors
        logger.error(f"System error during token verification: {str(e)}")
        raise RuntimeError(f"Token verification failed: {str(e)}")

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data.
    
    Args:
        data: The data to encrypt
        
    Returns:
        str: The encrypted data as a base64-encoded string
        
    Raises:
        ValueError: If data is empty/None or encryption key not configured
        RuntimeError: If encryption fails due to system error
    """
    if not data:
        logger.error("Empty data provided for encryption")
        raise ValueError("Data must not be empty")
        
    if not encryption_key:
        logger.error("ENCRYPTION_KEY environment variable not set")
        raise ValueError("ENCRYPTION_KEY must be configured")
        
    try:
        return fernet.encrypt(data.encode()).decode()
    except TypeError as e:
        # Data encoding error
        logger.error(f"Data encoding error: {str(e)}")
        raise ValueError(f"Data must be string: {str(e)}")
    except Exception as e:
        # System-level errors
        logger.error(f"System error during encryption: {str(e)}")
        raise RuntimeError(f"Encryption failed: {str(e)}")

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data.
    
    Args:
        encrypted_data: The encrypted data as a base64-encoded string
        
    Returns:
        str: The decrypted data
        
    Raises:
        ValueError: If data is empty/None, malformed, or encryption key not configured
        RuntimeError: If decryption fails due to system error
    """
    if not encrypted_data:
        logger.error("Empty data provided for decryption")
        raise ValueError("Encrypted data must not be empty")
        
    if not encryption_key:
        logger.error("ENCRYPTION_KEY environment variable not set")
        raise ValueError("ENCRYPTION_KEY must be configured")
        
    try:
        return fernet.decrypt(encrypted_data.encode()).decode()
    except (TypeError, ValueError) as e:
        # Data encoding/format error
        logger.error(f"Invalid encrypted data format: {str(e)}")
        raise ValueError(f"Invalid encrypted data format: {str(e)}")
    except Exception as e:
        # System-level errors or wrong key
        logger.error(f"System error during decryption: {str(e)}")
        raise RuntimeError(f"Decryption failed: {str(e)}")

def sanitize_email_content(content: str) -> str:
    """Remove sensitive information from email content.
    
    Removes or masks potentially sensitive information like:
    - Credit card numbers
    - Social security numbers
    - API keys and tokens
    - Passwords
    
    Args:
        content: The email content to sanitize
        
    Returns:
        str: The sanitized content with sensitive info removed/masked
        
    Raises:
        ValueError: If content is empty/None
        RuntimeError: If sanitization fails due to system error
    """
    if not content:
        logger.error("Empty content provided for sanitization")
        raise ValueError("Content must not be empty")
        
    try:
        # Remove credit card numbers (basic 16-digit pattern)
        content = re.sub(r'\b\d{16}\b', '[CREDIT_CARD]', content)
        
        # Remove SSN (XXX-XX-XXXX pattern)
        content = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', content)
        
        # Remove API keys/tokens (common patterns)
        content = re.sub(r'\b[A-Za-z0-9_-]{32,}\b', '[API_KEY]', content)
        
        # Remove anything that looks like a password
        content = re.sub(r'\b(?i)password\s*[:=]\s*\S+', '[PASSWORD]', content)
        
        return content
    except re.error as e:
        # Regex pattern error
        logger.error(f"Invalid regex pattern: {str(e)}")
        raise RuntimeError(f"Sanitization pattern error: {str(e)}")
    except Exception as e:
        # System-level errors
        logger.error(f"System error during content sanitization: {str(e)}")
        raise RuntimeError(f"Content sanitization failed: {str(e)}")

def validate_api_key(api_key: str) -> bool:
    """Validate API key format and expiration.
    
    Checks if the API key:
    1. Has valid format (base64 string)
    2. Contains required segments
    3. Has not expired
    
    Args:
        api_key: The API key to validate
        
    Returns:
        bool: True if API key is valid, False otherwise
        
    Raises:
        ValueError: If api_key is empty/None
        RuntimeError: If validation fails due to system error
    """
    if not api_key:
        logger.error("Empty API key provided")
        raise ValueError("API key must not be empty")
        
    try:
        # Basic format validation (base64)
        if not re.match(r'^[A-Za-z0-9+/=_-]+$', api_key):
            logger.warning(f"Invalid API key format")
            return False
            
        # Check required segments (key should have 3 parts separated by dots)
        parts = api_key.split('.')
        if len(parts) != 3:
            logger.warning(f"Invalid API key structure")
            return False
            
        # Check expiration (assuming middle segment is base64 encoded expiry timestamp)
        try:
            expiry_data = base64.b64decode(parts[1] + '=' * (-len(parts[1]) % 4))
            expiry = datetime.fromtimestamp(float(expiry_data))
            if expiry < datetime.utcnow():
                logger.warning(f"Expired API key")
                return False
        except:
            logger.warning(f"Could not verify API key expiration")
            return False
            
        return True
    except Exception as e:
        # System-level errors
        logger.error(f"System error during API key validation: {str(e)}")
        raise RuntimeError(f"API key validation failed: {str(e)}")

def check_permissions(user_id: str, resource: str, action: str) -> bool:
    """Check if user has permission to perform action on resource.
    
    Args:
        user_id: The ID of the user
        resource: The resource being accessed (e.g., 'email', 'analysis')
        action: The action being performed (e.g., 'read', 'write')
        
    Returns:
        bool: True if user has permission, False otherwise
        
    Raises:
        ValueError: If any input is empty/None
        RuntimeError: If permission check fails due to system error
    """
    if not user_id or not resource or not action:
        logger.error(f"Missing required permission check parameters: user_id={user_id}, resource={resource}, action={action}")
        raise ValueError("All permission check parameters must be provided")
        
    try:
        # TODO: Implement proper permission checking against a permission store
        # For now, implement basic rules:
        
        # 1. System resources require admin role
        if resource.startswith('system.'):
            logger.info(f"Checking system resource access for user {user_id}")
            return _is_admin(user_id)
            
        # 2. Personal resources require ownership
        if resource.startswith('user.'):
            resource_user_id = resource.split('.')[1]
            logger.info(f"Checking personal resource access for user {user_id}")
            return user_id == resource_user_id
            
        # 3. Public resources allow read access
        if resource.startswith('public.'):
            logger.info(f"Checking public resource access for user {user_id}")
            return action == 'read'
            
        # 4. Default deny all other access
        logger.warning(f"Access denied for user {user_id} to {resource} for action {action}")
        return False
        
    except Exception as e:
        # System-level errors
        logger.error(f"System error during permission check: {str(e)}")
        raise RuntimeError(f"Permission check failed: {str(e)}")
        
def _is_admin(user_id: str) -> bool:
    """Check if user has admin role."""
    # TODO: Implement proper role checking
    return user_id in ['admin', 'system']
