"""
KAVACH AI — Analytics Schemas
Dashboard and analytics response models.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class OverviewStats(BaseModel):
    """Platform-wide overview statistics."""
    total_users: int
    total_reports: int
    total_scans: int
    total_cases: int
    active_alerts: int
    threats_blocked: int
    total_amount_saved: float
    scams_detected_today: int
    # Distribution breakdowns
    reports_by_type: Dict[str, int]
    reports_by_status: Dict[str, int]
    reports_by_severity: Dict[str, int]
    scans_by_type: Dict[str, int]


class ThreatDistribution(BaseModel):
    """Threat type distribution for charts."""
    labels: List[str]
    values: List[int]
    percentages: List[float]


class TimelineDataPoint(BaseModel):
    """Single data point in a timeline."""
    date: str
    count: int
    category: Optional[str] = None


class TimelineData(BaseModel):
    """Temporal trend data."""
    period: str  # 'daily', 'weekly', 'monthly'
    data_points: List[TimelineDataPoint]
    total: int


class GeospatialPoint(BaseModel):
    """Single geographic data point."""
    latitude: float
    longitude: float
    city: Optional[str] = None
    state: Optional[str] = None
    count: int
    severity: str
    threat_type: Optional[str] = None


class GeospatialData(BaseModel):
    """Geographic crime intelligence data."""
    points: List[GeospatialPoint]
    hotspots: List[Dict[str, Any]]
    state_summary: Dict[str, int]
    total_incidents: int


class FraudNode(BaseModel):
    """Node in the fraud network graph."""
    id: str
    label: str
    node_type: str  # 'account', 'phone', 'person'
    risk_score: float
    is_flagged: bool
    metadata: Optional[Dict[str, Any]] = None


class FraudEdge(BaseModel):
    """Edge in the fraud network graph."""
    source: str
    target: str
    weight: float
    transaction_count: int
    total_amount: float
    edge_type: str  # 'transaction', 'communication', 'association'


class FraudNetworkData(BaseModel):
    """Fraud network graph data for visualization."""
    nodes: List[FraudNode]
    edges: List[FraudEdge]
    communities: List[Dict[str, Any]]
    central_nodes: List[str]
    risk_summary: Dict[str, Any]
