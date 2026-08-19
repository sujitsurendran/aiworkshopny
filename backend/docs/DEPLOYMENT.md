# Deployment Guide
**Project:** Verizon Customer Credit Platform v1.0  
**Version:** 1.0.0  
**Last Updated:** 2026-08-19

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Application Deployment](#application-deployment)
5. [Health Checks](#health-checks)
6. [Backup and Restore](#backup-and-restore)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Rollback Procedures](#rollback-procedures)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS:** Ubuntu 22.04 LTS, macOS 12+, or Windows 10/11
- **Python:** 3.10+ (3.12 recommended)
- **Node.js:** 18.0+ (18.x LTS recommended)
- **Database:** SQLite 3.35+ (for demo/dev) or PostgreSQL 14+ (for production)
- **Memory:** 2GB RAM minimum, 4GB recommended
- **Storage:** 10GB minimum free space

### Development Tools
```bash
# Python and pip
python3 --version  # Should be 3.10+
pip3 --version

# Node.js and npm
node --version     # Should be 18+
npm --version

# Git
git --version
```

---

## Environment Configuration

### Backend Environment Variables

Create `/repos/aiworkshopny/backend/.env` from `.env.example`:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./credit_platform.db
# Production: DATABASE_URL=postgresql://user:password@localhost:5432/credit_platform

# Security Configuration
SECRET_KEY=your-secret-key-min-32-chars-recommended
TOKEN_EXPIRY_SECONDS=3600

# API Configuration
API_PORT=9000
DEBUG=false

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Optional: Auto-seed on startup
AUTO_SEED=false
```

### Frontend Environment Variables

Create `/repos/aiworkshopny/frontend/.env` from `.env.example`:

```bash
# Backend API URL
VITE_API_URL=http://localhost:9000
```

### Environment Variable Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Database connection string | `sqlite:///./credit_platform.db` | Yes |
| `SECRET_KEY` | JWT signing secret (min 32 chars) | None | Yes |
| `TOKEN_EXPIRY_SECONDS` | JWT token expiry duration | `3600` | No |
| `API_PORT` | Backend API port | `9000` | No |
| `DEBUG` | Enable debug logging | `false` | No |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:5173,http://localhost:3000` | Yes |
| `AUTO_SEED` | Auto-run seed data on startup | `false` | No |
| `VITE_API_URL` | Frontend API base URL | `http://localhost:9000` | Yes |

### Generating SECRET_KEY

```bash
# Python method
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL method
openssl rand -base64 32
```

---

## Database Setup

### Development (SQLite)

```bash
cd /repos/aiworkshopny/backend

# Create database and tables
python3 -m app.database

# Seed default users and sample data
python3 -m app.seed
```

### Production (PostgreSQL)

```bash
# 1. Create database
psql -U postgres
CREATE DATABASE credit_platform;
CREATE USER credit_user WITH ENCRYPTED PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE credit_platform TO credit_user;
\q

# 2. Update .env
DATABASE_URL=postgresql://credit_user:your-secure-password@localhost:5432/credit_platform

# 3. Initialize schema
cd /repos/aiworkshopny/backend
python3 -m app.database

# 4. Seed data (optional)
python3 -m app.seed
```

### Database Schema Verification

```bash
# SQLite
sqlite3 credit_platform.db ".tables"
# Expected: 15 tables (users, roles, user_roles, cases, credit_assessments, etc.)

# PostgreSQL
psql -U credit_user -d credit_platform -c "\dt"
```

---

## Application Deployment

### Quick Start (Development)

```bash
cd /repos/aiworkshopny

# Unix/Mac
./start.sh

# Windows
start.bat
```

The startup script will:
1. Check Python 3.10+ and Node.js 18+ prerequisites
2. Install backend dependencies (`pip install .`)
3. Install frontend dependencies (`npm install`)
4. Initialize database
5. Run seed data (if AUTO_SEED=true)
6. Start backend on port 9000
7. Start frontend on port 5173
8. Print URLs and default credentials

### Manual Deployment

#### Backend

```bash
cd /repos/aiworkshopny/backend

# Install dependencies
pip install .

# Initialize database
python3 -m app.database

# Seed data (optional)
python3 -m app.seed

# Start application
uvicorn app.main:app --host 0.0.0.0 --port 9000 --workers 4
```

#### Frontend

```bash
cd /repos/aiworkshopny/frontend

# Install dependencies
npm install

# Development server
npm run dev -- --port 5173

# Production build
npm run build
# Serve dist/ with nginx or another static server
```

### Production Deployment (systemd)

#### Backend Service

Create `/etc/systemd/system/credit-platform-backend.service`:

```ini
[Unit]
Description=Verizon Customer Credit Platform Backend
After=network.target postgresql.service

[Service]
Type=simple
User=credit-platform
WorkingDirectory=/opt/credit-platform/backend
Environment="PATH=/opt/credit-platform/backend/.venv/bin"
ExecStart=/opt/credit-platform/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 9000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable credit-platform-backend
sudo systemctl start credit-platform-backend
sudo systemctl status credit-platform-backend
```

#### Frontend Service (nginx)

Create `/etc/nginx/sites-available/credit-platform-frontend`:

```nginx
server {
    listen 80;
    server_name credit.example.com;

    root /opt/credit-platform/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/v1/ {
        proxy_pass http://localhost:9000/api/v1/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/credit-platform-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Health Checks

### Backend Health Endpoint

```bash
curl http://localhost:9000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2026-08-19T00:15:00.000Z",
  "version": "1.0.0"
}
```

### Database Health Check

```bash
# SQLite
sqlite3 credit_platform.db "SELECT COUNT(*) FROM users;"
# Expected: 4 users if seeded

# PostgreSQL
psql -U credit_user -d credit_platform -c "SELECT COUNT(*) FROM users;"
```

### API Smoke Test

```bash
# Login endpoint
curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"password123"}'

# Expected: JWT token in response
```

---

## Backup and Restore

### Database Backup

#### SQLite

```bash
# Backup
sqlite3 credit_platform.db ".backup /backups/credit_platform_$(date +%Y%m%d_%H%M%S).db"

# Restore
cp /backups/credit_platform_20260819_001500.db credit_platform.db
```

#### PostgreSQL

```bash
# Backup
pg_dump -U credit_user -d credit_platform -F c -f /backups/credit_platform_$(date +%Y%m%d_%H%M%S).dump

# Restore
pg_restore -U credit_user -d credit_platform -c /backups/credit_platform_20260819_001500.dump
```

### Automated Backup (cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /usr/local/bin/backup_credit_platform.sh
```

Create `/usr/local/bin/backup_credit_platform.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/credit-platform"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
pg_dump -U credit_user -d credit_platform -F c -f "${BACKUP_DIR}/db_${DATE}.dump"

# Backup audit logs
tar -czf "${BACKUP_DIR}/logs_${DATE}.tar.gz" /var/log/credit-platform/

# Remove backups older than 30 days
find ${BACKUP_DIR} -type f -mtime +30 -delete

echo "Backup completed: ${DATE}"
```

### Backup Retention Policy

- **Daily backups:** Retain 7 days
- **Weekly backups:** Retain 4 weeks
- **Monthly backups:** Retain 12 months
- **Annual backups:** Retain 7 years (regulatory compliance)

---

## Monitoring and Logging

### Application Logs

#### Backend Logs
```bash
# Development (console)
tail -f /repos/aiworkshopny/backend/credit_platform.log

# Production (systemd)
journalctl -u credit-platform-backend -f
```

#### Frontend Logs
```bash
# Development (console)
npm run dev

# Production (nginx)
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Audit Events

```sql
-- Recent audit events
SELECT * FROM audit_events ORDER BY occurred_at DESC LIMIT 50;

-- SoD violations
SELECT * FROM audit_events WHERE action_type = 'sod_violation' ORDER BY occurred_at DESC;

-- Approval activity
SELECT * FROM audit_events WHERE entity_type = 'approval_request' ORDER BY occurred_at DESC;
```

### Performance Monitoring

```bash
# Backend response times
curl -w "\nTime: %{time_total}s\n" http://localhost:9000/api/v1/cases

# Database query performance
sqlite3 credit_platform.db "EXPLAIN QUERY PLAN SELECT * FROM cases WHERE current_status = 'NEW';"
```

### Key Metrics to Monitor

| Metric | Threshold | Alert Level |
|--------|-----------|-------------|
| API response time | > 2 seconds | Warning |
| Database query time | > 1 second | Warning |
| Memory usage | > 80% | Warning |
| Disk usage | > 90% | Critical |
| Failed login attempts | > 10/minute | Critical |
| SoD violations | > 5/hour | Warning |
| Audit event lag | > 5 minutes | Critical |

---

## Rollback Procedures

### Application Rollback

```bash
# 1. Stop services
sudo systemctl stop credit-platform-backend
sudo systemctl stop nginx

# 2. Restore previous version
cd /opt/credit-platform
rm -rf current
ln -s releases/v1.0.0-rc1 current

# 3. Restore database backup
pg_restore -U credit_user -d credit_platform -c /backups/credit_platform_pre_v1.0.0.dump

# 4. Start services
sudo systemctl start credit-platform-backend
sudo systemctl start nginx

# 5. Verify health
curl http://localhost:9000/health
```

### Database Rollback

```bash
# 1. Stop application
sudo systemctl stop credit-platform-backend

# 2. Backup current state
pg_dump -U credit_user -d credit_platform -F c -f /backups/rollback_source_$(date +%Y%m%d_%H%M%S).dump

# 3. Restore previous backup
pg_restore -U credit_user -d credit_platform -c /backups/credit_platform_20260818_020000.dump

# 4. Start application
sudo systemctl start credit-platform-backend
```

---

## Troubleshooting

### Common Issues

#### Issue: Backend fails to start

**Symptoms:**
```
Error: Database connection failed
```

**Resolution:**
```bash
# Check database connectivity
psql -U credit_user -d credit_platform -c "SELECT 1;"

# Verify DATABASE_URL in .env
cat backend/.env | grep DATABASE_URL

# Check database tables exist
psql -U credit_user -d credit_platform -c "\dt"
```

#### Issue: Frontend cannot connect to backend

**Symptoms:**
```
Network Error: Failed to fetch
```

**Resolution:**
```bash
# Check backend is running
curl http://localhost:9000/health

# Verify VITE_API_URL in frontend/.env
cat frontend/.env | grep VITE_API_URL

# Check CORS configuration
cat backend/.env | grep CORS_ORIGINS

# Restart frontend
npm run dev -- --port 5173
```

#### Issue: JWT token expired

**Symptoms:**
```
401 Unauthorized: Token has expired
```

**Resolution:**
```bash
# User must log in again to get new token
# Adjust TOKEN_EXPIRY_SECONDS in .env if needed (default: 3600s = 1 hour)

# Clear frontend localStorage
localStorage.removeItem('access_token');
```

#### Issue: SoD violation errors

**Symptoms:**
```
403 Forbidden: Segregation of duties violation
```

**Resolution:**
- SoD violations are intentional security controls
- User cannot approve their own requests
- Assign approval to different user with appropriate role
- Check audit_events table for violation details

#### Issue: Database locked (SQLite)

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Resolution:**
```bash
# Close all connections
pkill -f uvicorn

# Check for lock file
ls -la credit_platform.db-*

# Remove lock file if safe
rm credit_platform.db-wal credit_platform.db-shm

# Restart application
uvicorn app.main:app --host 0.0.0.0 --port 9000
```

### Debug Mode

Enable debug logging in `.env`:

```bash
DEBUG=true
```

Restart application and check detailed logs:

```bash
journalctl -u credit-platform-backend -f
```

### Support Contacts

- **Technical Issues:** Platform Team <platform-team@example.com>
- **Security Issues:** Security Team <security@example.com>
- **Business Questions:** Product Owner <product@example.com>

---

## Appendix

### Default Credentials (Seed Data)

| Role | Email | Password | Permissions |
|------|-------|----------|-------------|
| Order Management Analyst | analyst@example.com | password123 | Create cases, submit assessments |
| Customer Success Manager | csm@example.com | password123 | View cases, manage complaints/refunds |
| Sales Operations Manager | manager@example.com | password123 | Approve exceptions, view dashboards |
| VP Sales / Commercial Director | vp@example.com | password123 | Approve high-value exceptions, executive dashboards |

**⚠️ IMPORTANT:** Change all default passwords before production deployment!

### API Documentation

- **Swagger UI:** http://localhost:9000/docs
- **ReDoc:** http://localhost:9000/redoc
- **OpenAPI JSON:** http://localhost:9000/openapi.json

### Database Schema

15 tables:
- `users`, `roles`, `user_roles` (identity and RBAC)
- `cases` (customer credit review cases)
- `credit_assessments` (credit decisions)
- `approval_requests` (approval queue)
- `authority_rules`, `sod_rules` (governance policies)
- `fulfilment_records` (milestone tracking)
- `complaint_records` (complaint management)
- `refund_records` (returns and refunds)
- `renewal_reviews` (renewal risk tracking)
- `notifications` (in-app notifications)
- `export_requests` (export audit trail)
- `audit_events` (immutable audit log)

### Security Checklist

- [ ] Change SECRET_KEY from default
- [ ] Update default user passwords
- [ ] Configure CORS_ORIGINS for production domains
- [ ] Enable HTTPS/TLS for production
- [ ] Set DEBUG=false in production
- [ ] Configure PostgreSQL with strong password
- [ ] Enable database connection encryption
- [ ] Set up automated backups
- [ ] Configure log rotation
- [ ] Review and restrict file permissions
- [ ] Enable firewall rules (allow only 80/443)
- [ ] Set up monitoring and alerting

---

**Document Version:** 1.0.0  
**Last Reviewed:** 2026-08-19  
**Next Review Date:** 2026-09-19
