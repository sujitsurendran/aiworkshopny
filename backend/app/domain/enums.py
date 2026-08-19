"""
Domain enums for status, outcome, and role definitions.
"""
from enum import Enum


class CaseStatus(str, Enum):
    """Case status values."""
    NEW = "New"
    IN_REVIEW = "InReview"
    PENDING_APPROVAL = "PendingApproval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    REWORK_REQUIRED = "ReworkRequired"
    ON_HOLD = "OnHold"
    DECLINED = "Declined"
    RELEASED = "Released"
    FULFILLED = "Fulfilled"
    CANCELLED = "Cancelled"
    CLOSED = "Closed"


class OutcomeType(str, Enum):
    """Decision outcome types."""
    RELEASE = "Release"
    HOLD = "Hold"
    AMEND = "Amend"
    DECLINE = "Decline"


class ApprovalStatus(str, Enum):
    """Approval request status values."""
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    SENT_BACK = "SentBack"


class RoleType(str, Enum):
    """User role types."""
    ORDER_MANAGEMENT_ANALYST = "Order Management Analyst"
    CUSTOMER_SUCCESS_MANAGER = "Customer Success Manager"
    SALES_OPERATIONS_MANAGER = "Sales Operations Manager"
    VP_SALES_COMMERCIAL_DIRECTOR = "VP Sales / Commercial Director"


class RiskBand(str, Enum):
    """Risk band classification."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "VeryHigh"


class FulfilmentStatus(str, Enum):
    """Fulfilment milestone status."""
    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"


class ComplaintStatus(str, Enum):
    """Complaint record status."""
    OPEN = "Open"
    IN_PROGRESS = "InProgress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class RefundStatus(str, Enum):
    """Refund request status."""
    REQUESTED = "Requested"
    APPROVED = "Approved"
    PROCESSING = "Processing"
    PROCESSED = "Processed"
    REJECTED = "Rejected"


class RenewalStatus(str, Enum):
    """Renewal review status."""
    PENDING_REVIEW = "PendingReview"
    APPROVED = "Approved"
    REQUIRES_ATTENTION = "RequiresAttention"
    DECLINED = "Declined"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class ExportFormat(str, Enum):
    """Export file format."""
    CSV = "csv"
    PDF = "pdf"
