"""
KAVACH AI — Case & CaseNote Models
Law enforcement case management with lifecycle tracking.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CaseStatus(str, enum.Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    INVESTIGATING = "investigating"
    EVIDENCE_COLLECTED = "evidence_collected"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CasePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    report_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("reports.id"), nullable=False, index=True
    )
    assigned_to: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus), default=CaseStatus.OPEN, nullable=False
    )
    priority: Mapped[CasePriority] = mapped_column(
        Enum(CasePriority), default=CasePriority.MEDIUM, nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ────────────────────────────────────
    report = relationship("Report", back_populates="case")
    assigned_officer = relationship(
        "User", back_populates="assigned_cases", foreign_keys=[assigned_to]
    )
    notes = relationship(
        "CaseNote", back_populates="case", cascade="all, delete-orphan", lazy="selectin",
        order_by="CaseNote.created_at.desc()"
    )

    def __repr__(self) -> str:
        return f"<Case {self.case_number} status={self.status.value}>"


class CaseNote(Base):
    __tablename__ = "case_notes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    note_type: Mapped[str] = mapped_column(
        String(50), default="general", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ────────────────────────────────────
    case = relationship("Case", back_populates="notes")
    author = relationship("User", lazy="selectin")

    def __repr__(self) -> str:
        return f"<CaseNote case={self.case_id[:8]} by={self.author_id[:8]}>"
