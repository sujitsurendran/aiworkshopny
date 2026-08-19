"""
Approval repository for database access to approval_requests table.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.models import ApprovalRequest


class ApprovalRepository:
    """
    Repository for ApprovalRequest database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, approval_request_id: int) -> Optional[ApprovalRequest]:
        """
        Get approval request by ID.

        Args:
            approval_request_id: Approval request ID

        Returns:
            ApprovalRequest or None
        """
        return self.db.query(ApprovalRequest).filter(
            ApprovalRequest.id == approval_request_id
        ).first()

    def list_by_case(self, case_id: int) -> list[ApprovalRequest]:
        """
        List all approval requests for a case.

        Args:
            case_id: Case ID

        Returns:
            List of ApprovalRequests
        """
        return self.db.query(ApprovalRequest).filter(
            ApprovalRequest.case_id == case_id
        ).order_by(ApprovalRequest.created_at.desc()).all()

    def list_by_status(self, status: str, assigned_approver_id: Optional[int] = None) -> list[ApprovalRequest]:
        """
        List approval requests by status, optionally filtered by assigned approver.

        Args:
            status: Approval status
            assigned_approver_id: Optional approver ID filter

        Returns:
            List of ApprovalRequests
        """
        query = self.db.query(ApprovalRequest).filter(
            ApprovalRequest.status == status
        )

        if assigned_approver_id:
            query = query.filter(ApprovalRequest.assigned_approver_id == assigned_approver_id)

        return query.order_by(ApprovalRequest.created_at.desc()).all()
