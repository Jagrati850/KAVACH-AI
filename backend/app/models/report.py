"""
KAVACH AI — Report & Evidence Models
Citizens submit fraud/scam reports with optional evidence attachments.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReportType(str, enum.Enum):
    SCAM_CALL = "scam_call"
    PHISHING = "phishing"
    COUNTERFEIT_CURRENCY = "counterfeit_currency"
    UPI_FRAUD = "upi_fraud"
    DIGITAL_ARREST = "digital_arrest"
    DEEPFAKE = "deepfake"
    IDENTITY_THEFT = "identity_theft"
    OTHER = "other"


class ReportStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Severity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus), default=ReportStatus.SUBMITTED, nullable=False
    )
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity), default=Severity.MEDIUM, nullable=False
    )
    # Suspect / perpetrator info
    suspect_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    suspect_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suspect_account: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount_lost: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Geolocation
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # AI analysis result
    ai_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ai_threat_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Timestamps
    incident_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ────────────────────────────────────
    user = relationship("User", back_populates="reports")
    evidence = relationship(
        "ReportEvidence", back_populates="report", cascade="all, delete-orphan", lazy="selectin"
    )
    case = relationship("Case", back_populates="report", uselist=False, lazy="selectin")

    def __repr__(self) -> str:
        return f"<Report {self.id[:8]} type={self.report_type.value} status={self.status.value}>"


class ReportEvidence(Base):
    __tablename__ = "report_evidence"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    report_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ────────────────────────────────────
    report = relationship("Report", back_populates="evidence")

    def __repr__(self) -> str:
        return f"<Evidence {self.file_name} for report={self.report_id[:8]}>"
