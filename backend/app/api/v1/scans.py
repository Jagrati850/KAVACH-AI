"""
KAVACH AI — AI Scans API
Endpoints for scam text analysis, currency verification, and deepfake detection.
"""

import time
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser
from app.models.scan import Scan, ScanResult, ScanStatus, ScanType, Verdict
from app.models.threat import ThreatIntel, ThreatType
from app.models.report import Report
from app.schemas.scan import (
    ScamTextRequest,
    ScamCallRequest,
    ScanHistoryResponse,
    ScanResponse,
    ScanResultResponse,
    CheckEntityResponse,
    DenominationFeaturesResponse,
    CurrencyFeatureInfo,
)
from app.ai.orchestrator import AIOrchestrator


router = APIRouter()
orchestrator = AIOrchestrator()


@router.post("/scam-text", response_model=ScanResponse)
async def analyze_scam_text(
    payload: ScamTextRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Analyze text (SMS, WhatsApp, email, call transcript) for scam indicators."""
    start = time.time()

    # Create scan record
    scan = Scan(
        user_id=current_user.id,
        scan_type=ScanType.SCAM_TEXT,
        input_text=payload.text,
        status=ScanStatus.PROCESSING,
    )
    db.add(scan)
    await db.flush()

    # Run AI analysis
    try:
        analysis = await orchestrator.analyze_scam_text(
            text=payload.text,
            language=payload.language,
            context=payload.context,
        )

        processing_time = (time.time() - start) * 1000

        # Create result
        result = ScanResult(
            scan_id=scan.id,
            confidence_score=analysis["confidence_score"],
            verdict=Verdict(analysis["verdict"]),
            summary=analysis["summary"],
            detailed_analysis=analysis.get("detailed_analysis"),
            feature_scores=analysis.get("feature_scores"),
            risk_factors=analysis.get("risk_factors"),
            recommendations=analysis.get("recommendations"),
            processing_time_ms=processing_time,
        )
        db.add(result)

        scan.status = ScanStatus.COMPLETED
        await db.flush()

        return ScanResponse(
            id=scan.id,
            scan_type=scan.scan_type.value,
            status=scan.status.value,
            created_at=scan.created_at,
            result=ScanResultResponse.model_validate(result),
        )

    except Exception as e:
        scan.status = ScanStatus.FAILED
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}",
        )


@router.post("/currency-verify", response_model=ScanResponse)
async def verify_currency(
    file: UploadFile = File(...),
    denomination: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Upload a currency note image for authenticity verification."""
    start = time.time()

    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}",
        )

    # Read file content
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum 10MB.",
        )

    # Create scan record
    scan = Scan(
        user_id=current_user.id,
        scan_type=ScanType.CURRENCY,
        status=ScanStatus.PROCESSING,
    )
    db.add(scan)
    await db.flush()

    try:
        analysis = await orchestrator.analyze_currency(
            image_data=file_content,
            denomination=denomination,
        )

        processing_time = (time.time() - start) * 1000

        result = ScanResult(
            scan_id=scan.id,
            confidence_score=analysis["confidence_score"],
            verdict=Verdict(analysis["verdict"]),
            summary=analysis["summary"],
            detailed_analysis=analysis.get("detailed_analysis"),
            feature_scores=analysis.get("feature_scores"),
            risk_factors=analysis.get("risk_factors"),
            recommendations=analysis.get("recommendations"),
            processing_time_ms=processing_time,
        )
        db.add(result)

        scan.status = ScanStatus.COMPLETED
        await db.flush()

        return ScanResponse(
            id=scan.id,
            scan_type=scan.scan_type.value,
            status=scan.status.value,
            created_at=scan.created_at,
            result=ScanResultResponse.model_validate(result),
        )

    except Exception as e:
        scan.status = ScanStatus.FAILED
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Currency analysis failed: {str(e)}",
        )


