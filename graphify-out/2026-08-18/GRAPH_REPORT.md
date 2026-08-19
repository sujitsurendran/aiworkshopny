# Graph Report - aiworkshopny  (2026-08-18)

## Corpus Check
- 85 files · ~45,004 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1027 nodes · 1946 edges · 84 communities (61 shown, 23 thin omitted)
- Extraction: 70% EXTRACTED · 30% INFERRED · 0% AMBIGUOUS · INFERRED: 586 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2732d2d3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- README.md
- main.py
- package.json
- compilerOptions
- RiskBand
- models.py
- Quick Start
- compilerOptions
- start.sh
- ApprovalStatus
- ComplaintStatus
- FulfilmentStatus
- NotificationPriority
- OutcomeType
- RefundStatus
- RenewalStatus
- AuditRepository
- AuditService
- DomainError
- main.tsx
- stop.sh
- __init__.py
- verizon-credit-platform-backend
- CaseService
- CaseRepository
- DecisionService
- database.py
- main.py
- AuthorityEvaluationResult
- test_cases.py
- test_database.py
- init_db
- get_db
- .test_create_case_missing_required_fields
- .test_get_case_detail_not_found
- .test_create_case_success
- FastAPI
- handle_operation
- submit_assessment
- PaginatedResponse
- CaseSummary
- authority_policy_service.py
- .__init__
- .__init__
- CaseService
- DecisionService
- dashboards.py
- decode_access_token
- test_operations.py
- conftest.py
- test_get_outcome_distribution
- test_operational_dashboard_service
- .test_create_refund_success
- ExportRequest
- test_cases.py
- TestCaseEndpoints
- ApprovalSummary
- CaseUpdate
- test_executive_dashboard_service
- test_export_creates_audit_event
- test_export_invalid_source_type_combination
- DashboardMetric
- ErrorDetail
- ExportResponse
- FulfilmentPayload
- ExportRequestCreate
- OperationRequest
- PaginatedResponse
- RefundPayload
- RenewalPayload
- test_get_queue_ageing
- test_operational_dashboard_service
- test_export_operational_dashboard_csv

## God Nodes (most connected - your core abstractions)
1. `User` - 75 edges
2. `Case` - 73 edges
3. `ReportingRepository` - 39 edges
4. `CaseStatus` - 34 edges
5. `OutcomeType` - 34 edges
6. `Role` - 33 edges
7. `UserRole` - 30 edges
8. `ApprovalRequest` - 29 edges
9. `AuthorityRule` - 29 edges
10. `AuditService` - 29 edges

## Surprising Connections (you probably didn't know these)
- `login()` --indirect_call--> `Role`  [INFERRED]
  backend/app/api/auth.py → backend/app/domain/models.py
- `login()` --indirect_call--> `User`  [INFERRED]
  backend/app/api/auth.py → backend/app/domain/models.py
- `login()` --calls--> `SessionResponse`  [INFERRED]
  backend/app/api/auth.py → backend/app/domain/schemas.py
- `login()` --calls--> `create_access_token()`  [INFERRED]
  backend/app/api/auth.py → backend/app/security/auth.py
- `list_cases()` --calls--> `CaseSummary`  [INFERRED]
  backend/app/api/cases.py → backend/app/domain/schemas.py

## Import Cycles
- None detected.

## Communities (84 total, 23 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.06
Nodes (35): Access the Application, Architecture, Backend, Backend Development, Backend (.env), Compliance, CORS errors, Database initialization fails (+27 more)

### Community 1 - "main.py"
Cohesion: 0.22
Nodes (9): get_current_user(), get_current_user_roles(), Session, FastAPI dependency injection helpers for authentication and authorization., Require authentication without specific permission check.      Args:         cur, Extract and validate current user from JWT bearer token.      Args:         cred, Get role names for current authenticated user.      Args:         current_user:, require_auth() (+1 more)

### Community 2 - "package.json"
Cohesion: 0.08
Nodes (24): dependencies, react, react-dom, react-router-dom, description, devDependencies, autoprefixer, eslint (+16 more)

### Community 3 - "compilerOptions"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleResolution (+13 more)

### Community 4 - "RiskBand"
Cohesion: 0.16
Nodes (47): ApprovalStatus, CaseStatus, ComplaintStatus, ExportFormat, FulfilmentStatus, NotificationPriority, OutcomeType, Domain enums for status, outcome, and role definitions. (+39 more)

