"""
Case Management API endpoints matching LLD OpenAPI contract.
All endpoints enforce authentication via JWT middleware and validate input using Pydantic schemas.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.enums import CaseStatus, OutcomeType
from app.domain.models import User
from app.domain.schemas import (
    AssessmentRequest,
    AssessmentResponse,
    CaseCreate,
    CaseDetail,
    CaseSummary,
    CaseUpdate,
    PaginatedResponse,
)
from app.security.dependencies import get_current_user
from app.services.case_service import CaseService
from app.services.decision_service import DecisionService
from app.shared.errors import DomainError, NotFoundError, ValidationError

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("/", response_model=CaseDetail, status_code=status.HTTP_201_CREATED)
def create_case(
    payload: CaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new case with intake validation.
    Required fields: customer_id, order_reference, requested_terms, requested_outcome, requested_fulfilment_date.
    Returns 400 on validation failure.
    """
    try:
        # Validation: required fields
        if not payload.customer_id or not payload.order_reference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "customer_id and order_reference are required"
                }
            )

        service = CaseService(db)
        case = service.create_case(
            customer_id=payload.customer_id,
            order_reference=payload.order_reference,
            requested_terms=payload.requested_terms,
            requested_outcome=payload.requested_outcome,
            requested_fulfilment_date=payload.requested_fulfilment_date,
            created_by_id=current_user.id,
            priority=payload.priority,
            account_id=payload.account_id
        )

        return CaseDetail(
            id=case.id,
            customer_id=case.customer_id,
            account_id=case.account_id,
            order_reference=case.order_reference,
            requested_terms=case.requested_terms,
            requested_outcome=case.requested_outcome,
            current_status=case.current_status.value,
            priority=case.priority,
            exception_flag=case.exception_flag,
            risk_band=case.risk_band.value if case.risk_band else None,
            created_by_id=case.created_by_id,
            assigned_to_id=case.assigned_to_id,
            created_at=case.created_at,
            updated_at=case.updated_at,
            retention_until=case.retention_until
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message}
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message}
        )


@router.get("/", response_model=PaginatedResponse)
def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    exception_flag: Optional[bool] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    customer_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List cases with filtering and pagination.
    Returns paginated wrapper { items, total, page, page_size } matching cross-layer integration contract.
    """
    filters = {}
    if status:
        filters["status"] = status
    if exception_flag is not None:
        filters["exception_flag"] = exception_flag
    if assigned_to_id:
        filters["assigned_to_id"] = assigned_to_id
    if customer_id:
        filters["customer_id"] = customer_id

    service = CaseService(db)
    result = service.list_cases(filters=filters, page=page, page_size=page_size)

    # Convert items to CaseSummary
    items = [
        CaseSummary(
            id=case.id,
            customer_id=case.customer_id,
            order_reference=case.order_reference,
            current_status=case.current_status.value,
            requested_outcome=case.requested_outcome,
            exception_flag=case.exception_flag,
            assigned_to_id=case.assigned_to_id,
            updated_at=case.updated_at
        )
        for case in result.items
    ]

    return PaginatedResponse(
        items=items,
        total=result.total,
        page=result.page,
        page_size=result.page_size
    )


@router.get("/{case_id}", response_model=CaseDetail)
def get_case_detail(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get full case detail with nested intake, assessment, approvals, operations, and audit_preview.
    Returns 404 if case not found.
    """
    try:
        service = CaseService(db)
        case = service.get_case_detail(case_id)

        return CaseDetail(
            id=case.id,
            customer_id=case.customer_id,
            account_id=case.account_id,
            order_reference=case.order_reference,
            requested_terms=case.requested_terms,
            requested_outcome=case.requested_outcome,
            current_status=case.current_status.value,
            priority=case.priority,
            exception_flag=case.exception_flag,
            risk_band=case.risk_band.value if case.risk_band else None,
            created_by_id=case.created_by_id,
            assigned_to_id=case.assigned_to_id,
            created_at=case.created_at,
            updated_at=case.updated_at,
            retention_until=case.retention_until
        )

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message}
        )


@router.patch("/{case_id}", response_model=CaseDetail)
def update_case(
    case_id: int,
    payload: CaseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update case fields (intake patch, assessment update, status action, notes, attachments).
    Supports partial updates via PATCH.
    """
    try:
        service = CaseService(db)

        # Build updates dict from non-None fields
        updates = {}
        if payload.requested_terms is not None:
            updates["requested_terms"] = payload.requested_terms
        if payload.requested_outcome is not None:
            updates["requested_outcome"] = payload.requested_outcome
        if payload.requested_fulfilment_date is not None:
            updates["requested_fulfilment_date"] = payload.requested_fulfilment_date
        if payload.priority is not None:
            updates["priority"] = payload.priority
        if payload.exception_flag is not None:
            updates["exception_flag"] = payload.exception_flag
        if payload.risk_band is not None:
            updates["risk_band"] = payload.risk_band
        if payload.assigned_to_id is not None:
            updates["assigned_to_id"] = payload.assigned_to_id
        if payload.current_status is not None:
            updates["current_status"] = CaseStatus(payload.current_status)

        case = service.update_case(case_id, current_user.id, updates)

        return CaseDetail(
            id=case.id,
            customer_id=case.customer_id,
            account_id=case.account_id,
            order_reference=case.order_reference,
            requested_terms=case.requested_terms,
            requested_outcome=case.requested_outcome,
            current_status=case.current_status.value,
            priority=case.priority,
            exception_flag=case.exception_flag,
            risk_band=case.risk_band.value if case.risk_band else None,
            created_by_id=case.created_by_id,
            assigned_to_id=case.assigned_to_id,
            created_at=case.created_at,
            updated_at=case.updated_at,
            retention_until=case.retention_until
        )

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message}
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message}
        )


@router.post("/{case_id}/assessment", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def submit_assessment(
    case_id: int,
    payload: AssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit credit assessment recommendation for a case.
    Validates recommendation is one of: RELEASE, HOLD, AMEND, DECLINE.
    """
    try:
        # Validate recommendation
        try:
            recommendation = OutcomeType(payload.recommendation)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": f"Invalid recommendation: {payload.recommendation}. Must be RELEASE, HOLD, AMEND, or DECLINE"
                }
            )

        service = DecisionService(db)
        assessment = service.submit_recommendation(
            case_id=case_id,
            assessment_data=payload.assessment_data,
            recommendation=recommendation,
            rationale=payload.rationale,
            assessed_by_id=current_user.id
        )

        return AssessmentResponse(
            id=assessment.id,
            case_id=assessment.case_id,
            recommendation=assessment.recommendation.value,
            rationale=assessment.rationale,
            assessed_by_id=assessment.assessed_by_id,
            assessed_at=assessment.assessed_at
        )

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message}
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message}
        )
