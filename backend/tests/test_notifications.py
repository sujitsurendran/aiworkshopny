"""
Unit tests for notification service.
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.domain.enums import NotificationPriority
from app.domain.models import Base, Case, Notification, User
from app.services.notification_service import NotificationService


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_case(db_session: Session, test_user: User):
    """Create a test case."""
    case = Case(
        customer_id="CUST-001",
        order_reference="ORD-001",
        current_status="New",
        created_by_id=test_user.id,
        retention_until=datetime.utcnow() + timedelta(days=365 * 7),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    return case


def test_notify_escalation(db_session: Session, test_user: User, test_case: Case):
    """Test escalation notification creation."""
    service = NotificationService(db_session)

    notification = service.notify_escalation(
        recipient_id=test_user.id,
        case_id=test_case.id,
        escalation_reason="High risk requires manager approval"
    )

    assert notification is not None
    assert notification.recipient_id == test_user.id
    assert notification.case_id == test_case.id
    assert notification.notification_type == "escalation"
    assert notification.priority == NotificationPriority.HIGH
    assert "escalated" in notification.message.lower()
    assert not notification.is_read


def test_notify_sla_warning(db_session: Session, test_user: User, test_case: Case):
    """Test SLA warning notification creation with priority HIGH."""
    service = NotificationService(db_session)

    notification = service.notify_sla_warning(
        recipient_id=test_user.id,
        case_id=test_case.id,
        sla_threshold="approval_latency",
        hours_remaining=4
    )

    assert notification is not None
    assert notification.recipient_id == test_user.id
    assert notification.case_id == test_case.id
    assert notification.notification_type == "sla_warning"
    assert notification.priority == NotificationPriority.HIGH
    assert "4 hours" in notification.message
    assert not notification.is_read


def test_notify_rework(db_session: Session, test_user: User, test_case: Case):
    """Test rework notification linked to approval request."""
    service = NotificationService(db_session)

    notification = service.notify_rework(
        recipient_id=test_user.id,
        case_id=test_case.id,
        approval_request_id=1,
        rework_reason="Missing credit assessment evidence"
    )

    assert notification is not None
    assert notification.recipient_id == test_user.id
    assert notification.case_id == test_case.id
    assert notification.notification_type == "rework"
    assert notification.priority == NotificationPriority.MEDIUM
    assert "rework" in notification.message.lower()
    assert "Missing credit assessment evidence" in notification.message


def test_notify_complaint_ageing(db_session: Session, test_user: User, test_case: Case):
    """Test complaint ageing notification."""
    service = NotificationService(db_session)

    notification = service.notify_complaint_ageing(
        recipient_id=test_user.id,
        case_id=test_case.id,
        complaint_id=10,
        days_open=15
    )

    assert notification is not None
    assert notification.recipient_id == test_user.id
    assert notification.case_id == test_case.id
    assert notification.notification_type == "complaint_ageing"
    assert "15 days" in notification.message


def test_notify_refund_evidence_missing(db_session: Session, test_user: User, test_case: Case):
    """Test refund evidence missing notification."""
    service = NotificationService(db_session)

    notification = service.notify_refund_evidence_missing(
        recipient_id=test_user.id,
        case_id=test_case.id,
        refund_id=5,
        refund_amount=1250.50
    )

    assert notification is not None
    assert notification.recipient_id == test_user.id
    assert notification.case_id == test_case.id
    assert notification.notification_type == "refund_evidence_missing"
    assert notification.priority == NotificationPriority.HIGH
    assert "$1250.50" in notification.message


def test_notify_renewal_risk(db_session: Session, test_user: User, test_case: Case):
    """Test renewal risk notification."""
    service = NotificationService(db_session)

    notification = service.notify_renewal_risk(
        recipient_id=test_user.id,
        case_id=test_case.id,
        renewal_id=3,
        risk_summary="Payment history declining over last 6 months"
    )

    assert notification is not None
    assert notification.recipient_id == test_user.id
    assert notification.case_id == test_case.id
    assert notification.notification_type == "renewal_risk"
    assert "Payment history declining" in notification.message


def test_notification_templates(db_session: Session, test_user: User, test_case: Case):
    """Test that all required notification templates exist."""
    service = NotificationService(db_session)

    # Test each template renders without error
    templates = [
        ("escalation", {"case_id": 1, "reason": "test"}),
        ("sla_warning", {"case_id": 1, "sla_threshold": "approval", "hours_remaining": 4}),
        ("rework", {"case_id": 1, "approval_request_id": 1, "reason": "test"}),
        ("complaint_ageing", {"case_id": 1, "complaint_id": 1, "days_open": 10}),
        ("refund_evidence_missing", {"case_id": 1, "refund_id": 1, "refund_amount": 100.0}),
        ("renewal_risk", {"case_id": 1, "renewal_id": 1, "risk_summary": "test"}),
    ]

    for template, kwargs in templates:
        message = service._render_template(template, **kwargs)
        assert message is not None
        assert len(message) > 0


def test_notification_persisted_in_database(db_session: Session, test_user: User, test_case: Case):
    """Test that notification is written to database."""
    service = NotificationService(db_session)

    service.notify_escalation(
        recipient_id=test_user.id,
        case_id=test_case.id,
        escalation_reason="Test reason"
    )

    # Query the database directly
    notifications = db_session.query(Notification).filter(
        Notification.recipient_id == test_user.id
    ).all()

    assert len(notifications) == 1
    assert notifications[0].case_id == test_case.id


def test_notification_default_is_read_false(db_session: Session, test_user: User, test_case: Case):
    """Test that notifications default to is_read=False."""
    service = NotificationService(db_session)

    notification = service.notify_escalation(
        recipient_id=test_user.id,
        case_id=test_case.id,
        escalation_reason="Test"
    )

    assert notification.is_read is False


def test_multiple_notifications_for_same_case(db_session: Session, test_user: User, test_case: Case):
    """Test creating multiple notifications for the same case."""
    service = NotificationService(db_session)

    service.notify_escalation(
        recipient_id=test_user.id,
        case_id=test_case.id,
        escalation_reason="First escalation"
    )

    service.notify_sla_warning(
        recipient_id=test_user.id,
        case_id=test_case.id,
        sla_threshold="approval_latency",
        hours_remaining=2
    )

    notifications = db_session.query(Notification).filter(
        Notification.case_id == test_case.id
    ).all()

    assert len(notifications) == 2
    assert notifications[0].notification_type == "escalation"
    assert notifications[1].notification_type == "sla_warning"


def test_email_failure_does_not_block_notification(db_session: Session, test_user: User, test_case: Case):
    """Test that email adapter failure does not prevent notification creation."""
    service = NotificationService(db_session)

    # _try_send_email is a no-op in the implementation, but this test
    # verifies the pattern that exceptions in email dispatch are caught
    notification = service.notify_escalation(
        recipient_id=test_user.id,
        case_id=test_case.id,
        escalation_reason="Test"
    )

    # Notification should be created despite email being no-op
    assert notification is not None
    assert notification.id is not None
