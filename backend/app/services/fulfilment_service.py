"""
Fulfilment service for tracking milestones and blockers.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.enums import FulfilmentStatus
from app.domain.models import FulfilmentRecord
from app.services.audit_service import AuditService


class FulfilmentService:
    """
    Service for fulfilment milestone tracking.
    """

    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    def create_or_update_fulfilment(
        self,
        case_id: int,
        actor_id: int,
        milestone_name: str,
        status: FulfilmentStatus,
        blocker_description: Optional[str] = None
    ) -> FulfilmentRecord:
        """
        Create or update fulfilment milestone record.

        Args:
            case_id: Case ID
            actor_id: User performing action
            milestone_name: Milestone name
            status: Fulfilment status
            blocker_description: Optional blocker description

        Returns:
            FulfilmentRecord
        """
        # Check if milestone exists
        existing = self.db.query(FulfilmentRecord).filter(
            FulfilmentRecord.case_id == case_id,
            FulfilmentRecord.milestone_name == milestone_name
        ).first()

        if existing:
            # Update existing
            existing.status = status
            existing.blocker_description = blocker_description
            existing.updated_at = datetime.utcnow()

            if status == FulfilmentStatus.COMPLETED:
                existing.completed_at = datetime.utcnow()

            fulfilment = existing
            action_type = "UPDATE_FULFILMENT"
        else:
            # Create new
            fulfilment = FulfilmentRecord(
                case_id=case_id,
                milestone_name=milestone_name,
                status=status,
                blocker_description=blocker_description,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            if status == FulfilmentStatus.COMPLETED:
                fulfilment.completed_at = datetime.utcnow()

            self.db.add(fulfilment)
            self.db.flush()
            action_type = "CREATE_FULFILMENT"

        # Append audit event
        self.audit_service.append_event(
            entity_type="FulfilmentRecord",
            entity_id=fulfilment.id,
            action_type=action_type,
            actor_id=actor_id,
            payload={
                "case_id": case_id,
                "milestone_name": milestone_name,
                "status": status.value,
                "blocker_description": blocker_description
            }
        )

        self.db.commit()
        self.db.refresh(fulfilment)
        return fulfilment

    def list_fulfilment_for_case(self, case_id: int) -> list[FulfilmentRecord]:
        """
        List all fulfilment records for a case.

        Args:
            case_id: Case ID

        Returns:
            List of FulfilmentRecords
        """
        return self.db.query(FulfilmentRecord).filter(
            FulfilmentRecord.case_id == case_id
        ).order_by(FulfilmentRecord.created_at.desc()).all()
