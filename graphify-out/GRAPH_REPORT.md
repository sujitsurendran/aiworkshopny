# Graph Report - aiworkshopny  (2026-08-19)

## Corpus Check
- 109 files · ~91,661 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1359 nodes · 2263 edges · 101 communities (89 shown, 12 thin omitted)
- Extraction: 75% EXTRACTED · 25% INFERRED · 0% AMBIGUOUS · INFERRED: 563 edges (avg confidence: 0.63)
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
- create_access_token
- approvals.py
- .create_or_update_renewal
- Common Issues
- Final Verification Report
- Security Scan Results
- Application Deployment
- Monitoring and Logging
- Backup and Restore
- conftest.py
- Deployment Readiness
- Manual Testing Results
- Appendix
- Environment Configuration
- Health Checks
- Database Setup
- Linter Results
- Test Results
- Performance Test Results
- Known Issues and Limitations
- ApprovalActionRequest
- AssessmentRequest
- DashboardResponse
- ErrorDetail
- ExportRequestCreate
- LoginRequest
- OperationRequest
- test_get_queue_ageing
- test_export_creates_audit_event

## God Nodes (most connected - your core abstractions)
1. `User` - 75 edges
2. `Case` - 75 edges
3. `ReportingRepository` - 39 edges
4. `CaseStatus` - 34 edges
5. `OutcomeType` - 34 edges
6. `Role` - 33 edges
7. `UserRole` - 30 edges
8. `ApprovalRequest` - 29 edges
9. `AuditService` - 29 edges
10. `ExportService` - 29 edges

## Surprising Connections (you probably didn't know these)
- `handle_approval_action()` --calls--> `ApprovalService`  [INFERRED]
  backend/app/api/approvals.py → backend/app/services/approval_service.py
- `list_approvals()` --calls--> `ApprovalService`  [INFERRED]
  backend/app/api/approvals.py → backend/app/services/approval_service.py
- `login()` --indirect_call--> `Role`  [INFERRED]
  backend/app/api/auth.py → backend/app/domain/models.py
- `login()` --indirect_call--> `User`  [INFERRED]
  backend/app/api/auth.py → backend/app/domain/models.py
- `login()` --calls--> `SessionResponse`  [INFERRED]
  backend/app/api/auth.py → backend/app/domain/schemas.py

## Import Cycles
- None detected.

## Communities (101 total, 12 thin omitted)

### Community 0 - "README.md"
Cohesion: 0.06
Nodes (35): Access the Application, Architecture, Backend, Backend Development, Backend (.env), Compliance, CORS errors, Database initialization fails (+27 more)

### Community 1 - "main.py"
Cohesion: 0.04
Nodes (45): 1.1 Text Alternatives ✅ PASSED, 1.2 Time-based Media ✅ N/A, 1.3 Adaptable ✅ PASSED, 1.4 Distinguishable ✅ PASSED, 2.1 Keyboard Accessible ✅ PASSED, 2.2 Enough Time ✅ PASSED, 2.3 Seizures and Physical Reactions ✅ PASSED, 2.4 Navigable ✅ PASSED (+37 more)

### Community 2 - "package.json"
Cohesion: 0.07
Nodes (28): dependencies, react, react-dom, react-router-dom, description, devDependencies, autoprefixer, eslint (+20 more)

### Community 3 - "compilerOptions"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleResolution (+13 more)

### Community 4 - "RiskBand"
Cohesion: 0.16
Nodes (48): ApprovalStatus, CaseStatus, ComplaintStatus, ExportFormat, FulfilmentStatus, NotificationPriority, OutcomeType, Domain enums for status, outcome, and role definitions. (+40 more)

### Community 5 - "models.py"
Cohesion: 0.20
Nodes (10): CaseBase, CaseCreate, CaseSummary, ErrorResponse, Pydantic schemas for request/response validation matching LLD OpenAPI contract., Session response matching LLD SessionResponse schema., Standard error response envelope., Case creation request. (+2 more)

