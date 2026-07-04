"""
KAVACH AI — User Schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """Full user response model."""
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    organization: Optional[str] = None
    designation: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """User profile update payload."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{9,14}$")
    organization: Optional[str] = Field(None, max_length=255)
    designation: Optional[str] = Field(None, max_length=255)


class UserAdminUpdate(BaseModel):
    """Admin-level user update."""
    full_name: Optional[str] = None
    role: Optional[str] = Field(None, pattern=r"^(citizen|leo|bank_analyst|admin)$")
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserListResponse(BaseModel):
    """Paginated user list."""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
