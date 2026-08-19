"""
Unit tests for operations endpoints and operational services.
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.domain.enums import (
    CaseStatus,
    ComplaintStatus,
    FulfilmentStatus,
    RefundStatus,
    RenewalStatus,
)
from app.domain.models import Case, Role, User, UserRole
from app.security.auth import hash_password
from app.services.complaint_service import ComplaintService
from app.services.fulfilment_service import FulfilmentService
from app.services.refund_service import RefundService
from app.services.renewal_service import RenewalService


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
def test_user(db: Session):
    """Create test user with CSM role."""
    role = Role(
        id=1,
        name="Customer Success Manager"
    )
    db.add(role)
    db.flush()

    user = User(
        id=1,
        email="csm@example.com",
        password_hash=hash_password("password123"),
        full_name="Test CSM",
        is_active=True
    )
    db.add(user)
    db.flush()

    db.add(UserRole(user_id=1, role_id=1))
    db.commit()

    return user


@pytest.fixture
def test_case(db: Session, test_user):
    """Create test case."""
    case = Case(
        id=1,
        customer_id="CUST001",
        order_reference="ORD001",
        current_status=CaseStatus.IN_REVIEW,
        priority="Medium",
        exception_flag=False,
        created_by_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        retention_until=datetime.utcnow() + timedelta(days=365 * 7)
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case


class TestFulfilmentService:
    """Test FulfilmentService methods."""

    def test_create_fulfilment_success(self, db: Session, test_case, test_user):
        """Test creating fulfilment milestone."""
        service = FulfilmentService(db)

        record = service.create_or_update_fulfilment(
            case_id=test_case.id,
            actor_id=test_user.id,
            milestone_name="Order Confirmation",
            status=FulfilmentStatus.IN_PROGRESS,
            blocker_description=None
        )

        assert record.id is not None
        assert record.case_id == test_case.id
        assert record.milestone_name == "Order Confirmation"
        assert record.status == FulfilmentStatus.IN_PROGRESS
        assert record.blocker_description is None

    def test_update_fulfilment_milestone(self, db: Session, test_case, test_user):
        """Test updating existing fulfilment milestone."""
        service = FulfilmentService(db)

        # Create initial record
        record1 = service.create_or_update_fulfilment(
            case_id=test_case.id,
            actor_id=test_user.id,
            milestone_name="Shipping",
            status=FulfilmentStatus.PENDING
        )

        # Update same milestone
        record2 = service.create_or_update_fulfilment(
            case_id=test_case.id,
            actor_id=test_user.id,
            milestone_name="Shipping",
            status=FulfilmentStatus.COMPLETED
        )

        assert record2.id == record1.id
        assert record2.status == FulfilmentStatus.COMPLETED
        assert record2.completed_at is not None

    def test_update_fulfilment_with_blocker(self, db: Session, test_case, test_user):
        """Test updating fulfilment with blocker description."""
        service = FulfilmentService(db)

        record = service.create_or_update_fulfilment(
            case_id=test_case.id,
            actor_id=test_user.id,
            milestone_name="Delivery",
            status=FulfilmentStatus.BLOCKED,
            blocker_description="Address validation failed"
        )

        assert record.status == FulfilmentStatus.BLOCKED
        assert record.blocker_description == "Address validation failed"


class TestComplaintService:
    """Test ComplaintService methods."""

    def test_create_complaint_success(self, db: Session, test_case, test_user):
        """Test creating complaint linked to case."""
        service = ComplaintService(db)

        complaint = service.create_complaint(
            case_id=test_case.id,
            actor_id=test_user.id,
            complaint_description="Service quality issue"
        )

        assert complaint.id is not None
        assert complaint.case_id == test_case.id
        assert complaint.complaint_description == "Service quality issue"
        assert complaint.status == ComplaintStatus.OPEN

    def test_update_complaint_status(self, db: Session, test_case, test_user):
        """Test updating complaint status."""
        service = ComplaintService(db)

        complaint = service.create_complaint(
            case_id=test_case.id,
            actor_id=test_user.id,
            complaint_description="Test complaint"
        )

        updated = service.update_complaint(
            complaint_id=complaint.id,
            actor_id=test_user.id,
            status=ComplaintStatus.IN_PROGRESS,
            resolution_notes="Investigating issue"
        )

        assert updated.status == ComplaintStatus.IN_PROGRESS
        assert updated.resolution_notes == "Investigating issue"

    def test_resolve_complaint(self, db: Session, test_case, test_user):
        """Test resolving complaint."""
        service = ComplaintService(db)

        complaint = service.create_complaint(
            case_id=test_case.id,
            actor_id=test_user.id,
            complaint_description="Test complaint"
        )

        resolved = service.update_complaint(
            complaint_id=complaint.id,
            actor_id=test_user.id,
            status=ComplaintStatus.RESOLVED,
            resolution_notes="Issue resolved"
        )

        assert resolved.status == ComplaintStatus.RESOLVED
        assert resolved.resolved_at is not None


class TestRefundService:
    """Test RefundService methods."""

    def test_create_refund_success(self, db: Session, test_case, test_user):
        """Test creating refund without financial impact flag."""
        service = RefundService(db)

        refund = service.create_refund(
            case_id=test_case.id,
            actor_id=test_user.id,
            refund_amount=50.0,
            financial_impact_flag=False,
            evidence_confirmed=False
        )

        assert refund.id is not None
        assert refund.case_id == test_case.id
        assert refund.refund_amount == 50.0
        assert refund.status == RefundStatus.REQUESTED

    def test_create_refund_with_evidence(self, db: Session, test_case, test_user):
        """Test creating significant refund with evidence confirmation."""
        service = RefundService(db)

        refund = service.create_refund(
            case_id=test_case.id,
            actor_id=test_user.id,
            refund_amount=500.0,
            financial_impact_flag=True,
            evidence_confirmed=True
        )

        assert refund.refund_amount == 500.0
        assert refund.financial_impact_flag is True
        assert refund.evidence_confirmed is True

    def test_create_refund_without_evidence_fails(self, db: Session, test_case, test_user):
        """Test significant refund without evidence confirmation fails."""
        service = RefundService(db)

        with pytest.raises(Exception) as exc_info:
            service.create_refund(
                case_id=test_case.id,
                actor_id=test_user.id,
                refund_amount=1000.0,
                financial_impact_flag=True,
                evidence_confirmed=False
            )

        assert exc_info.value.status_code == 422
        assert "required evidence is missing" in str(exc_info.value.detail)

    def test_update_refund_status(self, db: Session, test_case, test_user):
        """Test updating refund status to processed."""
        service = RefundService(db)

        refund = service.create_refund(
            case_id=test_case.id,
            actor_id=test_user.id,
            refund_amount=100.0,
            financial_impact_flag=False,
            evidence_confirmed=False
        )

        processed = service.update_refund_status(
            refund_id=refund.id,
            actor_id=test_user.id,
            status=RefundStatus.PROCESSED
        )

        assert processed.status == RefundStatus.PROCESSED
        assert processed.processed_at is not None


class TestRenewalService:
    """Test RenewalService methods."""

    def test_create_renewal_success(self, db: Session, test_case, test_user):
        """Test creating renewal review."""
        service = RenewalService(db)

        renewal = service.create_or_update_renewal(
            case_id=test_case.id,
            actor_id=test_user.id,
            renewal_risk_summary="Medium risk account",
            status=RenewalStatus.PENDING_REVIEW,
            review_notes="Review required"
        )

        assert renewal.id is not None
        assert renewal.case_id == test_case.id
        assert renewal.renewal_risk_summary == "Medium risk account"
        assert renewal.status == RenewalStatus.PENDING_REVIEW

    def test_update_renewal(self, db: Session, test_case, test_user):
        """Test updating existing renewal review."""
        service = RenewalService(db)

        # Create initial renewal
        renewal1 = service.create_or_update_renewal(
            case_id=test_case.id,
            actor_id=test_user.id,
            renewal_risk_summary="Low risk",
            status=RenewalStatus.PENDING_REVIEW
        )

        # Update renewal
        renewal2 = service.create_or_update_renewal(
            case_id=test_case.id,
            actor_id=test_user.id,
            renewal_risk_summary="High risk - requires attention",
            status=RenewalStatus.APPROVED,
            review_notes="Updated risk assessment"
        )

        assert renewal2.id == renewal1.id
        assert renewal2.renewal_risk_summary == "High risk - requires attention"
        assert renewal2.status == RenewalStatus.APPROVED
