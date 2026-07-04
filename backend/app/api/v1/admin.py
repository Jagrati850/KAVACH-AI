"""
KAVACH AI — Admin API
User management, audit logs, and system health.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser, RequireAdmin
from app.models.audit import AuditLog
from app.models.user import User, UserRole
from app.schemas.user import UserAdminUpdate, UserListResponse, UserResponse

router = APIRouter()


@router.get("/users", response_model=UserListResponse, dependencies=[RequireAdmin])
async def list_users(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    role: str | None = Query(None),
    is_active: bool | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all users with filtering (Admin only)."""
    query = select(User)
    count_query = select(func.count()).select_from(User)

    if role:
        query = query.where(User.role == UserRole(role))
        count_query = count_query.where(User.role == UserRole(role))
    if is_active is not None:
        query = query.where(User.is_active == is_active)
        count_query = count_query.where(User.is_active == is_active)
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (User.full_name.ilike(search_filter)) | (User.email.ilike(search_filter))
        )
        count_query = count_query.where(
            (User.full_name.ilike(search_filter)) | (User.email.ilike(search_filter))
        )

    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    users = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.put("/users/{user_id}", response_model=UserResponse, dependencies=[RequireAdmin])
async def update_user(
    user_id: str,
    payload: UserAdminUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update user role, status, or verification (Admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.role is not None:
        user.role = UserRole(payload.role)
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.is_verified is not None:
        user.is_verified = payload.is_verified

    await db.flush()
    return UserResponse.model_validate(user)


@router.get("/audit-logs", dependencies=[RequireAdmin])
async def get_audit_logs(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    action: str | None = Query(None),
    user_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """View audit trail (Admin only)."""
    query = select(AuditLog).order_by(AuditLog.created_at.desc())

    if action:
        query = query.where(AuditLog.action == action)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource": log.resource,
                "resource_id": log.resource_id,
                "ip_address": log.ip_address,
                "details": log.details,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
        "page": page,
        "page_size": page_size,
    }


@router.get("/system-health", dependencies=[RequireAdmin])
async def system_health(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    """System health status."""
    # Check DB connectivity
    try:
        await db.execute(select(func.count()).select_from(User))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "operational",
        "database": db_status,
        "ai_engines": {
            "scam_detector": "active",
            "currency_detector": "active",
            "deepfake_detector": "active",
            "fraud_graph": "active",
            "geospatial": "active",
        },
        "version": "1.0.0",
    }
