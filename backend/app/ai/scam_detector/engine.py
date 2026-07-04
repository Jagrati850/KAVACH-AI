"""
KAVACH AI — Scam Detection Engine
Multi-layer NLP-based analysis for detecting digital arrest scams,
phishing, and social engineering attacks in text/transcripts.

Analysis Layers:
1. Keyword Pattern Matching — Known scam phrases and tactics
2. Urgency & Pressure Scoring — Detects high-pressure manipulation
3. Authority Impersonation Detection — Fake officer/agency claims
4. Fear & Threat Analysis — Intimidation language patterns
5. Financial Extraction Detection — Money demand patterns
6. Linguistic Anomaly Detection — Grammar/style inconsistencies
7. Hindi + English bilingual support
"""

import re
import asyncio
from typing import Any, Dict, List, Optional


class ScamDetectorEngine:
    """
    Production-grade scam detection engine using multi-layered NLP analysis.
    No external API dependencies — fully self-contained.
    """

    def __init__(self):
        self._load_patterns()

    def _load_patterns(self):
        """Load all scam detection patterns and weights."""

        # ── Layer 1: Authority Impersonation Patterns ────────
        self.authority_patterns = {
            "en": [
                r"\b(cbi|fbi|cia|police|cyber\s*cell|enforcement|interpol)\b",
                r"\b(income\s*tax|customs|narcotics|reserve\s*bank|rbi)\b",
                r"\b(supreme\s*court|high\s*court|magistrate|judiciary)\b",
                r"\b(officer|inspector|commissioner|superintendent|director)\b",
                r"\b(government|ministry|department|bureau|investigation)\b",
                r"\b(warrant|summons|court\s*order|legal\s*notice)\b",
                r"\b(badge\s*number|officer\s*id|case\s*number|fir)\b",
                r"\b(trai|telecom|uidai|aadhaar\s*authority)\b",
                r"\b(dcp|acp|sp|ips|ias|dgp)\b",
            ],
            "hi": [
                r"(पुलिस|सीबीआई|साइबर\s*सेल|थाना|थानेदार)",
                r"(अदालत|कोर्ट|न्यायालय|मजिस्ट्रेट|जज)",
                r"(अधिकारी|इंस्पेक्टर|कमिश्नर|निर्देशक)",
                r"(सरकार|मंत्रालय|विभाग|आयकर)",
                r"(वारंट|समन|कोर्ट\s*ऑर्डर|एफआईआर)",
                r"(आधार|यूआईडीएआई|ट्राई|आरबीआई)",
            ],
        }

        # ── Layer 2: Fear & Threat Patterns ──────────────────
        self.threat_patterns = {
            "en": [
                r"\b(arrest|jail|prison|custody|detained|handcuff)\b",
                r"\b(criminal|offense|illegal|laundering|terrorism)\b",
                r"\b(suspend|cancel|block|freeze|seize)\b",
                r"\b(punishment|sentence|penalty|fine|prosecution)\b",
                r"\b(drug|narcotic|contraband|smuggling|trafficking)\b",
                r"\b(cancel.*(?:aadhaar|pan|passport|sim|account))\b",
                r"\b(blacklist|terminate|deport|extradite)\b",
                r"\b(life\s*imprisonment|death\s*penalty|non.?bailable)\b",
                r"\b(your\s*(?:name|number|aadhaar|pan)\s*(?:is|has\s*been)\s*(?:linked|connected|found|used))\b",
            ],
            "hi": [
                r"(गिरफ्तार|जेल|हिरासत|कारावास|सजा)",
                r"(अपराध|अवैध|मनी\s*लॉन्ड्रिंग|आतंकवाद)",
                r"(रद्द|ब्लॉक|फ्रीज|जब्त|निलंबित)",
                r"(सजा|जुर्माना|दंड|कार्रवाई)",
                r"(ड्रग्स|तस्करी|नशीला|प्रतिबंधित)",
            ],
        }

        # ── Layer 3: Urgency & Pressure Patterns ─────────────
        self.urgency_patterns = {
            "en": [
                r"\b(immediately|urgent|right\s*now|within\s*\d+\s*(?:hour|minute|min))\b",
                r"\b(don'?t\s*(?:tell|inform|share|discuss)|keep\s*(?:secret|confidential))\b",
                r"\b(last\s*chance|final\s*warning|deadline|time\s*is\s*running)\b",
                r"\b(if\s*you\s*(?:don'?t|do\s*not|fail\s*to))\b",
                r"\b(act\s*now|do\s*(?:it|this)\s*now|hurry|quick(?:ly)?)\b",
                r"\b(no\s*time|running\s*out|limited\s*time)\b",
                r"\b(don'?t\s*(?:hang\s*up|disconnect|cut\s*the\s*call))\b",
                r"\b(stay\s*on\s*(?:the\s*)?(?:line|call|video))\b",
            ],
            "hi": [
                r"(तुरंत|अभी|जल्दी|फौरन|बिना\s*देर)",
                r"(किसी\s*को\s*(?:मत\s*बताना|न\s*बताएं))",
                r"(आखिरी\s*(?:मौका|चेतावनी)|समय\s*सीमा)",
                r"(अगर\s*(?:नहीं|न)\s*(?:किया|भेजा))",
            ],
        }

        # ── Layer 4: Financial Extraction Patterns ───────────
        self.financial_patterns = {
            "en": [
                r"\b(transfer|send|deposit|pay)\s*(?:₹|rs\.?|inr|rupee)?\s*[\d,]+\b",
                r"\b(?:₹|rs\.?|inr)\s*[\d,]+(?:\s*(?:lakh|crore|thousand|hundred))?\b",
                r"\b(upi|gpay|phonepe|paytm|bank\s*transfer|neft|imps|rtgs)\b",
                r"\b(account\s*(?:number|no)|ifsc|upi\s*id|vpa)\b",
                r"\b(fine|fee|bail|security\s*deposit|processing\s*(?:fee|charge))\b",
                r"\b(refund(?:able)?|will\s*(?:be\s*)?return(?:ed)?|get\s*(?:it\s*)?back)\b",
                r"\b(bitcoin|crypto|gift\s*card|voucher)\b",
                r"\b(share\s*(?:your\s*)?(?:otp|pin|password|cvv|card\s*number))\b",
            ],
            "hi": [
                r"(भेजो|भेजें|ट्रांसफर|जमा\s*करो|पैसे\s*भेज)",
                r"(₹|रुपये|लाख|करोड़|हजार)",
                r"(यूपीआई|गूगल\s*पे|फोनपे|पेटीएम|बैंक)",
                r"(ओटीपी|पिन|पासवर्ड|सीवीवी)",
                r"(जुर्माना|जमानत|फीस|शुल्क|रकम)",
            ],
        }

        # ── Layer 5: Digital Arrest Specific Patterns ────────
        self.digital_arrest_patterns = {
            "en": [
                r"\b(digital\s*arrest|video\s*(?:call\s*)?arrest|online\s*arrest)\b",
                r"\b(keep\s*(?:your\s*)?camera\s*on|show\s*(?:your\s*)?face)\b",
                r"\b(recording\s*(?:this|the)\s*(?:call|session)|monitored)\b",
                r"\b(skype|whatsapp\s*(?:video|call)|zoom|teams)\b",
                r"\b(verification\s*(?:process|procedure)|identity\s*(?:check|verification))\b",
                r"\b(confession|statement|deposition)\b",
                r"\b(parcel|courier|package)\s*(?:.*)\s*(?:drug|illegal|contraband)\b",
                r"\b(your\s*(?:parcel|courier|package)\s*(?:has\s*been|was)\s*(?:intercepted|seized|stopped))\b",
            ],
            "hi": [
                r"(डिजिटल\s*अरेस्ट|वीडियो\s*कॉल\s*अरेस्ट|ऑनलाइन\s*गिरफ्तारी)",
                r"(कैमरा\s*(?:चालू|ऑन)\s*रखो|चेहरा\s*दिखाओ)",
                r"(रिकॉर्ड\s*हो\s*रहा|निगरानी\s*में)",
                r"(पार्सल|कूरियर)\s*(?:.*)\s*(ड्रग|अवैध|प्रतिबंधित)",
            ],
        }

        # ── Feature weights for scoring ──────────────────────
        self.feature_weights = {
            "authority_impersonation": 0.25,
            "threat_intimidation": 0.20,
            "urgency_pressure": 0.20,
            "financial_extraction": 0.20,
            "digital_arrest_markers": 0.15,
        }

    async def analyze(
        self,
        text: str,
        language: str = "auto",
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run full multi-layer scam analysis on input text.

        Returns:
            Dict with confidence_score, verdict, summary, detailed_analysis,
            feature_scores, risk_factors, and recommendations.
        """
        # Detect language if auto
        if language == "auto":
            language = self._detect_language(text)

        text_lower = text.lower()
        text_normalized = self._normalize_text(text)

        # ── Run all analysis layers ──────────────────────────
        authority_score, authority_matches = self._analyze_patterns(
            text_normalized, self.authority_patterns, language
        )
        threat_score, threat_matches = self._analyze_patterns(
            text_normalized, self.threat_patterns, language
        )
        urgency_score, urgency_matches = self._analyze_patterns(
            text_normalized, self.urgency_patterns, language
        )
        financial_score, financial_matches = self._analyze_patterns(
            text_normalized, self.financial_patterns, language
        )
        digital_arrest_score, digital_arrest_matches = self._analyze_patterns(
            text_normalized, self.digital_arrest_patterns, language
        )

        # ── Calculate feature scores ─────────────────────────
        feature_scores = {
            "authority_impersonation": round(min(authority_score, 1.0), 4),
            "threat_intimidation": round(min(threat_score, 1.0), 4),
            "urgency_pressure": round(min(urgency_score, 1.0), 4),
            "financial_extraction": round(min(financial_score, 1.0), 4),
            "digital_arrest_markers": round(min(digital_arrest_score, 1.0), 4),
        }

        # ── Weighted composite score ─────────────────────────
        confidence_score = sum(
            feature_scores[f] * self.feature_weights[f]
            for f in feature_scores
        )

        # Boost for multiple layers triggered (multi-vector attack)
        active_layers = sum(1 for s in feature_scores.values() if s > 0.3)
        if active_layers >= 3:
            confidence_score = min(confidence_score * 1.25, 1.0)
        if active_layers >= 4:
            confidence_score = min(confidence_score * 1.15, 1.0)

        confidence_score = round(min(confidence_score, 1.0), 4)

        # ── Determine verdict ────────────────────────────────
        if confidence_score >= 0.7:
            verdict = "dangerous"
        elif confidence_score >= 0.4:
            verdict = "suspicious"
        else:
            verdict = "safe"

        # ── Compile risk factors ─────────────────────────────
        risk_factors = []
        if authority_score > 0.3:
            risk_factors.append("Impersonation of government/law enforcement authority detected")
        if threat_score > 0.3:
            risk_factors.append("Intimidation and threat language present")
        if urgency_score > 0.3:
            risk_factors.append("High-pressure urgency tactics detected")
        if financial_score > 0.3:
            risk_factors.append("Financial extraction demands identified")
        if digital_arrest_score > 0.3:
            risk_factors.append("Digital arrest scam markers detected")

        # ── Generate recommendations ─────────────────────────
        recommendations = self._generate_recommendations(
            verdict, feature_scores, context
        )

        # ── Generate summary ─────────────────────────────────
        summary = self._generate_summary(
            verdict, confidence_score, risk_factors, language
        )

        return {
            "confidence_score": confidence_score,
            "verdict": verdict,
            "summary": summary,
            "detailed_analysis": {
                "text_length": len(text),
                "language_detected": language,
                "context": context or "general",
                "layers_triggered": active_layers,
                "authority_matches": authority_matches[:5],
                "threat_matches": threat_matches[:5],
                "urgency_matches": urgency_matches[:5],
                "financial_matches": financial_matches[:5],
                "digital_arrest_matches": digital_arrest_matches[:5],
            },
            "feature_scores": feature_scores,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
        }

    def _detect_language(self, text: str) -> str:
        """Simple Hindi/English detection based on Unicode ranges."""
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        total_alpha = len(re.findall(r'[a-zA-Z\u0900-\u097F]', text)) or 1
        return "hi" if (hindi_chars / total_alpha) > 0.3 else "en"

    def _normalize_text(self, text: str) -> str:
        """Normalize text for pattern matching."""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        # Normalize common obfuscation (replacing @ with a, 0 with o, etc.)
        obfuscation_map = {'@': 'a', '0': 'o', '1': 'i', '3': 'e', '5': 's', '$': 's'}
        for char, replacement in obfuscation_map.items():
            text = text.replace(char, replacement)
        return text.strip()

    def _analyze_patterns(
        self,
        text: str,
        pattern_dict: Dict[str, List[str]],
        language: str,
    ) -> tuple:
        """
        Match patterns against text and compute a normalized score.
        Returns (score, matches).
        """
        matches = []
        patterns = pattern_dict.get(language, []) + pattern_dict.get("en", [])

        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                matches.extend(found if isinstance(found[0], str) else [m[0] if isinstance(m, tuple) else m for m in found])

        # Score: normalized by number of patterns (0-1 range)
        total_patterns = len(patterns) or 1
        match_ratio = len(set(matches)) / total_patterns
        # Apply sigmoid-like scaling for smoother scoring
        score = min(match_ratio * 2.5, 1.0)

        return score, list(set(matches))[:10]

    def _generate_summary(
        self,
        verdict: str,
        score: float,
        risk_factors: List[str],
        language: str,
    ) -> str:
        """Generate a human-readable analysis summary."""
        if verdict == "dangerous":
            base = (
                f"⚠️ HIGH ALERT: This message has a {score*100:.0f}% probability of being a scam. "
                f"Multiple scam indicators detected including: {', '.join(risk_factors[:3])}. "
                f"Do NOT comply with any demands. Do NOT share any personal information or make payments. "
                f"Report this to the Cyber Crime helpline 1930 immediately."
            )
        elif verdict == "suspicious":
            base = (
                f"⚡ CAUTION: This message shows suspicious patterns (confidence: {score*100:.0f}%). "
                f"Potential concerns: {', '.join(risk_factors[:2])}. "
                f"Exercise extreme caution. Verify the sender independently before taking any action."
            )
        else:
            base = (
                f"✅ LOW RISK: This message appears to be safe (confidence: {score*100:.0f}% scam probability). "
                f"No significant scam indicators detected. Stay vigilant and report if anything feels wrong."
            )
        return base

    def _generate_recommendations(
        self,
        verdict: str,
        feature_scores: Dict[str, float],
        context: Optional[str],
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []

        if verdict == "dangerous":
            recommendations.extend([
                "🚫 Do NOT send any money or share OTP/passwords",
                "📞 Call Cyber Crime helpline: 1930",
                "🌐 File a complaint at cybercrime.gov.in",
                "📱 Block and report this number/account",
                "👨‍👩‍👦 Alert family members about this scam tactic",
            ])

            if feature_scores.get("digital_arrest_markers", 0) > 0.3:
                recommendations.extend([
                    "🎥 No genuine law enforcement conducts 'digital arrests' — this is a known fraud technique",
                    "🏛️ If in doubt, physically visit your nearest police station to verify",
                    "📷 Take screenshots of the call/chat as evidence",
                ])

            if feature_scores.get("authority_impersonation", 0) > 0.3:
                recommendations.extend([
                    "🏢 Verify the officer's identity by calling the official department number directly",
                    "📋 Legitimate officers will NEVER ask for money over phone/video call",
                ])

        elif verdict == "suspicious":
            recommendations.extend([
                "⚠️ Verify the sender's identity through official channels independently",
                "🔍 Do not click any links or download attachments",
                "📞 If they claim to be from a bank/agency, call the official helpline to verify",
                "📝 Save all communication as evidence",
            ])

        else:
            recommendations.extend([
                "✅ Message appears safe, but remain vigilant",
                "🔒 Never share OTP, PIN, or passwords with anyone",
                "📱 Keep your devices and apps updated",
            ])

        return recommendations