@router.post("/deepfake-image", response_model=ScanResponse)
async def analyze_deepfake_image(
    file: UploadFile = File(...),
    context: Optional[str] = Form(None),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Upload an image for deepfake detection analysis."""
    start = time.time()

    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}",
        )

    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum 10MB.",
        )

    scan = Scan(
        user_id=current_user.id,
        scan_type=ScanType.DEEPFAKE_IMAGE,
        status=ScanStatus.PROCESSING,
    )
    db.add(scan)
    await db.flush()

    try:
        analysis = await orchestrator.analyze_deepfake_image(
            image_data=file_content,
            context=context,
        )

        processing_time = (time.time() - start) * 1000

        result = ScanResult(
            scan_id=scan.id,
            confidence_score=analysis["confidence_score"],
            verdict=Verdict(analysis["verdict"]),
            summary=analysis["summary"],
            detailed_analysis=analysis.get("detailed_analysis"),
            feature_scores=analysis.get("feature_scores"),
            risk_factors=analysis.get("risk_factors"),
            recommendations=analysis.get("recommendations"),
            processing_time_ms=processing_time,
        )
        db.add(result)

        scan.status = ScanStatus.COMPLETED
        await db.flush()

        return ScanResponse(
            id=scan.id,
            scan_type=scan.scan_type.value,
            status=scan.status.value,
            created_at=scan.created_at,
            result=ScanResultResponse.model_validate(result),
        )

    except Exception as e:
        scan.status = ScanStatus.FAILED
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deepfake analysis failed: {str(e)}",
        )


@router.get("/history", response_model=ScanHistoryResponse)
async def get_scan_history(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    scan_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Get the current user's scan history."""
    query = select(Scan).where(Scan.user_id == current_user.id)
    count_query = select(func.count()).select_from(Scan).where(Scan.user_id == current_user.id)

    if scan_type:
        query = query.where(Scan.scan_type == ScanType(scan_type))
        count_query = count_query.where(Scan.scan_type == ScanType(scan_type))

    query = query.order_by(Scan.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    scans = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return ScanHistoryResponse(
        scans=[
            ScanResponse(
                id=s.id,
                scan_type=s.scan_type.value,
                status=s.status.value,
                created_at=s.created_at,
                result=ScanResultResponse.model_validate(s.result) if s.result else None,
            )
            for s in scans
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


# ── Scam Call/Digital Arrest Tactic Analysis ───────────
@router.post("/scam-call", response_model=ScanResponse)
async def analyze_scam_call(
    payload: ScamCallRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Analyze call transcript content for authority impersonation and digital arrest fraud tactics."""
    start = time.time()

    scan = Scan(
        user_id=current_user.id,
        scan_type=ScanType.SCAM_CALL,
        input_text=payload.transcript,
        status=ScanStatus.PROCESSING,
    )
    db.add(scan)
    await db.flush()

    try:
        analysis = await orchestrator.analyze_scam_text(
            text=payload.transcript,
            language=payload.language,
            context="call_transcript",
        )

        processing_time = (time.time() - start) * 1000

        result = ScanResult(
            scan_id=scan.id,
            confidence_score=analysis["confidence_score"],
            verdict=Verdict(analysis["verdict"]),
            summary=analysis["summary"],
            detailed_analysis=analysis.get("detailed_analysis"),
            feature_scores=analysis.get("feature_scores"),
            risk_factors=analysis.get("risk_factors"),
            recommendations=analysis.get("recommendations"),
            processing_time_ms=processing_time,
        )
        db.add(result)

        scan.status = ScanStatus.COMPLETED
        await db.flush()

        return ScanResponse(
            id=scan.id,
            scan_type=scan.scan_type.value,
            status=scan.status.value,
            created_at=scan.created_at,
            result=ScanResultResponse.model_validate(result),
        )

    except Exception as e:
        scan.status = ScanStatus.FAILED
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scam call analysis failed: {str(e)}",
        )


# ── Deepfake Audio/Voice Clone Forensics ───────────────
@router.post("/deepfake-audio", response_model=ScanResponse)
async def analyze_deepfake_audio(
    file: UploadFile = File(...),
    context: Optional[str] = Form(None),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Upload an audio file (wav/mp3/ogg) to analyze for AI voice cloning indicators."""
    start = time.time()

    allowed_types = {"audio/wav", "audio/mpeg", "audio/mp3", "audio/ogg", "audio/x-wav"}
    if file.content_type not in allowed_types and not file.filename.lower().endswith(('.wav', '.mp3', '.ogg', '.mpeg')):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid file type. Allowed: WAV, MP3, OGG, MPEG.",
        )

    file_content = await file.read()
    if len(file_content) > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum 15MB.",
        )

    scan = Scan(
        user_id=current_user.id,
        scan_type=ScanType.DEEPFAKE_AUDIO,
        status=ScanStatus.PROCESSING,
    )
    db.add(scan)
    await db.flush()

    try:
        analysis = await orchestrator.analyze_deepfake_audio(
            audio_data=file_content,
            context=context,
        )

        processing_time = (time.time() - start) * 1000

        result = ScanResult(
            scan_id=scan.id,
            confidence_score=analysis["confidence_score"],
            verdict=Verdict(analysis["verdict"]),
            summary=analysis["summary"],
            detailed_analysis=analysis.get("detailed_analysis"),
            feature_scores=analysis.get("feature_scores"),
            risk_factors=analysis.get("risk_factors"),
            recommendations=analysis.get("recommendations"),
            processing_time_ms=processing_time,
        )
        db.add(result)

        scan.status = ScanStatus.COMPLETED
        await db.flush()

        return ScanResponse(
            id=scan.id,
            scan_type=scan.scan_type.value,
            status=scan.status.value,
            created_at=scan.created_at,
            result=ScanResultResponse.model_validate(result),
        )

    except Exception as e:
        scan.status = ScanStatus.FAILED
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deepfake audio analysis failed: {str(e)}",
        )


# ── Citizen Shield - Live Threat Registry Verification ──
@router.get("/check-entity", response_model=CheckEntityResponse)
async def check_entity(
    query: str = Query(..., min_length=3),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Check a phone number, UPI ID, domain, email, or bank account against known blacklisted indicators & citizen reports."""
    import re
    normalized = query.strip().lower()

    if re.search(r"@\w+", normalized):
        entity_type = "upi" if any(p in normalized for p in ["upi", "ybl", "paytm", "ok", "apl", "axl"]) else "email"
    elif re.search(r"^\+?[\d\s-]{8,15}$", normalized.replace(" ", "")):
        entity_type = "phone"
    elif "." in normalized and not "@" in normalized:
        entity_type = "domain"
    elif normalized.isdigit() and len(normalized) >= 9:
        entity_type = "bank_account"
    else:
        entity_type = "unknown"

    intel_search = await db.execute(
        select(ThreatIntel)
        .where(
            ThreatIntel.is_active == True,
            (ThreatIntel.pattern_name.ilike(f"%{normalized}%") | 
             ThreatIntel.description.ilike(f"%{normalized}%") |
             ThreatIntel.region.ilike(f"%{normalized}%"))
        )
    )
    intel_match = intel_search.scalars().first()

    report_search = await db.execute(
        select(func.count(Report.id))
        .where(
            (Report.suspect_phone.ilike(f"%{normalized}%")) |
            (Report.suspect_account.ilike(f"%{normalized}%")) |
            (Report.suspect_name.ilike(f"%{normalized}%"))
        )
    )
    report_count = report_search.scalar() or 0

    matched_blacklist = intel_match is not None
    threat_score = 0.0
    reason = "No threat markers or citizen flags found."
    risk_level = "safe"
    blacklist_details = None

    if matched_blacklist:
        threat_score = intel_match.risk_score
        reason = f"Blacklisted indicator found (Pattern: {intel_match.pattern_name}). Description: {intel_match.description}"
        blacklist_details = {
            "id": intel_match.id,
            "threat_type": intel_match.threat_type.value,
            "pattern_name": intel_match.pattern_name,
            "description": intel_match.description,
            "region": intel_match.region,
            "risk_score": intel_match.risk_score,
            "occurrences": intel_match.occurrences,
        }
        if report_count > 0:
            threat_score = min(threat_score + 0.05 * report_count, 1.0)
    elif report_count > 0:
        threat_score = min(0.3 + 0.15 * report_count, 0.95)
        reason = f"Entity flagged in {report_count} citizen scam reports. Exercise caution."

    if threat_score >= 0.75:
        risk_level = "critical"
    elif threat_score >= 0.5:
        risk_level = "high_risk"
    elif threat_score >= 0.2:
        risk_level = "suspicious"
    else:
        risk_level = "safe"

    is_safe = risk_level == "safe"

    recs = []
    if risk_level in ["critical", "high_risk"]:
        recs.extend([
            "🚫 DO NOT initiate any bank transfer or UPI payment to this recipient",
            "📞 Block this contact to prevent phishing or social engineering attempts",
            "🛡️ Please report additional occurrence details on KAVACH AI reporting portal"
        ])
    elif risk_level == "suspicious":
        recs.extend([
            "⚠️ Request secondary verification details before proceeding",
            "🔍 Inspect the domain URL or phone prefix for spoofing indicators",
        ])
    else:
        recs.extend([
            "✅ Entity has clean records on the KAVACH database.",
            "💡 Continue remaining vigilant during digital exchanges."
        ])

    return CheckEntityResponse(
        query=query,
        entity_type=entity_type,
        is_safe=is_safe,
        risk_level=risk_level,
        threat_score=round(threat_score, 4),
        reason=reason,
        matched_blacklist=matched_blacklist,
        blacklist_details=blacklist_details,
        report_history_count=report_count,
        recommendations=recs,
    )


# ── Denomination Specifications Check ─────────────────
@router.get("/currency/features/{denomination}", response_model=DenominationFeaturesResponse)
async def get_currency_features(denomination: str):
    """Retrieve security feature checkpoints and design details for specific denominations."""
    db_features = {
        "100": {
            "dimensions": "66 mm × 142 mm",
            "primary_color": "Lavender",
            "obverse_features": [
                {"feature_name": "Mahatma Gandhi Watermark", "description": "Gandhi portrait in light-transmitting window on the right side window", "location_on_note": "Right side watermark window", "verification_method": "Hold against light"},
                {"feature_name": "Windowed Security Thread", "description": "Blue thread with inscriptions 'भारत' and 'RBI' showing color shift from green to blue", "location_on_note": "Center-left of obverse", "verification_method": "Tilt note by 45 degrees"},
                {"feature_name": "See-Through Register", "description": "Numeral 100 which looks unified when held against light source", "location_on_note": "Left portion of note", "verification_method": "Look through light"}
            ],
            "reverse_features": [
                {"feature_name": "Rani Ki Vav Motif", "description": "Detailed engraving showing Indian stepwell heritage site Rani Ki Vav", "location_on_note": "Center-reverse", "verification_method": "Visual check"},
                {"feature_name": "Swachh Bharat Logo", "description": "Clean India logo with spectacles and slogan 'एक कदम स्वच्छता की ओर'", "location_on_note": "Bottom-left reverse", "verification_method": "Visual check"}
            ]
        },
        "200": {
            "dimensions": "66 mm × 146 mm",
            "primary_color": "Bright Yellow",
            "obverse_features": [
                {"feature_name": "Mahatma Gandhi Portrait", "description": "Gandhi portrait watermark in light window", "location_on_note": "Right window", "verification_method": "Hold against light"},
                {"feature_name": "Color Shift Security Thread", "description": "Thread appearing green at first, shifts to blue upon tilt", "location_on_note": "Left center", "verification_method": "Tilt note visually"},
                {"feature_name": "Devanagari Numerals", "description": "Numeral 200 prominently displayed in Devanagari script", "location_on_note": "Top center", "verification_method": "Visual inspection"}
            ],
            "reverse_features": [
                {"feature_name": "Sanchi Stupa Motif", "description": "Historic Buddhist complex representation", "location_on_note": "Center-reverse", "verification_method": "Visual inspection"},
                {"feature_name": "Year of Printing", "description": "The year in which the note was printed", "location_on_note": "Left side", "verification_method": "Check year text"}
            ]
        },
        "500": {
            "dimensions": "66 mm × 150 mm",
            "primary_color": "Stone Grey",
            "obverse_features": [
                {"feature_name": "Latent Image", "description": "Latent image containing number 500 block visible under sharp angle", "location_on_note": "Below Gandhi portrait window", "verification_method": "Hold note horizontally at eye level"},
                {"feature_name": "Bleed Lines for Blinds", "description": "5 raised tactile bleed lines for visually impaired users", "location_on_note": "Left and right border borders", "verification_method": "Feel the raised ink"},
                {"feature_name": "Ashoka Pillar", "description": "National emblem emblem detail in raised intaglio print", "location_on_note": "Right side", "verification_method": "Touch and inspect"}
            ],
            "reverse_features": [
                {"feature_name": "Red Fort Motif", "description": "Iconic Indian historical monument Red Fort with Tricolor flag", "location_on_note": "Center reverse", "verification_method": "Visual inspection"},
                {"feature_name": "Swachh Bharat Slogan", "description": "Spec spectacles emblem print", "location_on_note": "Bottom left", "verification_method": "Visual inspection"}
            ]
        },
        "2000": {
            "dimensions": "66 mm × 166 mm",
            "primary_color": "Magenta",
            "obverse_features": [
                {"feature_name": "Micro-lettering", "description": "Micro letters stating 'RBI', '2000' and 'भारत'", "location_on_note": "In small printing bands", "verification_method": "Use magnifying glass"},
                {"feature_name": "Intaglio Gandhi Portrait", "description": "Gandhi portrait printed in raised ink", "location_on_note": "Main face", "verification_method": "Touch-feel test"}
            ],
            "reverse_features": [
                {"feature_name": "Mangalyaan Spacecraft", "description": "Motif of Mars Orbiter Mission showing scientific heritage logo", "location_on_note": "Center reverse", "verification_method": "Visual inspection"}
            ]
        }
    }

    if denomination not in db_features:
        raise HTTPException(status_code=404, detail="Denomination details not found. Supported: 100, 200, 500, 2000")

    data = db_features[denomination]
    return DenominationFeaturesResponse(
        denomination=denomination,
        dimensions=data["dimensions"],
        primary_color=data["primary_color"],
        obverse_features=[
            CurrencyFeatureInfo(
                feature_name=f["feature_name"],
                description=f["description"],
                location_on_note=f["location_on_note"],
                verification_method=f["verification_method"],
            )
            for f in data["obverse_features"]
        ],
        reverse_features=[
            CurrencyFeatureInfo(
                feature_name=f["feature_name"],
                description=f["description"],
                location_on_note=f["location_on_note"],
                verification_method=f["verification_method"],
            )
            for f in data["reverse_features"]
        ],
    )



# ── Threat Intelligence Feed ───────────────────────────
@router.get("/threat-intel")
async def get_threat_intel_list(
    threat_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve multi-source Threat Intelligence indicators feed."""
    query = select(ThreatIntel).where(ThreatIntel.is_active == True)
    count_query = select(func.count()).select_from(ThreatIntel).where(ThreatIntel.is_active == True)

    if threat_type:
        query = query.where(ThreatIntel.threat_type == ThreatType(threat_type))
        count_query = count_query.where(ThreatIntel.threat_type == ThreatType(threat_type))

    query = query.order_by(ThreatIntel.last_seen.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    threats = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return {
        "threats": [
            {
                "id": t.id,
                "threat_type": t.threat_type.value,
                "pattern_name": t.pattern_name,
                "description": t.description,
                "risk_score": t.risk_score,
                "occurrences": t.occurrences,
                "region": t.region,
                "source": t.source,
                "last_seen": t.last_seen,
            }
            for t in threats
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }

