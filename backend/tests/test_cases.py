"""
Unit tests for case management endpoints and services.
Tests case CRUD, assessment submission, workflow rules, and audit logging.
"""
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.domain.enums import CaseStatus, OutcomeType
from app.domain.models import (
    Case,
    Role,
    User,
    UserRole,
)
from app.main import app
from app.security.auth import create_access_token, hash_password

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_cases.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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


@pytest.fixture(scope="function")
def db_session():
    """Create fresh database session for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session):
    """Create test user with analyst role."""
    role = Role(name="Order Management Analyst", description="Test analyst role")
    db_session.add(role)
    db_session.commit()

    user = User(
        email="analyst@example.com",
        password_hash=hash_password("password123"),
        full_name="Test Analyst",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    db_session.commit()

    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authorization headers with JWT token."""
    token = create_access_token(user_id=test_user.id, roles=["Order Management Analyst"])
    return {"Authorization": f"Bearer {token}"}


class TestCaseEndpoints:
    """Test case management API endpoints."""

    def test_create_case_success(self, db_session, auth_headers):
        """Test POST /api/v1/cases creates case successfully."""
        payload = {
            "customer_id": "CUST001",
            "order_reference": "ORD001",
            "requested_terms": "Net 30",
            "requested_outcome": "RELEASE",
            "requested_fulfilment_date": "2026-09-01T00:00:00Z",
            "priority": "High"
        }

        response = client.post("/api/v1/cases/", json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == "CUST001"
        assert data["order_reference"] == "ORD001"
        assert data["current_status"] == "New"
        assert data["priority"] == "High"

    def test_create_case_missing_required_fields(self, db_session, auth_headers):
        """Test POST /api/v1/cases returns 400 when required fields missing."""
        payload = {
            "requested_terms": "Net 30"
        }

        response = client.post("/api/v1/cases/", json=payload, headers=auth_headers)
        assert response.status_code == 422  # Pydantic validation

    def test_list_cases_paginated(self, db_session, test_user, auth_headers):
        """Test GET /api/v1/cases returns paginated wrapper."""
        # Create test cases
        for i in range(5):
            case = Case(
                customer_id=f"CUST{i:03d}",
                order_reference=f"ORD{i:03d}",
                current_status=CaseStatus.NEW,
                created_by_id=test_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                retention_until=datetime.utcnow() + timedelta(days=365 * 7)
            )
            db_session.add(case)
        db_session.commit()

        response = client.get("/api/v1/cases/?page=1&page_size=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert data["total"] == 5
        assert len(data["items"]) == 3
        assert data["page"] == 1
        assert data["page_size"] == 3

    def test_list_cases_with_filters(self, db_session, test_user, auth_headers):
        """Test GET /api/v1/cases applies filters correctly."""
        case1 = Case(
            customer_id="CUST001",
            order_reference="ORD001",
            current_status=CaseStatus.NEW,
            exception_flag=False,
            created_by_id=test_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            retention_until=datetime.utcnow() + timedelta(days=365 * 7)
        )
        case2 = Case(
            customer_id="CUST002",
            order_reference="ORD002",
            current_status=CaseStatus.IN_REVIEW,
            exception_flag=True,
            created_by_id=test_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            retention_until=datetime.utcnow() + timedelta(days=365 * 7)
        )
        db_session.add_all([case1, case2])
        db_session.commit()

        response = client.get("/api/v1/cases/?exception_flag=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["exception_flag"] is True

    def test_get_case_detail_success(self, db_session, test_user, auth_headers):
        """Test GET /api/v1/cases/{caseId} returns full case detail."""
        case = Case(
            customer_id="CUST001",
            order_reference="ORD001",
            current_status=CaseStatus.NEW,
            priority="Medium",
            created_by_id=test_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            retention_until=datetime.utcnow() + timedelta(days=365 * 7)
        )
        db_session.add(case)
        db_session.commit()
        db_session.refresh(case)

        response = client.get(f"/api/v1/cases/{case.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == case.id
        assert data["customer_id"] == "CUST001"
        assert data["order_reference"] == "ORD001"
        assert "retention_until" in data

    def test_get_case_detail_not_found(self, db_session, auth_headers):
        """Test GET /api/v1/cases/{caseId} returns 404 for non-existent case."""
        response = client.get("/api/v1/cases/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_update_case_success(self, db_session, test_user, auth_headers):
        """Test PATCH /api/v1/cases/{caseId} updates case fields."""
        case = Case(
            customer_id="CUST001",
            order_reference="ORD001",
            current_status=CaseStatus.NEW,
            priority="Medium",
            exception_flag=False,
            created_by_id=test_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            retention_until=datetime.utcnow() + timedelta(days=365 * 7)
        )
        db_session.add(case)
        db_session.commit()
        db_session.refresh(case)

        payload = {
            "priority": "High",
            "exception_flag": True
        }

        response = client.patch(f"/api/v1/cases/{case.id}", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "High"
        assert data["exception_flag"] is True

    def test_submit_assessment_success(self, db_session, test_user, auth_headers):
        """Test POST /api/v1/cases/{caseId}/assessment submits recommendation."""
        case = Case(
            customer_id="CUST001",
            order_reference="ORD001",
            current_status=CaseStatus.IN_REVIEW,
            created_by_id=test_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            retention_until=datetime.utcnow() + timedelta(days=365 * 7)
        )
        db_session.add(case)
        db_session.commit()
        db_session.refresh(case)

        payload = {
            "recommendation": "Release",
            "rationale": "Customer has good credit history and low risk profile"
        }

        response = client.post(f"/api/v1/cases/{case.id}/assessment", json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["recommendation"] == "Release"
        assert data["case_id"] == case.id
        assert "assessed_at" in data


class TestWorkflowRulesEngine:
    """Test workflow rules engine logic."""

    def test_evaluate_submission_with_sod_violation(self, db_session, test_user):
        """Test WorkflowRulesEngine.evaluateSubmission returns sod_violation=True when actor == requester."""
        from app.services.workflow_rules_engine import WorkflowRulesEngine

        case = Case(
            customer_id="CUST001",
            order_reference="ORD001",
            current_status=CaseStatus.IN_REVIEW,
            exception_flag=False,
            created_by_id=test_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            retention_until=datetime.utcnow() + timedelta(days=365 * 7)
        )
        db_session.add(case)
        db_session.commit()

        engine = WorkflowRulesEngine(db_session)
        result = engine.evaluate_submission(
            case=case,
            assessment_recommendation=OutcomeType.RELEASE,
            actor_role="Order Management Analyst",
            actor_id=test_user.id,
            requester_id=test_user.id  # Same as actor
        )

        assert result.sod_violation is True
        assert not result.eligible
        assert "SoD violation" in str(result.reasons)

    def test_evaluate_submission_no_sod_violation(self, db_session, test_user):
        """Test WorkflowRulesEngine.evaluateSubmission returns sod_violation=False when actor != requester."""
        from app.services.workflow_rules_engine import WorkflowRulesEngine

        # Create another user
        other_user = User(
            email="manager@example.com",
            password_hash=hash_password("password123"),
            full_name="Test Manager",
            is_active=True
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        case = Case(
            customer_id="CUST001",
            order_reference="ORD001",
            current_status=CaseStatus.IN_REVIEW,
            exception_flag=False,
            created_by_id=test_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            retention_until=datetime.utcnow() + timedelta(days=365 * 7)
        )
        db_session.add(case)
        db_session.commit()

        engine = WorkflowRulesEngine(db_session)
        result = engine.evaluate_submission(
            case=case,
            assessment_recommendation=OutcomeType.RELEASE,
            actor_role="Sales Operations Manager",
            actor_id=other_user.id,
            requester_id=test_user.id  # Different from actor
        )

        assert result.sod_violation is False

    def test_evaluate_submission_exception_flag_requires_escalation(self, db_session, test_user):
        """Test exception_flag=true requires manager review."""
        from app.services.workflow_rules_engine import WorkflowRulesEngine

        case = Case(
            customer_id="CUST001",
            order_reference="ORD001",
            current_status=CaseStatus.IN_REVIEW,
            exception_flag=True,  # Exception requires escalation
            created_by_id=test_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            retention_until=datetime.utcnow() + timedelta(days=365 * 7)
        )
        db_session.add(case)
        db_session.commit()

        engine = WorkflowRulesEngine(db_session)
        result = engine.evaluate_submission(
            case=case,
            assessment_recommendation=OutcomeType.RELEASE,
            actor_role="Order Management Analyst",
            actor_id=test_user.id + 1,
            requester_id=test_user.id
        )

        assert not result.eligible
        assert result.required_level == "Sales Operations Manager"
        assert "Exception flag" in str(result.reasons)


class TestAuditService:
    """Test audit service for immutable event logging."""

    def test_append_event_creates_audit_record(self, db_session, test_user):
        """Test AuditService.appendEvent creates audit record with hash."""
        from app.services.audit_service import AuditService

        service = AuditService(db_session)
        event = service.append_event(
            entity_type="Case",
            entity_id=123,
            action_type="CREATE",
            actor_id=test_user.id,
            payload={"customer_id": "CUST001"}
        )

        assert event.id is not None
        assert event.entity_type == "Case"
        assert event.entity_id == 123
        assert event.action_type == "CREATE"
        assert event.hash_value is not None
        assert len(event.hash_value) == 64  # SHA-256 hex digest

    def test_append_event_chains_hashes(self, db_session, test_user):
        """Test audit events maintain hash chain continuity."""
        from app.services.audit_service import AuditService

        service = AuditService(db_session)

        # First event
        event1 = service.append_event(
            entity_type="Case",
            entity_id=123,
            action_type="CREATE",
            actor_id=test_user.id,
            payload={"customer_id": "CUST001"}
        )
        assert event1.previous_hash is None

        # Second event for same entity
        event2 = service.append_event(
            entity_type="Case",
            entity_id=123,
            action_type="UPDATE",
            actor_id=test_user.id,
            payload={"status": "IN_REVIEW"}
        )
        assert event2.previous_hash == event1.hash_value
        assert event2.hash_value != event1.hash_value

    def test_audit_event_includes_required_fields(self, db_session, test_user):
        """Test audit events include all required fields per acceptance criteria."""
        from app.services.audit_service import AuditService

        service = AuditService(db_session)
        event = service.append_event(
            entity_type="Case",
            entity_id=456,
            action_type="APPROVE",
            actor_id=test_user.id,
            payload={"outcome": "RELEASE"}
        )

        # Verify required fields
        assert event.entity_type is not None
        assert event.entity_id is not None
        assert event.action_type is not None
        assert event.actor_id is not None
        assert event.occurred_at is not None
        assert event.payload_json is not None
        assert event.hash_value is not None
        assert event.retention_until is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
