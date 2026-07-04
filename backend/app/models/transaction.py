"""
KAVACH AI — Transaction Model
Financial transaction records for fraud pattern detection.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Float, String
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TransactionChannel(str, enum.Enum):
    UPI = "upi"
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    CARD = "card"
    WALLET = "wallet"
    CASH = "cash"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    transaction_ref: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    sender_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    sender_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    receiver_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    receiver_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    channel: Mapped[TransactionChannel] = mapped_column(
        Enum(TransactionChannel), nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Risk assessment
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    anomaly_flags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    flagged_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Location
    sender_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    receiver_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    def __repr__(self) -> str:
        return f"<Transaction {self.transaction_ref} ₹{self.amount} flagged={self.is_flagged}>"
