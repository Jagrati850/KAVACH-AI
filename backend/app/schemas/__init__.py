"""KAVACH AI — Pydantic Schemas Package"""

from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    PasswordChangeRequest,
)
from app.schemas.user import UserResponse, UserUpdate, UserListResponse
from app.schemas.scan import (
    ScamTextRequest,
    CurrencyVerifyRequest,
    DeepfakeAnalyzeRequest,
    ScanResponse,
    ScanResultResponse,
    ScanHistoryResponse,
)
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportListResponse,
)
from app.schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseNoteCreate,
    CaseNoteResponse,
)
from app.schemas.alert import (
    AlertResponse,
    NotificationResponse,
)
from app.schemas.analytics import (
    OverviewStats,
    ThreatDistribution,
    TimelineData,
    GeospatialData,
    FraudNetworkData,
)
