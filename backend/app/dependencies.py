"""
KAVACH AI — FastAPI Dependencies
Authentication and authorization dependency injectors for API routes.
"""

from typing import Annotated, List

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.permissions import Permission, has_permission
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User, UserRole

settings = get_settings()


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract and validate the current user from the Authorization header.
    Used as a dependency in protected routes.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Use access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing user identifier",
        )

    # Fetch user from DB
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return user


# ── Type alias for cleaner route signatures ─────────────────
CurrentUser = Annotated[User, Depends(get_current_user)]


# ── Permission-based dependency factories ────────────────────
def require_permissions(*permissions: Permission):
    """
    Factory that creates a dependency requiring specific permissions.

    Usage:
        @router.get("/cases", dependencies=[Depends(require_permissions(Permission.CASE_READ))])
    """
    async def _check(current_user: CurrentUser) -> User:
        user_role = UserRole(current_user.role) if isinstance(current_user.role, str) else current_user.role
        for perm in permissions:
            if not has_permission(user_role, perm):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {perm.value}",
                )
        return current_user
    return _check


def require_roles(*roles: UserRole):
    """
    Factory that creates a dependency requiring specific roles.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_roles(UserRole.ADMIN))])
    """
    async def _check(current_user: CurrentUser) -> User:
        user_role = UserRole(current_user.role) if isinstance(current_user.role, str) else current_user.role
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in roles]}",
            )
        return current_user
    return _check


# ── Common dependency combinations ──────────────────────────
RequireAdmin = Depends(require_roles(UserRole.ADMIN))
RequireLEO = Depends(require_roles(UserRole.LEO, UserRole.ADMIN))
RequireBankAnalyst = Depends(require_roles(UserRole.BANK_ANALYST, UserRole.ADMIN))
RequireAnalytics = Depends(require_roles(UserRole.LEO, UserRole.BANK_ANALYST, UserRole.ADMIN))
