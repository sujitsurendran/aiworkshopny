"""
FastAPI application initialization with CORS middleware and lifespan management.
"""
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import approvals, auth, cases, dashboards, exports, operations
from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Lifespan context manager for startup and shutdown events."""
    # Startup: initialize database
    init_db()

    # Optionally run seed data if AUTO_SEED environment variable is set
    if os.getenv("AUTO_SEED", "false").lower() == "true":
        from app.seed import run_seed
        run_seed()

    yield
    # Shutdown: cleanup if needed
    pass


# Create FastAPI application
app = FastAPI(
    title="Verizon Customer Credit Platform",
    description="Centralized customer credit review, approval governance, and operational oversight",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Configure CORS - allows Authorization and Content-Type headers
allowed_origins = settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(cases.router, prefix="/api/v1")
app.include_router(approvals.router, prefix="/api/v1")
app.include_router(operations.router, prefix="/api/v1")
app.include_router(dashboards.router, prefix="/api/v1")
app.include_router(exports.router, prefix="/api/v1")


# DEBUG_ROUTES
print(f"DEBUG: Number of routes registered: {len(app.routes)}", file=sys.stderr)
for r in app.routes:
    if hasattr(r, 'path'):
        print(f"DEBUG: Route: {r.path}", file=sys.stderr)

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer and monitoring."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Verizon Customer Credit Platform API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else None
    }