### Community 6 - "Quick Start"
Cohesion: 0.08
Nodes (23): cleanup_test_db(), override_get_db(), Unit tests for authentication, JWT validation, and RBAC enforcement. Tests cover, Test bcrypt password hashing., Test login with non-existent email returns 401., Test login with incorrect password returns 401., Test login with inactive user returns 401., Test accessing protected endpoint without token returns 403. (+15 more)

### Community 7 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 8 - "start.sh"
Cohesion: 0.38
Nodes (5): API_PORT, check_prerequisites(), DATABASE_URL, portable_sed(), start.sh script

### Community 9 - "ApprovalStatus"
Cohesion: 0.12
Nodes (13): check_sod_violation(), Check for segregation-of-duties violation.      Prevents an analyst from approvi, Reject an approval request with SoD enforcement.          Args:             appr, Send back an approval request for rework with SoD enforcement.          Args:, Approve an approval request with SoD enforcement.          Args:             app, Test SoD check detects self-approval violation., Test SoD check allows approval by different user., Test SoD check applies to reject action. (+5 more)

### Community 10 - "ComplaintStatus"
Cohesion: 0.20
Nodes (10): login(), Session, Authenticate user and return JWT token with user information.      Validates ema, Verify a password against a bcrypt hash.      Args:         plain_password: Plai, verify_password(), Test password verification with correct password., Test password verification with incorrect password., test_verify_password_correct() (+2 more)

### Community 11 - "FulfilmentStatus"
Cohesion: 0.14
Nodes (11): db(), Session, Unit tests for approval endpoints and approval service., Test approving request by different user., Test SoD check prevents self-approval., Create test database session., Test sending back request for rework., Test SoD check prevents self send-back. (+3 more)

### Community 12 - "NotificationPriority"
Cohesion: 0.07
Nodes (26): 1. ApprovalDecisionPage (`/approvals/:caseId`), 2. ApprovalQueuePage (`/approvals`), 3. ExceptionQueuePage (`/exceptions`), 4. FulfilmentPage (`/operations/fulfilment/:caseId`), 5. ComplaintPage (`/operations/complaints`), 6. RefundPage (`/operations/refunds`), 7. RenewalPage (`/operations/renewals`), Acceptance Criteria Status (+18 more)

### Community 13 - "OutcomeType"
Cohesion: 0.25
Nodes (8): check_permission(), Check if any of the user's roles grant the required permission.      Args:, Test permission check when user has required permission., Test permission check when user lacks required permission., Test permission check with multiple roles., test_check_permission_denied(), test_check_permission_granted(), test_check_permission_multiple_roles()

### Community 14 - "RefundStatus"
Cohesion: 0.25
Nodes (5): IdentityAdapter, SSO boundary adapter for corporate identity integration. MVP implementation is a, Validate SSO assertion and extract user identity claims.          Args:, Refresh SSO session using refresh token.          Args:             refresh_toke, Adapter boundary for corporate SSO integration.      MVP implementation is a stu

### Community 15 - "RenewalStatus"
Cohesion: 0.18
Nodes (10): enforce_sod_check(), Session, RBAC middleware, role-permission mapping, and segregation-of-duties rule enforce, Enforce segregation-of-duties check, raising 403 on violation.      Args:, Enforce permission requirement, raising 403 if not authorized.      Args:, require_permission(), Test require_permission does not raise when permission granted., Test require_permission raises 403 when permission denied. (+2 more)

### Community 16 - "AuditRepository"
Cohesion: 0.05
Nodes (38): 10. Server-Side Request Forgery (SSRF) ✅ N/A, 1. Broken Access Control ✅ PASSED, 2. Cryptographic Failures ✅ PASSED, 3. Injection ✅ PASSED, 4. Insecure Design ✅ PASSED, 5. Security Misconfiguration ✅ PASSED, 6. Vulnerable Components ✅ PASSED, 7. Identification and Authentication Failures ✅ PASSED (+30 more)

