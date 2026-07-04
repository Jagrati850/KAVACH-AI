"""
KAVACH AI — Scan & ScanResult Models
Tracks all AI analysis scans (scam, currency, deepfake) with detailed results.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScanType(str, enum.Enum):
    SCAM_TEXT = "scam_text"
    SCAM_CALL = "scam_call"
    CURRENCY = "currency"
    DEEPFAKE_IMAGE = "deepfake_image"
    DEEPFAKE_AUDIO = "deepfake_audio"
    DOCUMENT = "document"


class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Verdict(str, enum.Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"
    FAKE = "fake"
    GENUINE = "genuine"


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    scan_type: Mapped[ScanType] = mapped_column(Enum(ScanType), nullable=False)
    # Input can be text or a file path
    input_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus), default=ScanStatus.PENDING, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ────────────────────────────────────
    user = relationship("User", back_populates="scans")
    result = relationship(
        "ScanResult", back_populates="scan", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Scan {self.id[:8]} type={self.scan_type.value} status={self.status.value}>"


class ScanResult(Base):
    __tablename__ = "scan_results"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    scan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    verdict: Mapped[Verdict] = mapped_column(Enum(Verdict), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    # Detailed JSON analysis from AI engine
    detailed_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    feature_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    risk_factors: Mapped[list | None] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[list | None] = mapped_column(JSON, nullable=True)
    processing_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ────────────────────────────────────
    scan = relationship("Scan", back_populates="result")

    def __repr__(self) -> str:
        return f"<ScanResult scan={self.scan_id[:8]} verdict={self.verdict.value} conf={self.confidence_score:.2f}>"
