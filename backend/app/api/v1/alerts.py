"""
KAVACH AI — Alerts & Notifications API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser
from app.models.alert import Alert, Notification
from app.schemas.alert import (
    AlertListResponse,
    AlertResponse,
    NotificationListResponse,
    NotificationResponse,
)

router = APIRouter()


@router.get("/", response_model=AlertListResponse)
async def list_alerts(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    severity: str | None = Query(None),
    resolved: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """List system alerts."""
    query = select(Alert).order_by(Alert.created_at.desc())

    if severity:
        query = query.where(Alert.severity == severity)
    if resolved is not None:
        query = query.where(Alert.is_resolved == resolved)

    query = query.limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    count_result = await db.execute(select(func.count()).select_from(Alert))
    total = count_result.scalar()

    return AlertListResponse(
        alerts=[AlertResponse.model_validate(a) for a in alerts],
        total=total,
    )


@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
):
    """List current user's notifications."""
    query = select(Notification).where(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc())

    if unread_only:
        query = query.where(Notification.is_read == False)

    query = query.limit(limit)

    result = await db.execute(query)
    notifications = result.scalars().all()

    unread_count_result = await db.execute(
        select(func.count()).select_from(Notification).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )
    unread_count = unread_count_result.scalar()

    total_result = await db.execute(
        select(func.count()).select_from(Notification).where(
            Notification.user_id == current_user.id
        )
    )
    total = total_result.scalar()

    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        unread_count=unread_count,
        total=total,
    )


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    await db.flush()

    return {"message": "Notification marked as read"}


@router.put("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.flush()

    return {"message": "All notifications marked as read"}
