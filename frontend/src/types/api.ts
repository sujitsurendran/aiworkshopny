/**
 * TypeScript interfaces matching backend Pydantic schemas field-for-field.
 */

// ============================================================================
// Authentication Types
// ============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SessionResponse {
  user_id: string;
  email: string;
  full_name: string;
  roles: string[];
  access_token: string;
  expires_at: string;
}

// ============================================================================
// User Types
// ============================================================================

export interface UserResponse {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

// ============================================================================
// Case Types
// ============================================================================

export interface CaseCreate {
  customer_id: string;
  account_id?: string;
  order_reference: string;
  requested_terms?: string;
  requested_outcome?: string;
  requested_fulfilment_date?: string;
  priority?: string;
}

export interface CaseSummary {
  id: number;
  customer_id: string;
  order_reference: string;
  current_status: string;
  requested_outcome: string | null;
  exception_flag: boolean;
  assigned_to_id: number | null;
  updated_at: string;
}

export interface CaseDetail {
  id: number;
  customer_id: string;
  account_id: string | null;
  order_reference: string;
  requested_terms: string | null;
  requested_outcome: string | null;
  current_status: string;
  priority: string;
  exception_flag: boolean;
  risk_band: string | null;
  created_by_id: number;
  assigned_to_id: number | null;
  created_at: string;
  updated_at: string;
  retention_until: string;
}

export interface CaseUpdate {
  requested_terms?: string;
  requested_outcome?: string;
  requested_fulfilment_date?: string;
  priority?: string;
  exception_flag?: boolean;
  risk_band?: string;
  assigned_to_id?: number;
  current_status?: string;
}

export interface AssessmentRequest {
  assessment_data?: Record<string, unknown>;
  recommendation: string;
  rationale: string;
}

export interface AssessmentResponse {
  id: number;
  case_id: number;
  recommendation: string;
  rationale: string;
  assessed_by_id: number;
  assessed_at: string;
}

// ============================================================================
// Pagination Types
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ============================================================================
// Approval Types
// ============================================================================

export interface ApprovalActionRequest {
  action: string;
  justification?: string;
  approval_level?: string;
  decision_reason?: string;
}

export interface ApprovalSummary {
  id: number;
  case_id: number;
  requested_by_id: number;
  status: string;
  justification: string | null;
  approval_level: string | null;
  decision_reason: string | null;
  decided_at: string | null;
  created_at: string;
}

// ============================================================================
// Operations Types
// ============================================================================

export interface OperationRequest {
  operation_type: string;
  payload: Record<string, unknown>;
}

export interface OperationResponse {
  operation_type: string;
  record_id: number;
  message: string;
}

// ============================================================================
// Dashboard Types
// ============================================================================

export interface DashboardMetric {
  label: string;
  value: string | number;
  trend: string;
}

export interface DashboardResponse {
  dashboard_type: string;
  metrics: DashboardMetric[];
  widgets: Record<string, unknown>;
}

// ============================================================================
// Export Types
// ============================================================================

export interface ExportRequestCreate {
  source: string;
  export_type: string;
  filters?: Record<string, unknown>;
}

export interface ExportResponse {
  export_id: number;
  export_type: string;
  source: string;
  status: string;
  file_path: string;
  generated_at: string;
  content: string;
}

// ============================================================================
// Error Types
// ============================================================================

export interface ErrorDetail {
  field?: string;
  issue: string;
}

export interface ErrorResponse {
  code: string;
  message: string;
  details?: ErrorDetail[];
}
