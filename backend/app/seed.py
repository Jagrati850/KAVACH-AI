"""
KAVACH AI — Demo Data Seeder
Seeds the database with realistic demo data for hackathon presentation.
Run: python -m app.seed
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.database import async_session, init_db
from app.models.alert import Alert, AlertSeverity, AlertType, Notification
from app.models.case import Case, CaseNote, CasePriority, CaseStatus
from app.models.report import Report, ReportStatus, ReportType, Severity
from app.models.scan import Scan, ScanResult, ScanStatus, ScanType, Verdict
from app.models.threat import ThreatIntel, ThreatType
from app.models.transaction import Transaction, TransactionChannel
from app.models.user import User, UserRole


# ── India geo data for realistic locations ──────────────────
INDIAN_CITIES = [
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.076, "lon": 72.8777},
    {"city": "Delhi", "state": "Delhi", "lat": 28.7041, "lon": 77.1025},
    {"city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946},
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.385, "lon": 78.4867},
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707},
    {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lon": 88.3639},
    {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567},
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714},
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lon": 75.7873},
    {"city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lon": 80.9462},
    {"city": "Chandigarh", "state": "Punjab", "lat": 30.7333, "lon": 76.7794},
    {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lon": 77.4126},
    {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lon": 76.2673},
    {"city": "Guwahati", "state": "Assam", "lat": 26.1445, "lon": 91.7362},
    {"city": "Patna", "state": "Bihar", "lat": 25.6093, "lon": 85.1376},
    {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lon": 75.8577},
    {"city": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lon": 79.0882},
    {"city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lon": 83.2185},
    {"city": "Noida", "state": "Uttar Pradesh", "lat": 28.5355, "lon": 77.391},
    {"city": "Gurugram", "state": "Haryana", "lat": 28.4595, "lon": 77.0266},
]

# ── Realistic scam descriptions ─────────────────────────────
SCAM_REPORTS = [
    {
        "type": ReportType.DIGITAL_ARREST,
        "title": "Fake CBI officer demanded ₹5 lakh via video call",
        "description": "Received WhatsApp video call from person in police uniform claiming to be CBI officer. Showed fake warrant with my Aadhaar number. Said my bank account was used in money laundering. Demanded ₹5,00,000 to 'clear my name'. Kept me on call for 3 hours. I transferred ₹2,00,000 before realizing it was a scam.",
        "amount": 200000,
        "severity": Severity.CRITICAL,
    },
    {
        "type": ReportType.DIGITAL_ARREST,
        "title": "TRAI officer claiming SIM card linked to crime",
        "description": "Call from person claiming to be from TRAI saying my SIM card was involved in 14 illegal calls. Transferred to someone posing as Mumbai Police cyber cell. Showed fake police station on video. Asked to download specific app for 'verification'. Demanded ₹50,000 as security deposit.",
        "amount": 50000,
        "severity": Severity.CRITICAL,
    },
    {
        "type": ReportType.UPI_FRAUD,
        "title": "Fake UPI refund phishing attack",
        "description": "Received SMS saying UPI account will be blocked. Link redirected to fake bank website. Entered credentials. ₹35,000 deducted from account through multiple UPI transactions within 10 minutes.",
        "amount": 35000,
        "severity": Severity.HIGH,
    },
    {
        "type": ReportType.PHISHING,
        "title": "Fake KYC update email from SBI",
        "description": "Received email appearing to be from SBI asking to update KYC by clicking link. Website looked identical to SBI. After entering debit card details, ₹75,000 was withdrawn. Email sender address was sbi-kyc-update@gmail.com (not official).",
        "amount": 75000,
        "severity": Severity.HIGH,
    },
    {
        "type": ReportType.SCAM_CALL,
        "title": "Lottery/prize money scam via WhatsApp",
        "description": "WhatsApp message claiming I won ₹25 lakh in KBC lottery. Caller asked for ₹10,000 'processing fee'. After payment, demanded more for 'tax clearance'. Total lost: ₹45,000.",
        "amount": 45000,
        "severity": Severity.HIGH,
    },
    {
        "type": ReportType.COUNTERFEIT_CURRENCY,
        "title": "Counterfeit ₹500 notes received from ATM",
        "description": "Withdrew ₹10,000 from ATM near Market Road. 4 notes of ₹500 appeared different in texture and color-shifting ink was missing. Bank confirmed they are counterfeit. ATM surveillance footage collected.",
        "amount": 2000,
        "severity": Severity.MEDIUM,
    },
    {
        "type": ReportType.DEEPFAKE,
        "title": "Deepfake video used for extortion",
        "description": "Received deepfake video of myself in compromising situation. Demanded ₹2 lakh or video would be sent to contacts. Video appears to be generated using my social media photos. Filed complaint but scammer used anonymous VPN.",
        "amount": 200000,
        "severity": Severity.CRITICAL,
    },
    {
        "type": ReportType.IDENTITY_THEFT,
        "title": "Aadhaar used to open fake bank accounts",
        "description": "Discovered 3 bank accounts opened using my Aadhaar and PAN details in different states. Total ₹15 lakh laundered through these accounts. Have not shared documents with anyone. Suspect data leak from previous employer.",
        "amount": 1500000,
        "severity": Severity.CRITICAL,
    },
    {
        "type": ReportType.DIGITAL_ARREST,
        "title": "Customs department parcel interception scam",
        "description": "Called by person claiming parcel addressed to me was intercepted at Mumbai airport containing 5 passports and MDMA drugs. Transferred to fake NCB officer. Showed fake police station background on Skype. Demanded ₹3 lakh for bail. Kept on call for 6 hours.",
        "amount": 300000,
        "severity": Severity.CRITICAL,
    },
    {
        "type": ReportType.UPI_FRAUD,
        "title": "OLX seller reverse UPI scam",
        "description": "Listed phone for sale on OLX. Buyer sent QR code saying 'scan to receive payment'. After scanning and entering UPI PIN, ₹18,000 was deducted instead. Buyer blocked my number immediately.",
        "amount": 18000,
        "severity": Severity.MEDIUM,
    },
]


async def seed_database():
    """Seed the database with comprehensive demo data."""
    print("[SEED] KAVACH AI - Seeding demo data...")

    await init_db()

    async with async_session() as session:
        # ── 1. Create Users ──────────────────────────────
        users = {
            "citizen1": User(
                id=str(uuid.uuid4()),
                email="priya.sharma@gmail.com",
                full_name="Priya Sharma",
                password_hash=hash_password("Demo@2026"),
                phone="+919876543210",
                role=UserRole.CITIZEN,
                is_active=True,
                is_verified=True,
            ),
            "citizen2": User(
                id=str(uuid.uuid4()),
                email="rahul.verma@gmail.com",
                full_name="Rahul Verma",
                password_hash=hash_password("Demo@2026"),
                phone="+919876543211",
                role=UserRole.CITIZEN,
                is_active=True,
                is_verified=True,
            ),
            "citizen3": User(
                id=str(uuid.uuid4()),
                email="anita.gupta@gmail.com",
                full_name="Anita Gupta",
                password_hash=hash_password("Demo@2026"),
                phone="+919876543212",
                role=UserRole.CITIZEN,
                is_active=True,
                is_verified=True,
            ),
            "leo1": User(
                id=str(uuid.uuid4()),
                email="inspector.rajesh@cybercell.gov.in",
                full_name="Inspector Rajesh Kumar",
                password_hash=hash_password("Demo@2026"),
                phone="+919876543220",
                role=UserRole.LEO,
                organization="Cyber Crime Cell, Delhi Police",
                designation="Cyber Crime Inspector",
                is_active=True,
                is_verified=True,
            ),
            "leo2": User(
                id=str(uuid.uuid4()),
                email="dsp.meera@police.gov.in",
                full_name="DSP Meera Nair",
                password_hash=hash_password("Demo@2026"),
                phone="+919876543221",
                role=UserRole.LEO,
                organization="Kerala Police, Cyber Wing",
                designation="Deputy Superintendent",
                is_active=True,
                is_verified=True,
            ),
            "analyst1": User(
                id=str(uuid.uuid4()),
                email="vikram.shah@sbi.co.in",
                full_name="Vikram Shah",
                password_hash=hash_password("Demo@2026"),
                phone="+919876543230",
                role=UserRole.BANK_ANALYST,
                organization="State Bank of India",
                designation="Fraud Risk Analyst",
                is_active=True,
                is_verified=True,
            ),
            "admin": User(
                id=str(uuid.uuid4()),
                email="admin@kavach.ai",
                full_name="System Administrator",
                password_hash=hash_password("Admin@2026"),
                phone="+919876543200",
                role=UserRole.ADMIN,
                organization="KAVACH AI Platform",
                designation="System Administrator",
                is_active=True,
                is_verified=True,
            ),
        }

        for user in users.values():
            session.add(user)
        await session.flush()
        print(f"  ✅ Created {len(users)} users")

        # ── 2. Create Reports ────────────────────────────
        citizen_ids = [users["citizen1"].id, users["citizen2"].id, users["citizen3"].id]
        reports = []

        for i, scam_data in enumerate(SCAM_REPORTS):
            city_data = random.choice(INDIAN_CITIES)
            days_ago = random.randint(1, 30)
            report = Report(
                id=str(uuid.uuid4()),
                user_id=random.choice(citizen_ids),
                report_type=scam_data["type"],
                title=scam_data["title"],
                description=scam_data["description"],
                status=random.choice([
                    ReportStatus.SUBMITTED,
                    ReportStatus.UNDER_REVIEW,
                    ReportStatus.INVESTIGATING,
                    ReportStatus.RESOLVED,
                ]),
                severity=scam_data["severity"],
                suspect_phone=f"+91{random.randint(7000000000, 9999999999)}",
                amount_lost=scam_data["amount"],
                latitude=city_data["lat"] + random.uniform(-0.1, 0.1),
                longitude=city_data["lon"] + random.uniform(-0.1, 0.1),
                city=city_data["city"],
                state=city_data["state"],
                ai_threat_score=random.uniform(0.5, 0.98),
                created_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
            )
            session.add(report)
            reports.append(report)

        await session.flush()
        print(f"  ✅ Created {len(reports)} reports")

        # ── 3. Create Cases ──────────────────────────────
        case_count = 0
        for i, report in enumerate(reports[:6]):
            case = Case(
                id=str(uuid.uuid4()),
                case_number=f"KAV-2026-{str(i+1).zfill(4)}",
                report_id=report.id,
                assigned_to=random.choice([users["leo1"].id, users["leo2"].id]),
                status=random.choice([
                    CaseStatus.OPEN, CaseStatus.INVESTIGATING,
                    CaseStatus.EVIDENCE_COLLECTED, CaseStatus.RESOLVED,
                ]),
                priority=CasePriority.HIGH if report.severity in (Severity.CRITICAL, Severity.HIGH) else CasePriority.MEDIUM,
                title=f"Case: {report.title}",
                description=f"Investigation initiated based on citizen report. {report.description[:200]}",
                opened_at=report.created_at + timedelta(hours=random.randint(1, 24)),
            )
            session.add(case)
            case_count += 1

            # Add case notes
            note = CaseNote(
                case_id=case.id,
                author_id=users["leo1"].id,
                content="Initial review completed. Evidence collected and preserved. Initiating investigation.",
                note_type="update",
            )
            session.add(note)

        await session.flush()
        print(f"  ✅ Created {case_count} cases")

        # ── 4. Create Scans ─────────────────────────────
        scan_data = [
            {
                "type": ScanType.SCAM_TEXT,
                "text": "This is CBI calling. Your Aadhaar linked to money laundering. FIR registered. Transfer ₹50,000 now.",
                "verdict": Verdict.DANGEROUS,
                "score": 0.92,
            },
            {
                "type": ScanType.SCAM_TEXT,
                "text": "Dear customer, your SBI account KYC expired. Click to update: bit.ly/sbi-kyc",
                "verdict": Verdict.SUSPICIOUS,
                "score": 0.67,
            },
            {
                "type": ScanType.SCAM_TEXT,
                "text": "Hi, this is your delivery agent. Your Amazon package is at the lobby. Please collect.",
                "verdict": Verdict.SAFE,
                "score": 0.12,
            },
            {
                "type": ScanType.CURRENCY,
                "text": None,
                "verdict": Verdict.GENUINE,
                "score": 0.85,
            },
            {
                "type": ScanType.DEEPFAKE_IMAGE,
                "text": None,
                "verdict": Verdict.FAKE,
                "score": 0.88,
            },
        ]

        for sd in scan_data:
            scan = Scan(
                id=str(uuid.uuid4()),
                user_id=random.choice(citizen_ids),
                scan_type=sd["type"],
                input_text=sd["text"],
                status=ScanStatus.COMPLETED,
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 15)),
            )
            session.add(scan)
            await session.flush()

            result = ScanResult(
                scan_id=scan.id,
                confidence_score=sd["score"],
                verdict=sd["verdict"],
                summary=f"Analysis complete. Verdict: {sd['verdict'].value} (Confidence: {sd['score']*100:.0f}%)",
                detailed_analysis={"method": "multi_layer_analysis", "layers_triggered": random.randint(1, 5)},
                feature_scores={"authority": random.uniform(0, 1), "urgency": random.uniform(0, 1), "financial": random.uniform(0, 1)},
                risk_factors=["Pattern matched", "Known scam template"] if sd["score"] > 0.5 else [],
                recommendations=["Report to 1930", "Block sender"] if sd["score"] > 0.5 else ["Stay vigilant"],
                processing_time_ms=random.uniform(50, 500),
            )
            session.add(result)

        await session.flush()
        print(f"  ✅ Created {len(scan_data)} scans with results")

        # ── 5. Create Alerts ─────────────────────────────
        alert_data = [
            ("Digital arrest scam surge in Delhi NCR", AlertType.SCAM_DETECTED, AlertSeverity.CRITICAL, "Delhi", 28.7041, 77.1025),
            ("Counterfeit ₹500 notes detected in Mumbai", AlertType.COUNTERFEIT_DETECTED, AlertSeverity.HIGH, "Maharashtra", 19.076, 72.877),
            ("New phishing campaign targeting SBI customers", AlertType.SCAM_DETECTED, AlertSeverity.HIGH, "Pan India", 20.5937, 78.9629),
            ("Deepfake extortion ring busted in Bangalore", AlertType.DEEPFAKE_DETECTED, AlertSeverity.WARNING, "Karnataka", 12.9716, 77.594),
            ("UPI fraud pattern detected — OLX reverse payment scam", AlertType.HIGH_RISK_TRANSACTION, AlertSeverity.HIGH, "Maharashtra", 18.5204, 73.856),
            ("Fraud ring activity spiking in Gujarat", AlertType.FRAUD_RING_DETECTED, AlertSeverity.CRITICAL, "Gujarat", 23.0225, 72.571),
        ]

        for title, atype, sev, region, lat, lon in alert_data:
            alert = Alert(
                alert_type=atype,
                severity=sev,
                title=title,
                message=f"Automated alert: {title}. Immediate investigation recommended.",
                latitude=lat,
                longitude=lon,
                region=region,
                is_resolved=random.choice([True, False]),
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 10)),
            )
            session.add(alert)

        await session.flush()
        print(f"  ✅ Created {len(alert_data)} alerts")

        # ── 6. Create Transactions ───────────────────────
        sender_names = ["Rajesh Kumar", "Amit Shah", "Suresh Patel", "Priya Nair", "Deepak Malhotra"]
        receiver_names = ["Unknown Account", "Shell Corp A", "Vikram Joshi", "Cash Out Hub", "Crypto Exchange"]

        for i in range(30):
            is_suspicious = random.random() > 0.6
            txn = Transaction(
                transaction_ref=f"TXN{str(uuid.uuid4())[:8].upper()}",
                sender_id=f"ACC{random.randint(100000, 999999)}",
                sender_name=random.choice(sender_names),
                receiver_id=f"ACC{random.randint(100000, 999999)}",
                receiver_name=random.choice(receiver_names),
                amount=random.choice([
                    random.uniform(500, 5000),
                    random.uniform(10000, 50000),
                    random.uniform(50000, 500000),
                ]),
                channel=random.choice(list(TransactionChannel)),
                risk_score=random.uniform(0.6, 0.95) if is_suspicious else random.uniform(0.0, 0.3),
                is_flagged=is_suspicious,
                flagged_reason="Unusual pattern detected" if is_suspicious else None,
                sender_location=random.choice(INDIAN_CITIES)["city"],
                receiver_location=random.choice(INDIAN_CITIES)["city"],
                timestamp=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 720)),
            )
            session.add(txn)

        await session.flush()
        print("  ✅ Created 30 transactions")

        # ── 7. Create Threat Intel ───────────────────────
        threat_data = [
            (ThreatType.SCAM_PATTERN, "Digital Arrest — CBI Impersonation", "Caller poses as CBI officer, shows fake warrant, demands immediate transfer"),
            (ThreatType.SCAM_PATTERN, "TRAI SIM Block Scam", "Caller claims SIM will be blocked, transfers to fake police"),
            (ThreatType.SCAM_PATTERN, "Customs Parcel Interception", "Claims intercepted parcel with drugs, demands bail money"),
            (ThreatType.PHISHING_DOMAIN, "sbi-kyc-update.com", "Fake SBI KYC phishing domain targeting retail banking customers"),
            (ThreatType.FRAUD_NUMBER, "+91-8765-XXXXXX Series", "Series of numbers used in digital arrest scams across North India"),
            (ThreatType.COUNTERFEIT_SERIES, "₹500 Series AB-2024", "Counterfeit ₹500 notes with missing color-shifting ink detected in Maharashtra"),
        ]

        for ttype, name, desc in threat_data:
            threat = ThreatIntel(
                threat_type=ttype,
                pattern_name=name,
                description=desc,
                indicators={"keywords": name.split(), "risk": "high"},
                risk_score=random.uniform(0.6, 0.95),
                occurrences=random.randint(10, 500),
                region=random.choice(["Pan India", "North India", "Maharashtra", "South India"]),
                source="KAVACH AI Threat Intelligence",
                is_active=True,
            )
            session.add(threat)

        await session.flush()
        print(f"  ✅ Created {len(threat_data)} threat intelligence records")

        await session.commit()

    print("\n🎉 Demo data seeding complete!")
    print("\n📋 Demo Credentials:")
    print("  Citizen:  priya.sharma@gmail.com / Demo@2026")
    print("  LEO:      inspector.rajesh@cybercell.gov.in / Demo@2026")
    print("  Analyst:  vikram.shah@sbi.co.in / Demo@2026")
    print("  Admin:    admin@kavach.ai / Admin@2026")


if __name__ == "__main__":
    asyncio.run(seed_database())
