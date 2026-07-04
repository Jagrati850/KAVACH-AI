"""
KAVACH AI — Threat Intelligence Model
Known threat patterns, scam indicators, and intelligence feeds.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ThreatType(str, enum.Enum):
    SCAM_PATTERN = "scam_pattern"
    PHISHING_DOMAIN = "phishing_domain"
    FRAUD_NUMBER = "fraud_number"
    COUNTERFEIT_SERIES = "counterfeit_series"
    FRAUD_RING = "fraud_ring"
    MALWARE = "malware"


class ThreatIntel(Base):
    __tablename__ = "threat_intel"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    threat_type: Mapped[ThreatType] = mapped_column(
        Enum(ThreatType), nullable=False, index=True
    )
    pattern_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    indicators: Mapped[dict] = mapped_column(JSON, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    occurrences: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<ThreatIntel {self.pattern_name} type={self.threat_type.value}>"
