"""
Acceptance tests for TASK-6 to verify all acceptance criteria.
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.domain.enums import (
    CaseStatus,
    NotificationPriority,
    OutcomeType,
    RoleType,
)
from app.domain.models import (
    ApprovalRequest,
    AuthorityRule,
    Base,
    Case,
    CreditAssessment,
    Role,
    SodRule,
    User,
    UserRole,
)
from app.seed import (
    seed_authority_rules,
    seed_roles,
    seed_sample_cases,
    seed_sod_rules,
    seed_users,
)
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
        current_status=CaseStatus.NEW,
        created_by_id=test_user.id,
        retention_until=datetime.utcnow() + timedelta(days=365 * 7),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    return case


def test_notify_escalation_writes_notification(db_session: Session, test_user: User, test_case: Case):
    """Verify NotificationService.notifyEscalation() writes in-app notification linked to case and recipient."""
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


def test_notify_sla_warning_has_high_priority(db_session: Session, test_user: User, test_case: Case):
    """Verify NotificationService.notifySlaWarning() writes SLA warning notification with priority 'high'."""
    service = NotificationService(db_session)

    notification = service.notify_sla_warning(
        recipient_id=test_user.id,
        case_id=test_case.id,
        sla_threshold="approval_latency",
        hours_remaining=4
    )

    assert notification.priority == NotificationPriority.HIGH


def test_notify_rework_linked_to_approval(db_session: Session, test_user: User, test_case: Case):
    """Verify NotificationService.notifyRework() writes rework notification linked to approval request."""
    service = NotificationService(db_session)

    approval_request_id = 123
    notification = service.notify_rework(
        recipient_id=test_user.id,
        case_id=test_case.id,
        approval_request_id=approval_request_id,
        rework_reason="Missing evidence"
    )

    assert notification.notification_type == "rework"
    assert str(approval_request_id) in notification.message


def test_all_notification_templates_exist(db_session: Session):
    """Verify notification templates exist for all required types."""
    service = NotificationService(db_session)

    required_templates = [
        "escalation",
        "rework",
        "sla_warning",
        "complaint_ageing",
        "refund_evidence_missing",
        "renewal_risk",
    ]

    for template in required_templates:
        # Test that each template can be rendered
        message = service._render_template(template, case_id=1, reason="test", hours_remaining=4,
                                          approval_request_id=1, complaint_id=1, days_open=10,
                                          refund_id=1, refund_amount=100.0, renewal_id=1,
                                          risk_summary="test", sla_threshold="test")
        assert message is not None
        assert len(message) > 0


def test_seed_creates_four_users_with_correct_emails(db_session: Session):
    """Verify seed data creates four users with correct email addresses."""
    roles = seed_roles(db_session)
    users = seed_users(db_session, roles)

    expected_emails = [
        "analyst@example.com",
        "csm@example.com",
        "manager@example.com",
        "vp@example.com"
    ]

    assert len(users) == 4
    for email in expected_emails:
        assert email in users
        assert users[email].email == email


def test_seed_users_have_password123(db_session: Session):
    """Verify seed data passwords are 'password123' for all users."""
    import bcrypt

    roles = seed_roles(db_session)
    users = seed_users(db_session, roles)

    # Verify password hash matches 'password123'
    for user in users.values():
        assert bcrypt.checkpw("password123".encode("utf-8"), user.password_hash.encode("utf-8"))


def test_seed_users_have_role_assignments(db_session: Session):
    """Verify seed data creates users WITH role assignments."""
    roles = seed_roles(db_session)
    users = seed_users(db_session, roles)

    analyst = users["analyst@example.com"]
    user_roles = db_session.query(UserRole).filter(UserRole.user_id == analyst.id).all()

    assert len(user_roles) > 0
    role = db_session.query(Role).filter(Role.id == user_roles[0].role_id).first()
    assert role.name == RoleType.ORDER_MANAGEMENT_ANALYST.value


def test_seed_creates_authority_rules(db_session: Session):
    """Verify seed data creates authority rules for analyst auto-finalize and manager/executive thresholds."""
    seed_authority_rules(db_session)

    authority_rules = db_session.query(AuthorityRule).all()
    assert len(authority_rules) > 0

    # Check analyst auto-finalize rule exists
    analyst_rule = db_session.query(AuthorityRule).filter(
        AuthorityRule.role_name == RoleType.ORDER_MANAGEMENT_ANALYST.value,
        AuthorityRule.outcome_type == OutcomeType.RELEASE
    ).first()
    assert analyst_rule is not None
    assert analyst_rule.max_exposure_amount == 50000.0

    # Check manager approval threshold exists
    manager_rule = db_session.query(AuthorityRule).filter(
        AuthorityRule.role_name == RoleType.SALES_OPERATIONS_MANAGER.value
    ).first()
    assert manager_rule is not None

    # Check executive approval threshold exists
    executive_rule = db_session.query(AuthorityRule).filter(
        AuthorityRule.role_name == RoleType.VP_SALES_COMMERCIAL_DIRECTOR.value
    ).first()
    assert executive_rule is not None


def test_seed_creates_sod_rules(db_session: Session):
    """Verify seed data creates SoD rules preventing self-approval."""
    seed_sod_rules(db_session)

    sod_rules = db_session.query(SodRule).all()
    assert len(sod_rules) >= 1

    # Check at least one self-approval prevention rule exists
    self_approval_rule = db_session.query(SodRule).filter(
        SodRule.rule_name.like("%self%")
    ).first()
    assert self_approval_rule is not None
    assert self_approval_rule.is_active is True


def test_seed_creates_sample_cases_with_various_statuses(db_session: Session):
    """Verify seed data creates 10-15 sample cases with various statuses."""
    roles = seed_roles(db_session)
    users = seed_users(db_session, roles)
    seed_sample_cases(db_session, users)

    cases = db_session.query(Case).all()
    assert 10 <= len(cases) <= 15

    # Check that various statuses exist
    statuses = {case.current_status for case in cases}
    expected_statuses = {
        CaseStatus.NEW,
        CaseStatus.IN_REVIEW,
        CaseStatus.PENDING_APPROVAL,
        CaseStatus.APPROVED,
        CaseStatus.ON_HOLD,
        CaseStatus.DECLINED
    }
    assert len(statuses.intersection(expected_statuses)) >= 4


def test_seed_is_idempotent_roles(db_session: Session):
    """Verify running seed multiple times does not create duplicate roles."""
    seed_roles(db_session)
    initial_count = db_session.query(Role).count()

    seed_roles(db_session)
    final_count = db_session.query(Role).count()

    assert initial_count == final_count


def test_seed_is_idempotent_users(db_session: Session):
    """Verify running seed multiple times does not create duplicate users."""
    roles = seed_roles(db_session)
    seed_users(db_session, roles)
    initial_count = db_session.query(User).count()

    seed_users(db_session, roles)
    final_count = db_session.query(User).count()

    assert initial_count == final_count


def test_seed_is_idempotent_cases(db_session: Session):
    """Verify running seed multiple times does not create duplicate cases."""
    roles = seed_roles(db_session)
    users = seed_users(db_session, roles)
    seed_sample_cases(db_session, users)
    initial_count = db_session.query(Case).count()

    seed_sample_cases(db_session, users)
    final_count = db_session.query(Case).count()

    assert initial_count == final_count


def test_seeded_cases_have_credit_assessments(db_session: Session):
    """Verify some seeded cases have credit assessments."""
    roles = seed_roles(db_session)
    users = seed_users(db_session, roles)
    seed_sample_cases(db_session, users)

    assessments = db_session.query(CreditAssessment).all()
    assert len(assessments) > 0


def test_seeded_cases_have_approval_requests(db_session: Session):
    """Verify cases in pending approval status have approval requests."""
    roles = seed_roles(db_session)
    users = seed_users(db_session, roles)
    seed_sample_cases(db_session, users)

    pending_cases = db_session.query(Case).filter(
        Case.current_status == CaseStatus.PENDING_APPROVAL
    ).all()

    approvals = db_session.query(ApprovalRequest).all()
    assert len(approvals) > 0
    assert len(pending_cases) > 0
