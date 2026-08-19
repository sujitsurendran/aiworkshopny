"""
Dashboard API endpoints for operational and executive dashboards.
Provides KPI queries and aggregation with role-based filtering.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.reporting_repository import ReportingRepository
from app.security.dependencies import get_current_user
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    """Dependency for dashboard service."""
    reporting_repo = ReportingRepository(db)
    return DashboardService(reporting_repo)


@router.get("/operational")
def get_operational_dashboard(
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get operational dashboard with metrics and widgets.

    Returns dashboard response with:
    - metrics array (Total Cases, Pending Approval, Overdue Cases, Avg Approval Time)
    - widgets for case status distribution, exception volume, approval latency,
      operational alerts, queue ageing, outcome distribution
    """
    try:
        dashboard = dashboard_service.get_operational_dashboard()
        return dashboard
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DASHBOARD_ERROR",
                "message": f"Failed to load operational dashboard: {str(e)}"
            }
        )


@router.get("/executive")
def get_executive_dashboard(
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get executive dashboard with control health, escalation rate, and release readiness.

    Returns dashboard response with:
    - metrics array (Control Compliance, Escalation Rate, Release Readiness, SoD Violations)
    - widgets for control health, escalation metrics, release readiness, outcome distribution
    """
    try:
        dashboard = dashboard_service.get_executive_dashboard()
        return dashboard
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DASHBOARD_ERROR",
                "message": f"Failed to load executive dashboard: {str(e)}"
            }
        )
