# Verizon Customer Credit Platform v1.0

A self-contained internal web application that centralizes customer credit review, approval governance, fulfilment follow-through, and operational oversight.

## Overview

The Verizon Customer Credit Platform provides a single, auditable system for fast, policy-aligned, evidence-backed commercial decisions on customer orders while reducing manual coordination across credit, fulfilment, customer care, and sales oversight functions.

## Tech Stack

### Backend
- **Framework:** Python 3.10+ with FastAPI
- **Database:** SQLite (MVP) / PostgreSQL (Production)
- **ORM:** SQLAlchemy 2.0 (synchronous)
- **Authentication:** JWT with bcrypt password hashing

### Frontend
- **Framework:** React 18+ with TypeScript
- **Build Tool:** Vite 5
- **Router:** React Router DOM 6

## Architecture

This is a monolithic application with:
- Single backend API server
- Single-page application (SPA) frontend
- Relational database with 7-year retention compliance
- Role-based access control (RBAC)
- Immutable audit logging with hash chaining
- Segregation-of-duties enforcement

## Directory Structure

```
aiworkshopny/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API route controllers
│   │   ├── domain/      # ORM models, enums, schemas
│   │   ├── services/    # Business logic services
│   │   ├── repositories/# Data access repositories
│   │   ├── security/    # Auth, RBAC, JWT
│   │   └── shared/      # Utilities, errors, pagination
│   ├── tests/           # Backend tests
│   ├── pyproject.toml   # Python dependencies
│   └── .env.example     # Backend environment template
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── lib/         # API client, auth context, utils
│   │   └── types/       # TypeScript type definitions
│   ├── tests/           # Frontend tests
│   ├── package.json     # Node dependencies
│   └── .env.example     # Frontend environment template
├── shared_config.json   # Cross-layer integration contract
├── start.sh             # Unix/Mac startup script
├── start.bat            # Windows startup script
├── stop.sh              # Unix/Mac shutdown script
└── stop.bat             # Windows shutdown script
```

## Quick Start

### Prerequisites

- **Python:** 3.10 or higher
- **Node.js:** 18 or higher
- **npm:** 8 or higher

### Setup and Run

#### Linux / macOS
```bash
./start.sh
```

#### Windows
```cmd
start.bat
```

The startup script will:
1. Check prerequisites (Python 3.10+, Node.js 18+)
2. Install backend dependencies
3. Install frontend dependencies
4. Initialize database with schema
5. Load seed data with default users
6. Start backend API server on port 9000
7. Start frontend dev server on port 5173
8. Print access URLs and default credentials

### Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:9000
- **API Documentation:** http://localhost:9000/docs (when DEBUG=true)
- **Health Check:** http://localhost:9000/health

### Default Credentials

The seed data creates four users (one per role):

| Role | Email | Password |
|------|-------|----------|
| Order Management Analyst | analyst@example.com | password123 |
| Customer Success Manager | csm@example.com | password123 |
| Sales Operations Manager | manager@example.com | password123 |
| VP Sales / Commercial Director | vp@example.com | password123 |

**⚠️ Change these credentials in production!**

### Shutdown

#### Linux / macOS
```bash
./stop.sh
```

#### Windows
```cmd
stop.bat
```

## Environment Variables

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Database connection string | sqlite:///./verizon_credit.db |
| SECRET_KEY | JWT signing secret | (required in production) |
| TOKEN_EXPIRY_SECONDS | JWT token expiry duration | 86400 (24 hours) |
| API_PORT | Backend API port | 9000 |
| DEBUG | Enable debug mode | true |
| CORS_ORIGINS | Allowed CORS origins (comma-separated) | http://localhost:5173 |

### Frontend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_API_URL | Backend API base URL | http://localhost:9000 |

## Development

### Backend Development

```bash
cd backend

# Install dependencies
pip install .

# Install dev dependencies
pip install '.[dev]'

# Run tests
pytest tests/

# Run linter
ruff check app/

# Start backend only
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run tests
npm test

# Run linter
npm run lint

# Type check
npm run type-check

# Build for production
npm run build

# Start frontend only
npm run dev
```

## Testing

### Run All Tests

```bash
# Backend
cd backend && pytest tests/

# Frontend
cd frontend && npm test
```

## Database Schema

The platform uses a relational database with the following core tables:

- `users`, `roles`, `user_roles` - Identity and RBAC
- `cases` - Customer credit review cases
- `credit_assessments` - Credit validation findings
- `approval_requests` - Approval queue and decisions
- `authority_rules`, `sod_rules` - Governance policies
- `fulfilment_records` - Fulfilment tracking
- `complaint_records` - Complaint management
- `refund_records` - Refund and return handling
- `renewal_reviews` - Account renewal reviews
- `notifications` - In-app notification queue
- `export_requests` - Export audit trail
- `audit_events` - Immutable audit log with hash chaining

All tables include `retention_until` or `created_at` timestamps for 7-year retention compliance.

## Security Features

- JWT-based authentication with bcrypt password hashing
- Role-based access control (RBAC)
- Segregation-of-duties (SoD) enforcement
- Delegation-of-authority rules
- Input validation on all API endpoints
- Parameterized database queries (SQL injection protection)
- CORS configuration for frontend origins
- Immutable audit logging with hash chaining

## Performance Targets

- Sub-2-second page loads, search, and filtering for 95% of interactions
- Support 1000+ peak concurrent users
- 99.5% uptime during business hours

## Compliance

- 7-year record retention for cases, approvals, and audit events
- Immutable audit trail for all governed actions
- Evidence attachment and retention for compliance period
- WCAG 2.1 AA accessibility compliance

## Troubleshooting

### Port already in use

If ports 9000 or 5173 are already in use, the startup script will automatically find available ports and update the configuration.

### Database initialization fails

```bash
cd backend
python -m app.database
```

### Frontend build fails

Ensure all dependencies are installed:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS errors

Verify that `CORS_ORIGINS` in backend `.env` includes the frontend URL (http://localhost:5173).

## Support

For issues, questions, or feedback, contact the platform development team.

---

**Version:** 1.0.0  
**Last Updated:** 2026-08-18
