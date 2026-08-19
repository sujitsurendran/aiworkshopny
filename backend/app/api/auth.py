"""
Authentication API endpoint matching LLD OpenAPI contract.
Implements POST /api/v1/auth/login with JWT token and user object response.
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.domain.models import Role, User, UserRole
from app.domain.schemas import LoginRequest, SessionResponse
from app.security.auth import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=SessionResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token with user information.

    Validates email and password, then returns SessionResponse with:
    - user_id: User ID as string
    - email: User email
    - full_name: User display name
    - roles: List of role names
    - access_token: JWT token with user_id claim and exp expiry
    - expires_at: Token expiration timestamp

    Args:
        request: Login credentials (email, password)
        db: Database session

    Returns:
        SessionResponse with JWT token and user information

    Raises:
        HTTPException: 401 Unauthorized if credentials invalid
    """
    # Fetch user by email
    user = db.query(User).filter(User.email == request.email).first()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password using bcrypt
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Get user roles with proper join
    user_roles = (
        db.query(Role)
        .join(Role.user_roles)
        .filter(UserRole.user_id == user.id)
        .all()
    )
    role_names = [role.name for role in user_roles]

    # Create JWT access token with user_id and exp claims
    access_token = create_access_token(
        user_id=user.id,
        roles=role_names
    )

    # Calculate expiry timestamp
    expires_at = datetime.utcnow() + timedelta(seconds=settings.token_expiry_seconds)

    return SessionResponse(
        user_id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        roles=role_names,
        access_token=access_token,
        expires_at=expires_at
    )
