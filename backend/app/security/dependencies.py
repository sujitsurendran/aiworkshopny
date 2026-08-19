"""
FastAPI dependency injection helpers for authentication and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.models import Role, User
from app.security.auth import decode_access_token

# HTTP Bearer token security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate current user from JWT bearer token.

    Args:
        credentials: HTTP Authorization header with Bearer token
        db: Database session

    Returns:
        User object if authentication successful

    Raises:
        HTTPException: 401 Unauthorized if token invalid or user not found
    """
    token = credentials.credentials

    # Decode and validate JWT
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from token
    user_id_str = payload.get("user_id")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[str]:
    """
    Get role names for current authenticated user.

    Args:
        current_user: Current user from JWT token
        db: Database session

    Returns:
        List of role names assigned to the user
    """
    roles = (
        db.query(Role)
        .join(User.user_roles)
        .filter(User.id == current_user.id)
        .all()
    )

    return [role.name for role in roles]


def require_auth(current_user: User = Depends(get_current_user)) -> User:
    """
    Require authentication without specific permission check.

    Args:
        current_user: Current user from JWT token

    Returns:
        User object if authenticated
    """
    return current_user
