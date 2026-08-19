"""
SQLAlchemy ORM models matching LLD Section 9.3 DDL.
All models include retention_until or created_at for 7-year retention compliance.
"""
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship

from app.domain.enums import (
    ApprovalStatus,
    CaseStatus,
    ComplaintStatus,
    ExportFormat,
    FulfilmentStatus,
    NotificationPriority,
    OutcomeType,
    RefundStatus,
    RenewalStatus,
    RiskBand,
)

Base = declarative_base()


class User(Base):
    """User accounts with role-based access control."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    created_cases = relationship("Case", foreign_keys="Case.created_by_id", back_populates="created_by")
    assigned_cases = relationship("Case", foreign_keys="Case.assigned_to_id", back_populates="assigned_to")


class Role(Base):
    """Roles for RBAC."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class UserRole(Base):
    """Many-to-many relationship between users and roles."""
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

    __table_args__ = (
        Index("ix_user_roles_user_id", "user_id"),
        Index("ix_user_roles_role_id", "role_id"),
    )


class Case(Base):
    """Customer credit review cases."""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(100), nullable=False, index=True)
    account_id = Column(String(100), nullable=True)
    order_reference = Column(String(100), nullable=False, index=True)
    requested_terms = Column(String(255), nullable=True)
    requested_outcome = Column(String(50), nullable=True)
    requested_fulfilment_date = Column(DateTime, nullable=True)
    current_status = Column(SQLEnum(CaseStatus), nullable=False, default=CaseStatus.NEW)
    priority = Column(String(20), default="Medium", nullable=False)
    exception_flag = Column(Boolean, default=False, nullable=False)
    risk_band = Column(SQLEnum(RiskBand), nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    retention_until = Column(DateTime, nullable=False)

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_cases")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_cases")
    credit_assessments = relationship("CreditAssessment", back_populates="case", cascade="all, delete-orphan")
    approval_requests = relationship("ApprovalRequest", back_populates="case", cascade="all, delete-orphan")
    fulfilment_records = relationship("FulfilmentRecord", back_populates="case", cascade="all, delete-orphan")
    complaint_records = relationship("ComplaintRecord", back_populates="case", cascade="all, delete-orphan")
    refund_records = relationship("RefundRecord", back_populates="case", cascade="all, delete-orphan")
    renewal_reviews = relationship("RenewalReview", back_populates="case", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_cases_current_status_assigned_to", "current_status", "assigned_to_id"),
        Index("ix_cases_updated_at", "updated_at"),
    )


class CreditAssessment(Base):
    """Credit validation findings and recommendations."""
    __tablename__ = "credit_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    assessment_data = Column(JSON, nullable=True)
    recommendation = Column(SQLEnum(OutcomeType), nullable=True)
    rationale = Column(Text, nullable=True)
    assessed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="credit_assessments")


class ApprovalRequest(Base):
    """Approval requests for cases exceeding analyst authority."""
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(SQLEnum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING)
    justification = Column(Text, nullable=True)
    approval_level = Column(String(50), nullable=True)
    decision_reason = Column(Text, nullable=True)
    decided_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    retention_until = Column(DateTime, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="approval_requests")

    __table_args__ = (
        Index("ix_approval_requests_status_assigned", "status", "assigned_approver_id"),
    )


class AuthorityRule(Base):
    """Delegation-of-authority rules."""
    __tablename__ = "authority_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(100), nullable=False)
    outcome_type = Column(SQLEnum(OutcomeType), nullable=False)
    risk_band = Column(SQLEnum(RiskBand), nullable=True)
    max_exposure_amount = Column(Float, nullable=True)
    executive_approval_required = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SodRule(Base):
    """Segregation-of-duties rules."""
    __tablename__ = "sod_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FulfilmentRecord(Base):
    """Fulfilment tracking milestones and blockers."""
    __tablename__ = "fulfilment_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    milestone_name = Column(String(255), nullable=False)
    status = Column(SQLEnum(FulfilmentStatus), nullable=False, default=FulfilmentStatus.PENDING)
    blocker_description = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="fulfilment_records")


class ComplaintRecord(Base):
    """Complaint records linked to cases."""
    __tablename__ = "complaint_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    complaint_description = Column(Text, nullable=False)
    status = Column(SQLEnum(ComplaintStatus), nullable=False, default=ComplaintStatus.OPEN)
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="complaint_records")


class RefundRecord(Base):
    """Refund and return records."""
    __tablename__ = "refund_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    refund_amount = Column(Float, nullable=False)
    financial_impact_flag = Column(Boolean, default=False, nullable=False)
    evidence_confirmed = Column(Boolean, default=False, nullable=False)
    status = Column(SQLEnum(RefundStatus), nullable=False, default=RefundStatus.REQUESTED)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="refund_records")


class RenewalReview(Base):
    """Account renewal review records."""
    __tablename__ = "renewal_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    renewal_risk_summary = Column(Text, nullable=True)
    status = Column(SQLEnum(RenewalStatus), nullable=False, default=RenewalStatus.PENDING_REVIEW)
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="renewal_reviews")


class Notification(Base):
    """In-app notification records."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=True)
    notification_type = Column(String(50), nullable=False)
    priority = Column(SQLEnum(NotificationPriority), nullable=False, default=NotificationPriority.MEDIUM)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ExportRequest(Base):
    """Export request audit trail."""
    __tablename__ = "export_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    export_type = Column(String(50), nullable=False)
    export_format = Column(SQLEnum(ExportFormat), nullable=False)
    source = Column(String(100), nullable=False)
    filter_json = Column(JSON, nullable=True)
    file_path = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    retention_until = Column(DateTime, nullable=False)


class AuditEvent(Base):
    """Immutable append-only audit event store with hash chaining."""
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action_type = Column(String(100), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    payload_json = Column(JSON, nullable=True)
    hash_value = Column(String(64), nullable=False)
    previous_hash = Column(String(64), nullable=True)
    retention_until = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("ix_audit_events_entity_type_entity_id_occurred_at", "entity_type", "entity_id", "occurred_at"),
    )
