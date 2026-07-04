"""
KAVACH AI — Report Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    """Create a new fraud/scam report."""
    report_type: str = Field(
        ...,
        pattern=r"^(scam_call|phishing|counterfeit_currency|upi_fraud|digital_arrest|deepfake|identity_theft|other)$"
    )
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=20, max_length=5000)
    suspect_phone: Optional[str] = Field(None, max_length=20)
    suspect_name: Optional[str] = Field(None, max_length=255)
    suspect_account: Optional[str] = Field(None, max_length=255)
    amount_lost: Optional[float] = Field(None, ge=0)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    incident_date: Optional[datetime] = None

    model_config = {"json_schema_extra": {
        "example": {
            "report_type": "digital_arrest",
            "title": "Fake CBI officer demanded money via video call",
            "description": "Received a WhatsApp video call from person claiming to be CBI officer. Showed fake ID card and arrest warrant. Demanded ₹2,00,000 to clear my name from a fake case. The call lasted 45 minutes.",
            "suspect_phone": "+918765432109",
            "amount_lost": 200000,
            "city": "Mumbai",
            "state": "Maharashtra",
        }
    }}


class ReportUpdate(BaseModel):
    """Update report (status changes by LEO/Admin)."""
    status: Optional[str] = Field(
        None,
        pattern=r"^(submitted|under_review|investigating|resolved|dismissed)$"
    )
    severity: Optional[str] = Field(
        None,
        pattern=r"^(low|medium|high|critical)$"
    )
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = Field(None, min_length=20, max_length=5000)


class EvidenceResponse(BaseModel):
    """Evidence file metadata."""
    id: str
    file_name: str
    file_type: str
    file_size: int
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class ReportResponse(BaseModel):
    """Complete report response."""
    id: str
    user_id: str
    report_type: str
    title: str
    description: str
    status: str
    severity: str
    suspect_phone: Optional[str] = None
    suspect_name: Optional[str] = None
    suspect_account: Optional[str] = None
    amount_lost: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    ai_threat_score: Optional[float] = None
    incident_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    evidence: List[EvidenceResponse] = []

    model_config = {"from_attributes": True}


class ReportListResponse(BaseModel):
    """Paginated report list."""
    reports: List[ReportResponse]
    total: int
    page: int
    page_size: int
