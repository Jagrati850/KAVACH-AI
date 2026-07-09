"""
KAVACH AI — Reports API
CRUD endpoints for fraud/scam reports.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser, require_roles
from app.models.report import Report, ReportStatus, ReportType, Severity
from app.models.user import UserRole
from app.schemas.report import (
    ReportCreate,
    ReportListResponse,
    ReportResponse,
    ReportUpdate,
)
from app.ai.orchestrator import AIOrchestrator

router = APIRouter()
orchestrator = AIOrchestrator()


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: ReportCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Submit a new fraud/scam report."""
    report = Report(
        user_id=current_user.id,
        report_type=ReportType(payload.report_type),
        title=payload.title,
        description=payload.description,
        suspect_phone=payload.suspect_phone,
        suspect_name=payload.suspect_name,
        suspect_account=payload.suspect_account,
        amount_lost=payload.amount_lost,
        latitude=payload.latitude,
        longitude=payload.longitude,
        city=payload.city,
        state=payload.state,
        incident_date=payload.incident_date,
        severity=Severity.MEDIUM,
        status=ReportStatus.SUBMITTED,
    )

    # Auto-analyze the report description for threat scoring
    try:
        analysis = await orchestrator.analyze_scam_text(
            text=payload.description,
            language="auto",
            context="report",
        )
        report.ai_analysis = analysis.get("detailed_analysis")
        report.ai_threat_score = analysis.get("confidence_score", 0.0)

        # Auto-set severity based on AI score
        score = report.ai_threat_score
        if score >= 0.8:
            report.severity = Severity.CRITICAL
        elif score >= 0.6:
            report.severity = Severity.HIGH
        elif score >= 0.4:
            report.severity = Severity.MEDIUM
        else:
            report.severity = Severity.LOW
    except Exception:
        # AI failure shouldn't block report submission
        pass

    db.add(report)
    await db.flush()

    report_dict = {
        "id": report.id,
        "user_id": report.user_id,
        "report_type": report.report_type.value if hasattr(report.report_type, "value") else str(report.report_type),
        "title": report.title,
        "description": report.description,
        "status": report.status.value if hasattr(report.status, "value") else str(report.status),
        "severity": report.severity.value if hasattr(report.severity, "value") else str(report.severity),
        "suspect_phone": report.suspect_phone,
        "suspect_name": report.suspect_name,
        "suspect_account": report.suspect_account,
        "amount_lost": report.amount_lost,
        "latitude": report.latitude,
        "longitude": report.longitude,
        "city": report.city,
        "state": report.state,
        "ai_analysis": report.ai_analysis,
        "ai_threat_score": report.ai_threat_score,
        "incident_date": report.incident_date,
        "created_at": report.created_at,
        "updated_at": report.updated_at,
        "evidence": []
    }
    res_data = ReportResponse.model_validate(report_dict)

    # Automatically notify client of new report filing via generic Notification Service
    try:
        from app.services.sms import get_notification_service
        notif_service = get_notification_service()
        recipient_phone = current_user.phone or "+919876543210"
        await notif_service.send_custom_alert(
            phone=recipient_phone,
            message=f"KAVACH ALERT: scam report successfully submitted. Case ID: {report.id}. Severity tier: {report.severity.value.upper()}."
        )
    except Exception:
        pass

    return res_data


@router.get("/", response_model=ReportListResponse)
async def list_reports(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    report_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    List reports.
    - Citizens see only their own reports.
    - LEO/Admin see all reports.
    """
    user_role = UserRole(current_user.role) if isinstance(current_user.role, str) else current_user.role

    query = select(Report)
    count_query = select(func.count()).select_from(Report)

    # Role-based filtering
    if user_role == UserRole.CITIZEN:
        query = query.where(Report.user_id == current_user.id)
        count_query = count_query.where(Report.user_id == current_user.id)

    # Optional filters
    if report_type:
        query = query.where(Report.report_type == ReportType(report_type))
        count_query = count_query.where(Report.report_type == ReportType(report_type))
    if status_filter:
        query = query.where(Report.status == ReportStatus(status_filter))
        count_query = count_query.where(Report.status == ReportStatus(status_filter))
    if severity:
        query = query.where(Report.severity == Severity(severity))
        count_query = count_query.where(Report.severity == Severity(severity))

    query = query.order_by(Report.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    reports = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return ReportListResponse(
        reports=[ReportResponse.model_validate(r) for r in reports],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get report details by ID."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    user_role = UserRole(current_user.role) if isinstance(current_user.role, str) else current_user.role
    if user_role == UserRole.CITIZEN and report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return ReportResponse.model_validate(report)


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: str,
    payload: ReportUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update a report. LEO/Admin can change status and severity."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    user_role = UserRole(current_user.role) if isinstance(current_user.role, str) else current_user.role

    # Citizens can only update their own pending reports
    if user_role == UserRole.CITIZEN:
        if report.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        if report.status != ReportStatus.SUBMITTED:
            raise HTTPException(status_code=400, detail="Can only edit submitted reports")
        # Citizens can only update title/description
        if payload.title:
            report.title = payload.title
        if payload.description:
            report.description = payload.description
    else:
        # LEO/Admin can update everything
        if payload.status:
            report.status = ReportStatus(payload.status)
        if payload.severity:
            report.severity = Severity(payload.severity)
        if payload.title:
            report.title = payload.title
        if payload.description:
            report.description = payload.description

    await db.flush()

    # Map any existing evidence safe from lazy queries
    evidence_list = []
    try:
        for ev in (report.evidence or []):
            evidence_list.append({
                "id": ev.id,
                "file_name": ev.file_name,
                "file_type": ev.file_type,
                "file_size": ev.file_size,
                "uploaded_at": ev.uploaded_at
            })
    except Exception:
        pass

    report_dict = {
        "id": report.id,
        "user_id": report.user_id,
        "report_type": report.report_type.value if hasattr(report.report_type, "value") else str(report.report_type),
        "title": report.title,
        "description": report.description,
        "status": report.status.value if hasattr(report.status, "value") else str(report.status),
        "severity": report.severity.value if hasattr(report.severity, "value") else str(report.severity),
        "suspect_phone": report.suspect_phone,
        "suspect_name": report.suspect_name,
        "suspect_account": report.suspect_account,
        "amount_lost": report.amount_lost,
        "latitude": report.latitude,
        "longitude": report.longitude,
        "city": report.city,
        "state": report.state,
        "ai_analysis": report.ai_analysis,
        "ai_threat_score": report.ai_threat_score,
        "incident_date": report.incident_date,
        "created_at": report.created_at,
        "updated_at": report.updated_at,
        "evidence": evidence_list
    }
    res_data = ReportResponse.model_validate(report_dict)

    # Automatically notify client of investigation status update via generic Notification Service
    try:
        from app.services.sms import get_notification_service
        from app.models.user import User
        
        recipient_phone = current_user.phone or "+919876543210"
        if report.user_id != current_user.id:
            res_user = await db.execute(select(User).where(User.id == report.user_id))
            owner_user = res_user.scalar_one_or_none()
            if owner_user and owner_user.phone:
                recipient_phone = owner_user.phone
                
        notif_service = get_notification_service()
        await notif_service.notify_report_update(
            phone=recipient_phone,
            case_id=report.id,
            status=report.status.value.upper()
        )
    except Exception:
        pass

    return res_data
