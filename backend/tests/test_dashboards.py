"""
Tests for dashboard API endpoints and services.
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.domain.enums import ApprovalStatus, CaseStatus, RoleType
from app.domain.models import ApprovalRequest, Case, Role, User
from app.repositories.reporting_repository import ReportingRepository
from app.services.dashboard_service import DashboardService


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
    """Create sample cases for dashboard testing."""
    cases = []

    # Create cases across different statuses
    statuses = [
        CaseStatus.NEW,
        CaseStatus.IN_REVIEW,
        CaseStatus.PENDING_APPROVAL,
        CaseStatus.APPROVED,
        CaseStatus.ON_HOLD,
        CaseStatus.DECLINED,
        CaseStatus.RELEASED
    ]

    for idx, status in enumerate(statuses):
        case = Case(
            customer_id=f"CUST-{idx:03d}",
            order_reference=f"ORD-{idx:03d}",
            requested_terms="Standard",
            requested_outcome="Release",
            current_status=status,
            priority="Medium",
            exception_flag=(idx % 3 == 0),  # Every third case is exception
            created_by_id=sample_user.id,
            retention_until=datetime.utcnow() + timedelta(days=2555)
        )

        # Make some cases overdue
        if idx < 2:
            case.updated_at = datetime.utcnow() - timedelta(hours=72)

        cases.append(case)
        db.add(case)

    db.commit()

    for case in cases:
        db.refresh(case)

    return cases


@pytest.fixture
def sample_approvals(db: Session, sample_cases, sample_user: User):
    """Create sample approval requests for testing."""
    approvals = []

    # Create some pending and decided approvals
    for idx, case in enumerate(sample_cases[:5]):
        approval = ApprovalRequest(
            case_id=case.id,
            requested_by_id=sample_user.id,
            assigned_approver_id=sample_user.id,
            status=ApprovalStatus.PENDING if idx < 2 else ApprovalStatus.APPROVED,
            justification=f"Requires approval for case {case.id}",
            approval_level="Sales Operations Manager",
            retention_until=datetime.utcnow() + timedelta(days=2555)
        )

        # Set decided_at for approved requests
        if idx >= 2:
            approval.decided_at = datetime.utcnow()
            approval.decision_reason = "Approved after review"

        approvals.append(approval)
        db.add(approval)

    db.commit()

    for approval in approvals:
        db.refresh(approval)

    return approvals


def test_get_case_metrics(db: Session, sample_cases):
    """Test case metrics aggregation."""
    reporting_repo = ReportingRepository(db)
    metrics = reporting_repo.get_case_metrics()

    assert metrics["total_cases"] == len(sample_cases)
    assert metrics["pending_approval"] == 1  # One PENDING_APPROVAL case
    assert metrics["overdue_cases"] == 2  # Two cases with old updated_at


def test_get_case_status_distribution(db: Session, sample_cases):
    """Test case status distribution aggregation."""
    reporting_repo = ReportingRepository(db)
    distribution = reporting_repo.get_case_status_distribution()

    assert len(distribution) == 7  # 7 different statuses
    assert all("status" in item and "count" in item for item in distribution)

    # Each status appears exactly once
    for item in distribution:
        assert item["count"] == 1


def test_get_exception_volume(db: Session, sample_cases):
    """Test exception volume metrics."""
    reporting_repo = ReportingRepository(db)
    exception_volume = reporting_repo.get_exception_volume()

    # Every third case is exception (indices 0, 3, 6)
    assert exception_volume["total_exceptions"] == 3

    # Check open exceptions (non-terminal statuses)
    # Cases 0, 3 are exceptions, case 6 is RELEASED (terminal)
    assert exception_volume["open_exceptions"] >= 1


def test_get_approval_latency(db: Session, sample_approvals):
    """Test approval latency calculation."""
    reporting_repo = ReportingRepository(db)
    latency = reporting_repo.get_approval_latency()

    assert "avg_approval_hours" in latency
    assert "pending_approvals" in latency
    assert latency["pending_approvals"] == 2  # Two pending approvals


def test_get_queue_ageing(db: Session, sample_cases):
    """Test queue ageing buckets."""
    reporting_repo = ReportingRepository(db)
    ageing = reporting_repo.get_queue_ageing()

    assert len(ageing) == 4  # 4 age ranges
    assert all("age_range" in item and "count" in item for item in ageing)


def test_get_operational_alerts(db: Session, sample_cases, sample_approvals):
    """Test operational alerts generation."""
    reporting_repo = ReportingRepository(db)
    alerts = reporting_repo.get_operational_alerts()

    # Alerts is a list of alert dicts
    assert isinstance(alerts, list)

    # Each alert should have severity, message, and alert_type
    for alert in alerts:
        assert "severity" in alert
        assert "message" in alert
        assert "alert_type" in alert


def test_get_outcome_distribution(db: Session, sample_cases):
    """Test outcome distribution for terminal statuses."""
    reporting_repo = ReportingRepository(db)
    distribution = reporting_repo.get_outcome_distribution()

    # Terminal statuses in sample: APPROVED, DECLINED, RELEASED
    assert len(distribution) >= 1

    for item in distribution:
        assert item["outcome"] in [
            CaseStatus.APPROVED.value,
            CaseStatus.DECLINED.value,
            CaseStatus.RELEASED.value,
            CaseStatus.CANCELLED.value
        ]


def test_get_control_health_metrics(db: Session, sample_approvals):
    """Test control health metrics for executive dashboard."""
    reporting_repo = ReportingRepository(db)
    control_health = reporting_repo.get_control_health_metrics()

    assert "total_approvals" in control_health
    assert "sod_violations" in control_health
    assert "governed_actions" in control_health
    assert "control_compliance_rate" in control_health

    # Should have decided approvals
    assert control_health["total_approvals"] >= 3


def test_get_escalation_rate(db: Session, sample_cases, sample_approvals):
    """Test escalation rate calculation."""
    reporting_repo = ReportingRepository(db)
    escalation = reporting_repo.get_escalation_rate()

    assert "total_cases" in escalation
    assert "escalated_cases" in escalation
    assert "escalation_rate" in escalation

    assert escalation["total_cases"] == len(sample_cases)
    # At least one case had approval request
    assert escalation["escalated_cases"] >= 1


def test_get_release_readiness_indicators(db: Session, sample_cases):
    """Test release readiness indicators."""
    reporting_repo = ReportingRepository(db)
    readiness = reporting_repo.get_release_readiness_indicators()

    assert "ready_for_release" in readiness
    assert "blocked" in readiness
    assert "in_progress" in readiness
    assert "total" in readiness
    assert "readiness_rate" in readiness

    # Should have at least one ready case (APPROVED or RELEASED)
    assert readiness["ready_for_release"] >= 1


def test_operational_dashboard_service(db: Session, sample_cases, sample_approvals):
    """Test operational dashboard service integration."""
    reporting_repo = ReportingRepository(db)
    dashboard_service = DashboardService(reporting_repo)

    dashboard = dashboard_service.get_operational_dashboard()

    assert dashboard["dashboard_type"] == "operational"
    assert "metrics" in dashboard
    assert "widgets" in dashboard

    # Check metrics array
    assert len(dashboard["metrics"]) == 4
    metric_labels = [m["label"] for m in dashboard["metrics"]]
    assert "Total Cases" in metric_labels
    assert "Pending Approval" in metric_labels
    assert "Overdue Cases" in metric_labels
    assert "Avg Approval Time" in metric_labels

    # Check widgets
    widgets = dashboard["widgets"]
    assert "case_status_distribution" in widgets
    assert "exception_volume" in widgets
    assert "approval_latency" in widgets
    assert "operational_alerts" in widgets
    assert "queue_ageing" in widgets
    assert "outcome_distribution" in widgets


def test_executive_dashboard_service(db: Session, sample_cases, sample_approvals):
    """Test executive dashboard service integration."""
    reporting_repo = ReportingRepository(db)
    dashboard_service = DashboardService(reporting_repo)

    dashboard = dashboard_service.get_executive_dashboard()

    assert dashboard["dashboard_type"] == "executive"
    assert "metrics" in dashboard
    assert "widgets" in dashboard

    # Check metrics array
    assert len(dashboard["metrics"]) == 4
    metric_labels = [m["label"] for m in dashboard["metrics"]]
    assert "Control Compliance" in metric_labels
    assert "Escalation Rate" in metric_labels
    assert "Release Readiness" in metric_labels
    assert "SoD Violations" in metric_labels

    # Check widgets
    widgets = dashboard["widgets"]
    assert "control_health" in widgets
    assert "escalation_metrics" in widgets
    assert "release_readiness" in widgets
    assert "outcome_distribution" in widgets


def test_dashboard_performance(db: Session, sample_cases, sample_approvals):
    """Test dashboard query performance meets sub-2-second target."""
    import time

    reporting_repo = ReportingRepository(db)
    dashboard_service = DashboardService(reporting_repo)

    # Test operational dashboard
    start = time.time()
    dashboard_service.get_operational_dashboard()
    operational_duration = time.time() - start

    assert operational_duration < 2.0, f"Operational dashboard took {operational_duration:.2f}s"

    # Test executive dashboard
    start = time.time()
    dashboard_service.get_executive_dashboard()
    executive_duration = time.time() - start

    assert executive_duration < 2.0, f"Executive dashboard took {executive_duration:.2f}s"
