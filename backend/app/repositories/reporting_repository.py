"""
Reporting repository for optimized dashboard and reporting queries.
Uses indexed columns and summary aggregations for sub-2-second performance.
"""
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.enums import ApprovalStatus, CaseStatus
from app.domain.models import ApprovalRequest, AuditEvent, Case


class ReportingRepository:
    """Repository for optimized read queries for dashboards and reports."""

    def __init__(self, db: Session):
        self.db = db

    def get_case_metrics(self) -> Dict:
        """
        Get case count metrics for dashboard.
        Uses indexed current_status column for fast aggregation.
        """
        total_cases = self.db.query(func.count(Case.id)).scalar()

        pending_approval_count = (
            self.db.query(func.count(Case.id))
            .filter(Case.current_status == CaseStatus.PENDING_APPROVAL)
            .scalar()
        )

        # Overdue cases: cases updated more than 48 hours ago in non-terminal status
        overdue_threshold = datetime.utcnow() - timedelta(hours=48)
        overdue_count = (
            self.db.query(func.count(Case.id))
            .filter(
                Case.updated_at < overdue_threshold,
                Case.current_status.in_([
                    CaseStatus.NEW,
                    CaseStatus.IN_REVIEW,
                    CaseStatus.PENDING_APPROVAL,
                    CaseStatus.ON_HOLD,
                    CaseStatus.REWORK_REQUIRED
                ])
            )
            .scalar()
        )

        return {
            "total_cases": total_cases or 0,
            "pending_approval": pending_approval_count or 0,
            "overdue_cases": overdue_count or 0
        }

    def get_case_status_distribution(self) -> List[Dict]:
        """
        Get case count by status for distribution widget.
        Uses indexed current_status column.
        """
        results = (
            self.db.query(
                Case.current_status,
                func.count(Case.id).label("count")
            )
            .group_by(Case.current_status)
            .all()
        )

        return [
            {"status": row.current_status.value, "count": row.count}
            for row in results
        ]

    def get_exception_volume(self) -> Dict:
        """
        Get exception-flagged case counts.
        Uses indexed exception_flag column.
        """
        total_exceptions = (
            self.db.query(func.count(Case.id))
            .filter(Case.exception_flag.is_(True))
            .scalar()
        )

        open_exceptions = (
            self.db.query(func.count(Case.id))
            .filter(
                Case.exception_flag.is_(True),
                Case.current_status.in_([
                    CaseStatus.NEW,
                    CaseStatus.IN_REVIEW,
                    CaseStatus.PENDING_APPROVAL,
                    CaseStatus.ON_HOLD,
                    CaseStatus.REWORK_REQUIRED
                ])
            )
            .scalar()
        )

        return {
            "total_exceptions": total_exceptions or 0,
            "open_exceptions": open_exceptions or 0
        }

    def get_approval_latency(self) -> Dict:
        """
        Calculate average approval latency in hours.
        Uses indexed status and assigned_approver_id columns.
        """
        # Average time from creation to decision for decided approvals
        decided_approvals = (
            self.db.query(
                func.avg(
                    func.extract('epoch', ApprovalRequest.decided_at - ApprovalRequest.created_at) / 3600.0
                ).label("avg_hours")
            )
            .filter(ApprovalRequest.decided_at.isnot(None))
            .scalar()
        )

        # Count of pending approvals
        pending_count = (
            self.db.query(func.count(ApprovalRequest.id))
            .filter(ApprovalRequest.status == ApprovalStatus.PENDING)
            .scalar()
        )

        return {
            "avg_approval_hours": round(decided_approvals or 0, 2),
            "pending_approvals": pending_count or 0
        }

    def get_queue_ageing(self) -> List[Dict]:
        """
        Get case ageing by status bucket for queue management.
        Returns cases grouped by age ranges.
        """
        now = datetime.utcnow()
        one_day = now - timedelta(days=1)
        three_days = now - timedelta(days=3)
        seven_days = now - timedelta(days=7)

        # Count cases by age bucket
        age_ranges = [
            ("< 1 day", now, one_day),
            ("1-3 days", one_day, three_days),
            ("3-7 days", three_days, seven_days),
            ("> 7 days", seven_days, datetime.min)
        ]

        results = []
        for label, start, end in age_ranges:
            count = (
                self.db.query(func.count(Case.id))
                .filter(
                    Case.updated_at <= start,
                    Case.updated_at > end if end != datetime.min else True,
                    Case.current_status.in_([
                        CaseStatus.NEW,
                        CaseStatus.IN_REVIEW,
                        CaseStatus.PENDING_APPROVAL,
                        CaseStatus.ON_HOLD,
                        CaseStatus.REWORK_REQUIRED
                    ])
                )
                .scalar()
            )
            results.append({"age_range": label, "count": count or 0})

        return results

    def get_operational_alerts(self) -> List[Dict]:
        """
        Get operational alerts for dashboard.
        Returns list of alert items requiring attention.
        """
        alerts = []

        # Check for overdue approvals
        overdue_threshold = datetime.utcnow() - timedelta(hours=72)
        overdue_approvals = (
            self.db.query(func.count(ApprovalRequest.id))
            .filter(
                ApprovalRequest.status == ApprovalStatus.PENDING,
                ApprovalRequest.created_at < overdue_threshold
            )
            .scalar()
        )

        if overdue_approvals and overdue_approvals > 0:
            alerts.append({
                "severity": "high",
                "message": f"{overdue_approvals} approval(s) overdue (>72h)",
                "alert_type": "approval_overdue"
            })

        # Check for stalled cases
        stalled_threshold = datetime.utcnow() - timedelta(days=7)
        stalled_cases = (
            self.db.query(func.count(Case.id))
            .filter(
                Case.updated_at < stalled_threshold,
                Case.current_status.in_([
                    CaseStatus.IN_REVIEW,
                    CaseStatus.ON_HOLD,
                    CaseStatus.REWORK_REQUIRED
                ])
            )
            .scalar()
        )

        if stalled_cases and stalled_cases > 0:
            alerts.append({
                "severity": "medium",
                "message": f"{stalled_cases} case(s) stalled (>7 days)",
                "alert_type": "case_stalled"
            })

        # Check for high exception volume
        exception_threshold = 0.15  # 15% threshold
        total_open = (
            self.db.query(func.count(Case.id))
            .filter(
                Case.current_status.in_([
                    CaseStatus.NEW,
                    CaseStatus.IN_REVIEW,
                    CaseStatus.PENDING_APPROVAL,
                    CaseStatus.ON_HOLD,
                    CaseStatus.REWORK_REQUIRED
                ])
            )
            .scalar()
        )

        exception_count = (
            self.db.query(func.count(Case.id))
            .filter(
                Case.exception_flag.is_(True),
                Case.current_status.in_([
                    CaseStatus.NEW,
                    CaseStatus.IN_REVIEW,
                    CaseStatus.PENDING_APPROVAL,
                    CaseStatus.ON_HOLD,
                    CaseStatus.REWORK_REQUIRED
                ])
            )
            .scalar()
        )

        if total_open and total_open > 0:
            exception_rate = (exception_count or 0) / total_open
            if exception_rate > exception_threshold:
                alerts.append({
                    "severity": "high",
                    "message": f"Exception rate {exception_rate:.1%} exceeds {exception_threshold:.0%} threshold",
                    "alert_type": "high_exception_rate"
                })

        return alerts

    def get_outcome_distribution(self) -> List[Dict]:
        """
        Get case outcome distribution for executive summary.
        """
        # Get terminal status counts
        terminal_statuses = [
            CaseStatus.APPROVED,
            CaseStatus.DECLINED,
            CaseStatus.RELEASED,
            CaseStatus.CANCELLED
        ]

        results = (
            self.db.query(
                Case.current_status,
                func.count(Case.id).label("count")
            )
            .filter(Case.current_status.in_(terminal_statuses))
            .group_by(Case.current_status)
            .all()
        )

        return [
            {"outcome": row.current_status.value, "count": row.count}
            for row in results
        ]

    def get_control_health_metrics(self) -> Dict:
        """
        Get control health metrics for executive dashboard.
        Returns SoD compliance and audit coverage indicators.
        """
        # Count total approval decisions
        total_approvals = (
            self.db.query(func.count(ApprovalRequest.id))
            .filter(ApprovalRequest.decided_at.isnot(None))
            .scalar()
        )

        # Count SoD violations (audit events with control_violation action)
        sod_violations = (
            self.db.query(func.count(AuditEvent.id))
            .filter(
                AuditEvent.action_type == "control_violation",
                AuditEvent.entity_type == "approval_request"
            )
            .scalar()
        )

        # Count governed actions (all approval decisions + case mutations)
        governed_actions = (
            self.db.query(func.count(AuditEvent.id))
            .filter(
                AuditEvent.action_type.in_([
                    "create", "update", "approve", "reject", "send_back"
                ])
            )
            .scalar()
        )

        return {
            "total_approvals": total_approvals or 0,
            "sod_violations": sod_violations or 0,
            "governed_actions": governed_actions or 0,
            "control_compliance_rate": round(1.0 - ((sod_violations or 0) / max(1, governed_actions or 1)), 3)
        }

    def get_escalation_rate(self) -> Dict:
        """
        Get escalation rate metrics for executive dashboard.
        """
        # Count total cases created
        total_cases = self.db.query(func.count(Case.id)).scalar()

        # Count cases that required approval (escalation)
        escalated_cases = (
            self.db.query(func.count(func.distinct(ApprovalRequest.case_id)))
            .scalar()
        )

        return {
            "total_cases": total_cases or 0,
            "escalated_cases": escalated_cases or 0,
            "escalation_rate": round((escalated_cases or 0) / max(1, total_cases or 1), 3)
        }

    def get_release_readiness_indicators(self) -> Dict:
        """
        Get release readiness indicators for executive dashboard.
        Returns counts and percentages of cases in each readiness state.
        """
        # Cases ready for release (approved or released)
        ready_count = (
            self.db.query(func.count(Case.id))
            .filter(Case.current_status.in_([CaseStatus.APPROVED, CaseStatus.RELEASED]))
            .scalar()
        )

        # Cases blocked or on hold
        blocked_count = (
            self.db.query(func.count(Case.id))
            .filter(Case.current_status == CaseStatus.ON_HOLD)
            .scalar()
        )

        # Cases in progress
        in_progress_count = (
            self.db.query(func.count(Case.id))
            .filter(
                Case.current_status.in_([
                    CaseStatus.NEW,
                    CaseStatus.IN_REVIEW,
                    CaseStatus.PENDING_APPROVAL,
                    CaseStatus.REWORK_REQUIRED
                ])
            )
            .scalar()
        )

        total = (ready_count or 0) + (blocked_count or 0) + (in_progress_count or 0)

        return {
            "ready_for_release": ready_count or 0,
            "blocked": blocked_count or 0,
            "in_progress": in_progress_count or 0,
            "total": total,
            "readiness_rate": round((ready_count or 0) / max(1, total), 3)
        }
