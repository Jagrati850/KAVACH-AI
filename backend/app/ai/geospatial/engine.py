"""
KAVACH AI — Geospatial Crime Intelligence Engine
Geographic analysis for crime hotspot detection and prediction.

Techniques:
1. Kernel Density Estimation (KDE) for hotspot detection
2. DBSCAN clustering for geographic grouping
3. Temporal pattern analysis
4. State/district-level aggregation
"""

from typing import Any, Dict, List

import numpy as np
from scipy.stats import gaussian_kde
from sklearn.cluster import DBSCAN


class GeospatialEngine:
    """
    Geospatial crime intelligence engine.
    Detects crime hotspots and geographic patterns.
    """

    def __init__(self):
        # India bounding box (approximate)
        self.india_bounds = {
            "lat_min": 6.0, "lat_max": 37.0,
            "lon_min": 68.0, "lon_max": 97.0,
        }

    def analyze_hotspots(self, points: list) -> Dict[str, Any]:
        """
        Analyze geographic data points for crime hotspots.

        Args:
            points: List of GeospatialPoint objects with lat/lon.

        Returns:
            Hotspot analysis with clusters and density information.
        """
        if len(points) < 3:
            return {"hotspots": [], "clusters": [], "density_map": []}

        # Extract coordinates
        coords = np.array([
            [p.latitude if hasattr(p, 'latitude') else p['latitude'],
             p.longitude if hasattr(p, 'longitude') else p['longitude']]
            for p in points
            if (hasattr(p, 'latitude') and p.latitude) or
               (isinstance(p, dict) and p.get('latitude'))
        ])

        if len(coords) < 3:
            return {"hotspots": [], "clusters": [], "density_map": []}

        # ── DBSCAN Clustering ────────────────────────────
        # eps in degrees, roughly 50km at Indian latitudes
        clustering = DBSCAN(eps=0.5, min_samples=2).fit(coords)
        labels = clustering.labels_

        clusters = []
        unique_labels = set(labels) - {-1}  # Exclude noise

        for label in unique_labels:
            mask = labels == label
            cluster_coords = coords[mask]
            center_lat = np.mean(cluster_coords[:, 0])
            center_lon = np.mean(cluster_coords[:, 1])

            # Get severity of points in this cluster
            cluster_points = [p for i, p in enumerate(points) if mask[i] if i < len(mask)]

            clusters.append({
                "cluster_id": int(label),
                "center_latitude": round(float(center_lat), 4),
                "center_longitude": round(float(center_lon), 4),
                "point_count": int(np.sum(mask)),
                "radius_km": round(float(self._haversine_max_distance(cluster_coords)), 2),
            })

        # ── Kernel Density Estimation ────────────────────
        hotspots = []
        try:
            kde = gaussian_kde(coords.T, bw_method=0.3)

            # Create grid for density estimation
            lat_grid = np.linspace(coords[:, 0].min() - 0.5, coords[:, 0].max() + 0.5, 30)
            lon_grid = np.linspace(coords[:, 1].min() - 0.5, coords[:, 1].max() + 0.5, 30)
            lat_mesh, lon_mesh = np.meshgrid(lat_grid, lon_grid)
            positions = np.vstack([lat_mesh.ravel(), lon_mesh.ravel()])

            density = kde(positions).reshape(lat_mesh.shape)

            # Find peak density locations (hotspots)
            threshold = np.percentile(density, 90)

            for i in range(density.shape[0]):
                for j in range(density.shape[1]):
                    if density[i, j] >= threshold:
                        hotspots.append({
                            "latitude": round(float(lat_grid[j]), 4),
                            "longitude": round(float(lon_grid[i]), 4),
                            "intensity": round(float(density[i, j]), 6),
                            "risk_level": "high" if density[i, j] > np.percentile(density, 95) else "medium",
                        })

            # Limit hotspots to top 20
            hotspots = sorted(hotspots, key=lambda h: h['intensity'], reverse=True)[:20]

        except Exception:
            # KDE can fail with too few or collinear points
            pass

        return {
            "hotspots": hotspots,
            "clusters": sorted(clusters, key=lambda c: c['point_count'], reverse=True),
        }

    def _haversine_max_distance(self, coords: np.ndarray) -> float:
        """Calculate maximum pairwise distance in kilometers."""
        if len(coords) < 2:
            return 0.0

        center = coords.mean(axis=0)
        max_dist = 0.0

        for coord in coords:
            dist = self._haversine(center[0], center[1], coord[0], coord[1])
            max_dist = max(max_dist, dist)

        return max_dist

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great-circle distance between two points (km)."""
        R = 6371  # Earth's radius in km

        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))

        return R * c