### Community 17 - "AuditService"
Cohesion: 0.17
Nodes (7): ApprovalService, Service for approval authority handling with SoD enforcement., List all approval requests for a case.          Args:             case_id: Case, Create approval request linked to case.          Args:             case_id: Case, Test creating approval request., Test rejecting request by different user., Test SoD check prevents self-rejection.

### Community 18 - "DomainError"
Cohesion: 0.08
Nodes (23): Accessibility (WCAG 2.1 AA), Actions, Alert Severity Colors, CaseDetailPage Verification (`/cases/:caseId`), CaseIntakePage Verification (`/cases/new`), Color Matching, Colors, Cross-Page Consistency (+15 more)

### Community 19 - "main.tsx"
Cohesion: 0.05
Nodes (32): App(), LoginPage(), RequireAuth(), RequireAuthProps, Header(), Layout(), LayoutProps, NavItem (+24 more)

### Community 31 - "CaseService"
Cohesion: 0.11
Nodes (10): Case repository for database access. All queries use SQLAlchemy ORM without raw, Reporting repository for optimized dashboard and reporting queries. Uses indexed, Audit service for append-only event logging with hash chaining. All governed act, Complaint service for complaint management linked to cases., Decision service for credit assessment and recommendation capture. Orchestrates, Export service for CSV/PDF generation with permission filtering. Handles export, Fulfilment service for tracking milestones and blockers., Notification service for in-app notifications and optional synchronous email dis (+2 more)

### Community 32 - "CaseRepository"
Cohesion: 0.08
Nodes (26): Update refund status.          Args:             refund_id: Refund ID, List all refunds for a case.          Args:             case_id: Case ID, Service for refund and return record management., Create refund record with financial impact validation.          Args:, RefundService, Service for renewal review lifecycle management., Create or update renewal review record.          Args:             case_id: Case, List all renewal reviews for a case.          Args:             case_id: Case ID (+18 more)

### Community 33 - "DecisionService"
Cohesion: 0.15
Nodes (13): ApprovalSummary, AssessmentResponse, CaseUpdate, DashboardMetric, ExportResponse, PaginatedResponse, Case update request for PATCH operations., Credit assessment response. (+5 more)

### Community 34 - "database.py"
Cohesion: 0.18
Nodes (9): Authentication API endpoint matching LLD OpenAPI contract. Implements POST /api/, Application configuration using pydantic-settings. All environment-specific sett, Application settings loaded from environment variables., Settings, get_db(), Session, Database initialization and session management. Uses synchronous SQLAlchemy with, Dependency for FastAPI to get database session. (+1 more)

### Community 35 - "main.py"
Cohesion: 0.33
Nodes (5): health_check(), FastAPI application initialization with CORS middleware and lifespan management., Health check endpoint for load balancer and monitoring., Root endpoint with API information., root()

### Community 36 - "AuthorityEvaluationResult"
Cohesion: 0.40
Nodes (5): User creation request., User response without password., UserBase, UserCreate, UserResponse

### Community 37 - "test_cases.py"
Cohesion: 0.10
Nodes (28): Session, Tests for export API endpoints and services., Test CSV export with status filter., Test CSV export of operational dashboard., Test PDF export of operational dashboard., Test PDF export of executive dashboard., Create a sample user for testing., Test that export request is persisted in database. (+20 more)

### Community 38 - "test_database.py"
Cohesion: 0.20
Nodes (9): Basic database initialization tests., Test that database initializes without errors., Test that required indexes exist on critical tables., Test that audit_events table has hash_value and previous_hash columns., Test that retention_until columns exist on required tables., test_audit_events_hash_columns(), test_database_init(), test_required_indexes() (+1 more)

### Community 39 - "init_db"
Cohesion: 0.06
Nodes (20): AuditRepository, Session, Audit repository for append-only event logging with hash chaining., Repository for immutable audit event operations., Get the most recent hash for an entity to chain the next event., Compute SHA-256 hash from previous hash + normalized payload.         Ensures de, Append an immutable audit event with hash chaining.         NO update or delete, Query audit events with filters. (+12 more)

