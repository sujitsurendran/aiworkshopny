"""
Operations API endpoints for fulfilment, complaints, refunds, and renewals.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.enums import FulfilmentStatus, RenewalStatus
from app.domain.schemas import (
    ComplaintPayload,
    FulfilmentPayload,
    OperationRequest,
    OperationResponse,
    RefundPayload,
    RenewalPayload,
)
from app.security.dependencies import get_current_user
from app.services.complaint_service import ComplaintService
from app.services.fulfilment_service import FulfilmentService
from app.services.refund_service import RefundService
from app.services.renewal_service import RenewalService

router = APIRouter(prefix="/cases", tags=["operations"])


@router.post("/{case_id}/operations", response_model=OperationResponse, status_code=201)
def handle_operation(
    case_id: int,
    request: OperationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Polymorphic operations endpoint with operationType dispatch.

    Args:
        case_id: Case ID
        request: Operation request with operation_type and payload
        current_user: Current authenticated user
        db: Database session

    Returns:
        Operation response
    """
    actor_id = current_user["user_id"]
    operation_type = request.operation_type

    if operation_type == "fulfilment":
        # Handle fulfilment operation
        fulfilment_service = FulfilmentService(db)
        payload = FulfilmentPayload.model_validate(request.payload)

        # Parse status enum
        try:
            status_enum = FulfilmentStatus[payload.status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VAL_005", "message": f"Invalid fulfilment status: {payload.status}"}
            )

        record = fulfilment_service.create_or_update_fulfilment(
            case_id=case_id,
            actor_id=actor_id,
            milestone_name=payload.milestone_name,
            status=status_enum,
            blocker_description=payload.blocker_description
        )

        return OperationResponse(
            operation_type="fulfilment",
            record_id=record.id,
            message="Fulfilment milestone updated successfully"
        )

    elif operation_type == "complaint":
        # Handle complaint operation
        complaint_service = ComplaintService(db)
        payload = ComplaintPayload.model_validate(request.payload)

        record = complaint_service.create_complaint(
            case_id=case_id,
            actor_id=actor_id,
            complaint_description=payload.complaint_description
        )

        return OperationResponse(
            operation_type="complaint",
            record_id=record.id,
            message="Complaint created successfully"
        )

    elif operation_type == "refund":
        # Handle refund operation
        refund_service = RefundService(db)
        payload = RefundPayload.model_validate(request.payload)

        record = refund_service.create_refund(
            case_id=case_id,
            actor_id=actor_id,
            refund_amount=payload.refund_amount,
            financial_impact_flag=payload.financial_impact_flag,
            evidence_confirmed=payload.evidence_confirmed
        )

        return OperationResponse(
            operation_type="refund",
            record_id=record.id,
            message="Refund created successfully"
        )

    elif operation_type == "renewal":
        # Handle renewal operation
        renewal_service = RenewalService(db)
        payload = RenewalPayload.model_validate(request.payload)

        # Parse status enum
        status_enum = RenewalStatus.PENDING_REVIEW
        if payload.status:
            try:
                status_enum = RenewalStatus[payload.status.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": "VAL_006", "message": f"Invalid renewal status: {payload.status}"}
                )

        record = renewal_service.create_or_update_renewal(
            case_id=case_id,
            actor_id=actor_id,
            renewal_risk_summary=payload.renewal_risk_summary,
            status=status_enum,
            review_notes=payload.review_notes
        )

        return OperationResponse(
            operation_type="renewal",
            record_id=record.id,
            message="Renewal review created successfully"
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VAL_008", "message": f"Invalid operation_type: {operation_type}"}
        )
