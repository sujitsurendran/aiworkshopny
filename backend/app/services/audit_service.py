"""
Audit service for append-only event logging with hash chaining.
All governed actions must call appendEvent() in same transaction as business mutation.
"""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.models import AuditEvent
from app.repositories.audit_repository import AuditRepository


class AuditService:
    """
    Service for immutable audit event logging.
    Enforces hash chaining and 7-year retention policy.
    """

    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditRepository(db)

    def append_event(
        self,
        entity_type: str,
        entity_id: int,
        action_type: str,
        actor_id: int,
        payload: Optional[dict] = None
    ) -> AuditEvent:
        """
        Append an immutable audit event with hash chaining.

        Args:
            entity_type: Type of entity (e.g., "Case", "ApprovalRequest")
            entity_id: ID of the entity
            action_type: Action performed (e.g., "CREATE", "UPDATE", "APPROVE")
            actor_id: User ID who performed the action
            payload: Optional JSON payload with action details

        Returns:
            Created AuditEvent
        """
        # Get previous hash for chain continuity
        previous_hash = self.audit_repo.get_last_hash(entity_type, entity_id)

        # Compute hash from previous_hash + payload
        hash_value = self.audit_repo.compute_hash(previous_hash, payload or {})

        # Create audit event with 7-year retention
        event = AuditEvent(
            entity_type=entity_type,
            entity_id=entity_id,
            action_type=action_type,
            actor_id=actor_id,
            occurred_at=datetime.utcnow(),
            payload_json=payload,
            hash_value=hash_value,
            previous_hash=previous_hash,
            retention_until=datetime.utcnow() + timedelta(days=365 * 7)  # 7 years
        )

        return self.audit_repo.append(event)

    def get_timeline(
        self,
        entity_type: str,
        entity_id: int,
        limit: int = 50
    ) -> list[AuditEvent]:
        """
        Retrieve audit timeline for an entity.

        Args:
            entity_type: Type of entity
            entity_id: ID of the entity
            limit: Maximum events to return

        Returns:
            List of audit events ordered by occurred_at desc
        """
        return self.audit_repo.list_events(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit
        )
