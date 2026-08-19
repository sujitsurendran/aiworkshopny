"""
Authority policy service for delegation-of-authority rule evaluation.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.enums import OutcomeType, RiskBand
from app.domain.models import AuthorityRule


class AuthorityPolicyService:
    """
    Service for evaluating delegation-of-authority rules.
    """

    def __init__(self, db: Session):
        self.db = db

    def evaluate_authority(
        self,
        role_name: str,
        outcome_type: OutcomeType,
        risk_band: Optional[RiskBand] = None,
        exposure_amount: Optional[float] = None
    ) -> dict:
        """
        Evaluate authority rules and return eligible approver level.

        Args:
            role_name: User role name
            outcome_type: Requested outcome type
            risk_band: Risk band classification
            exposure_amount: Financial exposure amount

        Returns:
            Dict with eligible, required_level, reasons
        """
        # Query authority rules matching role and outcome
        query = self.db.query(AuthorityRule).filter(
            AuthorityRule.role_name == role_name,
            AuthorityRule.outcome_type == outcome_type
        )

        if risk_band:
            query = query.filter(
                (AuthorityRule.risk_band == risk_band) | (AuthorityRule.risk_band.is_(None))
            )

        rules = query.all()

        if not rules:
            # No matching rules, requires escalation
            return {
                "eligible": False,
                "required_level": "Sales Operations Manager",
                "reasons": ["No matching authority rule found"]
            }

        # Check exposure amount against rule thresholds
        eligible = False
        required_level = "Sales Operations Manager"
        reasons = []

        for rule in rules:
            if rule.executive_approval_required:
                required_level = "VP Sales / Commercial Director"
                reasons.append("Executive approval required by policy")
                continue

            if rule.max_exposure_amount is not None and exposure_amount is not None:
                if exposure_amount <= rule.max_exposure_amount:
                    eligible = True
                    required_level = rule.role_name
                    reasons.append(f"Within authority threshold: {rule.max_exposure_amount}")
                else:
                    reasons.append(f"Exceeds authority threshold: {rule.max_exposure_amount}")
            else:
                eligible = True
                required_level = rule.role_name
                reasons.append("Authority granted by rule")

        return {
            "eligible": eligible,
            "required_level": required_level,
            "reasons": reasons
        }

    def get_authority_rules(self, role_name: str) -> list[AuthorityRule]:
        """
        Get all authority rules for a role.

        Args:
            role_name: Role name

        Returns:
            List of AuthorityRule
        """
        return self.db.query(AuthorityRule).filter(
            AuthorityRule.role_name == role_name
        ).all()
