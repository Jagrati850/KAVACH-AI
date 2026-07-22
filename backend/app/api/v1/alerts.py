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


from pydantic import BaseModel, Field

class TestSMSRequest(BaseModel):
    phone_number: str | None = Field(None, description="Recipient phone number (defaults to settings.test_phone_number or current user's phone)")
    message: str = Field("KAVACH AI SMS System Test: Digital Safety Shield active.", description="Sample text body")
    template_id: str | None = Field(None, description="Optional Template ID override")
    variables: dict[str, str] | None = Field(None, description="Optional flow variables")

@router.post("/test-sms")
async def send_test_sms(
    payload: TestSMSRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Sends a test SMS alert through the generic Notification Service.
    """
    from app.services.sms import get_notification_service
    from app.config import get_settings
    from app.models.alert import Alert, AlertType, AlertSeverity, Notification
    from app.models.audit import AuditLog
    from app.models.user import User

    settings = get_settings()
    notif_service = get_notification_service()

    # Target: payload -> settings.test_phone_number -> current logged in user phone number
    target_phone = payload.phone_number or settings.test_phone_number or current_user.phone

    if not target_phone:
        raise HTTPException(
            status_code=400,
            detail="SMS Dispatch Error: No recipient phone number supplied or found in user details."
        )

    # 1. Trigger the SMS Dispatch Service (prints to console)
    success = await notif_service.send_custom_alert(
        phone=target_phone,
        message=payload.message
    )

    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"SMS Delivery failed."
        )

    # 2. Store broadcast alert message in DB
    alert = Alert(
        alert_type=AlertType.SYSTEM,
        severity=AlertSeverity.WARNING,
        title="Administrative Safety Broadcast",
        message=payload.message,
        alert_metadata={"recipient": target_phone}
    )
    db.add(alert)
    await db.flush()

    # 3. Create active Notification entries for all users
    users_res = await db.execute(select(User))
    all_users = users_res.scalars().all()
    for u in all_users:
        notif = Notification(
            user_id=u.id,
            alert_id=alert.id,
            title="Public Safety Broadcast Alert",
            message=payload.message,
            notification_type="broadcast",
            is_read=False
        )
        db.add(notif)

    # 4. Generate Audit Log Entry
    audit_log = AuditLog(
        user_id=current_user.id,
        action="broadcast_message",
        resource="broadcast",
        resource_id=target_phone,
        details={"message": payload.message, "recipient": target_phone}
    )
    db.add(audit_log)
    await db.flush()

    return {
        "success": True,
        "recipient": target_phone,
        "provider": settings.sms_provider,
        "message": "SMS alert processed by Notification Service successfully."
    }
