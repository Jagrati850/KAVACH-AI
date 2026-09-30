"""
KAVACH AI — Report Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    """Create a new citizen development request or report."""
    report_type: str = Field(
        ...,
        pattern=r"^(clean_air|water_sanitation|roads_transport|healthcare|education|digital_infra|electricity_energy|scam_call|phishing|counterfeit_currency|upi_fraud|digital_arrest|deepfake|identity_theft|other)$"
    )
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10, max_length=5000)
    infra_category: Optional[str] = Field(None, max_length=100)
    channel: Optional[str] = Field("web", max_length=50)
    language: Optional[str] = Field("en", max_length=20)
    affected_population: Optional[int] = Field(None, ge=0)
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
            "report_type": "clean_air",
            "title": "Severe Air Pollution & Dust Hazard in Industrial Corridor",
            "description": "High PM2.5 levels near Anand Vihar terminal due to unpaved roads and construction dust. Need immediate green barrier installation and continuous smog tower operation.",
            "infra_category": "Clean Air & Climate",
            "channel": "whatsapp",
            "language": "hi",
            "city": "Delhi",
            "state": "Delhi",
            "affected_population": 450000
        }
    }}


class ReportUpdate(BaseModel):
    """Update report (status changes by Policymaker/Admin)."""
    status: Optional[str] = Field(
        None,
        pattern=r"^(submitted|under_review|investigating|resolved|dismissed)$"
    )
    severity: Optional[str] = Field(
        None,
        pattern=r"^(low|medium|high|critical)$"
    )
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    priority_score: Optional[float] = Field(None, ge=0, le=100)


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
    infra_category: Optional[str] = None
    channel: Optional[str] = "web"
    language: Optional[str] = "en"
    priority_score: Optional[float] = 50.0
    affected_population: Optional[int] = None
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
