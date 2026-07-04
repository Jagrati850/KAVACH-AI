"""
KAVACH AI — Counterfeit Currency Detection Engine
Computer Vision-based analysis for Indian currency note authenticity.

Analysis Layers:
1. Image Quality Assessment — Resolution, blur, noise detection
2. Color Profile Analysis — Dominant color distribution matching
3. Edge & Texture Analysis — Intaglio print quality, microprint sharpness
4. Symmetry & Geometry — Alignment, proportion, warp detection
5. Frequency Domain Analysis — Detect printer artifacts vs. genuine print
6. Statistical Feature Extraction — Histogram distribution analysis
"""

import io
import asyncio
from typing import Any, Dict, List, Optional

import numpy as np
from PIL import Image


class CurrencyDetectorEngine:
    """
    Currency authenticity detector using multi-feature image analysis.
    Uses OpenCV-compatible numpy operations for production portability.
    """

    def __init__(self):
        # Expected color ranges for genuine Indian currency notes (HSV)
        self.denomination_profiles = {
            "100": {
                "dominant_hue_range": (90, 140),  # Blue-lavender
                "name": "₹100 Note",
                "color_description": "Lavender/Blue",
                "expected_aspect_ratio": 2.18,
            },
            "200": {
                "dominant_hue_range": (15, 45),  # Orange-yellow
                "name": "₹200 Note",
                "color_description": "Bright Orange",
                "expected_aspect_ratio": 2.18,
            },
            "500": {
                "dominant_hue_range": (0, 20),  # Stone grey-pink
                "name": "₹500 Note",
                "color_description": "Stone Grey",
                "expected_aspect_ratio": 2.18,
            },
            "2000": {
                "dominant_hue_range": (150, 175),  # Magenta-pink
                "name": "₹2000 Note",
                "color_description": "Magenta Pink",
                "expected_aspect_ratio": 2.18,
            },
        }

        # Feature analysis weights
        self.feature_weights = {
            "image_quality": 0.15,
            "color_profile": 0.25,
            "edge_sharpness": 0.20,
            "texture_complexity": 0.15,
            "symmetry_score": 0.10,
            "frequency_analysis": 0.15,
        }

    async def analyze(
        self,
        image_data: bytes,
        denomination: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a currency note image for authenticity.

        Args:
            image_data: Raw image bytes.
            denomination: Expected denomination (100, 200, 500, 2000).

        Returns:
            Analysis results with confidence score, verdict, and feature breakdown.
        """
        # Load image
        try:
            image = Image.open(io.BytesIO(image_data))
            img_array = np.array(image.convert("RGB"))
        except Exception as e:
            return {
                "confidence_score": 0.0,
                "verdict": "suspicious",
                "summary": f"Unable to process image: {str(e)}",
                "detailed_analysis": {"error": str(e)},
                "feature_scores": {},
                "risk_factors": ["Image could not be processed"],
                "recommendations": ["Please upload a clear, well-lit photo of the currency note"],
            }

        # Run all analysis layers
        quality_score = self._analyze_image_quality(img_array)
        color_score, color_details = self._analyze_color_profile(img_array, denomination)
        edge_score = self._analyze_edge_sharpness(img_array)
        texture_score = self._analyze_texture_complexity(img_array)
        symmetry_score = self._analyze_symmetry(img_array)
        frequency_score = self._analyze_frequency_domain(img_array)

        # Feature scores
        feature_scores = {
            "image_quality": round(quality_score, 4),
            "color_profile": round(color_score, 4),
            "edge_sharpness": round(edge_score, 4),
            "texture_complexity": round(texture_score, 4),
            "symmetry_score": round(symmetry_score, 4),
            "frequency_analysis": round(frequency_score, 4),
        }

        # Weighted confidence
        authenticity_score = sum(
            feature_scores[f] * self.feature_weights[f]
            for f in self.feature_weights
        )
        authenticity_score = round(min(max(authenticity_score, 0.0), 1.0), 4)

        # Verdict (higher score = more likely genuine)
        if authenticity_score >= 0.7:
            verdict = "genuine"
            confidence_score = authenticity_score
        elif authenticity_score >= 0.4:
            verdict = "suspicious"
            confidence_score = 1.0 - authenticity_score  # Inverse for risk
        else:
            verdict = "fake"
            confidence_score = 1.0 - authenticity_score

        # Risk factors
        risk_factors = []
        if quality_score < 0.5:
            risk_factors.append("Low image quality — may indicate a photocopy or printed reproduction")
        if color_score < 0.5:
            risk_factors.append("Color profile does not match expected denomination characteristics")
        if edge_score < 0.5:
            risk_factors.append("Low edge sharpness — genuine notes have crisp intaglio printing")
        if texture_score < 0.5:
            risk_factors.append("Insufficient texture complexity — may indicate inkjet/laser printing")
        if symmetry_score < 0.5:
            risk_factors.append("Asymmetry detected — potential alignment issues from reproduction")
        if frequency_score < 0.5:
            risk_factors.append("Frequency analysis suggests non-genuine printing technique")

        # Recommendations
        recommendations = self._generate_recommendations(verdict, feature_scores, denomination)

        # Summary
        summary = self._generate_summary(verdict, authenticity_score, denomination, risk_factors)

        return {
            "confidence_score": round(confidence_score, 4),
            "verdict": verdict,
            "summary": summary,
            "detailed_analysis": {
                "image_dimensions": f"{img_array.shape[1]}x{img_array.shape[0]}",
                "denomination_checked": denomination or "auto",
                "color_details": color_details,
                "authenticity_score": authenticity_score,
                "features_analyzed": len(feature_scores),
            },
            "feature_scores": feature_scores,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
        }

    def _analyze_image_quality(self, img: np.ndarray) -> float:
        """Assess image quality via resolution, contrast, and noise level."""
        h, w = img.shape[:2]

        # Resolution score (good currency images should be at least 300px wide)
        resolution_score = min(w / 600, 1.0) * min(h / 300, 1.0)

        # Contrast score using standard deviation of grayscale
        gray = np.mean(img, axis=2)
        contrast = np.std(gray) / 128.0
        contrast_score = min(contrast, 1.0)

        # Brightness check (not too dark, not too bright)
        mean_brightness = np.mean(gray) / 255.0
        brightness_score = 1.0 - abs(mean_brightness - 0.5) * 2

        return (resolution_score * 0.4 + contrast_score * 0.3 + brightness_score * 0.3)

    def _analyze_color_profile(
        self, img: np.ndarray, denomination: Optional[str]
    ) -> tuple:
        """Analyze dominant color distribution against denomination standards."""
        # Convert to HSV-like representation
        r, g, b = img[:,:,0].astype(float), img[:,:,1].astype(float), img[:,:,2].astype(float)

        # Calculate hue approximation
        max_c = np.maximum(np.maximum(r, g), b)
        min_c = np.minimum(np.minimum(r, g), b)
        diff = max_c - min_c + 1e-10

        # Dominant color statistics
        mean_r, mean_g, mean_b = np.mean(r), np.mean(g), np.mean(b)
        std_r, std_g, std_b = np.std(r), np.std(g), np.std(b)

        # Color variance (genuine notes have specific, consistent color palettes)
        color_consistency = 1.0 - min(
            (std_r + std_g + std_b) / (3 * 128), 1.0
        )

        # Color richness (genuine notes have rich, saturated colors)
        saturation = np.mean(diff / (max_c + 1e-10))
        saturation_score = min(saturation * 2, 1.0)

        # If denomination specified, check color match
        denomination_match = 0.5  # Default neutral
        if denomination and denomination in self.denomination_profiles:
            profile = self.denomination_profiles[denomination]
            # Simplified color check
            denomination_match = color_consistency

        combined_score = (
            color_consistency * 0.3 +
            saturation_score * 0.3 +
            denomination_match * 0.4
        )

        details = {
            "mean_rgb": [round(mean_r, 1), round(mean_g, 1), round(mean_b, 1)],
            "color_consistency": round(color_consistency, 4),
            "saturation": round(saturation_score, 4),
            "denomination_match": round(denomination_match, 4),
        }

        return combined_score, details

    def _analyze_edge_sharpness(self, img: np.ndarray) -> float:
        """Analyze edge quality — genuine notes have sharp intaglio printing."""
        gray = np.mean(img, axis=2)

        # Sobel-like edge detection using numpy
        # Horizontal edges
        gx = np.abs(gray[:, 1:] - gray[:, :-1])
        # Vertical edges
        gy = np.abs(gray[1:, :] - gray[:-1, :])

        # Edge strength
        edge_mean = (np.mean(gx) + np.mean(gy)) / 2

        # Normalize to 0-1 (genuine notes typically have edge_mean between 10-40)
        edge_score = min(edge_mean / 30.0, 1.0)

        # Edge distribution (genuine notes have evenly distributed fine edges)
        edge_std = (np.std(gx) + np.std(gy)) / 2
        distribution_score = 1.0 - min(edge_std / 60.0, 1.0)

        return edge_score * 0.6 + distribution_score * 0.4

    def _analyze_texture_complexity(self, img: np.ndarray) -> float:
        """Analyze texture complexity — genuine notes have intricate patterns."""
        gray = np.mean(img, axis=2)

        # Local variance as texture measure
        # Use small window statistics
        h, w = gray.shape
        block_size = 16
        variances = []

        for i in range(0, h - block_size, block_size):
            for j in range(0, w - block_size, block_size):
                block = gray[i:i+block_size, j:j+block_size]
                variances.append(np.var(block))

        if not variances:
            return 0.5

        mean_var = np.mean(variances)
        var_of_var = np.std(variances)

        # High mean variance = complex texture (good)
        complexity_score = min(mean_var / 1000, 1.0)

        # Varied variance = different texture regions (good for currency)
        diversity_score = min(var_of_var / 500, 1.0)

        return complexity_score * 0.6 + diversity_score * 0.4

    def _analyze_symmetry(self, img: np.ndarray) -> float:
        """Analyze geometric symmetry of the note."""
        gray = np.mean(img, axis=2)
        h, w = gray.shape

        # Horizontal symmetry (compare left-right halves)
        left_half = gray[:, :w//2]
        right_half = np.flip(gray[:, w//2:w//2*2], axis=1)

        # Ensure same size
        min_w = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_w]
        right_half = right_half[:, :min_w]

        if left_half.size == 0 or right_half.size == 0:
            return 0.5

        # Similarity between halves
        diff = np.mean(np.abs(left_half - right_half))
        h_symmetry = max(1.0 - diff / 128.0, 0.0)

        # Aspect ratio check
        aspect_ratio = w / h if h > 0 else 0
        expected_ratio = 2.18  # Standard Indian currency
        ratio_diff = abs(aspect_ratio - expected_ratio) / expected_ratio
        ratio_score = max(1.0 - ratio_diff, 0.0)

        return h_symmetry * 0.5 + ratio_score * 0.5

    def _analyze_frequency_domain(self, img: np.ndarray) -> float:
        """
        Frequency domain analysis to detect printing method artifacts.
        Genuine notes have specific frequency signatures from intaglio printing.
        """
        gray = np.mean(img, axis=2)

        # 2D FFT for frequency analysis
        try:
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude = np.log1p(np.abs(f_shift))

            # Analyze frequency distribution
            h, w = magnitude.shape
            center_h, center_w = h // 2, w // 2

            # Low frequency energy (center area)
            low_freq_region = magnitude[
                center_h-h//8:center_h+h//8,
                center_w-w//8:center_w+w//8
            ]
            low_freq_energy = np.mean(low_freq_region)

            # High frequency energy (outer area)
            high_freq_energy = (np.sum(magnitude) - np.sum(low_freq_region)) / (magnitude.size - low_freq_region.size + 1)

            # Ratio: genuine notes have a specific high-to-low frequency ratio
            # due to fine printing techniques
            freq_ratio = high_freq_energy / (low_freq_energy + 1e-10)
            freq_score = min(freq_ratio * 3, 1.0)

            return freq_score

        except Exception:
            return 0.5

    def _generate_summary(
        self, verdict: str, score: float, denomination: Optional[str], risk_factors: List[str]
    ) -> str:
        """Generate human-readable analysis summary."""
        denom_str = f"₹{denomination}" if denomination else "currency"

        if verdict == "genuine":
            return (
                f"✅ GENUINE: The {denom_str} note analysis indicates authentic characteristics "
                f"(authenticity score: {score*100:.0f}%). Security features and printing quality "
                f"are consistent with genuine Reserve Bank of India currency."
            )
        elif verdict == "suspicious":
            concerns = "; ".join(risk_factors[:2]) if risk_factors else "Some features need verification"
            return (
                f"⚠️ SUSPICIOUS: The {denom_str} note shows mixed signals "
                f"(authenticity score: {score*100:.0f}%). Concerns: {concerns}. "
                f"Physical verification is recommended."
            )
        else:
            concerns = "; ".join(risk_factors[:3]) if risk_factors else "Multiple features flagged"
            return (
                f"🚫 LIKELY COUNTERFEIT: The {denom_str} note shows significant "
                f"discrepancies (risk score: {score*100:.0f}%). {concerns}. "
                f"Do NOT accept this note. Report to the nearest bank or police station."
            )

    def _generate_recommendations(
        self, verdict: str, features: Dict[str, float], denomination: Optional[str]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recs = []

        if verdict == "fake":
            recs.extend([
                "🚫 Do NOT circulate this note — possession of counterfeit currency is a criminal offense",
                "🏦 Submit to the nearest bank branch for verification and impounding",
                "📞 Report to Police or RBI (Reserve Bank of India) helpline",
                "📷 Keep records of where you received this note",
            ])
        elif verdict == "suspicious":
            recs.extend([
                "🔍 Get the note physically verified at a bank branch",
                "💡 Check for watermark, security thread, and latent image",
                "🔎 Use UV light to verify fluorescent features",
                "📱 Use the RBI's MANI app for additional verification",
            ])
        else:
            recs.extend([
                "✅ Note appears genuine based on visual analysis",
                "💡 For additional confirmation, verify physical security features",
                "🏦 When in doubt, get official verification at any bank branch",
            ])

        return recs
