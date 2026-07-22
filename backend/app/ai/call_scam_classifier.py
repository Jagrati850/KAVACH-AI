"""
KAVACH AI — Call Transcript Scam Classifier
ML-based classifier for call transcripts trained on a balanced 15-category
dataset (4 normal-call classes + 11 scam classes).

Model: TF-IDF (word + char n-grams) → Logistic Regression
Artifact: backend/data/models/call_scam_classifier.joblib
Training:  backend/ml/train_call_scam_classifier.ipynb
Dataset:   backend/data/call_transcripts/call_transcripts_dataset.csv

Used by the /scans/scam-call and /scans/scam-call-audio endpoints.
The prediction varies with the transcript content — category, scam
probability, reason, and recommendations are all derived from the model.
"""

import asyncio
import os
from typing import Any, Dict, Optional

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "models", "call_scam_classifier.joblib"
)

# Human-readable labels for each category
CATEGORY_LABELS = {
    "genuine_banking_call": "Genuine Banking Call",
    "family_conversation": "Family / Personal Conversation",
    "customer_support": "Customer Support Call",
    "delivery_call": "Delivery / Courier Coordination Call",
    "lottery_scam": "Lottery / Prize Scam",
    "fake_cbi_police_call": "Fake CBI / Police Impersonation",
    "fake_kyc_update": "Fake KYC Update Scam",
    "upi_refund_scam": "UPI Refund Scam",
    "otp_scam": "OTP Theft Scam",
    "loan_scam": "Instant Loan Scam",
    "investment_scam": "Investment / Trading Scam",
    "sextortion": "Sextortion / Blackmail",
    "digital_arrest_scam": "Digital Arrest Scam",
    "courier_scam": "Courier Parcel Scam",
    "customs_scam": "Customs Duty Scam",
}

# Per-category reasons and recommended actions
CATEGORY_REASONS = {
    "genuine_banking_call": "Language matches routine bank communication: informational tone, no OTP/PIN demands, no urgency or threats.",
    "family_conversation": "Conversational personal language with no financial demands, threats, or impersonation markers.",
    "customer_support": "Matches standard customer-service phrasing: order/service references without credential or payment demands.",
    "delivery_call": "Routine delivery coordination language without customs threats, fees, or identity verification demands.",
    "lottery_scam": "Classic prize-bait pattern: unexpected winnings combined with an upfront 'fee/tax' demand and secrecy/urgency pressure.",
    "fake_cbi_police_call": "Law-enforcement impersonation markers: fabricated FIR/warrant threats with arrest pressure and payment or secrecy demands.",
    "fake_kyc_update": "Fake KYC-expiry pressure: account-blocking threats used to extract OTP, card details, or app installation.",
    "upi_refund_scam": "Refund-bait pattern: victims are tricked into entering their UPI PIN on a collect request, which SENDS money instead of receiving it.",
    "otp_scam": "Direct OTP-extraction attempt: fabricated fraud/order story engineered to make you reveal the one-time password.",
    "loan_scam": "Advance-fee loan fraud: 'pre-approved' loan requiring upfront processing/insurance charges before disbursal.",
    "investment_scam": "Guaranteed-returns fraud markers: unrealistic profit promises, WhatsApp 'VIP groups', and pressure to transfer to personal accounts.",
    "sextortion": "Blackmail/extortion pattern: threats to leak private content unless immediate payment is made, with police-avoidance pressure.",
    "digital_arrest_scam": "Digital-arrest hallmark: fake 'online custody' demanding continuous video call, isolation from family, and fund 'verification' transfers.",
    "courier_scam": "Parcel-crime hoax: fake contraband parcel linked to your identity, escalated to fake police to extract money/credentials.",
    "customs_scam": "Customs-fee fraud: fictitious held parcel requiring immediate duty/clearance payment under threat of prosecution.",
}

