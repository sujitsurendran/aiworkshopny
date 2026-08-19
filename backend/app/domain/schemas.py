"""
Pydantic schemas for request/response validation matching LLD OpenAPI contract.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

# ============================================================================
# Authentication Schemas
# ============================================================================

class LoginRequest(BaseModel):
    """Login request with email and password."""
    email: EmailStr
    password: str = Field(..., min_length=8)


class SessionResponse(BaseModel):
    """Session response matching LLD SessionResponse schema."""
    user_id: str
    email: str
    full_name: str
    roles: list[str]
    access_token: str
    expires_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user fields."""
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """User creation request."""
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """User response without password."""
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Case Schemas
# ============================================================================

class CaseBase(BaseModel):
    """Base case fields."""
    customer_id: str
    account_id: Optional[str] = None
    order_reference: str
    requested_terms: Optional[str] = None
    requested_outcome: Optional[str] = None


class CaseCreate(CaseBase):
    """Case creation request."""
    requested_fulfilment_date: Optional[datetime] = None
    priority: str = "Medium"


class CaseSummary(BaseModel):
    """Case summary for list views."""
    id: int
    customer_id: str
    order_reference: str
    current_status: str
    requested_outcome: Optional[str]
    exception_flag: bool
    assigned_to_id: Optional[int]
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseDetail(BaseModel):
    """Full case detail with nested relationships."""
    id: int
    customer_id: str
    account_id: Optional[str]
    order_reference: str
    requested_terms: Optional[str]
    requested_outcome: Optional[str]
    current_status: str
    priority: str
    exception_flag: bool
    risk_band: Optional[str]
    created_by_id: int
    assigned_to_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    retention_until: datetime

    model_config = {"from_attributes": True}


class CaseUpdate(BaseModel):
    """Case update request for PATCH operations."""
    requested_terms: Optional[str] = None
    requested_outcome: Optional[str] = None
    requested_fulfilment_date: Optional[datetime] = None
    priority: Optional[str] = None
    exception_flag: Optional[bool] = None
    risk_band: Optional[str] = None
    assigned_to_id: Optional[int] = None
    current_status: Optional[str] = None


class AssessmentRequest(BaseModel):
    """Credit assessment submission request."""
    assessment_data: Optional[dict] = None
    recommendation: str = Field(..., description="Outcome recommendation: RELEASE, HOLD, AMEND, DECLINE")
    rationale: str = Field(..., min_length=10)


class AssessmentResponse(BaseModel):
    """Credit assessment response."""
    id: int
    case_id: int
    recommendation: str
    rationale: str
    assessed_by_id: int
    assessed_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Pagination Schemas
# ============================================================================

class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    items: list
    total: int
    page: int
    page_size: int


# ============================================================================
# Approval Schemas
# ============================================================================

class ApprovalActionRequest(BaseModel):
    """Approval action request for approve/reject/send_back."""
    action: str = Field(..., description="Action: request_approval, approve, reject, send_back")
    justification: Optional[str] = None
    approval_level: Optional[str] = None
    decision_reason: Optional[str] = None


class ApprovalSummary(BaseModel):
    """Approval summary for list views."""
    id: int
    case_id: int
    requested_by_id: int
    status: str
    justification: Optional[str]
    approval_level: Optional[str]
    decision_reason: Optional[str]
    decided_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Operations Schemas
# ============================================================================

class OperationRequest(BaseModel):
    """Polymorphic operations request."""
    operation_type: str = Field(..., description="Operation type: fulfilment, complaint, refund, renewal")
    payload: dict = Field(..., description="Operation-specific payload")


class FulfilmentPayload(BaseModel):
    """Fulfilment operation payload."""
    milestone_name: str
    status: str
    blocker_description: Optional[str] = None


class ComplaintPayload(BaseModel):
    """Complaint operation payload."""
    complaint_description: str
    status: Optional[str] = None
    resolution_notes: Optional[str] = None


class RefundPayload(BaseModel):
    """Refund operation payload."""
    refund_amount: float
    financial_impact_flag: bool
    evidence_confirmed: bool


class RenewalPayload(BaseModel):
    """Renewal operation payload."""
    renewal_risk_summary: Optional[str] = None
    status: Optional[str] = None
    review_notes: Optional[str] = None


class OperationResponse(BaseModel):
    """Generic operation response."""
    operation_type: str
    record_id: int
    message: str


# ============================================================================
# Error Response Schemas
# ============================================================================

class ErrorDetail(BaseModel):
    """Error detail for validation errors."""
    field: Optional[str] = None
    issue: str


class ErrorResponse(BaseModel):
    """Standard error response envelope."""
    code: str
    message: str
    details: Optional[list[ErrorDetail]] = None


# ============================================================================
# Dashboard Schemas
# ============================================================================

class DashboardMetric(BaseModel):
    """Dashboard metric item."""
    label: str
    value: str | int | float
    trend: str = Field(..., description="Trend indicator: success, warning, danger, neutral")


class DashboardResponse(BaseModel):
    """Dashboard response with metrics and widgets."""
    dashboard_type: str
    metrics: list[DashboardMetric]
    widgets: dict


# ============================================================================
# Export Schemas
# ============================================================================

class ExportRequestCreate(BaseModel):
    """Export request creation payload."""
    source: str = Field(..., description="Export source: case_list, operational_dashboard, executive_dashboard")
    export_type: str = Field(..., description="Export type: csv, pdf")
    filters: Optional[dict] = None


class ExportResponse(BaseModel):
    """Export response with metadata and content."""
    export_id: int
    export_type: str
    source: str
    status: str
    file_path: str
    generated_at: str
    content: str
