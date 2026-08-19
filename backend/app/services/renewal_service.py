"""
Renewal service for account renewal review tracking.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.enums import RenewalStatus
from app.domain.models import RenewalReview
from app.services.audit_service import AuditService


class RenewalService:
    """
    Service for renewal review lifecycle management.
    """

    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    def create_or_update_renewal(
        self,
        case_id: int,
        actor_id: int,
        renewal_risk_summary: Optional[str] = None,
        status: RenewalStatus = RenewalStatus.PENDING_REVIEW,
        review_notes: Optional[str] = None
    ) -> RenewalReview:
        """
        Create or update renewal review record.

        Args:
            case_id: Case ID
            actor_id: User performing action
            renewal_risk_summary: Risk summary for renewal
            status: Renewal status
            review_notes: Optional review notes

        Returns:
            RenewalReview
        """
        # Check if renewal exists for this case
        existing = self.db.query(RenewalReview).filter(
            RenewalReview.case_id == case_id
        ).first()

        if existing:
            # Update existing
            existing.renewal_risk_summary = renewal_risk_summary
            existing.status = status
            existing.review_notes = review_notes
            existing.updated_at = datetime.utcnow()

            if status in [RenewalStatus.APPROVED, RenewalStatus.DECLINED]:
                existing.reviewed_at = datetime.utcnow()

            renewal = existing
            action_type = "UPDATE_RENEWAL"
        else:
            # Create new
            renewal = RenewalReview(
                case_id=case_id,
                renewal_risk_summary=renewal_risk_summary,
                status=status,
                review_notes=review_notes,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(renewal)
            self.db.flush()
            action_type = "CREATE_RENEWAL"

        # Append audit event
        self.audit_service.append_event(
            entity_type="RenewalReview",
            entity_id=renewal.id,
            action_type=action_type,
            actor_id=actor_id,
            payload={
                "case_id": case_id,
                "renewal_risk_summary": renewal_risk_summary,
                "status": status.value,
                "review_notes": review_notes
            }
        )

        self.db.commit()
        self.db.refresh(renewal)
        return renewal

    def list_renewals_for_case(self, case_id: int) -> list[RenewalReview]:
        """
        List all renewal reviews for a case.

        Args:
            case_id: Case ID

        Returns:
            List of RenewalReviews
        """
        return self.db.query(RenewalReview).filter(
            RenewalReview.case_id == case_id
        ).order_by(RenewalReview.created_at.desc()).all()
