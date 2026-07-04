"""
KAVACH AI — Authentication Schemas
Request/response models for auth endpoints.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration payload."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str | None = Field(None, pattern=r"^\+?[1-9]\d{9,14}$")
    role: str = Field(default="citizen", pattern=r"^(citizen|leo|bank_analyst|admin)$")
    organization: str | None = Field(None, max_length=255)
    designation: str | None = Field(None, max_length=255)

    model_config = {"json_schema_extra": {
        "example": {
            "email": "officer@cybercell.gov.in",
            "password": "SecureP@ss2026",
            "full_name": "Inspector Rajesh Kumar",
            "phone": "+919876543210",
            "role": "leo",
            "organization": "Cyber Crime Cell, Delhi Police",
            "designation": "Cyber Crime Inspector",
        }
    }}


class LoginRequest(BaseModel):
    """Login credentials."""
    email: EmailStr
    password: str

    model_config = {"json_schema_extra": {
        "example": {
            "email": "officer@cybercell.gov.in",
            "password": "SecureP@ss2026",
        }
    }}


class TokenResponse(BaseModel):
    """JWT token pair response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserBasicResponse"


class UserBasicResponse(BaseModel):
    """Minimal user info returned with auth tokens."""
    id: str
    email: str
    full_name: str
    role: str
    is_verified: bool


class RefreshRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Password change payload."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


# Rebuild models after forward reference
TokenResponse.model_rebuild()
