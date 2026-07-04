"""
KAVACH AI — API v1 Router
Aggregates all v1 sub-routers into a single router.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.scans import router as scans_router
from app.api.v1.reports import router as reports_router
from app.api.v1.cases import router as cases_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.admin import router as admin_router
from app.api.v1.rag import router as rag_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(scans_router, prefix="/scans", tags=["AI Scans"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(cases_router, prefix="/cases", tags=["Cases"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["Alerts & Notifications"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_router.include_router(rag_router, prefix="/rag", tags=["RAG Advisories"])