### Community 6 - "Quick Start"
Cohesion: 0.09
Nodes (21): cleanup_test_db(), override_get_db(), Unit tests for authentication, JWT validation, and RBAC enforcement. Tests cover, Test bcrypt password hashing., Test login with non-existent email returns 401., Test login with incorrect password returns 401., Test login with inactive user returns 401., Override database dependency for testing. (+13 more)

### Community 7 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 8 - "start.sh"
Cohesion: 0.38
Nodes (5): API_PORT, check_prerequisites(), DATABASE_URL, portable_sed(), start.sh script

### Community 9 - "ApprovalStatus"
Cohesion: 0.10
Nodes (17): check_sod_violation(), enforce_sod_check(), Session, RBAC middleware, role-permission mapping, and segregation-of-duties rule enforce, Enforce segregation-of-duties check, raising 403 on violation.      Args:, Check for segregation-of-duties violation.      Prevents an analyst from approvi, Reject an approval request with SoD enforcement.          Args:             appr, Send back an approval request for rework with SoD enforcement.          Args: (+9 more)

### Community 10 - "ComplaintStatus"
Cohesion: 0.20
Nodes (10): login(), Session, Authenticate user and return JWT token with user information.      Validates ema, Verify a password against a bcrypt hash.      Args:         plain_password: Plai, verify_password(), Test password verification with correct password., Test password verification with incorrect password., test_verify_password_correct() (+2 more)

### Community 11 - "FulfilmentStatus"
Cohesion: 0.09
Nodes (22): Case, Customer credit review cases., Create a new case with intake data.          Args:             customer_id: Cust, test_case(), Test GET /api/v1/cases returns paginated wrapper., Test GET /api/v1/cases applies filters correctly., Test GET /api/v1/cases/{caseId} returns full case detail., Test PATCH /api/v1/cases/{caseId} updates case fields. (+14 more)

### Community 12 - "NotificationPriority"
Cohesion: 0.20
Nodes (10): create_access_token(), Create a JWT access token with user_id claim and expiry.      Args:         user, Test JWT token creation with user_id claim and exp., Test JWT token decoding with valid token., Test JWT token decoding with expired token., test_create_access_token(), test_decode_access_token_expired(), test_decode_access_token_valid() (+2 more)

### Community 13 - "OutcomeType"
Cohesion: 0.25
Nodes (8): check_permission(), Check if any of the user's roles grant the required permission.      Args:, Test permission check when user has required permission., Test permission check when user lacks required permission., Test permission check with multiple roles., test_check_permission_denied(), test_check_permission_granted(), test_check_permission_multiple_roles()

### Community 14 - "RefundStatus"
Cohesion: 0.25
Nodes (5): IdentityAdapter, SSO boundary adapter for corporate identity integration. MVP implementation is a, Validate SSO assertion and extract user identity claims.          Args:, Refresh SSO session using refresh token.          Args:             refresh_toke, Adapter boundary for corporate SSO integration.      MVP implementation is a stu

### Community 15 - "RenewalStatus"
Cohesion: 0.33
Nodes (6): Enforce permission requirement, raising 403 if not authorized.      Args:, require_permission(), Test require_permission does not raise when permission granted., Test require_permission raises 403 when permission denied., test_require_permission_forbidden(), test_require_permission_success()

### Community 16 - "AuditRepository"
Cohesion: 0.06
Nodes (20): AuditRepository, Session, Audit repository for append-only event logging with hash chaining., Repository for immutable audit event operations., Get the most recent hash for an entity to chain the next event., Compute SHA-256 hash from previous hash + normalized payload.         Ensures de, Append an immutable audit event with hash chaining.         NO update or delete, Query audit events with filters. (+12 more)

### Community 17 - "AuditService"
Cohesion: 0.05
Nodes (32): ApprovalActionRequest, handle_approval_action(), list_approvals(), Session, Approval API endpoints for approval request creation and approve/reject/send-bac, List all approval requests for a case.      Args:         case_id: Case ID, Handle approval actions: request_approval, approve, reject, send_back.      Args, ApprovalRepository (+24 more)

### Community 18 - "DomainError"
Cohesion: 0.08
Nodes (23): Accessibility (WCAG 2.1 AA), Actions, Alert Severity Colors, CaseDetailPage Verification (`/cases/:caseId`), CaseIntakePage Verification (`/cases/new`), Color Matching, Colors, Cross-Page Consistency (+15 more)

### Community 19 - "main.tsx"
Cohesion: 0.08
Nodes (21): App(), LoginPage(), RequireAuth(), RequireAuthProps, Header(), Layout(), LayoutProps, NavItem (+13 more)