CATEGORY_RECOMMENDATIONS = {
    "_safe_common": [
        "✅ No scam indicators detected in this call transcript",
        "🔒 As a habit, never share OTP, PIN, CVV, or passwords on any call",
        "📞 If anything felt off, verify by calling the official number of the organization",
    ],
    "lottery_scam": [
        "🚫 Do NOT pay any 'registration fee' or 'tax' — real lotteries never ask winners to pay",
        "📵 Block the caller and do not share bank details",
        "🛡️ Report the number on the KAVACH portal and cybercrime.gov.in",
    ],
    "fake_cbi_police_call": [
        "🚫 Hang up immediately — police/CBI never demand money or interrogate over phone calls",
        "📞 Verify any real case by visiting your nearest police station in person",
        "🛡️ Report to 1930 cyber helpline and the KAVACH portal",
    ],
    "fake_kyc_update": [
        "🚫 Never share OTP or install apps on a caller's instruction — banks never do KYC over calls",
        "🏦 Update KYC only by visiting your branch or the bank's official app/website",
        "🛡️ Report the number to your bank's fraud helpline and KAVACH",
    ],
    "upi_refund_scam": [
        "🚫 NEVER enter your UPI PIN to 'receive' money — PIN is only needed to SEND money",
        "❌ Reject any unexpected collect requests on your UPI apps",
        "🛡️ Report the UPI ID on the KAVACH portal and to your bank",
    ],
    "otp_scam": [
        "🚫 Never read out an OTP on a call — no genuine bank/company will ever ask",
        "🔐 If you already shared an OTP, call your bank's hotline immediately to freeze the account",
        "🛡️ Report the incident at 1930 and the KAVACH portal",
    ],
    "loan_scam": [
        "🚫 Do not pay any upfront 'processing fee' — genuine lenders deduct charges from disbursal",
        "📋 Verify lenders on the RBI registered-NBFC list before sharing documents",
        "🛡️ Report the app/number on the KAVACH portal",
    ],
    "investment_scam": [
        "🚫 Do not transfer money to personal accounts for 'guaranteed returns' — all such promises are fraud",
        "📉 Verify advisors on SEBI's registered-intermediary list",
        "🛡️ Report the group/number at cybercrime.gov.in and KAVACH",
    ],
    "sextortion": [
        "🚫 Do NOT pay — payment leads to escalating demands, not deletion",
        "📸 Preserve evidence (screenshots, numbers) and stop all contact",
        "👮 Report immediately at 1930 / cybercrime.gov.in — cases are handled confidentially",
    ],
    "digital_arrest_scam": [
        "🚨 'Digital arrest' does NOT exist in Indian law — disconnect the call immediately",
        "🚫 Never transfer funds for 'verification' and never stay on forced video calls",
        "👮 Call 1930 right away and report on the KAVACH portal",
    ],
    "courier_scam": [
        "🚫 Hang up — couriers never transfer calls to 'police' about parcels",
        "📦 Track shipments only on the courier's official website with your tracking ID",
        "🛡️ Report the number at 1930 and the KAVACH portal",
    ],
    "customs_scam": [
        "🚫 Do not pay any customs 'duty' over UPI — real customs duties are paid through official channels only",
        "📦 Verify any parcel issue directly with India Post/courier official helplines",
        "🛡️ Report the caller at 1930 and the KAVACH portal",
    ],
}


class CallScamClassifier:
    """Lazy-loading wrapper around the trained joblib artifact."""

    def __init__(self):
        self._artifact = None

    def _load(self):
        if self._artifact is None:
            import joblib
            self._artifact = joblib.load(os.path.abspath(MODEL_PATH))
        return self._artifact

    def _predict_sync(self, text: str) -> Dict[str, Any]:
        artifact = self._load()
        model = artifact["model"]
        scam_set = set(artifact["scam_categories"])

        proba = model.predict_proba([text])[0]
        classes = model.classes_

        # Top category + scam probability mass
        ranked = sorted(zip(classes, proba), key=lambda x: -x[1])
        top_cat, top_p = ranked[0]
        scam_prob = float(sum(p for c, p in zip(classes, proba) if c in scam_set))
        is_scam = top_cat in scam_set

        return {
            "category": str(top_cat),
            "category_confidence": float(top_p),
            "scam_probability": scam_prob,
            "is_scam": bool(is_scam),
            "top3": [(str(c), float(p)) for c, p in ranked[:3]],
        }

    async def analyze(
        self,
        transcript: str,
        language: str = "auto",
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Classify a call transcript. Returns a dict compatible with the
        existing ScanResult fields (verdict / confidence_score / summary /
        recommendations) plus scam category details in detailed_analysis.
        """
        pred = await asyncio.to_thread(self._predict_sync, transcript)

        category = pred["category"]
        label = CATEGORY_LABELS.get(category, category)
        scam_prob = pred["scam_probability"]
        is_scam = pred["is_scam"]

        # Verdict mapping on scam probability
        if is_scam and scam_prob >= 0.65:
            verdict = "dangerous"
        elif is_scam or scam_prob >= 0.40:
            verdict = "suspicious"
        else:
            verdict = "safe"

        reason = CATEGORY_REASONS.get(category, "Classified by the call-transcript ML model.")

        if verdict == "safe":
            summary = (
                f"✅ NOT A SCAM — classified as '{label}' "
                f"({scam_prob*100:.0f}% scam probability). {reason}"
            )
            recommendations = CATEGORY_RECOMMENDATIONS["_safe_common"]
            risk_factors = []
        else:
            risk_word = "HIGH RISK" if verdict == "dangerous" else "MEDIUM RISK"
            summary = (
                f"🚨 {risk_word} — SCAM DETECTED: '{label}' "
                f"({scam_prob*100:.0f}% scam probability). {reason}"
            )
            recommendations = CATEGORY_RECOMMENDATIONS.get(
                category, CATEGORY_RECOMMENDATIONS["digital_arrest_scam"]
            )
            risk_factors = [f"Call matches known '{label}' fraud pattern", reason]

        return {
            "confidence_score": round(scam_prob, 4),
            "verdict": verdict,
            "summary": summary,
            "detailed_analysis": {
                "model": "call_scam_classifier v1.0 (TF-IDF + LogisticRegression)",
                "is_scam": is_scam,
                "scam_category": category,
                "scam_category_label": label,
                "category_confidence": round(pred["category_confidence"], 4),
                "scam_probability": round(scam_prob, 4),
                "reason": reason,
                "top_predictions": [
                    {"category": c, "label": CATEGORY_LABELS.get(c, c), "probability": round(p, 4)}
                    for c, p in pred["top3"]
                ],
                "language": language,
                "context": context,
            },
            "feature_scores": {
                "scam_probability": round(scam_prob, 4),
                "category_confidence": round(pred["category_confidence"], 4),
            },
            "risk_factors": risk_factors,
            "recommendations": recommendations,
        }
