"""
Tests for export API endpoints and services.
"""
import json
from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.domain.enums import CaseStatus, RoleType
from app.domain.models import Case, ExportRequest, Role, User
from app.repositories.audit_repository import AuditRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.reporting_repository import ReportingRepository
from app.services.export_service import ExportService


@pytest.fixture
def sample_user(db: Session):
    """Create a sample user for testing."""
    from app.domain.models import UserRole

    role = Role(name=RoleType.ORDER_MANAGEMENT_ANALYST)
    db.add(role)
    db.commit()
    db.refresh(role)

    user = User(
        email="analyst@example.com",
        full_name="Test Analyst",
        password_hash="$2b$12$test",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create user-role mapping
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db.add(user_role)
    db.commit()

    return user


@pytest.fixture
def sample_cases(db: Session, sample_user: User):
    """Create sample cases for export testing."""
    cases = []

    statuses = [
        CaseStatus.NEW,
        CaseStatus.IN_REVIEW,
        CaseStatus.PENDING_APPROVAL,
        CaseStatus.APPROVED,
        CaseStatus.DECLINED
    ]

    for idx, status in enumerate(statuses):
        case = Case(
            customer_id=f"CUST-{idx:03d}",
            order_reference=f"ORD-{idx:03d}",
            requested_terms="Standard",
            requested_outcome="Release",
            current_status=status,
            priority="Medium",
            exception_flag=(idx % 2 == 0),
            created_by_id=sample_user.id,
            retention_until=datetime.utcnow() + timedelta(days=2555)
        )
        cases.append(case)
        db.add(case)

    db.commit()

    for case in cases:
        db.refresh(case)

    return cases


@pytest.fixture
def export_service(db: Session):
    """Create export service instance."""
    case_repo = CaseRepository(db)
    reporting_repo = ReportingRepository(db)
    return ExportService(db, case_repo, reporting_repo)


def test_export_case_list_csv(db: Session, sample_cases, sample_user: User, export_service: ExportService):
    """Test CSV export of case list."""
    result = export_service.create_export_request(
        source="case_list",
        export_type="csv",
        filters={},
        requested_by_id=sample_user.id
    )

    assert result["export_type"] == "csv"
    assert result["source"] == "case_list"
    assert result["status"] == "completed"
    assert "content" in result

    # Check CSV content
    content = result["content"]
    assert "case_id,customer_id,order_reference,status" in content
    assert "CUST-000" in content


def test_export_case_list_csv_with_filters(db: Session, sample_cases, sample_user: User, export_service: ExportService):
    """Test CSV export with status filter."""
    result = export_service.create_export_request(
        source="case_list",
        export_type="csv",
        filters={"status": "New"},
        requested_by_id=sample_user.id
    )

    assert result["status"] == "completed"
    content = result["content"]

    # Should only include NEW status cases
    lines = content.strip().split("\n")
    # Header + 1 NEW case
    assert len(lines) == 2


def test_export_operational_dashboard_csv(db: Session, sample_cases, sample_user: User, export_service: ExportService):
    """Test CSV export of operational dashboard."""
    result = export_service.create_export_request(
        source="operational_dashboard",
        export_type="csv",
        filters=None,
        requested_by_id=sample_user.id
    )

    assert result["export_type"] == "csv"
    assert result["source"] == "operational_dashboard"
    assert result["status"] == "completed"

    content = result["content"]
    assert "Operational Dashboard Export" in content
    assert "Key Metrics" in content
    assert "Total Cases" in content


def test_export_operational_dashboard_pdf(db: Session, sample_cases, sample_user: User, export_service: ExportService):
    """Test PDF export of operational dashboard."""
    result = export_service.create_export_request(
        source="operational_dashboard",
        export_type="pdf",
        filters=None,
        requested_by_id=sample_user.id
    )

    assert result["export_type"] == "pdf"
    assert result["source"] == "operational_dashboard"
    assert result["status"] == "completed"

    content = result["content"]
    assert "OPERATIONAL DASHBOARD REPORT" in content
    assert "KEY METRICS" in content
    assert "Total Cases:" in content


def test_export_executive_dashboard_pdf(db: Session, sample_cases, sample_user: User, export_service: ExportService):
    """Test PDF export of executive dashboard."""
    result = export_service.create_export_request(
        source="executive_dashboard",
        export_type="pdf",
        filters=None,
        requested_by_id=sample_user.id
    )

    assert result["export_type"] == "pdf"
    assert result["source"] == "executive_dashboard"
    assert result["status"] == "completed"

    content = result["content"]
    assert "EXECUTIVE DASHBOARD REPORT" in content
    assert "CONTROL HEALTH" in content
    assert "ESCALATION METRICS" in content
    assert "RELEASE READINESS" in content


def test_export_creates_audit_event(db: Session, sample_cases, sample_user: User, export_service: ExportService):
    """Test that export creates audit event."""

    result = export_service.create_export_request(
        source="case_list",
        export_type="csv",
        filters={"status": "Approved"},
        requested_by_id=sample_user.id
    )

    # Check audit event was created using audit repository
    audit_repo = AuditRepository(db)
    audit_events = audit_repo.list_events(
        entity_type="export_request",
        entity_id=result["export_id"]
    )

    assert len(audit_events) > 0
    audit_event = audit_events[0]
    assert audit_event.action_type == "export_generated"
    assert audit_event.actor_id == sample_user.id

    # Check payload includes required fields
    if isinstance(audit_event.payload_json, str):
        payload = json.loads(audit_event.payload_json)
    else:
        payload = audit_event.payload_json

    assert payload["export_type"] == "csv"
    assert payload["source"] == "case_list"
    assert payload["requested_by"] == sample_user.id


def test_export_request_persisted(db: Session, sample_cases, sample_user: User, export_service: ExportService):
    """Test that export request is persisted in database."""
    result = export_service.create_export_request(
        source="case_list",
        export_type="csv",
        filters={},
        requested_by_id=sample_user.id
    )

    # Check export request exists
    export_request = db.query(ExportRequest).filter(
        ExportRequest.id == result["export_id"]
    ).first()

    assert export_request is not None
    assert export_request.export_type == "csv"
    assert export_request.source == "case_list"
    assert export_request.status == "completed"
    assert export_request.requested_by_id == sample_user.id
    assert export_request.file_path is not None
    assert export_request.created_at is not None
    assert export_request.retention_until is not None


def test_export_invalid_source_type_combination(db: Session, sample_user: User, export_service: ExportService):
    """Test that invalid source/type combination raises error."""
    with pytest.raises(ValueError) as exc_info:
        export_service.create_export_request(
            source="case_list",
            export_type="pdf",  # Invalid: case_list doesn't support PDF
            filters={},
            requested_by_id=sample_user.id
        )

    assert "Unsupported" in str(exc_info.value)


def test_export_unsupported_source(db: Session, sample_user: User, export_service: ExportService):
    """Test that unsupported source raises error."""
    with pytest.raises(ValueError) as exc_info:
        export_service.create_export_request(
            source="invalid_source",
            export_type="csv",
            filters={},
            requested_by_id=sample_user.id
        )

    assert "Unsupported" in str(exc_info.value)


def test_export_csv_formatting(db: Session, sample_cases, sample_user: User, export_service: ExportService):
    """Test CSV export formatting is correct."""
    result = export_service.create_export_request(
        source="case_list",
        export_type="csv",
        filters={},
        requested_by_id=sample_user.id
    )

    content = result["content"]
    lines = content.strip().split("\n")

    # Header line
    header = lines[0]
    assert "case_id" in header
    assert "customer_id" in header
    assert "order_reference" in header
    assert "status" in header

    # Data lines
    assert len(lines) > 1  # At least one data row


def test_export_pdf_formatting(db: Session, sample_cases, sample_user: User, export_service: ExportService):
    """Test PDF export formatting is correct."""
    result = export_service.create_export_request(
        source="operational_dashboard",
        export_type="pdf",
        filters=None,
        requested_by_id=sample_user.id
    )

    content = result["content"]

    # Check report structure
    assert "=" * 60 in content  # Report separator
    assert "Generated:" in content
    assert "KEY METRICS" in content
    assert "-" * 60 in content  # Section separator


def test_export_with_role_filter(db: Session, sample_cases, sample_user: User, export_service: ExportService):
    """Test export filtering by caller role (permission filtering)."""

    # Export with assigned_to filter (simulating role-based filtering)
    result = export_service.create_export_request(
        source="case_list",
        export_type="csv",
        filters={"assigned_to_id": sample_user.id},
        requested_by_id=sample_user.id
    )

    assert result["status"] == "completed"

    # Verify filter was recorded in audit event
    audit_repo = AuditRepository(db)
    audit_events = audit_repo.list_events(
        entity_type="export_request",
        entity_id=result["export_id"]
    )

    assert len(audit_events) > 0
    audit_event = audit_events[0]

    if isinstance(audit_event.payload_json, str):
        payload = json.loads(audit_event.payload_json)
    else:
        payload = audit_event.payload_json

    filter_json = json.loads(payload["filter_json"])
    assert filter_json.get("assigned_to_id") == sample_user.id