### Community 40 - "get_db"
Cohesion: 0.10
Nodes (21): ApprovalActionRequest, ApprovalSummary, AssessmentRequest, AssessmentResponse, CaseCreate, CaseDetail, CaseSummary, CaseUpdate (+13 more)

### Community 41 - ".test_create_case_missing_required_fields"
Cohesion: 0.11
Nodes (26): Session, Tests for dashboard API endpoints and services., Test case metrics aggregation., Test case status distribution aggregation., Test exception volume metrics., Test approval latency calculation., Create a sample user for testing., Test operational alerts generation. (+18 more)

### Community 42 - ".test_get_case_detail_not_found"
Cohesion: 0.08
Nodes (13): Session, Calculate average approval latency in hours.         Uses indexed status and ass, Get case ageing by status bucket for queue management.         Returns cases gro, Repository for optimized read queries for dashboards and reports., Get operational alerts for dashboard.         Returns list of alert items requir, Get case count metrics for dashboard.         Uses indexed current_status column, Get case outcome distribution for executive summary., Get control health metrics for executive dashboard.         Returns SoD complian (+5 more)

### Community 43 - ".test_create_case_success"
Cohesion: 0.06
Nodes (56): init_db(), Initialize database by creating all tables., lifespan(), Lifespan context manager for startup and shutdown events., hash_password(), Session, Idempotent seed data for default users, authority rules, SoD rules, and sample c, Seed authority rules for approval routing.     - Analyst can auto-finalize low-r (+48 more)

### Community 44 - "FastAPI"
Cohesion: 0.29
Nodes (4): Operations API endpoints for fulfilment, complaints, refunds, and renewals., Approval service for approval request creation, approve/reject/send-back actions, Refund service for returns and refund processing with financial impact validatio, FastAPI

### Community 45 - "handle_operation"
Cohesion: 0.14
Nodes (14): handle_operation(), Session, Polymorphic operations endpoint with operationType dispatch.      Args:, ComplaintPayload, FulfilmentPayload, OperationResponse, Fulfilment operation payload., Complaint operation payload. (+6 more)

### Community 46 - "submit_assessment"
Cohesion: 0.18
Nodes (9): FulfilmentService, Service for fulfilment milestone tracking., Create or update fulfilment milestone record.          Args:             case_id, List all fulfilment records for a case.          Args:             case_id: Case, Test updating existing fulfilment milestone., Test updating fulfilment with blocker description., Test FulfilmentService methods., Test creating fulfilment milestone. (+1 more)

### Community 47 - "PaginatedResponse"
Cohesion: 0.06
Nodes (49): User accounts with role-based access control., User, get_current_user(), get_current_user_roles(), Session, FastAPI dependency injection helpers for authentication and authorization., Require authentication without specific permission check.      Args:         cur, Extract and validate current user from JWT bearer token.      Args:         cred (+41 more)

### Community 48 - "CaseSummary"
Cohesion: 0.12
Nodes (10): CaseRepository, Session, Repository for Case entity database operations., Retrieve case by ID with all relationships loaded., Update an existing case., Add credit assessment to case., Session, Session (+2 more)

### Community 49 - "authority_policy_service.py"
Cohesion: 0.13
Nodes (14): env, browser, es2021, extends, parser, parserOptions, ecmaVersion, project (+6 more)

### Community 50 - ".__init__"
Cohesion: 0.13
Nodes (11): DashboardService, Dashboard service for KPI queries and aggregation. Orchestrates reporting reposi, Service for dashboard KPI queries and aggregation., Get operational dashboard with metrics and widgets for day-to-day operations., Get executive dashboard with control health, escalation rate, and release readin, Test operational dashboard service integration., Test executive dashboard service integration., Test dashboard query performance meets sub-2-second target. (+3 more)