### Community 31 - "CaseService"
Cohesion: 0.11
Nodes (10): Case repository for database access. All queries use SQLAlchemy ORM without raw, Reporting repository for optimized dashboard and reporting queries. Uses indexed, Audit service for append-only event logging with hash chaining. All governed act, Case service orchestrating case CRUD operations. Handles case creation, updates,, Complaint service for complaint management linked to cases., Export service for CSV/PDF generation with permission filtering. Handles export, Fulfilment service for tracking milestones and blockers., Notification service for in-app notifications and optional synchronous email dis (+2 more)

### Community 32 - "CaseRepository"
Cohesion: 0.07
Nodes (26): FulfilmentService, Service for fulfilment milestone tracking., Create or update fulfilment milestone record.          Args:             case_id, List all fulfilment records for a case.          Args:             case_id: Case, Update refund status.          Args:             refund_id: Refund ID, List all refunds for a case.          Args:             case_id: Case ID, Service for refund and return record management., Create refund record with financial impact validation.          Args: (+18 more)

### Community 33 - "DecisionService"
Cohesion: 0.18
Nodes (11): ApprovalActionRequest, AssessmentResponse, FulfilmentPayload, LoginRequest, Credit assessment response., Login request with email and password., Approval action request for approve/reject/send_back., Fulfilment operation payload. (+3 more)

### Community 34 - "database.py"
Cohesion: 0.18
Nodes (9): Authentication API endpoint matching LLD OpenAPI contract. Implements POST /api/, Application configuration using pydantic-settings. All environment-specific sett, Application settings loaded from environment variables., Settings, get_db(), Session, Database initialization and session management. Uses synchronous SQLAlchemy with, Dependency for FastAPI to get database session. (+1 more)

### Community 35 - "main.py"
Cohesion: 0.17
Nodes (10): health_check(), FastAPI application initialization with CORS middleware and lifespan management., Health check endpoint for load balancer and monitoring., Root endpoint with API information., root(), db(), override_get_db(), Shared pytest fixtures for all test modules. (+2 more)

### Community 36 - "AuthorityEvaluationResult"
Cohesion: 0.27
Nodes (9): CaseBase, CaseCreate, Pydantic schemas for request/response validation matching LLD OpenAPI contract., User creation request., User response without password., Case creation request., UserBase, UserCreate (+1 more)

### Community 37 - "test_cases.py"
Cohesion: 0.11
Nodes (24): Session, Tests for export API endpoints and services., Test CSV export of case list., Test CSV export with status filter., Test PDF export of operational dashboard., Test PDF export of executive dashboard., Test that export creates audit event., Test that export request is persisted in database. (+16 more)

### Community 38 - "test_database.py"
Cohesion: 0.25
Nodes (7): Basic database initialization tests., Test that required indexes exist on critical tables., Test that audit_events table has hash_value and previous_hash columns., Test that retention_until columns exist on required tables., test_audit_events_hash_columns(), test_required_indexes(), test_retention_columns()

### Community 39 - "init_db"
Cohesion: 0.33
Nodes (6): init_db(), Initialize database by creating all tables., lifespan(), Lifespan context manager for startup and shutdown events., Test that database initializes without errors., test_database_init()

### Community 40 - "get_db"
Cohesion: 0.10
Nodes (20): ApprovalActionRequest, ApprovalSummary, AssessmentRequest, AssessmentResponse, CaseCreate, CaseDetail, CaseSummary, CaseUpdate (+12 more)

### Community 41 - ".test_create_case_missing_required_fields"
Cohesion: 0.11
Nodes (24): Session, Tests for dashboard API endpoints and services., Test case metrics aggregation., Test case status distribution aggregation., Test exception volume metrics., Test approval latency calculation., Test operational alerts generation., Test outcome distribution for terminal statuses. (+16 more)

### Community 42 - ".test_get_case_detail_not_found"
Cohesion: 0.08
Nodes (13): Session, Calculate average approval latency in hours.         Uses indexed status and ass, Get case ageing by status bucket for queue management.         Returns cases gro, Repository for optimized read queries for dashboards and reports., Get operational alerts for dashboard.         Returns list of alert items requir, Get case count metrics for dashboard.         Uses indexed current_status column, Get case outcome distribution for executive summary., Get control health metrics for executive dashboard.         Returns SoD complian (+5 more)

