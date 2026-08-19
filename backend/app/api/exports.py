"""
Export API endpoints for CSV/PDF generation.
Handles export request creation and file download with permission filtering.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.case_repository import CaseRepository
from app.repositories.reporting_repository import ReportingRepository
from app.security.dependencies import get_current_user
from app.services.export_service import ExportService

router = APIRouter(prefix="/exports", tags=["exports"])


class ExportRequest(BaseModel):
    """Export request payload."""
    source: str
    export_type: str
    filters: Optional[dict] = None


def get_export_service(db: Session = Depends(get_db)) -> ExportService:
    """Dependency for export service."""
    case_repo = CaseRepository(db)
    reporting_repo = ReportingRepository(db)
    return ExportService(db, case_repo, reporting_repo)


@router.post("")
def create_export(
    request: ExportRequest,
    current_user: dict = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """
    Create export request and generate export file.

    Supported combinations:
    - source: case_list, export_type: csv
    - source: operational_dashboard, export_type: csv
    - source: operational_dashboard, export_type: pdf
    - source: executive_dashboard, export_type: pdf

    Returns export metadata with content (in-memory for MVP).
    Logs audit event with export_type, source, filter_json, requested_by.
    """
    # Validate source and export_type combination
    valid_combinations = [
        ("case_list", "csv"),
        ("operational_dashboard", "csv"),
        ("operational_dashboard", "pdf"),
        ("executive_dashboard", "pdf")
    ]

    if (request.source, request.export_type) not in valid_combinations:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_EXPORT_REQUEST",
                "message": f"Invalid export combination: source={request.source}, export_type={request.export_type}"
            }
        )

    try:
        export_response = export_service.create_export_request(
            source=request.source,
            export_type=request.export_type,
            filters=request.filters,
            requested_by_id=current_user["user_id"]
        )
        return export_response
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "EXPORT_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "EXPORT_ERROR",
                "message": f"Failed to generate export: {str(e)}"
            }
        )
