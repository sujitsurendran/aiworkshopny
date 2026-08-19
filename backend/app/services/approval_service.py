"""
Approval service for approval request creation, approve/reject/send-back actions,
SoD enforcement, and authority policy evaluation.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domain.enums import ApprovalStatus, CaseStatus
from app.domain.models import ApprovalRequest, Case
from app.repositories.approval_repository import ApprovalRepository
from app.security.authorization import check_sod_violation
from app.services.audit_service import AuditService


class ApprovalService:
    """
    Service for approval authority handling with SoD enforcement.
    """

    def __init__(self, db: Session):
        self.db = db
        self.approval_repo = ApprovalRepository(db)
        self.audit_service = AuditService(db)

    def create_approval_request(
        self,
        case_id: int,
        requested_by_id: int,
        justification: str,
        approval_level: str,
        assigned_approver_id: Optional[int] = None
    ) -> ApprovalRequest:
        """
        Create approval request linked to case.

        Args:
            case_id: Case requiring approval
            requested_by_id: User who requested approval
            justification: Reason for approval request
            approval_level: Authority level required
            assigned_approver_id: Optional specific approver

        Returns:
            Created ApprovalRequest
        """
        # Create approval request
        approval_request = ApprovalRequest(
            case_id=case_id,
            requested_by_id=requested_by_id,
            assigned_approver_id=assigned_approver_id,
            status=ApprovalStatus.PENDING,
            justification=justification,
            approval_level=approval_level,
            created_at=datetime.utcnow(),
            retention_until=datetime.utcnow() + timedelta(days=365 * 7)
        )

        self.db.add(approval_request)
        self.db.flush()

        # Append audit event
        self.audit_service.append_event(
            entity_type="ApprovalRequest",
            entity_id=approval_request.id,
            action_type="REQUEST_APPROVAL",
            actor_id=requested_by_id,
            payload={
                "case_id": case_id,
                "justification": justification,
                "approval_level": approval_level
            }
        )

        self.db.commit()
        self.db.refresh(approval_request)
        return approval_request

    def approve_request(
        self,
        approval_request_id: int,
        actor_id: int,
        decision_reason: Optional[str] = None
    ) -> ApprovalRequest:
        """
        Approve an approval request with SoD enforcement.

        Args:
            approval_request_id: ID of approval request
            actor_id: User performing approval
            decision_reason: Optional reason for decision

        Returns:
            Updated ApprovalRequest

        Raises:
            HTTPException: 403 if SoD violation detected
            HTTPException: 404 if approval request not found
            HTTPException: 409 if approval already decided
        """
        approval_request = self.approval_repo.get_by_id(approval_request_id)

        if not approval_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NF_001", "message": "Approval request not found"}
            )

        # Check if already decided
        if approval_request.status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "STATE_002", "message": "Approval request already decided"}
            )

        # SoD check: actor cannot approve their own request
        if check_sod_violation(actor_id, approval_request.requested_by_id, "approve"):
            # Append audit event for control violation
            self.audit_service.append_event(
                entity_type="ApprovalRequest",
                entity_id=approval_request_id,
                action_type="SOD_VIOLATION",
                actor_id=actor_id,
                payload={
                    "action": "approve",
                    "requested_by": approval_request.requested_by_id,
                    "violation": "self_approval"
                }
            )
            self.db.commit()

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "AUTHZ_001", "message": "Segregation of duties violation: You cannot approve your own request"}
            )

        # Update approval request
        approval_request.status = ApprovalStatus.APPROVED
        approval_request.decision_reason = decision_reason
        approval_request.decided_at = datetime.utcnow()

        # Update case status
        case = self.db.query(Case).filter(Case.id == approval_request.case_id).first()
        if case:
            case.current_status = CaseStatus.APPROVED

        # Append audit event
        self.audit_service.append_event(
            entity_type="ApprovalRequest",
            entity_id=approval_request_id,
            action_type="APPROVE",
            actor_id=actor_id,
            payload={
                "case_id": approval_request.case_id,
                "decision_reason": decision_reason
            }
        )

        self.db.commit()
        self.db.refresh(approval_request)
        return approval_request

    def reject_request(
        self,
        approval_request_id: int,
        actor_id: int,
        decision_reason: str
    ) -> ApprovalRequest:
        """
        Reject an approval request with SoD enforcement.

        Args:
            approval_request_id: ID of approval request
            actor_id: User performing rejection
            decision_reason: Reason for rejection

        Returns:
            Updated ApprovalRequest

        Raises:
            HTTPException: 403 if SoD violation detected
            HTTPException: 404 if approval request not found
        """
        approval_request = self.approval_repo.get_by_id(approval_request_id)

        if not approval_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NF_001", "message": "Approval request not found"}
            )

        # SoD check
        if check_sod_violation(actor_id, approval_request.requested_by_id, "reject"):
            self.audit_service.append_event(
                entity_type="ApprovalRequest",
                entity_id=approval_request_id,
                action_type="SOD_VIOLATION",
                actor_id=actor_id,
                payload={
                    "action": "reject",
                    "requested_by": approval_request.requested_by_id,
                    "violation": "self_rejection"
                }
            )
            self.db.commit()

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "AUTHZ_001", "message": "Segregation of duties violation: You cannot reject your own request"}
            )

        # Update approval request
        approval_request.status = ApprovalStatus.REJECTED
        approval_request.decision_reason = decision_reason
        approval_request.decided_at = datetime.utcnow()

        # Update case status
        case = self.db.query(Case).filter(Case.id == approval_request.case_id).first()
        if case:
            case.current_status = CaseStatus.REJECTED

        # Append audit event
        self.audit_service.append_event(
            entity_type="ApprovalRequest",
            entity_id=approval_request_id,
            action_type="REJECT",
            actor_id=actor_id,
            payload={
                "case_id": approval_request.case_id,
                "decision_reason": decision_reason
            }
        )

        self.db.commit()
        self.db.refresh(approval_request)
        return approval_request

    def send_back_request(
        self,
        approval_request_id: int,
        actor_id: int,
        decision_reason: str
    ) -> ApprovalRequest:
        """
        Send back an approval request for rework with SoD enforcement.

        Args:
            approval_request_id: ID of approval request
            actor_id: User sending back request
            decision_reason: Reason for sending back

        Returns:
            Updated ApprovalRequest

        Raises:
            HTTPException: 403 if SoD violation detected
            HTTPException: 404 if approval request not found
        """
        approval_request = self.approval_repo.get_by_id(approval_request_id)

        if not approval_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NF_001", "message": "Approval request not found"}
            )

        # SoD check
        if check_sod_violation(actor_id, approval_request.requested_by_id, "send_back"):
            self.audit_service.append_event(
                entity_type="ApprovalRequest",
                entity_id=approval_request_id,
                action_type="SOD_VIOLATION",
                actor_id=actor_id,
                payload={
                    "action": "send_back",
                    "requested_by": approval_request.requested_by_id,
                    "violation": "self_send_back"
                }
            )
            self.db.commit()

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "AUTHZ_001", "message": "Segregation of duties violation: You cannot send back your own request"}
            )

        # Update approval request
        approval_request.status = ApprovalStatus.SENT_BACK
        approval_request.decision_reason = decision_reason
        approval_request.decided_at = datetime.utcnow()

        # Update case status
        case = self.db.query(Case).filter(Case.id == approval_request.case_id).first()
        if case:
            case.current_status = CaseStatus.REWORK_REQUIRED

        # Append audit event
        self.audit_service.append_event(
            entity_type="ApprovalRequest",
            entity_id=approval_request_id,
            action_type="SEND_BACK",
            actor_id=actor_id,
            payload={
                "case_id": approval_request.case_id,
                "decision_reason": decision_reason
            }
        )

        self.db.commit()
        self.db.refresh(approval_request)
        return approval_request

    def list_approvals_for_case(self, case_id: int) -> list[ApprovalRequest]:
        """
        List all approval requests for a case.

        Args:
            case_id: Case ID

        Returns:
            List of ApprovalRequests
        """
        return self.approval_repo.list_by_case(case_id)
