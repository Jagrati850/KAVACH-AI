"""
KAVACH AI — Role-Based Access Control (RBAC)
Permission definitions and enforcement for all user roles.
"""

from enum import Enum
from typing import Set

from app.models.user import UserRole


class Permission(str, Enum):
    """Fine-grained permissions for RBAC."""
    # Scan operations
    SCAN_CREATE = "scan:create"
    SCAN_READ_OWN = "scan:read_own"
    SCAN_READ_ALL = "scan:read_all"

    # Report operations
    REPORT_CREATE = "report:create"
    REPORT_READ_OWN = "report:read_own"
    REPORT_READ_ALL = "report:read_all"
    REPORT_UPDATE = "report:update"
    REPORT_DELETE = "report:delete"

    # Case operations
    CASE_CREATE = "case:create"
    CASE_READ = "case:read"
    CASE_UPDATE = "case:update"
    CASE_ASSIGN = "case:assign"
    CASE_CLOSE = "case:close"

    # Transaction operations
    TRANSACTION_READ = "transaction:read"
    TRANSACTION_FLAG = "transaction:flag"

    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    THREAT_MAP_VIEW = "threat_map:view"
    FRAUD_GRAPH_VIEW = "fraud_graph:view"

    # Alert operations
    ALERT_READ = "alert:read"
    ALERT_RESOLVE = "alert:resolve"

    # User management
    USER_READ_ALL = "user:read_all"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # System
    SYSTEM_HEALTH = "system:health"
    AUDIT_LOG_READ = "audit:read"


# ── Role → Permission Mapping ───────────────────────────────
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.CITIZEN: {
        Permission.SCAN_CREATE,
        Permission.SCAN_READ_OWN,
        Permission.REPORT_CREATE,
        Permission.REPORT_READ_OWN,
    },

    UserRole.LEO: {
        Permission.SCAN_CREATE,
        Permission.SCAN_READ_OWN,
        Permission.SCAN_READ_ALL,
        Permission.REPORT_CREATE,
        Permission.REPORT_READ_OWN,
        Permission.REPORT_READ_ALL,
        Permission.REPORT_UPDATE,
        Permission.CASE_CREATE,
        Permission.CASE_READ,
        Permission.CASE_UPDATE,
        Permission.CASE_ASSIGN,
        Permission.CASE_CLOSE,
        Permission.ANALYTICS_VIEW,
        Permission.THREAT_MAP_VIEW,
        Permission.FRAUD_GRAPH_VIEW,
        Permission.ALERT_READ,
        Permission.ALERT_RESOLVE,
    },

    UserRole.BANK_ANALYST: {
        Permission.SCAN_CREATE,
        Permission.SCAN_READ_OWN,
        Permission.TRANSACTION_READ,
        Permission.TRANSACTION_FLAG,
        Permission.ANALYTICS_VIEW,
        Permission.THREAT_MAP_VIEW,
        Permission.FRAUD_GRAPH_VIEW,
        Permission.ALERT_READ,
    },

    UserRole.ADMIN: {
        # Admin gets everything
        perm for perm in Permission
    },
}


def has_permission(role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())


def get_permissions(role: UserRole) -> Set[Permission]:
    """Get all permissions for a given role."""
    return ROLE_PERMISSIONS.get(role, set())


def require_any(*permissions: Permission):
    """Check if user has ANY of the specified permissions."""
    def checker(role: UserRole) -> bool:
        user_perms = get_permissions(role)
        return bool(user_perms & set(permissions))
    return checker


def require_all(*permissions: Permission):
    """Check if user has ALL of the specified permissions."""
    def checker(role: UserRole) -> bool:
        user_perms = get_permissions(role)
        return set(permissions).issubset(user_perms)
    return checker
