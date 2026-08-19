"""
RBAC middleware, role-permission mapping, and segregation-of-duties rule enforcement.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# Role-permission mapping for RBAC enforcement
ROLE_PERMISSIONS = {
    "Order Management Analyst": [
        "cases:create",
        "cases:update",
        "cases:read",
        "cases:submit",
        "assessments:create",
        "assessments:update",
        "notes:create",
        "attachments:create",
    ],
    "Customer Success Manager": [
        "cases:read",
        "complaints:create",
        "complaints:update",
        "refunds:create",
        "refunds:update",
        "renewals:create",
        "renewals:update",
    ],
    "Sales Operations Manager": [
        "cases:read",
        "approvals:read",
        "approvals:approve",
        "approvals:reject",
        "approvals:send_back",
        "dashboards:operational",
        "exports:create",
    ],
    "VP Sales / Commercial Director": [
        "cases:read",
        "approvals:read",
        "approvals:approve",
        "approvals:reject",
        "approvals:send_back",
        "dashboards:executive",
        "dashboards:operational",
        "exports:create",
    ],
}


def check_permission(user_roles: list[str], required_permission: str) -> bool:
    """
    Check if any of the user's roles grant the required permission.

    Args:
        user_roles: List of role names assigned to the user
        required_permission: Permission string (e.g., "cases:create")

    Returns:
        True if user has permission, False otherwise
    """
    for role in user_roles:
        if role in ROLE_PERMISSIONS:
            if required_permission in ROLE_PERMISSIONS[role]:
                return True
    return False


def require_permission(user_roles: list[str], required_permission: str) -> None:
    """
    Enforce permission requirement, raising 403 if not authorized.

    Args:
        user_roles: List of role names assigned to the user
        required_permission: Permission string (e.g., "cases:create")

    Raises:
        HTTPException: 403 Forbidden if permission check fails
    """
    if not check_permission(user_roles, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {required_permission}"
        )


def check_sod_violation(actor_id: int, requester_id: int, action: str) -> bool:
    """
    Check for segregation-of-duties violation.

    Prevents an analyst from approving their own case recommendation.

    Args:
        actor_id: User ID of the person performing the action
        requester_id: User ID of the person who requested approval
        action: Action being performed (e.g., "approve")

    Returns:
        True if SoD violation detected, False otherwise
    """
    # Core SoD rule: Cannot approve your own request
    if action in ["approve", "reject", "send_back"]:
        if actor_id == requester_id:
            return True

    return False


def enforce_sod_check(db: Session, actor_id: int, requester_id: int, action: str) -> None:
    """
    Enforce segregation-of-duties check, raising 403 on violation.

    Args:
        db: Database session
        actor_id: User ID of the person performing the action
        requester_id: User ID of the person who requested approval
        action: Action being performed

    Raises:
        HTTPException: 403 Forbidden if SoD violation detected
    """
    violation = check_sod_violation(actor_id, requester_id, action)

    if violation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Segregation of duties violation: You cannot approve your own request"
        )
