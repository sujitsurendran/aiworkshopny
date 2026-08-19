"""
Case service orchestrating case CRUD operations.
Handles case creation, updates, retrieval, and status transitions.
"""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.enums import CaseStatus
from app.domain.models import Case
from app.repositories.case_repository import CaseRepository
from app.services.audit_service import AuditService
from app.shared.errors import NotFoundError, ValidationError
from app.shared.pagination import PaginatedResponse


class CaseService:
    """
    Service for case management operations.
    Orchestrates case CRUD, state transitions, and audit logging.
    """

    def __init__(self, db: Session):
        self.db = db
        self.case_repo = CaseRepository(db)
        self.audit_service = AuditService(db)

    def create_case(
        self,
        customer_id: str,
        order_reference: str,
        requested_terms: Optional[str],
        requested_outcome: Optional[str],
        requested_fulfilment_date: Optional[datetime],
        created_by_id: int,
        priority: str = "Medium",
        account_id: Optional[str] = None
    ) -> Case:
        """
        Create a new case with intake data.

        Args:
            customer_id: Customer identifier (required)
            order_reference: Order reference (required)
            requested_terms: Requested payment terms
            requested_outcome: Requested outcome type
            requested_fulfilment_date: Requested fulfilment date
            created_by_id: User ID creating the case
            priority: Case priority (default "Medium")
            account_id: Optional account identifier

        Returns:
            Created Case
        """
        # Validation
        if not customer_id or not order_reference:
            raise ValidationError("customer_id and order_reference are required")

        # Create case with 7-year retention
        case = Case(
            customer_id=customer_id,
            account_id=account_id,
            order_reference=order_reference,
            requested_terms=requested_terms,
            requested_outcome=requested_outcome,
            requested_fulfilment_date=requested_fulfilment_date,
            current_status=CaseStatus.NEW,
            priority=priority,
            exception_flag=False,
            created_by_id=created_by_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            retention_until=datetime.utcnow() + timedelta(days=365 * 7)  # 7 years
        )

        created_case = self.case_repo.create(case)

        # Audit case creation
        self.audit_service.append_event(
            entity_type="Case",
            entity_id=created_case.id,
            action_type="CREATE",
            actor_id=created_by_id,
            payload={
                "customer_id": customer_id,
                "order_reference": order_reference,
                "status": CaseStatus.NEW.value
            }
        )

        return created_case

    def get_case_detail(self, case_id: int) -> Case:
        """
        Retrieve full case detail with all relationships.

        Args:
            case_id: Case ID

        Returns:
            Case with nested intake, assessment, approvals, operations

        Raises:
            NotFoundError: If case does not exist
        """
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case", str(case_id))
        return case

    def list_cases(
        self,
        filters: Optional[dict] = None,
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedResponse:
        """
        List cases with filtering and pagination.

        Args:
            filters: Optional filter dict (status, exception_flag, assigned_to_id, customer_id)
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            PaginatedResponse with items, total, page, page_size
        """
        items, total = self.case_repo.list_cases(
            filters=filters or {},
            page=page,
            page_size=page_size
        )

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )

    def update_case(
        self,
        case_id: int,
        actor_id: int,
        updates: dict
    ) -> Case:
        """
        Update case fields.

        Args:
            case_id: Case ID to update
            actor_id: User ID performing update
            updates: Dict of field updates

        Returns:
            Updated Case
        """
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case", str(case_id))

        # Apply permitted updates
        permitted_fields = [
            "requested_terms", "requested_outcome", "requested_fulfilment_date",
            "priority", "exception_flag", "risk_band", "assigned_to_id", "current_status"
        ]

        changed_fields = {}
        for field, value in updates.items():
            if field in permitted_fields and hasattr(case, field):
                old_value = getattr(case, field)
                setattr(case, field, value)
                changed_fields[field] = {"old": str(old_value), "new": str(value)}

        updated_case = self.case_repo.update(case)

        # Audit the update
        if changed_fields:
            self.audit_service.append_event(
                entity_type="Case",
                entity_id=case_id,
                action_type="UPDATE",
                actor_id=actor_id,
                payload={"changes": changed_fields}
            )

        return updated_case