### Community 43 - ".test_create_case_success"
Cohesion: 0.09
Nodes (33): Seed the four primary roles.      Returns:         Dictionary mapping role name, seed_roles(), db_session(), Session, Acceptance tests for TASK-6 to verify all acceptance criteria., Verify NotificationService.notifyRework() writes rework notification linked to a, Verify notification templates exist for all required types., Verify seed data creates four users with correct email addresses. (+25 more)

### Community 44 - "FastAPI"
Cohesion: 0.18
Nodes (8): handle_operation(), Session, Operations API endpoints for fulfilment, complaints, refunds, and renewals., Polymorphic operations endpoint with operationType dispatch.      Args:, Approval service for approval request creation, approve/reject/send-back actions, Refund service for returns and refund processing with financial impact validatio, FastAPI, OperationRequest

### Community 47 - "PaginatedResponse"
Cohesion: 0.12
Nodes (32): User accounts with role-based access control., User, NotificationService, Session, Service for creating and dispatching notifications., db_session(), Session, Unit tests for notification service. (+24 more)

### Community 48 - "CaseSummary"
Cohesion: 0.11
Nodes (11): CaseRepository, Session, Repository for Case entity database operations., Retrieve case by ID with all relationships loaded., List cases with optional filtering and pagination.         Returns (items, total, Update an existing case., Add credit assessment to case., Session (+3 more)

### Community 49 - "authority_policy_service.py"
Cohesion: 0.20
Nodes (8): Service for renewal review lifecycle management., Create or update renewal review record.          Args:             case_id: Case, List all renewal reviews for a case.          Args:             case_id: Case ID, RenewalService, Test RenewalService methods., Test creating renewal review., Test updating existing renewal review., TestRenewalService

### Community 50 - ".__init__"
Cohesion: 0.12
Nodes (13): get_dashboard_service(), get_executive_dashboard(), get_operational_dashboard(), Session, Dashboard API endpoints for operational and executive dashboards. Provides KPI q, Dependency for dashboard service., Get operational dashboard with metrics and widgets.      Returns dashboard respo, Get executive dashboard with control health, escalation rate, and release readin (+5 more)

### Community 51 - ".__init__"
Cohesion: 0.15
Nodes (10): ComplaintService, List all complaints for a case.          Args:             case_id: Case ID, Service for complaint lifecycle management., Create complaint record linked to case.          Args:             case_id: Case, Update complaint status and resolution notes.          Args:             complai, Test ComplaintService methods., Test creating complaint linked to case., Test updating complaint status. (+2 more)

### Community 52 - "CaseService"
Cohesion: 0.19
Nodes (7): Create rework notification when approval is sent back to analyst.          Args:, Create notification for ageing complaint.          Args:             recipient_i, Create notification when refund requires evidence confirmation.          Args:, Create notification for renewal risk.          Args:             recipient_id: S, Render notification message from template.          Args:             template:, Optional synchronous email dispatch.         Failures are logged but do not bloc, Create SLA warning notification when case is ageing.          Args:

### Community 53 - "DecisionService"
Cohesion: 0.05
Nodes (41): AssessmentRequest, create_case(), get_case_detail(), list_cases(), Session, Case Management API endpoints matching LLD OpenAPI contract. All endpoints enfor, List cases with filtering and pagination.     Returns paginated wrapper { items,, Get full case detail with nested intake, assessment, approvals, operations, and (+33 more)

### Community 55 - "decode_access_token"
Cohesion: 0.17
Nodes (11): decode_access_token(), hash_password(), Authentication services: JWT creation/validation and bcrypt password hashing. Us, Hash a password using bcrypt.      Args:         password: Plain text password, Decode and validate a JWT access token.      Args:         token: JWT token stri, Test JWT token decoding with invalid token., Test successful login returns JWT token and user object., Test accessing protected endpoint with valid token succeeds. (+3 more)

### Community 56 - "test_operations.py"
Cohesion: 0.15
Nodes (13): AuthorityRule, Delegation-of-authority rules., AuthorityPolicyService, Session, Authority policy service for delegation-of-authority rule evaluation., Service for evaluating delegation-of-authority rules., Evaluate authority rules and return eligible approver level.          Args:, Get all authority rules for a role.          Args:             role_name: Role n (+5 more)

### Community 58 - "test_get_outcome_distribution"
Cohesion: 0.16
Nodes (18): hash_password(), Session, Idempotent seed data for default users, authority rules, SoD rules, and sample c, Seed authority rules for approval routing.     - Analyst can auto-finalize low-r, Seed segregation-of-duties rules preventing self-approval., Seed 10-15 sample cases with various statuses., Hash password using bcrypt., Execute seed data generation.     Idempotent - checks existence before inserting (+10 more)

### Community 59 - "test_operational_dashboard_service"
Cohesion: 0.18
Nodes (9): AuthorityEvaluationResult, Session, Workflow rules engine for state transitions, routing logic, and authority evalua, Check segregation-of-duties rules.         Returns True if actor cannot approve/, Result of authority evaluation matching LLD contract.     Contains routing decis, Evaluates workflow rules for case submission, approval routing, and state transi, Evaluate case submission for approval routing requirements.          Args:, Check delegation-of-authority rules against actor role and case context. (+1 more)

### Community 60 - ".test_create_refund_success"
Cohesion: 0.23
Nodes (7): ExportService, Generate CSV export of case list with filters.          Args:             filter, Generate CSV export of operational dashboard metrics.          Returns:, Generate PDF report for operational dashboard.         For MVP, returns text-bas, Service for export generation with audit logging., Generate PDF report for executive dashboard.         For MVP, returns text-based, Create export request and generate export file.          Args:             sourc

### Community 61 - "ExportRequest"
Cohesion: 0.25
Nodes (8): create_export(), ExportRequest, get_export_service(), Session, Export API endpoints for CSV/PDF generation. Handles export request creation and, Export request payload., Dependency for export service., Create export request and generate export file.      Supported combinations:

### Community 62 - "test_cases.py"
Cohesion: 0.25
Nodes (7): db_session(), override_get_db(), Unit tests for case management endpoints and services. Tests case CRUD, assessme, Override database dependency for testing., Create fresh database session for each test., Create test user with analyst role., test_user()

### Community 63 - "TestCaseEndpoints"
Cohesion: 0.12
Nodes (16): RoleType, Many-to-many relationship between users and roles., UserRole, Create a test user with role., test_user(), Test POST /api/v1/cases returns 400 when required fields missing., Test GET /api/v1/cases/{caseId} returns 404 for non-existent case., Test workflow rules engine logic. (+8 more)

### Community 64 - "ApprovalSummary"
Cohesion: 0.22
Nodes (4): CardContentProps, CardHeaderProps, CardProps, CardTitleProps

### Community 65 - "CaseUpdate"
Cohesion: 0.33
Nodes (5): paginate(), PaginatedResponse, Pagination utilities for list endpoints matching cross-layer integration contrac, Paginated response wrapper matching shared_config.json contract.     Returns { i, Apply pagination to a SQLAlchemy query.      Args:         query: SQLAlchemy que

## Knowledge Gaps
- **128 isolated node(s):** `verizon-credit-platform-backend`, `name`, `version`, `description`, `type` (+123 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Case` connect `FulfilmentStatus` to `CaseRepository`, `RiskBand`, `ApprovalStatus`, `.test_get_case_detail_not_found`, `.test_create_case_success`, `PaginatedResponse`, `CaseSummary`, `AuditService`, `authority_policy_service.py`, `.__init__`, `DecisionService`, `test_operations.py`, `test_get_outcome_distribution`, `test_operational_dashboard_service`, `TestCaseEndpoints`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `User` connect `PaginatedResponse` to `CaseRepository`, `main.py`, `RiskBand`, `test_cases.py`, `Quick Start`, `.test_create_case_missing_required_fields`, `ComplaintStatus`, `FulfilmentStatus`, `.test_create_case_success`, `AuditService`, `authority_policy_service.py`, `test_export_operational_dashboard_csv`, `.__init__`, `DecisionService`, `test_operations.py`, `test_get_outcome_distribution`, `test_cases.py`, `TestCaseEndpoints`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `ReportingRepository` connect `.test_get_case_detail_not_found` to `test_executive_dashboard_service`, `RiskBand`, `.test_create_case_missing_required_fields`, `FulfilmentStatus`, `CaseSummary`, `test_get_queue_ageing`, `.__init__`, `test_operational_dashboard_service`, `.test_create_refund_success`, `ExportRequest`, `CaseService`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `User` (e.g. with `login()` and `ApprovalStatus`) actually correct?**
  _`User` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Case` (e.g. with `ApprovalStatus` and `CaseStatus`) actually correct?**
  _`Case` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `ReportingRepository` (e.g. with `get_dashboard_service()` and `ExportRequest`) actually correct?**
  _`ReportingRepository` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `CaseStatus` (e.g. with `update_case()` and `ApprovalRequest`) actually correct?**
  _`CaseStatus` has 31 INFERRED edges - model-reasoned connections that need verification._