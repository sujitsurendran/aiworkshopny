"""
Refund service for returns and refund processing with financial impact validation.
"""
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domain.enums import RefundStatus
from app.domain.models import RefundRecord
from app.services.audit_service import AuditService


class RefundService:
    """
    Service for refund and return record management.
    """

    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    def create_refund(
        self,
        case_id: int,
        actor_id: int,
        refund_amount: float,
        financial_impact_flag: bool,
        evidence_confirmed: bool
    ) -> RefundRecord:
        """
        Create refund record with financial impact validation.

        Args:
            case_id: Case ID
            actor_id: User creating refund
            refund_amount: Refund amount
            financial_impact_flag: Whether refund has significant financial impact
            evidence_confirmed: Whether evidence has been confirmed

        Returns:
            RefundRecord

        Raises:
            HTTPException: 422 if significant refund lacks evidence confirmation
        """
        # Validate evidence for significant refunds
        if financial_impact_flag and not evidence_confirmed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "CTRL_001",
                    "message": "Refund cannot be completed because required evidence is missing.",
                    "details": [
                        {
                            "field": "evidence_confirmed",
                            "issue": "required_for_financially_significant_refund"
                        }
                    ]
                }
            )

        refund = RefundRecord(
            case_id=case_id,
            refund_amount=refund_amount,
            financial_impact_flag=financial_impact_flag,
            evidence_confirmed=evidence_confirmed,
            status=RefundStatus.REQUESTED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(refund)
        self.db.flush()

        # Append audit event
        self.audit_service.append_event(
            entity_type="RefundRecord",
            entity_id=refund.id,
            action_type="CREATE_REFUND",
            actor_id=actor_id,
            payload={
                "case_id": case_id,
                "refund_amount": refund_amount,
                "financial_impact_flag": financial_impact_flag,
                "evidence_confirmed": evidence_confirmed
            }
        )

        self.db.commit()
        self.db.refresh(refund)
        return refund

    def update_refund_status(
        self,
        refund_id: int,
        actor_id: int,
        status: RefundStatus
    ) -> RefundRecord:
        """
        Update refund status.

        Args:
            refund_id: Refund ID
            actor_id: User updating status
            status: New status

        Returns:
            Updated RefundRecord
        """
        refund = self.db.query(RefundRecord).filter(
            RefundRecord.id == refund_id
        ).first()

        if not refund:
            raise ValueError(f"Refund {refund_id} not found")

        refund.status = status
        refund.updated_at = datetime.utcnow()

        if status == RefundStatus.PROCESSED:
            refund.processed_at = datetime.utcnow()

        # Append audit event
        self.audit_service.append_event(
            entity_type="RefundRecord",
            entity_id=refund_id,
            action_type="UPDATE_REFUND",
            actor_id=actor_id,
            payload={
                "status": status.value
            }
        )

        self.db.commit()
        self.db.refresh(refund)
        return refund

    def list_refunds_for_case(self, case_id: int) -> list[RefundRecord]:
        """
        List all refunds for a case.

        Args:
            case_id: Case ID

        Returns:
            List of RefundRecords
        """
        return self.db.query(RefundRecord).filter(
            RefundRecord.case_id == case_id
        ).order_by(RefundRecord.created_at.desc()).all()
