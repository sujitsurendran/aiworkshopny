"""
Complaint service for complaint management linked to cases.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.enums import ComplaintStatus
from app.domain.models import ComplaintRecord
from app.services.audit_service import AuditService


class ComplaintService:
    """
    Service for complaint lifecycle management.
    """

    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    def create_complaint(
        self,
        case_id: int,
        actor_id: int,
        complaint_description: str
    ) -> ComplaintRecord:
        """
        Create complaint record linked to case.

        Args:
            case_id: Case ID
            actor_id: User creating complaint
            complaint_description: Description of complaint

        Returns:
            ComplaintRecord
        """
        complaint = ComplaintRecord(
            case_id=case_id,
            complaint_description=complaint_description,
            status=ComplaintStatus.OPEN,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(complaint)
        self.db.flush()

        # Append audit event
        self.audit_service.append_event(
            entity_type="ComplaintRecord",
            entity_id=complaint.id,
            action_type="CREATE_COMPLAINT",
            actor_id=actor_id,
            payload={
                "case_id": case_id,
                "complaint_description": complaint_description
            }
        )

        self.db.commit()
        self.db.refresh(complaint)
        return complaint

    def update_complaint(
        self,
        complaint_id: int,
        actor_id: int,
        status: Optional[ComplaintStatus] = None,
        resolution_notes: Optional[str] = None
    ) -> ComplaintRecord:
        """
        Update complaint status and resolution notes.

        Args:
            complaint_id: Complaint ID
            actor_id: User updating complaint
            status: New status
            resolution_notes: Resolution notes

        Returns:
            Updated ComplaintRecord
        """
        complaint = self.db.query(ComplaintRecord).filter(
            ComplaintRecord.id == complaint_id
        ).first()

        if not complaint:
            raise ValueError(f"Complaint {complaint_id} not found")

        if status:
            complaint.status = status
            if status == ComplaintStatus.RESOLVED:
                complaint.resolved_at = datetime.utcnow()

        if resolution_notes:
            complaint.resolution_notes = resolution_notes

        complaint.updated_at = datetime.utcnow()

        # Append audit event
        self.audit_service.append_event(
            entity_type="ComplaintRecord",
            entity_id=complaint_id,
            action_type="UPDATE_COMPLAINT",
            actor_id=actor_id,
            payload={
                "status": status.value if status else None,
                "resolution_notes": resolution_notes
            }
        )

        self.db.commit()
        self.db.refresh(complaint)
        return complaint

    def list_complaints_for_case(self, case_id: int) -> list[ComplaintRecord]:
        """
        List all complaints for a case.

        Args:
            case_id: Case ID

        Returns:
            List of ComplaintRecords
        """
        return self.db.query(ComplaintRecord).filter(
            ComplaintRecord.case_id == case_id
        ).order_by(ComplaintRecord.created_at.desc()).all()
