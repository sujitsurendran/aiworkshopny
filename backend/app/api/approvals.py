"""
Approval API endpoints for approval request creation and approve/reject/send-back actions.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.schemas import ApprovalActionRequest, ApprovalSummary
from app.security.dependencies import get_current_user
from app.services.approval_service import ApprovalService

router = APIRouter(prefix="/cases", tags=["approvals"])


@router.post("/{case_id}/approvals", status_code=201)
def handle_approval_action(
    case_id: int,
    request: ApprovalActionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle approval actions: request_approval, approve, reject, send_back.

    Args:
        case_id: Case ID
        request: Approval action request
        current_user: Current authenticated user
        db: Database session

    Returns:
        Approval summary or action result
    """
    approval_service = ApprovalService(db)
    actor_id = current_user["user_id"]

    if request.action == "request_approval":
        # Create approval request
        if not request.justification or not request.approval_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VAL_001", "message": "justification and approval_level are required for request_approval"}
            )

        approval = approval_service.create_approval_request(
            case_id=case_id,
            requested_by_id=actor_id,
            justification=request.justification,
            approval_level=request.approval_level
        )

        return ApprovalSummary.model_validate(approval)

    elif request.action == "approve":
        # Approve existing approval request
        # For simplicity, find pending approval for this case
        pending_approvals = approval_service.list_approvals_for_case(case_id)
        pending = next((a for a in pending_approvals if a.status.value == "PENDING"), None)

        if not pending:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NF_001", "message": "No pending approval request found for this case"}
            )

        approval = approval_service.approve_request(
            approval_request_id=pending.id,
            actor_id=actor_id,
            decision_reason=request.decision_reason
        )

        return ApprovalSummary.model_validate(approval)

    elif request.action == "reject":
        # Reject existing approval request
        if not request.decision_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VAL_002", "message": "decision_reason is required for reject"}
            )

        pending_approvals = approval_service.list_approvals_for_case(case_id)
        pending = next((a for a in pending_approvals if a.status.value == "PENDING"), None)

        if not pending:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NF_001", "message": "No pending approval request found for this case"}
            )

        approval = approval_service.reject_request(
            approval_request_id=pending.id,
            actor_id=actor_id,
            decision_reason=request.decision_reason
        )

        return ApprovalSummary.model_validate(approval)

    elif request.action == "send_back":
        # Send back existing approval request
        if not request.decision_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VAL_003", "message": "decision_reason is required for send_back"}
            )

        pending_approvals = approval_service.list_approvals_for_case(case_id)
        pending = next((a for a in pending_approvals if a.status.value == "PENDING"), None)

        if not pending:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NF_001", "message": "No pending approval request found for this case"}
            )

        approval = approval_service.send_back_request(
            approval_request_id=pending.id,
            actor_id=actor_id,
            decision_reason=request.decision_reason
        )

        return ApprovalSummary.model_validate(approval)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VAL_004", "message": f"Invalid action: {request.action}"}
        )


@router.get("/{case_id}/approvals", response_model=list[ApprovalSummary])
def list_approvals(
    case_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all approval requests for a case.

    Args:
        case_id: Case ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of approval summaries
    """
    approval_service = ApprovalService(db)
    approvals = approval_service.list_approvals_for_case(case_id)

    return [ApprovalSummary.model_validate(a) for a in approvals]
