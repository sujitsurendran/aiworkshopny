"""
Pagination utilities for list endpoints matching cross-layer integration contract.
"""
from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response wrapper matching shared_config.json contract.
    Returns { items, total, page, page_size }.
    """
    items: List[T]
    total: int
    page: int
    page_size: int

    model_config = {"from_attributes": True}


def paginate(query, page: int = 1, page_size: int = 20):
    """
    Apply pagination to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Tuple of (items, total_count)
    """
    total = query.count()
    offset = (page - 1) * page_size
    items = query.limit(page_size).offset(offset).all()
    return items, total
