"""
Case repository for database access.
All queries use SQLAlchemy ORM without raw SQL string interpolation.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.domain.enums import CaseStatus
from app.domain.models import (
    Case,
    CreditAssessment,
)


class CaseRepository:
    """Repository for Case entity database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, case: Case) -> Case:
        """Create a new case."""
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case

    def get_by_id(self, case_id: int) -> Optional[Case]:
        """Retrieve case by ID with all relationships loaded."""
        return (
            self.db.query(Case)
            .options(
                joinedload(Case.credit_assessments),
                joinedload(Case.approval_requests),
                joinedload(Case.fulfilment_records),
                joinedload(Case.complaint_records),
                joinedload(Case.refund_records),
                joinedload(Case.renewal_reviews),
                joinedload(Case.created_by),
                joinedload(Case.assigned_to)
            )
            .filter(Case.id == case_id)
            .first()
        )

    def list_cases(
        self,
        filters: dict = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Case], int]:
        """
        List cases with optional filtering and pagination.
        Returns (items, total_count).
        """
        query = self.db.query(Case)

        if filters:
            if filters.get("status"):
                query = query.filter(Case.current_status == CaseStatus(filters["status"]))
            if filters.get("exception_flag") is not None:
                query = query.filter(Case.exception_flag == filters["exception_flag"])
            if filters.get("assigned_to_id"):
                query = query.filter(Case.assigned_to_id == filters["assigned_to_id"])
            if filters.get("customer_id"):
                query = query.filter(Case.customer_id == filters["customer_id"])

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(Case.updated_at.desc()).limit(page_size).offset(offset).all()

        return items, total

    def update(self, case: Case) -> Case:
        """Update an existing case."""
        case.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(case)
        return case

    def add_assessment(self, assessment: CreditAssessment) -> CreditAssessment:
        """Add credit assessment to case."""
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment
