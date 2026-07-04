"""
KAVACH AI — Case Schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CaseCreate(BaseModel):
    """Create a case from a report."""
    report_id: str
    priority: str = Field(
        default="medium",
        pattern=r"^(low|medium|high|critical)$"
    )
    title: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    assigned_to: Optional[str] = None


class CaseUpdate(BaseModel):
    """Update case details."""
    status: Optional[str] = Field(
        None,
        pattern=r"^(open|assigned|investigating|evidence_collected|resolved|closed)$"
    )
    priority: Optional[str] = Field(
        None,
        pattern=r"^(low|medium|high|critical)$"
    )
    assigned_to: Optional[str] = None
    description: Optional[str] = Field(None, max_length=5000)
    resolution_notes: Optional[str] = Field(None, max_length=5000)


class CaseNoteCreate(BaseModel):
    """Add a note to a case."""
    content: str = Field(..., min_length=5, max_length=5000)
    note_type: str = Field(
        default="general",
        pattern=r"^(general|evidence|interview|update|closing)$"
    )


class CaseNoteResponse(BaseModel):
    """Case note response."""
    id: str
    case_id: str
    author_id: str
    content: str
    note_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CaseResponse(BaseModel):
    """Complete case response."""
    id: str
    case_number: str
    report_id: str
    assigned_to: Optional[str] = None
    status: str
    priority: str
    title: str
    description: Optional[str] = None
    resolution_notes: Optional[str] = None
    opened_at: datetime
    closed_at: Optional[datetime] = None
    updated_at: datetime
    notes: List[CaseNoteResponse] = []

    model_config = {"from_attributes": True}


class CaseListResponse(BaseModel):
    """Paginated case list."""
    cases: List[CaseResponse]
    total: int
    page: int
    page_size: int
