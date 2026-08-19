"""
Authentication services: JWT creation/validation and bcrypt password hashing.
Uses PyJWT (NOT python-jose) and bcrypt (NOT passlib).
"""
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt

from app.config import settings


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password string
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored bcrypt hash

    Returns:
        True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: int, roles: list[str], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with user_id claim and expiry.

    Args:
        user_id: User ID to embed in token
        roles: List of role names for the user
        expires_delta: Optional custom expiry duration

    Returns:
        JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(seconds=settings.token_expiry_seconds)

    expire = datetime.utcnow() + expires_delta

    payload = {
        "user_id": str(user_id),  # Convert to string for JWT
        "roles": roles,
        "exp": expire,
        "iat": datetime.utcnow()
    }

    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    return token


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dict if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
