"""
Export service for CSV/PDF generation with permission filtering.
Handles export request creation, file generation, and audit logging.
"""
import csv
import io
import json
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.domain.enums import ExportFormat
from app.domain.models import ExportRequest
from app.repositories.case_repository import CaseRepository
from app.repositories.reporting_repository import ReportingRepository
from app.services.audit_service import AuditService


class ExportService:
    """Service for export generation with audit logging."""

    def __init__(
        self,
        db: Session,
        case_repo: CaseRepository,
        reporting_repo: ReportingRepository
    ):
        self.db = db
        self.case_repo = case_repo
        self.reporting_repo = reporting_repo
        self.audit_service = AuditService(db)

    def create_export_request(
        self,
        source: str,
        export_type: str,
        filters: Optional[Dict],
        requested_by_id: int
    ) -> Dict:
        """
        Create export request and generate export file.

        Args:
            source: Export source (case_list, operational_dashboard, executive_dashboard)
            export_type: Export type (csv, pdf)
            filters: Optional filters for data selection
            requested_by_id: User ID of requester

        Returns:
            Export response with download metadata
        """
        # Create export request record
        export_request = ExportRequest(
            export_type=export_type,
            export_format=ExportFormat.CSV if export_type == "csv" else ExportFormat.PDF,
            source=source,
            requested_by_id=requested_by_id,
            status="pending",
            filter_json=filters or {},
            retention_until=datetime.utcnow().replace(year=datetime.utcnow().year + 7)
        )
        self.db.add(export_request)
        self.db.commit()
        self.db.refresh(export_request)

        # Generate export based on source and type
        if export_type == "csv":
            if source == "case_list":
                content = self._generate_case_list_csv(filters or {})
            elif source == "operational_dashboard":
                content = self._generate_operational_dashboard_csv()
            else:
                raise ValueError(f"Unsupported CSV export source: {source}")
        elif export_type == "pdf":
            if source == "operational_dashboard":
                content = self._generate_operational_dashboard_pdf()
            elif source == "executive_dashboard":
                content = self._generate_executive_dashboard_pdf()
            else:
                raise ValueError(f"Unsupported PDF export source: {source}")
        else:
            raise ValueError(f"Unsupported export type: {export_type}")

        # Update export request with completion
        export_request.status = "completed"
        export_request.file_path = f"exports/{export_request.id}.{export_type}"
        self.db.commit()
        self.db.refresh(export_request)

        # Append audit event
        self.audit_service.append_event(
            entity_type="export_request",
            entity_id=export_request.id,
            action_type="export_generated",
            actor_id=requested_by_id,
            payload={
                "export_type": export_type,
                "source": source,
                "filter_json": json.dumps(filters or {}),
                "requested_by": requested_by_id
            }
        )

        return {
            "export_id": export_request.id,
            "export_type": export_type,
            "source": source,
            "status": "completed",
            "file_path": export_request.file_path,
            "generated_at": export_request.created_at.isoformat(),
            "content": content  # In-memory content for MVP; in production would be S3 URL
        }

    def _generate_case_list_csv(self, filters: Dict) -> str:
        """
        Generate CSV export of case list with filters.

        Args:
            filters: Filter dict for case query

        Returns:
            CSV content as string
        """
        # Fetch cases with filters (no pagination for export)
        cases, _ = self.case_repo.list_cases(filters=filters, page=1, page_size=10000)

        # Write CSV to in-memory buffer
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "case_id",
                "customer_id",
                "order_reference",
                "status",
                "priority",
                "exception_flag",
                "risk_band",
                "assigned_to_id",
                "created_at",
                "updated_at"
            ]
        )
        writer.writeheader()

        for case in cases:
            writer.writerow({
                "case_id": case.id,
                "customer_id": case.customer_id,
                "order_reference": case.order_reference,
                "status": case.current_status.value,
                "priority": case.priority,
                "exception_flag": case.exception_flag,
                "risk_band": case.risk_band or "",
                "assigned_to_id": case.assigned_to_id or "",
                "created_at": case.created_at.isoformat(),
                "updated_at": case.updated_at.isoformat()
            })

        return output.getvalue()

    def _generate_operational_dashboard_csv(self) -> str:
        """
        Generate CSV export of operational dashboard metrics.

        Returns:
            CSV content as string
        """
        # Fetch dashboard data
        case_metrics = self.reporting_repo.get_case_metrics()
        status_distribution = self.reporting_repo.get_case_status_distribution()
        exception_volume = self.reporting_repo.get_exception_volume()
        approval_latency = self.reporting_repo.get_approval_latency()

        # Write CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Write metrics section
        writer.writerow(["Operational Dashboard Export"])
        writer.writerow(["Generated:", datetime.utcnow().isoformat()])
        writer.writerow([])

        writer.writerow(["Key Metrics"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Cases", case_metrics["total_cases"]])
        writer.writerow(["Pending Approval", case_metrics["pending_approval"]])
        writer.writerow(["Overdue Cases", case_metrics["overdue_cases"]])
        writer.writerow(["Avg Approval Hours", approval_latency["avg_approval_hours"]])
        writer.writerow([])

        # Write status distribution
        writer.writerow(["Case Status Distribution"])
        writer.writerow(["Status", "Count"])
        for item in status_distribution:
            writer.writerow([item["status"], item["count"]])
        writer.writerow([])

        # Write exception volume
        writer.writerow(["Exception Volume"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Exceptions", exception_volume["total_exceptions"]])
        writer.writerow(["Open Exceptions", exception_volume["open_exceptions"]])

        return output.getvalue()

    def _generate_operational_dashboard_pdf(self) -> str:
        """
        Generate PDF report for operational dashboard.
        For MVP, returns text-based report; production would use reportlab or similar.

        Returns:
            PDF-like text content
        """
        # Fetch dashboard data
        case_metrics = self.reporting_repo.get_case_metrics()
        status_distribution = self.reporting_repo.get_case_status_distribution()
        exception_volume = self.reporting_repo.get_exception_volume()
        approval_latency = self.reporting_repo.get_approval_latency()
        alerts = self.reporting_repo.get_operational_alerts()

        # Build text report (MVP; production would use reportlab)
        lines = [
            "=" * 60,
            "OPERATIONAL DASHBOARD REPORT",
            "=" * 60,
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "KEY METRICS",
            "-" * 60,
            f"Total Cases:           {case_metrics['total_cases']}",
            f"Pending Approval:      {case_metrics['pending_approval']}",
            f"Overdue Cases:         {case_metrics['overdue_cases']}",
            f"Avg Approval Time:     {approval_latency['avg_approval_hours']:.1f} hours",
            "",
            "CASE STATUS DISTRIBUTION",
            "-" * 60
        ]

        for item in status_distribution:
            lines.append(f"{item['status']:25} {item['count']:>5}")

        lines.extend([
            "",
            "EXCEPTION VOLUME",
            "-" * 60,
            f"Total Exceptions:      {exception_volume['total_exceptions']}",
            f"Open Exceptions:       {exception_volume['open_exceptions']}",
            "",
            "OPERATIONAL ALERTS",
            "-" * 60
        ])

        if alerts:
            for alert in alerts:
                lines.append(f"[{alert['severity'].upper()}] {alert['message']}")
        else:
            lines.append("No alerts")

        lines.append("=" * 60)

        return "\n".join(lines)

    def _generate_executive_dashboard_pdf(self) -> str:
        """
        Generate PDF report for executive dashboard.
        For MVP, returns text-based report; production would use reportlab or similar.

        Returns:
            PDF-like text content
        """
        # Fetch executive metrics
        control_health = self.reporting_repo.get_control_health_metrics()
        escalation = self.reporting_repo.get_escalation_rate()
        release_readiness = self.reporting_repo.get_release_readiness_indicators()
        outcome_distribution = self.reporting_repo.get_outcome_distribution()

        # Build text report
        lines = [
            "=" * 60,
            "EXECUTIVE DASHBOARD REPORT",
            "=" * 60,
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "CONTROL HEALTH",
            "-" * 60,
            f"Total Approvals:       {control_health['total_approvals']}",
            f"SoD Violations:        {control_health['sod_violations']}",
            f"Governed Actions:      {control_health['governed_actions']}",
            f"Compliance Rate:       {control_health['control_compliance_rate'] * 100:.1f}%",
            "",
            "ESCALATION METRICS",
            "-" * 60,
            f"Total Cases:           {escalation['total_cases']}",
            f"Escalated Cases:       {escalation['escalated_cases']}",
            f"Escalation Rate:       {escalation['escalation_rate'] * 100:.1f}%",
            "",
            "RELEASE READINESS",
            "-" * 60,
            f"Ready for Release:     {release_readiness['ready_for_release']}",
            f"Blocked:               {release_readiness['blocked']}",
            f"In Progress:           {release_readiness['in_progress']}",
            f"Readiness Rate:        {release_readiness['readiness_rate'] * 100:.1f}%",
            "",
            "OUTCOME DISTRIBUTION",
            "-" * 60
        ]

        for item in outcome_distribution:
            lines.append(f"{item['outcome']:25} {item['count']:>5}")

        lines.append("=" * 60)

        return "\n".join(lines)
