"""
Decision service for credit assessment and recommendation capture.
Orchestrates assessment recording and outcome finalization.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.enums import CaseStatus, OutcomeType
from app.domain.models import Case, CreditAssessment
from app.repositories.case_repository import CaseRepository
from app.services.audit_service import AuditService
from app.shared.errors import NotFoundError


class DecisionService:
    """
    Service for credit assessment and recommendation handling.
    Captures analyst findings and final outcomes.
    """

    def __init__(self, db: Session):
        self.db = db
        self.case_repo = CaseRepository(db)
        self.audit_service = AuditService(db)

    def submit_recommendation(
        self,
        case_id: int,
        assessment_data: Optional[dict],
        recommendation: OutcomeType,
        rationale: str,
        assessed_by_id: int
    ) -> CreditAssessment:
        """
        Submit credit assessment recommendation for a case.

        Args:
            case_id: Case ID being assessed
            assessment_data: Optional structured assessment data
            recommendation: Recommended outcome (RELEASE, HOLD, AMEND, DECLINE)
            rationale: Justification for recommendation
            assessed_by_id: User ID of analyst submitting recommendation

        Returns:
            Created CreditAssessment
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case", str(case_id))

        # Create assessment
        assessment = CreditAssessment(
            case_id=case_id,
            assessment_data=assessment_data,
            recommendation=recommendation,
            rationale=rationale,
            assessed_by_id=assessed_by_id,
            assessed_at=datetime.utcnow()
        )

        saved_assessment = self.case_repo.add_assessment(assessment)

        # Audit the recommendation
        self.audit_service.append_event(
            entity_type="CreditAssessment",
            entity_id=saved_assessment.id,
            action_type="SUBMIT_RECOMMENDATION",
            actor_id=assessed_by_id,
            payload={
                "case_id": case_id,
                "recommendation": recommendation.value,
                "rationale": rationale
            }
        )

        return saved_assessment

    def finalize_outcome(
        self,
        case_id: int,
        outcome: OutcomeType,
        actor_id: int,
        notes: Optional[str] = None
    ) -> Case:
        """
        Finalize case outcome after assessment and approvals.

        Args:
            case_id: Case ID to finalize
            outcome: Final outcome (RELEASE, HOLD, AMEND, DECLINE)
            actor_id: User ID finalizing the outcome
            notes: Optional finalization notes

        Returns:
            Updated Case with final status
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case", str(case_id))

        # Map outcome to case status
        status_map = {
            OutcomeType.RELEASE: CaseStatus.APPROVED,
            OutcomeType.HOLD: CaseStatus.ON_HOLD,
            OutcomeType.AMEND: CaseStatus.APPROVED,  # Amended approval
            OutcomeType.DECLINE: CaseStatus.DECLINED
        }

        case.current_status = status_map.get(outcome, CaseStatus.IN_REVIEW)
        updated_case = self.case_repo.update(case)

        # Audit the outcome finalization
        self.audit_service.append_event(
            entity_type="Case",
            entity_id=case_id,
            action_type="FINALIZE_OUTCOME",
            actor_id=actor_id,
            payload={
                "outcome": outcome.value,
                "status": updated_case.current_status.value,
                "notes": notes
            }
        )

        return updated_case
