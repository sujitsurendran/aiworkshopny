"""
Database initialization and session management.
Uses synchronous SQLAlchemy with SQLite for MVP.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.domain.models import Base

# Create synchronous engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database by creating all tables."""
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at {settings.database_url}")


if __name__ == "__main__":
    # Allow running as module: python -m app.database
    init_db()
