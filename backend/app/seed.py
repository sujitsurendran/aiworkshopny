"""
Idempotent seed data for default users, authority rules, SoD rules, and sample cases.
Callable standalone via `python -m app.seed` or from startup.
"""
from datetime import datetime, timedelta

import bcrypt
from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.domain.enums import (
    ApprovalStatus,
    CaseStatus,
    OutcomeType,
    RiskBand,
    RoleType,
)
from app.domain.models import (
    ApprovalRequest,
    AuthorityRule,
    Case,
    CreditAssessment,
    Role,
    SodRule,
    User,
    UserRole,
)


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def seed_roles(db: Session) -> dict[str, Role]:
    """
    Seed the four primary roles.

    Returns:
        Dictionary mapping role name to Role object
    """
    role_names = [
        RoleType.ORDER_MANAGEMENT_ANALYST.value,
        RoleType.CUSTOMER_SUCCESS_MANAGER.value,
        RoleType.SALES_OPERATIONS_MANAGER.value,
        RoleType.VP_SALES_COMMERCIAL_DIRECTOR.value,
    ]

    roles = {}
    for role_name in role_names:
        existing_role = db.query(Role).filter(Role.name == role_name).first()
        if existing_role:
            roles[role_name] = existing_role
        else:
            role = Role(
                name=role_name,
                description=f"System role: {role_name}",
                created_at=datetime.utcnow()
            )
            db.add(role)
            db.flush()
            roles[role_name] = role

    db.commit()
    print(f"Seeded {len(roles)} roles")
    return roles