### Community 51 - ".__init__"
Cohesion: 0.15
Nodes (10): ComplaintService, List all complaints for a case.          Args:             case_id: Case ID, Service for complaint lifecycle management., Create complaint record linked to case.          Args:             case_id: Case, Update complaint status and resolution notes.          Args:             complai, Test ComplaintService methods., Test creating complaint linked to case., Test updating complaint status. (+2 more)

### Community 52 - "CaseService"
Cohesion: 0.13
Nodes (14): Acceptance Criteria Checklist, Accessibility Tests, Documentation Generated, Health and Deployment, Linting and Type Checking, Non-Blocking Warnings, Overall Status, Performance Tests (+6 more)

### Community 53 - "DecisionService"
Cohesion: 0.06
Nodes (38): AssessmentRequest, create_case(), get_case_detail(), list_cases(), Session, Case Management API endpoints matching LLD OpenAPI contract. All endpoints enfor, List cases with filtering and pagination.     Returns paginated wrapper { items,, Get full case detail with nested intake, assessment, approvals, operations, and (+30 more)

### Community 54 - "dashboards.py"
Cohesion: 0.33
Nodes (4): DecisionService, Service for credit assessment and recommendation handling.     Captures analyst, Submit credit assessment recommendation for a case.          Args:             c, Finalize case outcome after assessment and approvals.          Args:

### Community 55 - "decode_access_token"
Cohesion: 0.17
Nodes (11): decode_access_token(), hash_password(), Authentication services: JWT creation/validation and bcrypt password hashing. Us, Hash a password using bcrypt.      Args:         password: Plain text password, Decode and validate a JWT access token.      Args:         token: JWT token stri, Test JWT token decoding with invalid token., Test successful login returns JWT token and user object., Test accessing protected endpoint with valid token succeeds. (+3 more)

### Community 56 - "test_operations.py"
Cohesion: 0.13
Nodes (15): AuthorityRule, Delegation-of-authority rules., AuthorityPolicyService, Session, Authority policy service for delegation-of-authority rule evaluation., Service for evaluating delegation-of-authority rules., Evaluate authority rules and return eligible approver level.          Args:, Get all authority rules for a role.          Args:             role_name: Role n (+7 more)

### Community 57 - "conftest.py"
Cohesion: 0.07
Nodes (29): client(), db_session(), Integration tests for cross-layer contract verification and end-to-end workflows, Verify backend CaseCreateRequest schema matches frontend intake form payload exa, Verify backend router column references match ORM model column definitions., Verify all seeded roles have entries in RBAC permission map.      Seeded roles:, Verify frontend api-client.ts reads base URL from VITE_API_URL env variable., Integration test: login → store token → call GET /api/v1/cases with auth header (+21 more)

### Community 58 - "test_get_outcome_distribution"
Cohesion: 0.22
Nodes (8): get_dashboard_service(), get_executive_dashboard(), get_operational_dashboard(), Session, Dashboard API endpoints for operational and executive dashboards. Provides KPI q, Dependency for dashboard service., Get operational dashboard with metrics and widgets.      Returns dashboard respo, Get executive dashboard with control health, escalation rate, and release readin

### Community 59 - "test_operational_dashboard_service"
Cohesion: 0.06
Nodes (34): Case, Customer credit review cases., List cases with optional filtering and pagination.         Returns (items, total, AuthorityEvaluationResult, Session, Workflow rules engine for state transitions, routing logic, and authority evalua, Check segregation-of-duties rules.         Returns True if actor cannot approve/, Result of authority evaluation matching LLD contract.     Contains routing decis (+26 more)

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
Cohesion: 0.09
Nodes (21): Acceptance Criteria Verification Results, ✅ All seeded roles have entries in RBAC permission map, ✅ Backend `CaseCreateRequest` schema matches frontend intake form payload exactly, ✅ Backend `CaseDetailResponse` schema matches frontend `CaseDetail` interface field-for-field, ✅ Backend integration tests pass: `pytest tests/test_integration.py`, ✅ Backend Pydantic `SessionResponse` schema matches frontend auth store setter field-for-field, ✅ Backend router column references match ORM model `models.py` column definitions, ✅ CORS verification: frontend at `http://localhost:5173` can call backend at `http://localhost:9000` without CORS errors (+13 more)

### Community 64 - "ApprovalSummary"
Cohesion: 0.22
Nodes (4): CardContentProps, CardHeaderProps, CardProps, CardTitleProps

### Community 65 - "CaseUpdate"
Cohesion: 0.33
Nodes (5): paginate(), PaginatedResponse, Pagination utilities for list endpoints matching cross-layer integration contrac, Paginated response wrapper matching shared_config.json contract.     Returns { i, Apply pagination to a SQLAlchemy query.      Args:         query: SQLAlchemy que

### Community 66 - "test_executive_dashboard_service"
Cohesion: 0.20
Nodes (10): Acceptance Criteria Verification, ✅ Accessibility Tests, ✅ Backend Linter, ⚠️ Backend Type Checker, ✅ Deployment Readiness, ✅ Frontend Linter, ✅ Frontend Type Checker, ✅ Performance Tests (+2 more)

### Community 67 - "test_export_creates_audit_event"
Cohesion: 0.14
Nodes (8): ApprovalRepository, Session, Approval repository for database access to approval_requests table., Repository for ApprovalRequest database operations., Get approval request by ID.          Args:             approval_request_id: Appr, List all approval requests for a case.          Args:             case_id: Case, List approval requests by status, optionally filtered by assigned approver., Session

### Community 69 - "create_access_token"
Cohesion: 0.20
Nodes (10): create_access_token(), Create a JWT access token with user_id claim and expiry.      Args:         user, Test JWT token creation with user_id claim and exp., Test JWT token decoding with valid token., Test JWT token decoding with expired token., test_create_access_token(), test_decode_access_token_expired(), test_decode_access_token_valid() (+2 more)

### Community 70 - "approvals.py"
Cohesion: 0.29
Nodes (7): ApprovalActionRequest, handle_approval_action(), list_approvals(), Session, Approval API endpoints for approval request creation and approve/reject/send-bac, List all approval requests for a case.      Args:         case_id: Case ID, Handle approval actions: request_approval, approve, reject, send_back.      Args

### Community 71 - ".create_or_update_renewal"
Cohesion: 0.22
Nodes (8): Application Rollback, Database Rollback, Deployment Guide, Development Tools, Prerequisites, Rollback Procedures, System Requirements, Table of Contents

### Community 72 - "Common Issues"
Cohesion: 0.22
Nodes (9): Common Issues, Debug Mode, Issue: Backend fails to start, Issue: Database locked (SQLite), Issue: Frontend cannot connect to backend, Issue: JWT token expired, Issue: SoD violation errors, Support Contacts (+1 more)

### Community 76 - "Final Verification Report"
Cohesion: 0.22
Nodes (8): Backend (mypy), Build Phase Complete: ✅ APPROVED, Executive Summary, Final Verification Report, Frontend (tsc), Sign-off, Table of Contents, Type Checker Results

### Community 77 - "Security Scan Results"
Cohesion: 0.22
Nodes (9): 1. SQL Injection Patterns, 2. Hardcoded Secrets, 3. Forbidden Libraries, 4. Auth Middleware Coverage, 5. SoD Enforcement, 6. Audit Logging, OWASP Top 10 Compliance, Security Audit Results (+1 more)

### Community 78 - "Application Deployment"
Cohesion: 0.25
Nodes (8): Application Deployment, Backend, Backend Service, Frontend, Frontend Service (nginx), Manual Deployment, Production Deployment (systemd), Quick Start (Development)

### Community 79 - "Monitoring and Logging"
Cohesion: 0.29
Nodes (7): Application Logs, Audit Events, Backend Logs, Frontend Logs, Key Metrics to Monitor, Monitoring and Logging, Performance Monitoring

### Community 80 - "Backup and Restore"
Cohesion: 0.33
Nodes (6): Automated Backup (cron), Backup and Restore, Backup Retention Policy, Database Backup, PostgreSQL, SQLite

### Community 81 - "conftest.py"
Cohesion: 0.33
Nodes (5): db(), override_get_db(), Shared pytest fixtures for all test modules., Override database dependency for testing., Create fresh database session for each test.

### Community 82 - "Deployment Readiness"
Cohesion: 0.33
Nodes (6): Accessibility Checklist, Deployment Documentation, Deployment Readiness, Health Endpoint, Security Audit Report, Startup Scripts

### Community 83 - "Manual Testing Results"
Cohesion: 0.33
Nodes (6): Accessibility Test Results, Color Contrast, Keyboard Navigation, Manual Testing Results, Screen Reader Testing, WCAG 2.1 AA Compliance

### Community 84 - "Appendix"
Cohesion: 0.40
Nodes (5): API Documentation, Appendix, Database Schema, Default Credentials (Seed Data), Security Checklist

### Community 85 - "Environment Configuration"
Cohesion: 0.40
Nodes (5): Backend Environment Variables, Environment Configuration, Environment Variable Reference, Frontend Environment Variables, Generating SECRET_KEY

### Community 86 - "Health Checks"
Cohesion: 0.50
Nodes (4): API Smoke Test, Backend Health Endpoint, Database Health Check, Health Checks

### Community 87 - "Database Setup"
Cohesion: 0.50
Nodes (4): Database Schema Verification, Database Setup, Development (SQLite), Production (PostgreSQL)

### Community 88 - "Linter Results"
Cohesion: 0.67
Nodes (3): Backend (ruff), Frontend (eslint), Linter Results

### Community 89 - "Test Results"
Cohesion: 0.67
Nodes (3): Backend Unit Tests, Frontend Unit Tests, Test Results

### Community 90 - "Performance Test Results"
Cohesion: 0.67
Nodes (3): Dashboard Query Performance, Page Load Performance, Performance Test Results

### Community 91 - "Known Issues and Limitations"
Cohesion: 0.67
Nodes (3): Known Issues and Limitations, Priority: LOW, Priority: NONE

## Knowledge Gaps
- **336 isolated node(s):** `verizon-credit-platform-backend`, `root`, `browser`, `es2021`, `extends` (+331 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `PaginatedResponse` to `CaseRepository`, `RiskBand`, `test_cases.py`, `Quick Start`, `test_export_creates_audit_event`, `.test_create_case_missing_required_fields`, `ComplaintStatus`, `FulfilmentStatus`, `.test_create_case_success`, `submit_assessment`, `.__init__`, `DecisionService`, `test_operations.py`, `test_operational_dashboard_service`, `test_cases.py`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `Case` connect `test_operational_dashboard_service` to `CaseRepository`, `RiskBand`, `test_cases.py`, `ApprovalStatus`, `.test_get_case_detail_not_found`, `.test_create_case_success`, `FulfilmentStatus`, `.test_create_case_missing_required_fields`, `submit_assessment`, `PaginatedResponse`, `CaseSummary`, `AuditService`, `.__init__`, `DecisionService`, `dashboards.py`, `test_operations.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `ReportingRepository` connect `.test_get_case_detail_not_found` to `test_get_queue_ageing`, `RiskBand`, `.test_create_case_missing_required_fields`, `CaseSummary`, `.__init__`, `test_get_outcome_distribution`, `test_operational_dashboard_service`, `.test_create_refund_success`, `ExportRequest`, `CaseService`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `User` (e.g. with `login()` and `ApprovalStatus`) actually correct?**
  _`User` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `Case` (e.g. with `ApprovalStatus` and `CaseStatus`) actually correct?**
  _`Case` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `ReportingRepository` (e.g. with `get_dashboard_service()` and `ExportRequest`) actually correct?**
  _`ReportingRepository` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `CaseStatus` (e.g. with `update_case()` and `ApprovalRequest`) actually correct?**
  _`CaseStatus` has 31 INFERRED edges - model-reasoned connections that need verification._