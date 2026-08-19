"""
Audit repository for append-only event logging with hash chaining.
"""
import hashlib
import json
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.domain.models import AuditEvent


class AuditRepository:
    """Repository for immutable audit event operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_last_hash(self, entity_type: str, entity_id: int) -> Optional[str]:
        """Get the most recent hash for an entity to chain the next event."""
        last_event = (
            self.db.query(AuditEvent)
            .filter(AuditEvent.entity_type == entity_type, AuditEvent.entity_id == entity_id)
            .order_by(desc(AuditEvent.occurred_at))
            .first()
        )
        return last_event.hash_value if last_event else None

    def compute_hash(self, previous_hash: Optional[str], payload: dict) -> str:
        """
        Compute SHA-256 hash from previous hash + normalized payload.
        Ensures deterministic hash computation.
        """
        normalized_payload = json.dumps(payload, sort_keys=True)
        hash_input = f"{previous_hash or ''}{normalized_payload}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def append(self, event: AuditEvent) -> AuditEvent:
        """
        Append an immutable audit event with hash chaining.
        NO update or delete operations are permitted.
        """
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_events(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        actor_id: Optional[int] = None,
        limit: int = 100
    ) -> list[AuditEvent]:
        """Query audit events with filters."""
        query = self.db.query(AuditEvent)

        if entity_type:
            query = query.filter(AuditEvent.entity_type == entity_type)
        if entity_id:
            query = query.filter(AuditEvent.entity_id == entity_id)
        if actor_id:
            query = query.filter(AuditEvent.actor_id == actor_id)

        return query.order_by(desc(AuditEvent.occurred_at)).limit(limit).all()
