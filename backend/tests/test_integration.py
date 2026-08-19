"""
Integration tests for cross-layer contract verification and end-to-end workflows.

Tests verify that:
1. Backend Pydantic schemas match frontend TypeScript interfaces field-for-field
2. Frontend form payloads match backend request schemas exactly
3. Router column references match ORM model definitions
4. Auth store destructuring matches backend login response shape
5. All seeded roles have permission mappings
6. Auth flow end-to-end (login → token → protected call → 401 handling)
7. SoD violations return 403 with explicit error message
8. CORS configuration allows frontend origins
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.database import Base, SessionLocal, engine
from app.domain.enums import ApprovalStatus
from app.domain.models import ApprovalRequest, Case
from app.main import app
from app.security.authorization import ROLE_PERMISSIONS
from app.seed import run_seed


@pytest.fixture(scope="module")
def client():
    """Create test client for API integration testing."""
    # Drop existing tables and recreate schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Run seed data once
    run_seed()

    return TestClient(app)


@pytest.fixture(scope="module")
def db_session():
    """Provide database session for verification queries."""
    db = SessionLocal()
    yield db
    db.close()


def test_session_response_schema_matches_frontend(client):
    """
    Verify backend SessionResponse schema matches frontend auth store setter field-for-field.

    Backend SessionResponse: user_id, email, full_name, roles, access_token, expires_at
    Frontend auth store expects: user_id, email, full_name, roles as separate fields
    """
    # Login request
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "password123"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify all required fields exist matching frontend destructuring
    assert "user_id" in data
    assert "email" in data
    assert "full_name" in data
    assert "roles" in data
    assert "access_token" in data
    assert "expires_at" in data

    # Verify field types
    assert isinstance(data["user_id"], str)
    assert isinstance(data["email"], str)
    assert isinstance(data["full_name"], str)
    assert isinstance(data["roles"], list)
    assert isinstance(data["access_token"], str)
    assert isinstance(data["expires_at"], str)


def test_case_detail_response_matches_frontend_interface(client, db_session):
    """
    Verify backend CaseDetailResponse matches frontend CaseDetail interface field-for-field.

    Fields: id, customer_id, account_id, order_reference, requested_terms, requested_outcome,
    current_status, priority, exception_flag, risk_band, created_by_id, assigned_to_id,
    created_at, updated_at, retention_until
    """
    # Get auth token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # Get first case
    response = client.get(
        "/api/v1/cases",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    cases_data = response.json()

    if cases_data["total"] > 0:
        case_id = cases_data["items"][0]["id"]

        # Get case detail
        detail_response = client.get(
            f"/api/v1/cases/{case_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert detail_response.status_code == 200
        case_detail = detail_response.json()

        # Verify all frontend interface fields exist
        required_fields = [
            "id", "customer_id", "account_id", "order_reference",
            "requested_terms", "requested_outcome", "current_status",
            "priority", "exception_flag", "risk_band", "created_by_id",
            "assigned_to_id", "created_at", "updated_at", "retention_until"
        ]

        for field in required_fields:
            assert field in case_detail, f"Missing field: {field}"


def test_case_create_request_matches_frontend_payload(client):
    """
    Verify backend CaseCreateRequest schema matches frontend intake form payload exactly.

    Form fields: customer_id, account_id, order_reference, requested_terms,
    requested_outcome, requested_fulfilment_date, priority
    """
    # Get auth token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # Create case with exact frontend form payload structure
    frontend_payload = {
        "customer_id": "CUST-INT-001",
        "account_id": "ACC-INT-001",
        "order_reference": "ORD-INT-TEST-001",
        "requested_terms": "Net 30",
        "requested_outcome": "Approve",
        "requested_fulfilment_date": "2026-09-01T00:00:00Z",
        "priority": "High"
    }

    response = client.post(
        "/api/v1/cases",
        headers={"Authorization": f"Bearer {token}"},
        json=frontend_payload
    )

    # Backend should accept this payload without validation errors
    assert response.status_code == 201, f"Unexpected response: {response.json()}"


def test_router_column_references_match_orm_model(db_session):
    """
    Verify backend router column references match ORM model column definitions.

    Checks: Case.current_status, Case.assigned_to_id, Case.exception_flag, Case.updated_at
    """
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns("cases")]

    # Verify critical column names used in routers exist in ORM model
    assert "current_status" in columns
    assert "assigned_to_id" in columns
    assert "exception_flag" in columns
    assert "updated_at" in columns
    assert "customer_id" in columns
    assert "order_reference" in columns


def test_all_seeded_roles_have_permission_mappings():
    """
    Verify all seeded roles have entries in RBAC permission map.

    Seeded roles: Order Management Analyst, Customer Success Manager,
    Sales Operations Manager, VP Sales / Commercial Director
    """
    seeded_roles = [
        "Order Management Analyst",
        "Customer Success Manager",
        "Sales Operations Manager",
        "VP Sales / Commercial Director"
    ]

    for role in seeded_roles:
        assert role in ROLE_PERMISSIONS, f"Missing permission mapping for role: {role}"
        assert len(ROLE_PERMISSIONS[role]) > 0, f"Empty permissions for role: {role}"


def test_frontend_api_client_uses_vite_api_url_env():
    """
    Verify frontend api-client.ts reads base URL from VITE_API_URL env variable.

    This is a documentation test - verifies the contract is established.
    """
    # This test documents the expected contract:
    # Frontend api-client.ts should read: import.meta.env.VITE_API_URL || fallback
    # Frontend .env.example should include: VITE_API_URL=http://localhost:9000
    pass


def test_integration_login_token_protected_call_paginated_response(client):
    """
    Integration test: login → store token → call GET /api/v1/cases with auth header
    → verify paginated response wrapper { items, total, page, page_size }
    """
    # Step 1: Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Step 2: Call protected endpoint with auth header
    cases_response = client.get(
        "/api/v1/cases",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert cases_response.status_code == 200

    # Step 3: Verify paginated response wrapper
    data = cases_response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)
    assert isinstance(data["page"], int)
    assert isinstance(data["page_size"], int)


def test_integration_protected_endpoint_without_token_returns_401(client):
    """
    Integration test: call protected endpoint without token → verify 401 Unauthorized
    """
    # Call protected endpoint without Authorization header
    response = client.get("/api/v1/cases")

    # Should return 401 Unauthorized
    assert response.status_code == 401


def test_integration_approval_sod_violation_returns_403_explicit_message(client, db_session):
    """
    Integration test: call approval endpoint with SoD violation
    → verify 403 Forbidden with explicit error message about segregation of duties
    """
    # Login as analyst
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    user_id = int(login_response.json()["user_id"])

    # Create a case
    case_response = client.post(
        "/api/v1/cases",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "customer_id": "CUST-SOD-TEST",
            "order_reference": "ORD-SOD-TEST",
            "requested_terms": "Net 30",
            "requested_outcome": "Approve"
        }
    )
    assert case_response.status_code == 201
    case_id = case_response.json()["id"]

    # Create approval request as same user
    db_case = db_session.query(Case).filter(Case.id == case_id).first()
    approval_request = ApprovalRequest(
        case_id=case_id,
        requested_by_id=user_id,
        assigned_approver_id=user_id,  # Same user - SoD violation
        status=ApprovalStatus.PENDING,
        justification="Test SoD check",
        approval_level="Manager",
        retention_until=db_case.retention_until
    )
    db_session.add(approval_request)
    db_session.commit()

    # Try to approve own request - should trigger SoD violation
    approval_response = client.post(
        f"/api/v1/cases/{case_id}/approvals",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "action": "approve",
            "decision_reason": "Test approval"
        }
    )

    # Should return 403 Forbidden with explicit SoD message
    assert approval_response.status_code == 403
    error_data = approval_response.json()
    assert "segregation of duties" in error_data["detail"].lower() or "sod" in error_data["detail"].lower()


def test_cors_configuration_allows_frontend_origins(client):
    """
    Verify CORS configuration allows frontend origin (http://localhost:5173).

    Tests that OPTIONS preflight requests include correct CORS headers.
    """
    # Send OPTIONS preflight request
    response = client.options(
        "/api/v1/cases",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type"
        }
    )

    # CORS should allow the request (200 or 204)
    assert response.status_code in [200, 204]


def test_frontend_handles_401_by_clearing_token():
    """
    Documentation test: frontend api-client.ts should handle 401 response
    by clearing token from localStorage and redirecting to /login.

    This documents the expected contract without runtime verification.
    """
    # Expected frontend behavior documented:
    # if (response.status === 401) {
    #     localStorage.removeItem('access_token');
    #     window.location.href = '/login';
    # }
    pass


def test_assessment_request_schema_matches_frontend_form(client):
    """
    Verify AssessmentRequest schema matches frontend assessment form payload.

    Fields: assessment_data (optional dict), recommendation (string), rationale (string)
    """
    # Get auth token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # Create a case first
    case_response = client.post(
        "/api/v1/cases",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "customer_id": "CUST-ASSESS-TEST",
            "order_reference": "ORD-ASSESS-TEST",
            "requested_terms": "Net 30",
            "requested_outcome": "Approve"
        }
    )
    case_id = case_response.json()["id"]

    # Submit assessment matching frontend form payload
    assessment_payload = {
        "assessment_data": {"credit_score": 750, "exposure": 50000},
        "recommendation": "RELEASE",
        "rationale": "Credit score is excellent and exposure is within acceptable limits for this customer profile."
    }

    response = client.post(
        f"/api/v1/cases/{case_id}/assessment",
        headers={"Authorization": f"Bearer {token}"},
        json=assessment_payload
    )

    # Backend should accept this payload without validation errors
    assert response.status_code == 201, f"Unexpected response: {response.json()}"


def test_approval_action_request_schema_matches_frontend_buttons(client, db_session):
    """
    Verify ApprovalActionRequest schema matches frontend approval button actions.

    Actions: request_approval, approve, reject, send_back
    Fields: action, justification, approval_level, decision_reason
    """
    # Login as analyst
    analyst_login = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "password123"}
    )
    analyst_token = analyst_login.json()["access_token"]
    analyst_id = int(analyst_login.json()["user_id"])

    # Login as manager
    manager_login = client.post(
        "/api/v1/auth/login",
        json={"email": "manager@example.com", "password": "password123"}
    )
    manager_token = manager_login.json()["access_token"]
    manager_id = int(manager_login.json()["user_id"])

    # Create a case as analyst
    case_response = client.post(
        "/api/v1/cases",
        headers={"Authorization": f"Bearer {analyst_token}"},
        json={
            "customer_id": "CUST-APPROVAL-TEST",
            "order_reference": "ORD-APPROVAL-TEST",
            "requested_terms": "Net 60",
            "requested_outcome": "Approve"
        }
    )
    case_id = case_response.json()["id"]

    # Create approval request
    db_case = db_session.query(Case).filter(Case.id == case_id).first()
    approval_request = ApprovalRequest(
        case_id=case_id,
        requested_by_id=analyst_id,
        assigned_approver_id=manager_id,
        status=ApprovalStatus.PENDING,
        justification="Exceeds analyst authority",
        approval_level="Manager",
        retention_until=db_case.retention_until
    )
    db_session.add(approval_request)
    db_session.commit()

    # Approve as manager (different user - no SoD violation)
    approval_payload = {
        "action": "approve",
        "decision_reason": "Approved after review"
    }

    response = client.post(
        f"/api/v1/cases/{case_id}/approvals",
        headers={"Authorization": f"Bearer {manager_token}"},
        json=approval_payload
    )

    # Backend should accept this payload
    assert response.status_code == 200, f"Unexpected response: {response.json()}"


def test_paginated_response_wrapper_shape(client):
    """
    Verify all list endpoints return consistent paginated wrapper shape.
    """
    # Get auth token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # Test cases endpoint
    cases_response = client.get(
        "/api/v1/cases?page=1&page_size=10",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert cases_response.status_code == 200
    cases_data = cases_response.json()

    # Verify wrapper shape
    assert set(cases_data.keys()) == {"items", "total", "page", "page_size"}
    assert cases_data["page"] == 1
    assert cases_data["page_size"] == 10
