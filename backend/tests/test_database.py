"""
Basic database initialization tests.
"""
from sqlalchemy import inspect

from app.database import engine, init_db


def test_database_init():
    """Test that database initializes without errors."""
    init_db()

    # Verify engine is created
    assert engine is not None

    # Verify inspector can connect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    # Verify all required tables exist
    expected_tables = [
        "users", "roles", "user_roles", "cases", "credit_assessments",
        "approval_requests", "authority_rules", "sod_rules",
        "fulfilment_records", "complaint_records", "refund_records",
        "renewal_reviews", "notifications", "export_requests", "audit_events"
    ]

    for table in expected_tables:
        assert table in tables, f"Table {table} not found in database"


def test_required_indexes():
    """Test that required indexes exist on critical tables."""
    inspector = inspect(engine)

    # Check cases indexes
    cases_indexes = inspector.get_indexes("cases")
    [idx["name"] for idx in cases_indexes]
    assert any("current_status" in str(idx) for idx in cases_indexes), "Missing index on cases(current_status, assigned_to_id)"
    assert any("updated_at" in idx["name"] for idx in cases_indexes), "Missing index on cases(updated_at)"

    # Check approval_requests indexes
    approval_indexes = inspector.get_indexes("approval_requests")
    assert any("status" in str(idx) for idx in approval_indexes), "Missing index on approval_requests(status, assigned_approver_id)"

    # Check audit_events indexes
    audit_indexes = inspector.get_indexes("audit_events")
    assert any("entity_type" in str(idx) or "occurred_at" in str(idx) for idx in audit_indexes), "Missing index on audit_events"


def test_audit_events_hash_columns():
    """Test that audit_events table has hash_value and previous_hash columns."""
    inspector = inspect(engine)
    columns = inspector.get_columns("audit_events")
    column_names = [col["name"] for col in columns]

    assert "hash_value" in column_names, "audit_events table missing hash_value column"
    assert "previous_hash" in column_names, "audit_events table missing previous_hash column"


def test_retention_columns():
    """Test that retention_until columns exist on required tables."""
    inspector = inspect(engine)

    # Check cases table
    cases_columns = inspector.get_columns("cases")
    cases_column_names = [col["name"] for col in cases_columns]
    assert "retention_until" in cases_column_names, "cases table missing retention_until column"

    # Check approval_requests table
    approval_columns = inspector.get_columns("approval_requests")
    approval_column_names = [col["name"] for col in approval_columns]
    assert "retention_until" in approval_column_names, "approval_requests table missing retention_until column"

    # Check audit_events table
    audit_columns = inspector.get_columns("audit_events")
    audit_column_names = [col["name"] for col in audit_columns]
    assert "retention_until" in audit_column_names, "audit_events table missing retention_until column"
