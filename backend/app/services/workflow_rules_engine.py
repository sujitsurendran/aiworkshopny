"""
Workflow rules engine for state transitions, routing logic, and authority evaluation.
Evaluates delegation-of-authority thresholds and exception classification.
"""
from typing import Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.domain.enums import OutcomeType, RiskBand
from app.domain.models import AuthorityRule, Case


class AuthorityEvaluationResult(BaseModel):
    """
    Result of authority evaluation matching LLD contract.
    Contains routing decision and control check outcomes.
    """
    eligible: bool
    required_level: Optional[str] = None
    reasons: list[str] = []
    sod_violation: bool = False


class WorkflowRulesEngine:
    """
    Evaluates workflow rules for case submission, approval routing, and state transitions.
    Pure business logic without external dependencies.
    """

    def __init__(self, db: Session):
        self.db = db

    def evaluate_submission(
        self,
        case: Case,
        assessment_recommendation: Optional[OutcomeType],
        actor_role: str,
        actor_id: int,
        requester_id: int
    ) -> AuthorityEvaluationResult:
        """
        Evaluate case submission for approval routing requirements.

        Args:
            case: Case being evaluated
            assessment_recommendation: Analyst's recommendation
            actor_role: Current actor's role
            actor_id: Current actor's user ID
            requester_id: Original requester's user ID

        Returns:
            AuthorityEvaluationResult with routing decision
        """
        reasons = []

        # Check segregation of duties
        sod_violation = self._check_sod_violation(actor_id, requester_id)
        if sod_violation:
            reasons.append("SoD violation: Cannot approve own request")

        # Check authority rules
        authority_result = self._check_authority_rules(
            actor_role=actor_role,
            outcome_type=assessment_recommendation,
            risk_band=case.risk_band
        )

        if not authority_result["eligible"]:
            reasons.append(
                f"Authority threshold exceeded: requires {authority_result['required_level']}"
            )

        # Determine if exception flag requires escalation
        if case.exception_flag:
            reasons.append("Exception flag set: requires manager review")
            return AuthorityEvaluationResult(
                eligible=False,
                required_level="Sales Operations Manager",
                reasons=reasons,
                sod_violation=sod_violation
            )

        return AuthorityEvaluationResult(
            eligible=authority_result["eligible"] and not sod_violation,
            required_level=authority_result.get("required_level"),
            reasons=reasons,
            sod_violation=sod_violation
        )

    def _check_authority_rules(
        self,
        actor_role: str,
        outcome_type: Optional[OutcomeType],
        risk_band: Optional[RiskBand]
    ) -> dict:
        """
        Check delegation-of-authority rules against actor role and case context.

        Returns:
            Dict with 'eligible' boolean and optional 'required_level'
        """
        if not outcome_type:
            return {"eligible": True}

        # Query authority rules matching role, outcome, and risk band
        rules = (
            self.db.query(AuthorityRule)
            .filter(
                AuthorityRule.role_name == actor_role,
                AuthorityRule.outcome_type == outcome_type
            )
            .all()
        )

        # If no rules exist for this combination, default to requiring approval
        if not rules:
            return {
                "eligible": False,
                "required_level": "Sales Operations Manager"
            }

        # Check if any rule permits auto-finalize
        for rule in rules:
            if rule.risk_band == risk_band or rule.risk_band is None:
                if not rule.executive_approval_required:
                    return {"eligible": True}
                else:
                    return {
                        "eligible": False,
                        "required_level": "VP Sales / Commercial Director"
                    }

        # Default to requiring manager approval
        return {
            "eligible": False,
            "required_level": "Sales Operations Manager"
        }

    def _check_sod_violation(self, actor_id: int, requester_id: int) -> bool:
        """
        Check segregation-of-duties rules.
        Returns True if actor cannot approve/reject/send_back their own request.
        """
        # Core SoD rule: actor cannot act on their own request
        return actor_id == requester_id
