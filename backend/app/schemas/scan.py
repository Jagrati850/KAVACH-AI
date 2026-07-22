"""
KAVACH AI — Scan Schemas
Request/response models for all AI scan endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Scam Text Analysis ──────────────────────────────────────
class ScamTextRequest(BaseModel):
    """Analyze text (SMS, WhatsApp, email) for scam indicators."""
    text: str = Field(..., min_length=10, max_length=10000)
    language: str = Field(default="auto", pattern=r"^(auto|en|hi)$")
    context: Optional[str] = Field(
        None,
        description="Additional context: 'sms', 'whatsapp', 'email', 'call_transcript'"
    )

    model_config = {"json_schema_extra": {
        "example": {
            "text": "This is CBI officer calling. Your Aadhaar has been linked to money laundering case. FIR #4521 registered. You must transfer ₹50,000 immediately or face arrest within 2 hours.",
            "language": "en",
            "context": "call_transcript",
        }
    }}


class ScamCallRequest(BaseModel):
    """Analyze call transcript content."""
    transcript: str = Field(..., min_length=10, max_length=10000)
    language: str = Field(default="auto", pattern=r"^(auto|en|hi)$")
    caller_phone: Optional[str] = Field(None, max_length=20)

    model_config = {"json_schema_extra": {
        "example": {
            "transcript": "Hello, I am calling from Mumbai Customs. Your parcel containing MDMA drugs has been intercepted. You are under digital custody. Connect immediately on Skype face call or you will be arrested.",
            "language": "en",
            "caller_phone": "+918765432109"
        }
    }}



# ── Currency Verification ───────────────────────────────────
class CurrencyVerifyRequest(BaseModel):
    """Request metadata for currency image verification (file uploaded separately)."""
    denomination: Optional[str] = Field(
        None,
        description="Expected denomination: 100, 200, 500, 2000",
        pattern=r"^(100|200|500|2000)?$"
    )
    notes: Optional[str] = Field(None, max_length=500)


# ── Deepfake Analysis ───────────────────────────────────────
class DeepfakeAnalyzeRequest(BaseModel):
    """Request metadata for deepfake analysis (file uploaded separately)."""
    media_type: str = Field(
        default="image",
        pattern=r"^(image|audio)$",
        description="Type of media to analyze"
    )
    context: Optional[str] = Field(None, max_length=500)


# ── Scan Response Models ────────────────────────────────────
class ScanResultResponse(BaseModel):
    """Detailed AI analysis result."""
    confidence_score: float
    verdict: str
    summary: str
    detailed_analysis: Optional[Dict[str, Any]] = None
    feature_scores: Optional[Dict[str, float]] = None
    risk_factors: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    processing_time_ms: Optional[float] = None

    model_config = {"from_attributes": True}


class ScanResponse(BaseModel):
    """Complete scan response with result."""
    id: str
    scan_type: str
    status: str
    created_at: datetime
    result: Optional[ScanResultResponse] = None

    model_config = {"from_attributes": True}


class ScamCallAudioResponse(ScanResponse):
    """Scan response for uploaded call audio, including the auto-generated transcript."""
    transcript: str
    detected_language: Optional[str] = None
    language_probability: Optional[float] = None
    audio_duration_seconds: Optional[float] = None
    case_number: Optional[str] = None


class ScanHistoryResponse(BaseModel):
    """Paginated scan history."""
    scans: List[ScanResponse]
    total: int
    page: int
    page_size: int


# ── Citizen Shield & Currency Specs Schemas ──────────────────
class CheckEntityResponse(BaseModel):
    """Result of checking a phone, email, UPI ID, bank account, or domain against blacklist."""
    query: str
    entity_type: str
    is_safe: bool
    risk_level: str
    threat_score: float
    reason: str
    matched_blacklist: bool
    blacklist_details: Optional[Dict[str, Any]] = None
    report_history_count: int
    recommendations: List[str]


class CurrencyFeatureInfo(BaseModel):
    """Details about a specific security feature of a currency note."""
    feature_name: str
    description: str
    location_on_note: str
    verification_method: str


class DenominationFeaturesResponse(BaseModel):
    """Expected security features and metadata for a specific denomination."""
    denomination: str
    dimensions: str
    primary_color: str
    obverse_features: List[CurrencyFeatureInfo]
    reverse_features: List[CurrencyFeatureInfo]

