"""
Dashboard service for KPI queries and aggregation.
Orchestrates reporting repository queries for operational and executive dashboards.
"""
from typing import Dict

from app.repositories.reporting_repository import ReportingRepository


class DashboardService:
    """Service for dashboard KPI queries and aggregation."""

    def __init__(self, reporting_repo: ReportingRepository):
        self.reporting_repo = reporting_repo

    def get_operational_dashboard(self) -> Dict:
        """
        Get operational dashboard with metrics and widgets for day-to-day operations.

        Returns:
            Dashboard response with metrics array and widgets for:
            - Case status distribution
            - Exception volume
            - Approval latency
            - Operational alerts
            - Queue ageing
        """
        # Fetch core metrics
        case_metrics = self.reporting_repo.get_case_metrics()
        approval_metrics = self.reporting_repo.get_approval_latency()

        # Compute average approval time metric
        avg_approval_time = f"{approval_metrics['avg_approval_hours']:.1f}h"

        # Build metrics array
        metrics = [
            {
                "label": "Total Cases",
                "value": case_metrics["total_cases"],
                "trend": "neutral"
            },
            {
                "label": "Pending Approval",
                "value": case_metrics["pending_approval"],
                "trend": "warning" if case_metrics["pending_approval"] > 10 else "neutral"
            },
            {
                "label": "Overdue Cases",
                "value": case_metrics["overdue_cases"],
                "trend": "danger" if case_metrics["overdue_cases"] > 0 else "success"
            },
            {
                "label": "Avg Approval Time",
                "value": avg_approval_time,
                "trend": "success" if approval_metrics['avg_approval_hours'] < 24 else "warning"
            }
        ]

        # Build widgets
        widgets = {
            "case_status_distribution": self.reporting_repo.get_case_status_distribution(),
            "exception_volume": self.reporting_repo.get_exception_volume(),
            "approval_latency": approval_metrics,
            "operational_alerts": self.reporting_repo.get_operational_alerts(),
            "queue_ageing": self.reporting_repo.get_queue_ageing(),
            "outcome_distribution": self.reporting_repo.get_outcome_distribution()
        }

        return {
            "dashboard_type": "operational",
            "metrics": metrics,
            "widgets": widgets
        }

    def get_executive_dashboard(self) -> Dict:
        """
        Get executive dashboard with control health, escalation rate, and release readiness.

        Returns:
            Dashboard response with executive-level indicators:
            - Control health metrics (SoD compliance, audit coverage)
            - Escalation rate
            - Release readiness indicators
            - High-level outcome distribution
        """
        # Fetch executive metrics
        control_health = self.reporting_repo.get_control_health_metrics()
        escalation = self.reporting_repo.get_escalation_rate()
        release_readiness = self.reporting_repo.get_release_readiness_indicators()

        # Build executive metrics
        metrics = [
            {
                "label": "Control Compliance",
                "value": f"{control_health['control_compliance_rate'] * 100:.1f}%",
                "trend": "success" if control_health['control_compliance_rate'] >= 0.95 else "warning"
            },
            {
                "label": "Escalation Rate",
                "value": f"{escalation['escalation_rate'] * 100:.1f}%",
                "trend": "neutral"
            },
            {
                "label": "Release Readiness",
                "value": f"{release_readiness['readiness_rate'] * 100:.1f}%",
                "trend": "success" if release_readiness['readiness_rate'] >= 0.70 else "warning"
            },
            {
                "label": "SoD Violations",
                "value": control_health['sod_violations'],
                "trend": "danger" if control_health['sod_violations'] > 0 else "success"
            }
        ]

        # Build widgets
        widgets = {
            "control_health": control_health,
            "escalation_metrics": escalation,
            "release_readiness": release_readiness,
            "outcome_distribution": self.reporting_repo.get_outcome_distribution()
        }

        return {
            "dashboard_type": "executive",
            "metrics": metrics,
            "widgets": widgets
        }
