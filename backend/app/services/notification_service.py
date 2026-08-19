"""
Notification service for in-app notifications and optional synchronous email dispatch.
Writes to notifications table in same transaction as triggering business action.
Email adapter failures do not block core transaction.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.enums import NotificationPriority
from app.domain.models import Notification


class NotificationService:
    """Service for creating and dispatching notifications."""

    def __init__(self, db: Session):
        self.db = db

    def notify_escalation(
        self,
        recipient_id: int,
        case_id: int,
        escalation_reason: str,
        priority: NotificationPriority = NotificationPriority.HIGH
    ) -> Notification:
        """
        Create escalation notification for approval or exception routing.

        Args:
            recipient_id: User ID to receive the notification
            case_id: Case being escalated
            escalation_reason: Reason for escalation
            priority: Notification priority (default HIGH)

        Returns:
            Created notification record
        """
        message = self._render_template(
            template="escalation",
            case_id=case_id,
            reason=escalation_reason
        )

        notification = Notification(
            recipient_id=recipient_id,
            case_id=case_id,
            notification_type="escalation",
            priority=priority,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )

        self.db.add(notification)
        self.db.flush()

        # Optional email dispatch (failures logged but do not block transaction)
        self._try_send_email(recipient_id, message)

        return notification

    def notify_sla_warning(
        self,
        recipient_id: int,
        case_id: int,
        sla_threshold: str,
        hours_remaining: int
    ) -> Notification:
        """
        Create SLA warning notification when case is ageing.

        Args:
            recipient_id: User ID to receive the notification
            case_id: Case approaching SLA breach
            sla_threshold: SLA type (e.g., "approval_latency")
            hours_remaining: Hours until SLA breach

        Returns:
            Created notification record with priority HIGH
        """
        message = self._render_template(
            template="sla_warning",
            case_id=case_id,
            sla_threshold=sla_threshold,
            hours_remaining=hours_remaining
        )

        notification = Notification(
            recipient_id=recipient_id,
            case_id=case_id,
            notification_type="sla_warning",
            priority=NotificationPriority.HIGH,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )

        self.db.add(notification)
        self.db.flush()

        self._try_send_email(recipient_id, message)

        return notification

    def notify_rework(
        self,
        recipient_id: int,
        case_id: int,
        approval_request_id: int,
        rework_reason: str
    ) -> Notification:
        """
        Create rework notification when approval is sent back to analyst.

        Args:
            recipient_id: Analyst user ID
            case_id: Case requiring rework
            approval_request_id: Approval request that was sent back
            rework_reason: Reason for sending back

        Returns:
            Created notification record
        """
        message = self._render_template(
            template="rework",
            case_id=case_id,
            approval_request_id=approval_request_id,
            reason=rework_reason
        )

        notification = Notification(
            recipient_id=recipient_id,
            case_id=case_id,
            notification_type="rework",
            priority=NotificationPriority.MEDIUM,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )

        self.db.add(notification)
        self.db.flush()

        self._try_send_email(recipient_id, message)

        return notification

    def notify_complaint_ageing(
        self,
        recipient_id: int,
        case_id: int,
        complaint_id: int,
        days_open: int
    ) -> Notification:
        """
        Create notification for ageing complaint.

        Args:
            recipient_id: CSM user ID
            case_id: Related case
            complaint_id: Complaint record ID
            days_open: Number of days complaint has been open

        Returns:
            Created notification record
        """
        message = self._render_template(
            template="complaint_ageing",
            case_id=case_id,
            complaint_id=complaint_id,
            days_open=days_open
        )

        notification = Notification(
            recipient_id=recipient_id,
            case_id=case_id,
            notification_type="complaint_ageing",
            priority=NotificationPriority.MEDIUM,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )

        self.db.add(notification)
        self.db.flush()

        self._try_send_email(recipient_id, message)

        return notification

    def notify_refund_evidence_missing(
        self,
        recipient_id: int,
        case_id: int,
        refund_id: int,
        refund_amount: float
    ) -> Notification:
        """
        Create notification when refund requires evidence confirmation.

        Args:
            recipient_id: Manager user ID
            case_id: Related case
            refund_id: Refund record ID
            refund_amount: Amount of refund

        Returns:
            Created notification record
        """
        message = self._render_template(
            template="refund_evidence_missing",
            case_id=case_id,
            refund_id=refund_id,
            refund_amount=refund_amount
        )

        notification = Notification(
            recipient_id=recipient_id,
            case_id=case_id,
            notification_type="refund_evidence_missing",
            priority=NotificationPriority.HIGH,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )

        self.db.add(notification)
        self.db.flush()

        self._try_send_email(recipient_id, message)

        return notification

    def notify_renewal_risk(
        self,
        recipient_id: int,
        case_id: int,
        renewal_id: int,
        risk_summary: str
    ) -> Notification:
        """
        Create notification for renewal risk.

        Args:
            recipient_id: Sales operations manager user ID
            case_id: Related case
            renewal_id: Renewal review record ID
            risk_summary: Risk summary text

        Returns:
            Created notification record
        """
        message = self._render_template(
            template="renewal_risk",
            case_id=case_id,
            renewal_id=renewal_id,
            risk_summary=risk_summary
        )

        notification = Notification(
            recipient_id=recipient_id,
            case_id=case_id,
            notification_type="renewal_risk",
            priority=NotificationPriority.MEDIUM,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )

        self.db.add(notification)
        self.db.flush()

        self._try_send_email(recipient_id, message)

        return notification

    def _render_template(self, template: str, **kwargs) -> str:
        """
        Render notification message from template.

        Args:
            template: Template name
            **kwargs: Template variables

        Returns:
            Rendered message text
        """
        templates = {
            "escalation": "Case #{case_id} has been escalated. Reason: {reason}",
            "sla_warning": "Case #{case_id} is approaching SLA breach. {sla_threshold} has {hours_remaining} hours remaining.",
            "rework": "Case #{case_id} approval request #{approval_request_id} has been sent back for rework. Reason: {reason}",
            "complaint_ageing": "Complaint #{complaint_id} for case #{case_id} has been open for {days_open} days.",
            "refund_evidence_missing": "Refund #{refund_id} for case #{case_id} (amount: ${refund_amount:.2f}) requires evidence confirmation.",
            "renewal_risk": "Renewal #{renewal_id} for case #{case_id} has risk: {risk_summary}"
        }

        template_str = templates.get(template, "Notification for case #{case_id}")
        return template_str.format(**kwargs)

    def _try_send_email(self, recipient_id: int, message: str) -> None:
        """
        Optional synchronous email dispatch.
        Failures are logged but do not block the transaction.

        Args:
            recipient_id: User ID to email
            message: Email message body
        """
        try:
            # Email adapter stub - would integrate with SMTP or email service
            # For MVP, this is a no-op
            pass
        except Exception as e:
            # Log error but do not raise - email failure must not block notification creation
            print(f"Email dispatch failed for user {recipient_id}: {e}")
