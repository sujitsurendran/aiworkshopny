"""
Unit tests for approval endpoints and approval service.
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.domain.enums import ApprovalStatus, CaseStatus, OutcomeType
from app.domain.models import AuthorityRule, Case, Role, User, UserRole
from app.security.auth import hash_password
from app.services.approval_service import ApprovalService
from app.services.authority_policy_service import AuthorityPolicyService


@pytest.fixture
def db() -> Session:
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def test_users(db: Session):
    """Create test users with roles."""
    # Create roles
    analyst_role = Role(
        id=1,
        name="Order Management Analyst"
    )
    manager_role = Role(
        id=2,
        name="Sales Operations Manager"
    )

    db.add_all([analyst_role, manager_role])
    db.flush()

    # Create users
    analyst = User(
        id=1,
        email="analyst@example.com",
        password_hash=hash_password("password123"),
        full_name="Test Analyst",
        is_active=True
    )
    manager = User(
        id=2,
        email="manager@example.com",
        password_hash=hash_password("password123"),
        full_name="Test Manager",
        is_active=True
    )

    db.add_all([analyst, manager])
    db.flush()

    # Assign roles
    db.add(UserRole(user_id=1, role_id=1))
    db.add(UserRole(user_id=2, role_id=2))
    db.commit()

    return {"analyst": analyst, "manager": manager}


@pytest.fixture
def test_case(db: Session, test_users):
    """Create test case."""
    case = Case(
        id=1,
        customer_id="CUST001",
        order_reference="ORD001",
        current_status=CaseStatus.IN_REVIEW,
        priority="High",
        exception_flag=False,
        created_by_id=test_users["analyst"].id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        retention_until=datetime.utcnow() + timedelta(days=365 * 7)
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case


class TestApprovalService:
    """Test ApprovalService methods."""

    def test_create_approval_request_success(self, db: Session, test_case, test_users):
        """Test creating approval request."""
        service = ApprovalService(db)

        approval = service.create_approval_request(
            case_id=test_case.id,
            requested_by_id=test_users["analyst"].id,
            justification="Exceeds analyst authority threshold",
            approval_level="Sales Operations Manager"
        )

        assert approval.id is not None
        assert approval.case_id == test_case.id
        assert approval.requested_by_id == test_users["analyst"].id
        assert approval.status == ApprovalStatus.PENDING
        assert approval.justification == "Exceeds analyst authority threshold"
        assert approval.approval_level == "Sales Operations Manager"

    def test_approve_request_success(self, db: Session, test_case, test_users):
        """Test approving request by different user."""
        service = ApprovalService(db)

        # Create approval request
        approval = service.create_approval_request(
            case_id=test_case.id,
            requested_by_id=test_users["analyst"].id,
            justification="Test approval",
            approval_level="Manager"
        )

        # Approve by manager (different user)
        approved = service.approve_request(
            approval_request_id=approval.id,
            actor_id=test_users["manager"].id,
            decision_reason="Approved based on evidence"
        )

        assert approved.status == ApprovalStatus.APPROVED
        assert approved.decision_reason == "Approved based on evidence"
        assert approved.decided_at is not None

    def test_approve_request_sod_violation(self, db: Session, test_case, test_users):
        """Test SoD check prevents self-approval."""
        service = ApprovalService(db)

        # Create approval request
        approval = service.create_approval_request(
            case_id=test_case.id,
            requested_by_id=test_users["analyst"].id,
            justification="Test approval",
            approval_level="Manager"
        )

        # Attempt to approve by same user (SoD violation)
        with pytest.raises(Exception) as exc_info:
            service.approve_request(
                approval_request_id=approval.id,
                actor_id=test_users["analyst"].id,
                decision_reason="Attempting self-approval"
            )

        assert exc_info.value.status_code == 403
        assert "Segregation of duties violation" in str(exc_info.value.detail)

    def test_reject_request_success(self, db: Session, test_case, test_users):
        """Test rejecting request by different user."""
        service = ApprovalService(db)

        approval = service.create_approval_request(
            case_id=test_case.id,
            requested_by_id=test_users["analyst"].id,
            justification="Test approval",
            approval_level="Manager"
        )

        rejected = service.reject_request(
            approval_request_id=approval.id,
            actor_id=test_users["manager"].id,
            decision_reason="Insufficient evidence"
        )

        assert rejected.status == ApprovalStatus.REJECTED
        assert rejected.decision_reason == "Insufficient evidence"

    def test_reject_request_sod_violation(self, db: Session, test_case, test_users):
        """Test SoD check prevents self-rejection."""
        service = ApprovalService(db)

        approval = service.create_approval_request(
            case_id=test_case.id,
            requested_by_id=test_users["analyst"].id,
            justification="Test approval",
            approval_level="Manager"
        )

        with pytest.raises(Exception) as exc_info:
            service.reject_request(
                approval_request_id=approval.id,
                actor_id=test_users["analyst"].id,
                decision_reason="Self-reject"
            )

        assert exc_info.value.status_code == 403

    def test_send_back_request_success(self, db: Session, test_case, test_users):
        """Test sending back request for rework."""
        service = ApprovalService(db)

        approval = service.create_approval_request(
            case_id=test_case.id,
            requested_by_id=test_users["analyst"].id,
            justification="Test approval",
            approval_level="Manager"
        )

        sent_back = service.send_back_request(
            approval_request_id=approval.id,
            actor_id=test_users["manager"].id,
            decision_reason="Need more evidence"
        )

        assert sent_back.status == ApprovalStatus.SENT_BACK
        assert sent_back.decision_reason == "Need more evidence"

    def test_send_back_request_sod_violation(self, db: Session, test_case, test_users):
        """Test SoD check prevents self send-back."""
        service = ApprovalService(db)

        approval = service.create_approval_request(
            case_id=test_case.id,
            requested_by_id=test_users["analyst"].id,
            justification="Test approval",
            approval_level="Manager"
        )

        with pytest.raises(Exception) as exc_info:
            service.send_back_request(
                approval_request_id=approval.id,
                actor_id=test_users["analyst"].id,
                decision_reason="Self send-back"
            )

        assert exc_info.value.status_code == 403


class TestAuthorityPolicyService:
    """Test AuthorityPolicyService methods."""

    def test_evaluate_authority_eligible(self, db: Session):
        """Test authority evaluation when user is eligible."""
        # Create authority rule
        rule = AuthorityRule(
            role_name="Order Management Analyst",
            outcome_type=OutcomeType.RELEASE,
            max_exposure_amount=10000.0,
            executive_approval_required=False
        )
        db.add(rule)
        db.commit()

        service = AuthorityPolicyService(db)

        result = service.evaluate_authority(
            role_name="Order Management Analyst",
            outcome_type=OutcomeType.RELEASE,
            exposure_amount=5000.0
        )

        assert result["eligible"] is True
        assert result["required_level"] == "Order Management Analyst"
        assert "Within authority threshold" in result["reasons"][0]

    def test_evaluate_authority_exceeds_threshold(self, db: Session):
        """Test authority evaluation when amount exceeds threshold."""
        rule = AuthorityRule(
            role_name="Order Management Analyst",
            outcome_type=OutcomeType.RELEASE,
            max_exposure_amount=10000.0,
            executive_approval_required=False
        )
        db.add(rule)
        db.commit()

        service = AuthorityPolicyService(db)

        result = service.evaluate_authority(
            role_name="Order Management Analyst",
            outcome_type=OutcomeType.RELEASE,
            exposure_amount=15000.0
        )

        assert result["eligible"] is False
        assert "Exceeds authority threshold" in result["reasons"][0]

    def test_evaluate_authority_executive_required(self, db: Session):
        """Test authority evaluation when executive approval is required."""
        rule = AuthorityRule(
            role_name="Sales Operations Manager",
            outcome_type=OutcomeType.RELEASE,
            max_exposure_amount=50000.0,
            executive_approval_required=True
        )
        db.add(rule)
        db.commit()

        service = AuthorityPolicyService(db)

        result = service.evaluate_authority(
            role_name="Sales Operations Manager",
            outcome_type=OutcomeType.RELEASE,
            exposure_amount=30000.0
        )

        assert result["required_level"] == "VP Sales / Commercial Director"
        assert "Executive approval required" in result["reasons"][0]
