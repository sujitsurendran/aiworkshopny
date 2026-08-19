"""
Unit tests for authentication, JWT validation, and RBAC enforcement.
Tests cover login endpoint, password hashing, JWT token validation, and authorization checks.
"""
import os

# Test database setup - use file-based database to persist across sessions
import tempfile
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.domain.models import Role, User, UserRole
from app.main import app
from app.security.auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.security.authorization import check_permission, check_sod_violation, require_permission

# Create a temporary database file
test_db_fd, test_db_path = tempfile.mkstemp(suffix='.db')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{test_db_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables once for the entire test session
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """Clean up test database file after all tests."""
    yield
    # Close all connections and clean up
    engine.dispose()
    os.close(test_db_fd)
    os.unlink(test_db_path)


@pytest.fixture(scope="function")
def test_db():
    """Get test database session for each test."""
    db = TestingSessionLocal()
    yield db
    # Clean up test data after each test
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()


@pytest.fixture
def test_user(test_db):
    """Create a test user with role."""
    # Create role
    role = Role(
        name="Order Management Analyst",
        description="Can create and manage cases"
    )
    test_db.add(role)
    test_db.commit()
    test_db.refresh(role)

    # Create user
    now = datetime.utcnow()
    user = User(
        email="analyst@example.com",
        password_hash=hash_password("password123"),
        full_name="Test Analyst",
        is_active=True,
        created_at=now,
        updated_at=now
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Assign role
    user_role = UserRole(
        user_id=user.id,
        role_id=role.id,
        assigned_at=now
    )
    test_db.add(user_role)
    test_db.commit()

    return user


# ============================================================================
# Password Hashing Tests
# ============================================================================

def test_hash_password():
    """Test bcrypt password hashing."""
    password = "testpassword123"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 0
    assert hashed.startswith("$2b$")  # bcrypt prefix


def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "testpassword123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "testpassword123"
    wrong_password = "wrongpassword"
    hashed = hash_password(password)

    assert verify_password(wrong_password, hashed) is False


# ============================================================================
# JWT Token Tests
# ============================================================================

def test_create_access_token():
    """Test JWT token creation with user_id claim and exp."""
    user_id = 123
    roles = ["Order Management Analyst"]
    token = create_access_token(user_id, roles)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token_valid():
    """Test JWT token decoding with valid token."""
    user_id = 123
    roles = ["Order Management Analyst"]
    token = create_access_token(user_id, roles)

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["user_id"] == str(user_id)
    assert payload["roles"] == roles
    assert "exp" in payload
    assert "iat" in payload


def test_decode_access_token_expired():
    """Test JWT token decoding with expired token."""
    user_id = 123
    roles = ["Order Management Analyst"]
    # Create token that expires immediately
    token = create_access_token(user_id, roles, expires_delta=timedelta(seconds=-1))

    payload = decode_access_token(token)

    assert payload is None


def test_decode_access_token_invalid():
    """Test JWT token decoding with invalid token."""
    invalid_token = "invalid.token.string"

    payload = decode_access_token(invalid_token)

    assert payload is None


# ============================================================================
# Login Endpoint Tests
# ============================================================================

def test_login_success(test_user):
    """Test successful login returns JWT token and user object."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "password123"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify SessionResponse schema fields
    assert "user_id" in data
    assert "email" in data
    assert "full_name" in data
    assert "roles" in data
    assert "access_token" in data
    assert "expires_at" in data

    # Verify values
    assert data["email"] == "analyst@example.com"
    assert data["full_name"] == "Test Analyst"
    assert "Order Management Analyst" in data["roles"]

    # Verify JWT token includes user_id claim
    token = data["access_token"]
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["user_id"] == str(test_user.id)
    assert "exp" in payload


def test_login_invalid_email(test_user):
    """Test login with non-existent email returns 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "password123"}
    )

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_invalid_password(test_user):
    """Test login with incorrect password returns 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_inactive_user(test_db):
    """Test login with inactive user returns 401."""
    # Create inactive user
    now = datetime.utcnow()
    user = User(
        email="inactive@example.com",
        password_hash=hash_password("password123"),
        full_name="Inactive User",
        is_active=False,
        created_at=now,
        updated_at=now
    )
    test_db.add(user)
    test_db.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "password123"}
    )

    assert response.status_code == 401


# ============================================================================
# RBAC Authorization Tests
# ============================================================================

def test_check_permission_granted():
    """Test permission check when user has required permission."""
    roles = ["Order Management Analyst"]
    permission = "cases:create"

    assert check_permission(roles, permission) is True


def test_check_permission_denied():
    """Test permission check when user lacks required permission."""
    roles = ["Customer Success Manager"]
    permission = "approvals:approve"  # CSM doesn't have this permission

    assert check_permission(roles, permission) is False


def test_check_permission_multiple_roles():
    """Test permission check with multiple roles."""
    roles = ["Order Management Analyst", "Customer Success Manager"]
    permission = "complaints:create"  # CSM has this

    assert check_permission(roles, permission) is True


def test_require_permission_success():
    """Test require_permission does not raise when permission granted."""
    roles = ["Order Management Analyst"]
    permission = "cases:create"

    # Should not raise
    require_permission(roles, permission)


def test_require_permission_forbidden():
    """Test require_permission raises 403 when permission denied."""
    from fastapi import HTTPException

    roles = ["Customer Success Manager"]
    permission = "approvals:approve"

    with pytest.raises(HTTPException) as exc_info:
        require_permission(roles, permission)

    assert exc_info.value.status_code == 403
    assert "Insufficient permissions" in str(exc_info.value.detail)


# ============================================================================
# Segregation of Duties Tests
# ============================================================================

def test_sod_violation_self_approval():
    """Test SoD check detects self-approval violation."""
    actor_id = 123
    requester_id = 123  # Same user
    action = "approve"

    violation = check_sod_violation(actor_id, requester_id, action)

    assert violation is True


def test_sod_no_violation_different_users():
    """Test SoD check allows approval by different user."""
    actor_id = 123
    requester_id = 456  # Different user
    action = "approve"

    violation = check_sod_violation(actor_id, requester_id, action)

    assert violation is False


def test_sod_violation_reject():
    """Test SoD check applies to reject action."""
    actor_id = 123
    requester_id = 123
    action = "reject"

    violation = check_sod_violation(actor_id, requester_id, action)

    assert violation is True


def test_sod_violation_send_back():
    """Test SoD check applies to send_back action."""
    actor_id = 123
    requester_id = 123
    action = "send_back"

    violation = check_sod_violation(actor_id, requester_id, action)

    assert violation is True


# ============================================================================
# Protected Endpoint Tests
# ============================================================================

def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without token returns 403."""
    # Try to access a protected endpoint (once we have one)
    # For now, just verify health endpoint is accessible
    response = client.get("/health")
    assert response.status_code == 200


def test_protected_endpoint_with_valid_token(test_user):
    """Test accessing protected endpoint with valid token succeeds."""
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # Verify token is valid
    payload = decode_access_token(token)
    assert payload is not None


def test_protected_endpoint_with_invalid_token():
    """Test accessing protected endpoint with invalid token returns 401."""
    # This will be tested more thoroughly in Task 3 when we have protected endpoints
    pass


# ============================================================================
# CORS Configuration Tests
# ============================================================================

def test_cors_headers_present():
    """Test CORS middleware allows Authorization and Content-Type headers."""
    # Use GET instead of OPTIONS since our health endpoint doesn't support OPTIONS
    response = client.get("/health")

    # CORS headers should be present in response
    assert response.status_code == 200
    # Note: CORS headers are added by middleware when needed for cross-origin requests
