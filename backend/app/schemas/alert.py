"""
KAVACH AI — Alert & Notification Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AlertResponse(BaseModel):
    """Alert response."""
    id: str
    alert_type: str
    severity: str
    title: str
    message: str
    alert_metadata: Optional[Dict[str, Any]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    region: Optional[str] = None
    is_resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    """Alert list."""
    alerts: List[AlertResponse]
    total: int


class NotificationResponse(BaseModel):
    """User notification."""
    id: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    action_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Notification list."""
    notifications: List[NotificationResponse]
    unread_count: int
    total: int