def seed_users(db: Session, roles: dict[str, Role]) -> dict[str, User]:
    """
    Seed four default users (one per role) with password 'password123'.

    Returns:
        Dictionary mapping email to User object
    """
    users_data = [
        {
            "email": "analyst@example.com",
            "full_name": "Alice Analyst",
            "role": RoleType.ORDER_MANAGEMENT_ANALYST.value,
        },
        {
            "email": "csm@example.com",
            "full_name": "Bob Customer Success",
            "role": RoleType.CUSTOMER_SUCCESS_MANAGER.value,
        },
        {
            "email": "manager@example.com",
            "full_name": "Carol Manager",
            "role": RoleType.SALES_OPERATIONS_MANAGER.value,
        },
        {
            "email": "vp@example.com",
            "full_name": "Dave VP Sales",
            "role": RoleType.VP_SALES_COMMERCIAL_DIRECTOR.value,
        },
    ]

    password_hash = hash_password("password123")
    users = {}

    for user_data in users_data:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            users[user_data["email"]] = existing_user
        else:
            user = User(
                email=user_data["email"],
                password_hash=password_hash,
                full_name=user_data["full_name"],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(user)
            db.flush()

            # Assign role
            role = roles[user_data["role"]]
            user_role = UserRole(
                user_id=user.id,
                role_id=role.id,
                assigned_at=datetime.utcnow()
            )
            db.add(user_role)
            users[user_data["email"]] = user

    db.commit()
    print(f"Seeded {len(users)} users with role assignments")
    return users


def seed_authority_rules(db: Session) -> None:
    """
    Seed authority rules for approval routing.
    - Analyst can auto-finalize low-risk releases up to threshold
    - Manager approval required for medium/high risk or high-value cases
    - Executive approval required for exceptional circumstances
    """
    rules_data = [
        {
            "role_name": RoleType.ORDER_MANAGEMENT_ANALYST.value,
            "outcome_type": OutcomeType.RELEASE,
            "risk_band": RiskBand.LOW,
            "max_exposure_amount": 50000.0,
            "executive_approval_required": False,
        },
        {
            "role_name": RoleType.SALES_OPERATIONS_MANAGER.value,
            "outcome_type": OutcomeType.RELEASE,
            "risk_band": RiskBand.MEDIUM,
            "max_exposure_amount": 200000.0,
            "executive_approval_required": False,
        },
        {
            "role_name": RoleType.SALES_OPERATIONS_MANAGER.value,
            "outcome_type": OutcomeType.RELEASE,
            "risk_band": RiskBand.HIGH,
            "max_exposure_amount": 500000.0,
            "executive_approval_required": False,
        },
        {
            "role_name": RoleType.VP_SALES_COMMERCIAL_DIRECTOR.value,
            "outcome_type": OutcomeType.RELEASE,
            "risk_band": RiskBand.VERY_HIGH,
            "max_exposure_amount": None,
            "executive_approval_required": True,
        },
        {
            "role_name": RoleType.SALES_OPERATIONS_MANAGER.value,
            "outcome_type": OutcomeType.AMEND,
            "risk_band": None,
            "max_exposure_amount": None,
            "executive_approval_required": False,
        },
        {
            "role_name": RoleType.VP_SALES_COMMERCIAL_DIRECTOR.value,
            "outcome_type": OutcomeType.DECLINE,
            "risk_band": None,
            "max_exposure_amount": None,
            "executive_approval_required": True,
        },
    ]

    for rule_data in rules_data:
        existing_rule = db.query(AuthorityRule).filter(
            AuthorityRule.role_name == rule_data["role_name"],
            AuthorityRule.outcome_type == rule_data["outcome_type"],
            AuthorityRule.risk_band == rule_data["risk_band"]
        ).first()

        if not existing_rule:
            rule = AuthorityRule(**rule_data, created_at=datetime.utcnow())
            db.add(rule)

    db.commit()
    print("Seeded authority rules")


def seed_sod_rules(db: Session) -> None:
    """
    Seed segregation-of-duties rules preventing self-approval.
    """
    rules_data = [
        {
            "rule_name": "Analyst cannot approve own recommendation",
            "description": "Prevents analyst from approving their own case recommendation or approval request",
            "is_active": True,
        },
        {
            "rule_name": "Approver cannot reject own submission",
            "description": "Prevents conflict of interest in rejection decisions",
            "is_active": True,
        },
        {
            "rule_name": "No self-authorization for exceptions",
            "description": "Exception-flagged cases must be approved by a different user than the requester",
            "is_active": True,
        },
    ]

    for rule_data in rules_data:
        existing_rule = db.query(SodRule).filter(
            SodRule.rule_name == rule_data["rule_name"]
        ).first()

        if not existing_rule:
            rule = SodRule(**rule_data, created_at=datetime.utcnow())
            db.add(rule)

    db.commit()
    print("Seeded SoD rules")


def seed_sample_cases(db: Session, users: dict[str, User]) -> None:
    """
    Seed 10-15 sample cases with various statuses.
    """
    analyst = users["analyst@example.com"]
    csm = users["csm@example.com"]
    manager = users["manager@example.com"]
    vp = users["vp@example.com"]

    retention_7_years = datetime.utcnow() + timedelta(days=365 * 7)

    cases_data = [
        {
            "customer_id": "CUST-001",
            "account_id": "ACC-001",
            "order_reference": "ORD-1001",
            "requested_terms": "Net 30",
            "requested_outcome": "New Order Release",
            "requested_fulfilment_date": datetime.utcnow() + timedelta(days=7),
            "current_status": CaseStatus.NEW,
            "priority": "High",
            "exception_flag": False,
            "risk_band": RiskBand.LOW,
            "created_by_id": analyst.id,
            "assigned_to_id": analyst.id,
        },
        {
            "customer_id": "CUST-002",
            "account_id": "ACC-002",
            "order_reference": "ORD-1002",
            "requested_terms": "Net 60",
            "requested_outcome": "Credit Extension",
            "requested_fulfilment_date": datetime.utcnow() + timedelta(days=14),
            "current_status": CaseStatus.IN_REVIEW,
            "priority": "Medium",
            "exception_flag": False,
            "risk_band": RiskBand.MEDIUM,
            "created_by_id": analyst.id,
            "assigned_to_id": analyst.id,
        },
        {
            "customer_id": "CUST-003",
            "account_id": "ACC-003",
            "order_reference": "ORD-1003",
            "requested_terms": "Net 90",
            "requested_outcome": "High-Value Release",
            "requested_fulfilment_date": datetime.utcnow() + timedelta(days=10),
            "current_status": CaseStatus.PENDING_APPROVAL,
            "priority": "High",
            "exception_flag": True,
            "risk_band": RiskBand.HIGH,
            "created_by_id": analyst.id,
            "assigned_to_id": manager.id,
        },
        {
            "customer_id": "CUST-004",
            "account_id": "ACC-004",
            "order_reference": "ORD-1004",
            "requested_terms": "Net 30",
            "requested_outcome": "Standard Release",
            "requested_fulfilment_date": datetime.utcnow() + timedelta(days=5),
            "current_status": CaseStatus.APPROVED,
            "priority": "Medium",
            "exception_flag": False,
            "risk_band": RiskBand.LOW,
            "created_by_id": analyst.id,
            "assigned_to_id": csm.id,
        },
        {
            "customer_id": "CUST-005",
            "account_id": "ACC-005",
            "order_reference": "ORD-1005",
            "requested_terms": "Net 45",
            "requested_outcome": "Contract Amendment",
            "requested_fulfilment_date": datetime.utcnow() + timedelta(days=30),
            "current_status": CaseStatus.ON_HOLD,
            "priority": "Low",
            "exception_flag": False,
            "risk_band": RiskBand.MEDIUM,
            "created_by_id": analyst.id,
            "assigned_to_id": analyst.id,
        },
        {
            "customer_id": "CUST-006",
            "account_id": "ACC-006",
            "order_reference": "ORD-1006",
            "requested_terms": "Net 30",
            "requested_outcome": "Credit Decline",
            "requested_fulfilment_date": None,
            "current_status": CaseStatus.DECLINED,
            "priority": "Medium",
            "exception_flag": False,
            "risk_band": RiskBand.VERY_HIGH,
            "created_by_id": analyst.id,
            "assigned_to_id": None,
        },
        {
            "customer_id": "CUST-007",
            "account_id": "ACC-007",
            "order_reference": "ORD-1007",
            "requested_terms": "Net 60",
            "requested_outcome": "Large Enterprise Release",
            "requested_fulfilment_date": datetime.utcnow() + timedelta(days=21),
            "current_status": CaseStatus.PENDING_APPROVAL,
            "priority": "High",
            "exception_flag": True,
            "risk_band": RiskBand.VERY_HIGH,
            "created_by_id": analyst.id,
            "assigned_to_id": vp.id,
        },
        {
            "customer_id": "CUST-008",
            "account_id": "ACC-008",
            "order_reference": "ORD-1008",
            "requested_terms": "Net 30",
            "requested_outcome": "Standard Release",
            "requested_fulfilment_date": datetime.utcnow() + timedelta(days=7),
            "current_status": CaseStatus.RELEASED,
            "priority": "Medium",
            "exception_flag": False,
            "risk_band": RiskBand.LOW,
            "created_by_id": analyst.id,
            "assigned_to_id": csm.id,
        },
        {
            "customer_id": "CUST-009",
            "account_id": "ACC-009",
            "order_reference": "ORD-1009",
            "requested_terms": "Net 45",
            "requested_outcome": "Renewal Review",
            "requested_fulfilment_date": datetime.utcnow() + timedelta(days=60),
            "current_status": CaseStatus.IN_REVIEW,
            "priority": "Medium",
            "exception_flag": False,
            "risk_band": RiskBand.MEDIUM,
            "created_by_id": analyst.id,
            "assigned_to_id": analyst.id,
        },
        {
            "customer_id": "CUST-010",
            "account_id": "ACC-010",
            "order_reference": "ORD-1010",
            "requested_terms": "Net 30",
            "requested_outcome": "Priority Release",
            "requested_fulfilment_date": datetime.utcnow() + timedelta(days=3),
            "current_status": CaseStatus.APPROVED,
            "priority": "High",
            "exception_flag": False,
            "risk_band": RiskBand.LOW,
            "created_by_id": analyst.id,
            "assigned_to_id": csm.id,
        },
        {
            "customer_id": "CUST-011",
            "account_id": "ACC-011",
            "order_reference": "ORD-1011",
            "requested_terms": "Net 60",
            "requested_outcome": "Exception Request",
            "requested_fulfilment_date": datetime.utcnow() + timedelta(days=14),
            "current_status": CaseStatus.PENDING_APPROVAL,
            "priority": "High",
            "exception_flag": True,
            "risk_band": RiskBand.HIGH,
            "created_by_id": analyst.id,
            "assigned_to_id": manager.id,
        },
        {
            "customer_id": "CUST-012",
            "account_id": "ACC-012",
            "order_reference": "ORD-1012",
            "requested_terms": "Net 30",
            "requested_outcome": "Standard Release",
            "requested_fulfilment_date": datetime.utcnow() + timedelta(days=5),
            "current_status": CaseStatus.NEW,
            "priority": "Low",
            "exception_flag": False,
            "risk_band": RiskBand.LOW,
            "created_by_id": analyst.id,
            "assigned_to_id": analyst.id,
        },
    ]

    for case_data in cases_data:
        existing_case = db.query(Case).filter(
            Case.order_reference == case_data["order_reference"]
        ).first()

        if not existing_case:
            case_data["retention_until"] = retention_7_years
            case = Case(**case_data, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
            db.add(case)
            db.flush()

            # Add credit assessment for some cases
            if case.current_status in [CaseStatus.IN_REVIEW, CaseStatus.PENDING_APPROVAL, CaseStatus.APPROVED]:
                assessment = CreditAssessment(
                    case_id=case.id,
                    assessment_data={"credit_score": 720, "exposure": 150000, "payment_history": "Good"},
                    recommendation=OutcomeType.RELEASE if case.risk_band in [RiskBand.LOW, RiskBand.MEDIUM] else OutcomeType.HOLD,
                    rationale="Based on credit score and payment history",
                    assessed_by_id=analyst.id,
                    assessed_at=datetime.utcnow()
                )
                db.add(assessment)

            # Add approval requests for cases in pending approval status
            if case.current_status == CaseStatus.PENDING_APPROVAL:
                approval = ApprovalRequest(
                    case_id=case.id,
                    requested_by_id=analyst.id,
                    assigned_approver_id=case.assigned_to_id,
                    status=ApprovalStatus.PENDING,
                    justification=f"Exception approval required for {case.order_reference}",
                    approval_level="Manager" if case.assigned_to_id == manager.id else "Executive",
                    created_at=datetime.utcnow(),
                    retention_until=retention_7_years
                )
                db.add(approval)

    db.commit()
    print(f"Seeded {len(cases_data)} sample cases with assessments and approvals")


def run_seed() -> None:
    """
    Execute seed data generation.
    Idempotent - checks existence before inserting.
    """
    print("Starting seed data generation...")

    # Initialize database
    init_db()

    # Create session
    db = SessionLocal()

    try:
        # Seed in dependency order
        roles = seed_roles(db)
        users = seed_users(db, roles)
        seed_authority_rules(db)
        seed_sod_rules(db)
        seed_sample_cases(db, users)

        print("Seed data generation complete!")
        print("\nDefault credentials:")
        print("  analyst@example.com / password123")
        print("  csm@example.com / password123")
        print("  manager@example.com / password123")
        print("  vp@example.com / password123")
    except Exception as e:
        print(f"Error during seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
