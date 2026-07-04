"""
KAVACH AI — Cases API
Law enforcement case management.
"""

import random
import string
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser, RequireLEO
from app.models.case import Case, CaseNote, CasePriority, CaseStatus
from app.models.user import UserRole
from app.schemas.case import (
    CaseCreate,
    CaseListResponse,
    CaseNoteCreate,
    CaseNoteResponse,
    CaseResponse,
    CaseUpdate,
)

router = APIRouter()


def generate_case_number() -> str:
    """Generate a unique case number like KAV-2026-A3X9."""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"KAV-2026-{suffix}"


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED, dependencies=[RequireLEO])
async def create_case(
    payload: CaseCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a new case from a report (LEO/Admin only)."""
    case = Case(
        case_number=generate_case_number(),
        report_id=payload.report_id,
        assigned_to=payload.assigned_to or current_user.id,
        status=CaseStatus.OPEN if not payload.assigned_to else CaseStatus.ASSIGNED,
        priority=CasePriority(payload.priority),
        title=payload.title,
        description=payload.description,
    )
    db.add(case)
    await db.flush()

    return CaseResponse.model_validate(case)


@router.get("/", response_model=CaseListResponse, dependencies=[RequireLEO])
async def list_cases(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    case_status: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
    assigned_to_me: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List cases with filtering (LEO/Admin only)."""
    query = select(Case)
    count_query = select(func.count()).select_from(Case)

    if case_status:
        query = query.where(Case.status == CaseStatus(case_status))
        count_query = count_query.where(Case.status == CaseStatus(case_status))
    if priority:
        query = query.where(Case.priority == CasePriority(priority))
        count_query = count_query.where(Case.priority == CasePriority(priority))
    if assigned_to_me:
        query = query.where(Case.assigned_to == current_user.id)
        count_query = count_query.where(Case.assigned_to == current_user.id)

    query = query.order_by(Case.opened_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    cases = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return CaseListResponse(
        cases=[CaseResponse.model_validate(c) for c in cases],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{case_id}", response_model=CaseResponse, dependencies=[RequireLEO])
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get case details."""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return CaseResponse.model_validate(case)


@router.put("/{case_id}", response_model=CaseResponse, dependencies=[RequireLEO])
async def update_case(
    case_id: str,
    payload: CaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update case status, priority, assignment, or resolution."""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if payload.status:
        case.status = CaseStatus(payload.status)
        if payload.status in ("resolved", "closed"):
            case.closed_at = datetime.now(timezone.utc)
    if payload.priority:
        case.priority = CasePriority(payload.priority)
    if payload.assigned_to:
        case.assigned_to = payload.assigned_to
        if case.status == CaseStatus.OPEN:
            case.status = CaseStatus.ASSIGNED
    if payload.description:
        case.description = payload.description
    if payload.resolution_notes:
        case.resolution_notes = payload.resolution_notes

    await db.flush()
    return CaseResponse.model_validate(case)


@router.post("/{case_id}/notes", response_model=CaseNoteResponse, status_code=status.HTTP_201_CREATED, dependencies=[RequireLEO])
async def add_case_note(
    case_id: str,
    payload: CaseNoteCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Add a note to a case."""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    note = CaseNote(
        case_id=case_id,
        author_id=current_user.id,
        content=payload.content,
        note_type=payload.note_type,
    )
    db.add(note)
    await db.flush()

    return CaseNoteResponse.model_validate(note)
