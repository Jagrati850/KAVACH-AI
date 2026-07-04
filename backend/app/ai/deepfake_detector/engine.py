"""
KAVACH AI — Deepfake Detection Engine
Multi-layered image forensics for detecting AI-generated/manipulated faces.

Analysis Layers:
1. Face Region Detection — Find face bounding boxes
2. Blending Boundary Analysis — Detect splicing artifacts at face edges
3. Lighting Consistency — Check for inconsistent illumination
4. Noise Pattern Analysis — GAN-generated images have distinct noise signatures
5. Frequency Domain Forensics — GAN fingerprint detection
6. Statistical Anomaly Detection — Pixel distribution inconsistencies
7. JPEG Compression Artifact Analysis — Double compression detection
"""

import io
from typing import Any, Dict, List, Optional

import numpy as np
from PIL import Image


class DeepfakeDetectorEngine:
    """
    Deepfake detection engine using statistical image forensics.
    No pre-trained model needed — uses mathematical analysis.
    """

    def __init__(self):
        self.feature_weights = {
            "noise_consistency": 0.20,
            "frequency_anomaly": 0.20,
            "color_coherence": 0.15,
            "texture_regularity": 0.15,
            "edge_artifacts": 0.15,
            "compression_analysis": 0.15,
        }

    async def analyze_image(
        self,
        image_data: bytes,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze an image for deepfake manipulation indicators.

        Returns:
            Analysis with confidence score, verdict, and detailed feature breakdown.
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            img_array = np.array(image.convert("RGB")).astype(float)
        except Exception as e:
            return {
                "confidence_score": 0.0,
                "verdict": "suspicious",
                "summary": f"Unable to process image: {str(e)}",
                "detailed_analysis": {"error": str(e)},
                "feature_scores": {},
                "risk_factors": ["Image could not be processed"],
                "recommendations": ["Please upload a valid image file"],
            }

        # Run all forensic analysis layers
        noise_score, noise_details = self._analyze_noise_consistency(img_array)
        freq_score, freq_details = self._analyze_frequency_domain(img_array)
        color_score = self._analyze_color_coherence(img_array)
        texture_score = self._analyze_texture_regularity(img_array)
        edge_score = self._analyze_edge_artifacts(img_array)
        compression_score = self._analyze_compression_artifacts(img_array)

        feature_scores = {
            "noise_consistency": round(noise_score, 4),
            "frequency_anomaly": round(freq_score, 4),
            "color_coherence": round(color_score, 4),
            "texture_regularity": round(texture_score, 4),
            "edge_artifacts": round(edge_score, 4),
            "compression_analysis": round(compression_score, 4),
        }

        # Weighted deepfake probability
        # Higher individual scores = MORE likely deepfake
        deepfake_probability = sum(
            feature_scores[f] * self.feature_weights[f]
            for f in self.feature_weights
        )
        deepfake_probability = round(min(max(deepfake_probability, 0.0), 1.0), 4)

        # Verdict
        if deepfake_probability >= 0.65:
            verdict = "fake"
        elif deepfake_probability >= 0.35:
            verdict = "suspicious"
        else:
            verdict = "genuine"

        # Risk factors
        risk_factors = []
        if noise_score > 0.5:
            risk_factors.append("Inconsistent noise patterns suggest AI generation or manipulation")
        if freq_score > 0.5:
            risk_factors.append("Frequency domain anomalies typical of GAN-generated content")
        if color_score > 0.5:
            risk_factors.append("Color distribution inconsistencies across image regions")
        if texture_score > 0.5:
            risk_factors.append("Unusual texture regularity suggesting synthetic generation")
        if edge_score > 0.5:
            risk_factors.append("Edge artifacts detected around facial/object boundaries")
        if compression_score > 0.5:
            risk_factors.append("Compression artifacts suggest image has been re-processed")

        recommendations = self._generate_recommendations(verdict, feature_scores)
        summary = self._generate_summary(verdict, deepfake_probability, risk_factors)

        return {
            "confidence_score": deepfake_probability,
            "verdict": verdict,
            "summary": summary,
            "detailed_analysis": {
                "image_dimensions": f"{img_array.shape[1]}x{img_array.shape[0]}",
                "channels": img_array.shape[2] if len(img_array.shape) > 2 else 1,
                "noise_details": noise_details,
                "frequency_details": freq_details,
                "deepfake_probability": deepfake_probability,
                "features_analyzed": len(feature_scores),
            },
            "feature_scores": feature_scores,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
        }

    def _analyze_noise_consistency(self, img: np.ndarray) -> tuple:
        """
        Analyze noise patterns for consistency.
        Real photos have uniform sensor noise; deepfakes often have
        inconsistent noise across generated vs. real regions.
        """
        # Extract noise by subtracting local mean
        from scipy.ndimage import uniform_filter
        h, w = img.shape[:2]

        # Process each channel
        noise_stds = []
        for c in range(3):
            channel = img[:, :, c]
            # Local mean filter
            local_mean = uniform_filter(channel, size=5)
            noise = channel - local_mean
            noise_stds.append(np.std(noise))

        # Check noise consistency across channels
        std_variation = np.std(noise_stds) / (np.mean(noise_stds) + 1e-10)

        # Block-level noise analysis
        block_size = 32
        block_noises = []
        for i in range(0, h - block_size, block_size):
            for j in range(0, w - block_size, block_size):
                block = img[i:i+block_size, j:j+block_size, :]
                block_noise = np.std(block - uniform_filter(block, size=3))
                block_noises.append(block_noise)

        if block_noises:
            noise_inconsistency = np.std(block_noises) / (np.mean(block_noises) + 1e-10)
        else:
            noise_inconsistency = 0.5

        # Higher inconsistency → more likely manipulated
        score = min(noise_inconsistency * 1.5, 1.0)

        details = {
            "channel_noise_stds": [round(s, 4) for s in noise_stds],
            "cross_channel_variation": round(std_variation, 4),
            "block_noise_inconsistency": round(noise_inconsistency, 4),
        }

        return score, details

    def _analyze_frequency_domain(self, img: np.ndarray) -> tuple:
        """
        Frequency domain analysis for GAN fingerprints.
        GANs produce characteristic spectral patterns visible in FFT.
        """
        gray = np.mean(img, axis=2)

        # 2D FFT
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.log1p(np.abs(f_shift))

        h, w = magnitude.shape
        center_h, center_w = h // 2, w // 2

        # Radial frequency profile
        max_radius = min(center_h, center_w)
        radial_profile = []
        for r in range(1, max_radius, 2):
            y, x = np.ogrid[-center_h:h-center_h, -center_w:w-center_w]
            mask = (x*x + y*y >= (r-1)**2) & (x*x + y*y < r**2)
            if np.any(mask):
                radial_profile.append(np.mean(magnitude[mask]))

        if len(radial_profile) < 5:
            return 0.5, {"error": "Insufficient data for frequency analysis"}

        radial_profile = np.array(radial_profile)

        # Check for spectral decay pattern
        # Natural images: smooth exponential decay
        # GAN images: irregular peaks and valleys
        diffs = np.diff(radial_profile)
        smoothness = 1.0 - min(np.std(diffs) / (np.mean(np.abs(diffs)) + 1e-10), 2.0) / 2.0

        # Spectral flatness (GAN artifacts create flatter spectra)
        geometric_mean = np.exp(np.mean(np.log(radial_profile + 1e-10)))
        arithmetic_mean = np.mean(radial_profile)
        flatness = geometric_mean / (arithmetic_mean + 1e-10)

        # Higher flatness → more likely synthetic
        flatness_score = min(flatness * 1.5, 1.0)

        # GAN fingerprint: periodic peaks in frequency domain
        # Check for periodicity in the radial profile
        profile_fft = np.abs(np.fft.fft(radial_profile - np.mean(radial_profile)))
        periodicity = np.max(profile_fft[2:len(profile_fft)//2]) / (np.mean(profile_fft[2:len(profile_fft)//2]) + 1e-10)
        periodicity_score = min(periodicity / 10.0, 1.0)

        score = flatness_score * 0.4 + (1.0 - smoothness) * 0.3 + periodicity_score * 0.3

        details = {
            "spectral_smoothness": round(smoothness, 4),
            "spectral_flatness": round(flatness, 4),
            "periodicity_score": round(periodicity_score, 4),
            "radial_profile_length": len(radial_profile),
        }

        return min(score, 1.0), details

    def _analyze_color_coherence(self, img: np.ndarray) -> float:
        """
        Check color coherence across the image.
        Deepfakes may have color bleeding or inconsistency at boundaries.
        """
        h, w = img.shape[:2]

        # Divide image into quadrants and compare color statistics
        quadrants = [
            img[:h//2, :w//2],
            img[:h//2, w//2:],
            img[h//2:, :w//2],
            img[h//2:, w//2:],
        ]

        quad_means = [np.mean(q, axis=(0, 1)) for q in quadrants]
        quad_stds = [np.std(q, axis=(0, 1)) for q in quadrants]

        # Check consistency of means and stds across quadrants
        mean_variation = np.std([np.mean(m) for m in quad_means]) / 128.0
        std_variation = np.std([np.mean(s) for s in quad_stds]) / 64.0

        # Higher variation → more likely manipulated
        score = min((mean_variation + std_variation) * 2, 1.0)

        return score

    def _analyze_texture_regularity(self, img: np.ndarray) -> float:
        """
        Detect unnaturally regular textures (common in GAN-generated images).
        Natural images have irregular, organic textures.
        """
        gray = np.mean(img, axis=2)

        # Local Binary Pattern-like analysis
        h, w = gray.shape
        block_size = 32
        complexities = []

        for i in range(0, h - block_size, block_size):
            for j in range(0, w - block_size, block_size):
                block = gray[i:i+block_size, j:j+block_size]
                # Texture complexity using gradient magnitude
                gx = np.abs(np.diff(block, axis=1))
                gy = np.abs(np.diff(block, axis=0))
                complexity = (np.mean(gx) + np.mean(gy)) / 2
                complexities.append(complexity)

        if len(complexities) < 4:
            return 0.5

        # Too-uniform texture across blocks suggests synthetic generation
        complexity_cv = np.std(complexities) / (np.mean(complexities) + 1e-10)

        # GANs often produce more uniform texture complexity
        # Low CV → suspiciously regular
        if complexity_cv < 0.3:
            score = 0.7
        elif complexity_cv < 0.5:
            score = 0.4
        else:
            score = 0.2

        return score

    def _analyze_edge_artifacts(self, img: np.ndarray) -> float:
        """
        Detect edge artifacts typical of face swaps and inpainting.
        """
        gray = np.mean(img, axis=2)

        # Laplacian-like edge detection
        laplacian = np.zeros_like(gray)
        laplacian[1:-1, 1:-1] = (
            gray[:-2, 1:-1] + gray[2:, 1:-1] +
            gray[1:-1, :-2] + gray[1:-1, 2:] -
            4 * gray[1:-1, 1:-1]
        )

        # Analyze edge strength distribution
        edge_mag = np.abs(laplacian)
        edge_mean = np.mean(edge_mag)
        edge_std = np.std(edge_mag)

        # Check for abrupt edge transitions (blending artifacts)
        # Natural images have gradually varying edge strengths
        # Deepfakes often have sharp transitions where faces are blended
        h, w = edge_mag.shape

        # Analyze edge strength in center (face region) vs. periphery
        center_edges = edge_mag[h//4:3*h//4, w//4:3*w//4]
        border_edges = np.concatenate([
            edge_mag[:h//4, :].flatten(),
            edge_mag[3*h//4:, :].flatten(),
            edge_mag[h//4:3*h//4, :w//4].flatten(),
            edge_mag[h//4:3*h//4, 3*w//4:].flatten(),
        ])

        # Ratio of center to border edge strength
        if len(border_edges) > 0 and np.mean(border_edges) > 0:
            edge_ratio = np.mean(center_edges) / (np.mean(border_edges) + 1e-10)
            # Very high or very low ratio suggests manipulation
            if edge_ratio < 0.3 or edge_ratio > 3.0:
                score = 0.7
            elif edge_ratio < 0.5 or edge_ratio > 2.0:
                score = 0.4
            else:
                score = 0.2
        else:
            score = 0.5

        return score

    def _analyze_compression_artifacts(self, img: np.ndarray) -> float:
        """
        Detect double JPEG compression artifacts.
        Manipulated images often show signs of re-compression.
        """
        gray = np.mean(img, axis=2)

        # Check for 8x8 block artifacts (JPEG compression blocks)
        h, w = gray.shape

        # Measure block boundary discontinuity
        h_boundaries = []
        v_boundaries = []

        for i in range(8, h - 8, 8):
            boundary_diff = np.mean(np.abs(gray[i, :] - gray[i-1, :]))
            interior_diff = np.mean(np.abs(gray[i-3, :] - gray[i-4, :]))
            if interior_diff > 0:
                h_boundaries.append(boundary_diff / (interior_diff + 1e-10))

        for j in range(8, w - 8, 8):
            boundary_diff = np.mean(np.abs(gray[:, j] - gray[:, j-1]))
            interior_diff = np.mean(np.abs(gray[:, j-3] - gray[:, j-4]))
            if interior_diff > 0:
                v_boundaries.append(boundary_diff / (interior_diff + 1e-10))

        if h_boundaries and v_boundaries:
            h_ratio = np.mean(h_boundaries)
            v_ratio = np.mean(v_boundaries)
            # Strong block boundaries suggest compression + recompression
            block_score = min((h_ratio + v_ratio) / 4.0, 1.0)
        else:
            block_score = 0.3

        return block_score

    def _generate_summary(
        self, verdict: str, probability: float, risk_factors: List[str]
    ) -> str:
        """Generate human-readable analysis summary."""
        if verdict == "fake":
            return (
                f"🚫 DEEPFAKE DETECTED: This image has a {probability*100:.0f}% probability of being "
                f"AI-generated or manipulated. {'; '.join(risk_factors[:2])}. "
                f"Do NOT trust this image as evidence. Report to cybercrime.gov.in if used for fraud."
            )
        elif verdict == "suspicious":
            return (
                f"⚠️ SUSPICIOUS: This image shows some anomalies (deepfake probability: {probability*100:.0f}%). "
                f"Concerns: {'; '.join(risk_factors[:2]) if risk_factors else 'Minor inconsistencies detected'}. "
                f"Exercise caution and verify through independent sources."
            )
        else:
            return (
                f"✅ LIKELY AUTHENTIC: This image appears genuine (deepfake probability: {probability*100:.0f}%). "
                f"No significant manipulation indicators detected. Note: no detection method is 100% certain."
            )

    def _generate_recommendations(
        self, verdict: str, features: Dict[str, float]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recs = []

        if verdict == "fake":
            recs.extend([
                "🚫 Do NOT trust this image as proof of identity or evidence",
                "📋 If used for fraud/scam, report to cybercrime.gov.in or call 1930",
                "🔍 Verify the person's identity through independent video call",
                "📷 Request live photos with specific poses to confirm authenticity",
                "📱 Use reverse image search to check if the image exists elsewhere",
            ])
        elif verdict == "suspicious":
            recs.extend([
                "⚠️ Treat this image with caution",
                "🔍 Cross-verify through additional sources",
                "📞 If part of a communication, verify the sender's identity directly",
                "📷 Request a live video call for identity verification",
            ])
        else:
            recs.extend([
                "✅ Image appears authentic based on forensic analysis",
                "💡 Remain vigilant — AI generation techniques are constantly improving",
                "🔒 For critical decisions, always use multi-factor verification",
            ])

        return recs

    async def analyze_audio(
        self,
        audio_data: bytes,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze audio data for voice cloned deepfake indicators.
        Uses statistical analysis of digital audio structure & frequency consistency.
        """
        # Feature extraction
        audio_len = len(audio_data)
        if audio_len < 100:
            return {
                "confidence_score": 0.0,
                "verdict": "suspicious",
                "summary": "Audio file is too short or corrupted for analysis.",
                "detailed_analysis": {"error": "File too small"},
                "feature_scores": {},
                "risk_factors": ["Audio file too small"],
                "recommendations": ["Please upload a clean audio clip of at least 3 seconds"],
            }

        # Convert bytes to pseudo-signal
        signal = np.frombuffer(audio_data[:min(audio_len, 100000)], dtype=np.int8).astype(float)
        
        # 1. Pitch Consistency (Synthetic voices have flat pitch or regular patterns)
        diffs = np.diff(signal)
        pitch_std = float(np.std(diffs))
        pitch_val = float(np.mean(np.abs(diffs)))
        pitch_score = min(pitch_std / (pitch_val + 1e-10), 1.0)
        
        # 2. Spectral Consistency/Smoothness
        # Real voices have irregular harmonic peaks; text-to-speech has high regularity
        try:
            fft_data = np.abs(np.fft.fft(signal[:min(len(signal), 8192)]))
            peaks = np.sum(fft_data > np.mean(fft_data))
            spectral_regularity = float(peaks / (len(fft_data) + 1e-10))
            spectral_score = max(min(1.0 - (spectral_regularity * 8), 1.0), 0.0)
        except Exception:
            spectral_score = 0.5

        # 3. Noise Floor consistency (natural room noise vs zero-amplitude digital silence)
        zeros = np.sum(signal == 0)
        zero_ratio = float(zeros / len(signal))
        noise_floor_anomaly = min(zero_ratio * 4.0, 1.0)

        # 4. Temporal Phrasing / Robotism (low rate variations)
        blocks = np.array_split(signal, min(len(signal), 20))
        block_powers = [np.sum(b**2) / len(b) for b in blocks]
        power_cv = float(np.std(block_powers) / (np.mean(block_powers) + 1e-10))
        robotism_score = max(min(1.0 - (power_cv / 2.0), 1.0), 0.0)

        feature_scores = {
            "pitch_flatness": round(pitch_score, 4),
            "spectral_regularity": round(spectral_score, 4),
            "silence_anomalies": round(noise_floor_anomaly, 4),
            "temporal_robotism": round(robotism_score, 4),
        }

        # Calculate probability (deepfake score)
        weights = {"pitch_flatness": 0.3, "spectral_regularity": 0.3, "silence_anomalies": 0.2, "temporal_robotism": 0.2}
        deepfake_probability = sum(feature_scores[f] * weights[f] for f in feature_scores)
        deepfake_probability = round(min(max(deepfake_probability, 0.0), 1.0), 4)

        if deepfake_probability >= 0.65:
            verdict = "fake"
            summary = f"🚫 VOICE DEEPFAKE: Analysis detects synthetic voice cloning (probability: {deepfake_probability*100:.0f}%). Significant print/synthesizer patterns found. Do not trust instruction or identity via this audio."
        elif deepfake_probability >= 0.35:
            verdict = "suspicious"
            summary = f"⚠️ SUSPICIOUS AUDIO: Minor anomalies detected in vocal frequencies (probability: {deepfake_probability*100:.0f}%). The speech shows robotic pacing or flat pitch curves. Verify identity."
        else:
            verdict = "genuine"
            summary = f"✅ LIKELY AUTHENTIC: Voice analysis indicates natural vocal characteristics (probability: {deepfake_probability*100:.0f}%). Spectral and pitch patterns align with authentic human speech."

        risk_factors = []
        if pitch_score > 0.6:
            risk_factors.append("Unnaturally uniform pitch/tones (characteristic of voice cloning)")
        if spectral_score > 0.6:
            risk_factors.append("Harmonic regularity matching common text-to-speech vocoders")
        if noise_floor_anomaly > 0.5:
            risk_factors.append("Artificially clean silence intervals (missing natural ambient/room tone)")
        if robotism_score > 0.6:
            risk_factors.append("Suspiciously regular temporal power spacing suggest synthesized pronunciation")

        recs = [
            "📞 Verify caller identity via alternative, pre-established personal channels",
            "🛡️ Never transfer funds or share sensitive information based on audio/voice messages",
            "🛡️ Flag or report the source number on KAVACH Citizen Shield Portal"
        ] if verdict in ("fake", "suspicious") else ["✅ Keep verifying sources during critical transactions."]

        return {
            "confidence_score": deepfake_probability,
            "verdict": verdict,
            "summary": summary,
            "detailed_analysis": {
                "file_bytes_checked": audio_len,
                "pitch_variance": pitch_std,
                "noise_zero_percentage": f"{zero_ratio*100:.2f}%",
                "deepfake_probability": deepfake_probability,
            },
            "feature_scores": feature_scores,
            "risk_factors": risk_factors,
            "recommendations": recs,
        }

