"""
KAVACH AI — Analytics API
Dashboard statistics, threat distribution, timeline, geospatial, and fraud network data.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, case as sql_case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser, RequireAnalytics
from app.models.alert import Alert
from app.models.case import Case
from app.models.report import Report, ReportStatus, ReportType, Severity
from app.models.scan import Scan, ScanType
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.analytics import (
    FraudNetworkData,
    GeospatialData,
    OverviewStats,
    ThreatDistribution,
    TimelineData,
    TimelineDataPoint,
    GeospatialPoint,
)
from app.ai.fraud_graph.engine import FraudGraphEngine
from app.ai.geospatial.engine import GeospatialEngine

router = APIRouter()
fraud_graph_engine = FraudGraphEngine()
geospatial_engine = GeospatialEngine()


@router.get("/overview", response_model=OverviewStats, dependencies=[RequireAnalytics])
async def get_overview(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get platform-wide overview statistics for the dashboard."""
    # Total counts
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    total_reports = (await db.execute(select(func.count()).select_from(Report))).scalar() or 0
    total_scans = (await db.execute(select(func.count()).select_from(Scan))).scalar() or 0
    total_cases = (await db.execute(select(func.count()).select_from(Case))).scalar() or 0
    active_alerts = (await db.execute(
        select(func.count()).select_from(Alert).where(Alert.is_resolved == False)
    )).scalar() or 0

    # Reports by type
    rbt_result = await db.execute(
        select(Report.report_type, func.count()).group_by(Report.report_type)
    )
    reports_by_type = {row[0].value if hasattr(row[0], 'value') else str(row[0]): row[1] for row in rbt_result.all()}

    # Reports by status
    rbs_result = await db.execute(
        select(Report.status, func.count()).group_by(Report.status)
    )
    reports_by_status = {row[0].value if hasattr(row[0], 'value') else str(row[0]): row[1] for row in rbs_result.all()}

    # Reports by severity
    rbsev_result = await db.execute(
        select(Report.severity, func.count()).group_by(Report.severity)
    )
    reports_by_severity = {row[0].value if hasattr(row[0], 'value') else str(row[0]): row[1] for row in rbsev_result.all()}

    # Scans by type
    sbt_result = await db.execute(
        select(Scan.scan_type, func.count()).group_by(Scan.scan_type)
    )
    scans_by_type = {row[0].value if hasattr(row[0], 'value') else str(row[0]): row[1] for row in sbt_result.all()}

    # Amount saved (from resolved high-severity reports)
    amount_result = await db.execute(
        select(func.coalesce(func.sum(Report.amount_lost), 0.0))
        .where(Report.status == ReportStatus.RESOLVED)
    )
    total_amount_saved = amount_result.scalar() or 0.0

    # Threats blocked = resolved + dismissed reports
    threats_blocked = (await db.execute(
        select(func.count()).select_from(Report).where(
            Report.status.in_([ReportStatus.RESOLVED, ReportStatus.DISMISSED])
        )
    )).scalar() or 0

    return OverviewStats(
        total_users=total_users,
        total_reports=total_reports,
        total_scans=total_scans,
        total_cases=total_cases,
        active_alerts=active_alerts,
        threats_blocked=threats_blocked,
        total_amount_saved=total_amount_saved,
        scams_detected_today=total_scans,  # Simplified for hackathon
        reports_by_type=reports_by_type,
        reports_by_status=reports_by_status,
        reports_by_severity=reports_by_severity,
        scans_by_type=scans_by_type,
    )


@router.get("/threats", response_model=ThreatDistribution, dependencies=[RequireAnalytics])
async def get_threat_distribution(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get the distribution of threat types for charts."""
    result = await db.execute(
        select(Report.report_type, func.count())
        .group_by(Report.report_type)
        .order_by(func.count().desc())
    )
    rows = result.all()

    labels = [row[0].value if hasattr(row[0], 'value') else str(row[0]) for row in rows]
    values = [row[1] for row in rows]
    total = sum(values) or 1
    percentages = [round(v / total * 100, 1) for v in values]

    return ThreatDistribution(labels=labels, values=values, percentages=percentages)


@router.get("/timeline", response_model=TimelineData, dependencies=[RequireAnalytics])
async def get_timeline(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    period: str = "daily",
):
    """Get temporal trend data for reports."""
    # Get all reports ordered by date
    result = await db.execute(
        select(Report).order_by(Report.created_at.asc())
    )
    reports = result.scalars().all()

    # Group by date
    from collections import Counter
    date_counts = Counter()
    for r in reports:
        date_key = r.created_at.strftime("%Y-%m-%d")
        date_counts[date_key] += 1

    data_points = [
        TimelineDataPoint(date=date, count=count)
        for date, count in sorted(date_counts.items())
    ]

    return TimelineData(
        period=period,
        data_points=data_points,
        total=sum(date_counts.values()),
    )


@router.get("/geospatial", response_model=GeospatialData, dependencies=[RequireAnalytics])
async def get_geospatial_data(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get geographic crime intelligence data for maps."""
    result = await db.execute(select(Report).where(Report.latitude.is_not(None)))
    reports = result.scalars().all()

    points = [
        GeospatialPoint(
            latitude=r.latitude,
            longitude=r.longitude,
            city=r.city,
            state=r.state,
            count=1,
            severity=r.severity.value if hasattr(r.severity, 'value') else str(r.severity),
            threat_type=r.report_type.value if hasattr(r.report_type, 'value') else str(r.report_type),
        )
        for r in reports
        if r.latitude and r.longitude
    ]

    # Run hotspot analysis
    analysis = geospatial_engine.analyze_hotspots(points)

    # State summary
    from collections import Counter
    state_summary = Counter(r.state for r in reports if r.state)

    return GeospatialData(
        points=points,
        hotspots=analysis.get("hotspots", []),
        state_summary=dict(state_summary),
        total_incidents=len(points),
    )


@router.get("/fraud-network", response_model=FraudNetworkData, dependencies=[RequireAnalytics])
async def get_fraud_network(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get fraud network graph data for visualization."""
    result = await db.execute(select(Transaction))
    transactions = result.scalars().all()

    network_data = fraud_graph_engine.build_network(transactions)

    return FraudNetworkData(**network_data)
