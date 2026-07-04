# KAVACH AI — Backend API Reference Catalog

This catalog outlines every route, parameter, and authorization tier configured in the KAVACH AI FastAPI backend.

---

## ── 1. Root & Diagnostics ──────────────────────────────

### 📡 Server Health check
- **Endpoint**: `GET /health`
- **Auth**: None (Public)
- **Role Tier**: Universal
- **Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "ai_modules": [
    "scam_detector",
    "currency_detector",
    "deepfake_detector",
    "fraud_graph",
    "geospatial_intelligence"
  ]
}
```

---

## ── 2. Authentications (JWT) ─────────────────────────

### 👤 Citizen/Officer Registry
- **Endpoint**: `POST /api/v1/auth/register`
- **Payload**:
```json
{
  "email": "user@domain.com",
  "password": "SecurePassword123#",
  "full_name": "Rajesh Kumar",
  "phone": "+919876543210"
}
```
- **Response** (`201 Created`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "role": "citizen"
}
```

### 🔑 User Login / Authenticator
- **Endpoint**: `POST /api/v1/auth/login`
- **Payload**:
```json
{
  "email": "priya.sharma@gmail.com",
  "password": "Demo@2026"
}
```
- **Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "role": "citizen"
}
```

### 👤 Fetch Account Details
- **Endpoint**: `GET /api/v1/auth/me`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Response**:
```json
{
  "id": "ee0e021d-728f-4453-be48-0aba9703893d",
  "email": "priya.sharma@gmail.com",
  "full_name": "Priya Sharma",
  "phone": "+919876543210",
  "role": "citizen",
  "is_active": true,
  "is_verified": true,
  "created_at": "2026-07-04T12:00:00Z"
}
```

---

## ── 3. AI Safety Scans ─────────────────────────────────

### 💬 Text Scam Scan (SMS, Email, WA)
- **Endpoint**: `POST /api/v1/scans/scam-text`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Payload**:
```json
{
  "text": "Dear user, your phone number has won 25,00,000 INR from KBC. Send 10,000 INR bank transfer processing charges directly to this wallet address to claim.",
  "context": "whatsapp"
}
```
- **Response**:
```json
{
  "id": "bb0c021d-728f-4453-be48-0aba9703893a",
  "scan_type": "scam_text",
  "status": "completed",
  "created_at": "2026-07-04T12:05:00Z",
  "result": {
    "confidence_score": 0.957,
    "verdict": "suspicious",
    "summary": "High-risk lottery/cash award scam detected.",
    "detailed_analysis": {
      "has_urgency": false,
      "scam_phrases_found": ["won", "kbc", "lottery"],
      "threat_context": "whatsapp"
    },
    "risk_factors": ["Financial extraction patterns matching KBC scams"],
    "recommendations": ["Do not share banking information or transfer processing charges."],
    "processing_time_ms": 12.4
  }
}
```

### 🗣️ Call Transcript Scam Tactic analysis
- **Endpoint**: `POST /api/v1/scans/scam-call`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Payload**:
```json
{
  "transcript": "I am Customs officer at Cargo office Mumbai. We retrieved a package with MDMA drugs registered to your name.",
  "language": "en"
}
```
- **Response**:
```json
{
  "id": "cb0c021d-728f-4453-be48-0aba9703893b",
  "scan_type": "scam_call",
  "status": "completed",
  "created_at": "2026-07-04T12:06:00Z",
  "result": {
    "confidence_score": 0.884,
    "verdict": "suspicious",
    "summary": "Impersonation alert of Customs Officer alleging drug interception (Digital Arrest tactic).",
    "detailed_analysis": {
      "impersonation_keywords": ["customs", "officer"],
      "scam_category": "Digital Arrest Scam"
    },
    "risk_factors": ["Authority coercion", "Skype continuous surveillance coercion"],
    "recommendations": ["Hang up instantly. Law enforcement does not perform virtual arrests or custody over videocalls."],
    "processing_time_ms": 15.3
  }
}
```

### 🕵️ Entity Registry Risk Checker
- **Endpoint**: `GET /api/v1/scans/check-entity`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Query Params**:
  - `query=919876543210` (Phone, UPI ID, Domain URL, Email or Bank Account number)
- **Response**:
```json
{
  "entity": "919876543210",
  "is_blacklisted": true,
  "risk_score": 0.95,
  "reason": "Entity matched blacklisted indicator inside threat intelligence feed (Mule account / Spam caller registries)."
}
```

### 🛡️ Threat Intelligence Indicators Feed
- **Endpoint**: `GET /api/v1/scans/threat-intel`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Response**:
```json
{
  "items": [
    {
      "value": "electricity-power-delhi.com",
      "type": "domain",
      "risk_level": "critical",
      "reported_by": "CERT-In"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### 💵 Spec Security features Registry
- **Endpoint**: `GET /api/v1/scans/currency/features/{denomination}`
- **Auth**: None (Public)
- **Paths**: `{denomination}` values include: `10`, `20`, `50`, `100`, `200`, `500`.
- **Response**:
```json
{
  "denomination": "500",
  "features": [
    {
      "name": "Devenagari denomination numeral",
      "description": "₹500 visible in Devenagari font at bottom center."
    },
    {
      "name": "Color-shifting threat thread",
      "description": "Windowed security thread shifts from green to blue when shifted."
    }
  ]
}
```

---

## ── 4. Forensics Uploads (Multi-part Form) ────────────────

### 📸 Deepfake Image Integrity forensics
- **Endpoint**: `POST /api/v1/scans/deepfake-image`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Form Data**:
  - `file`: (Binary image file e.g., JPEG/PNG, limit <10MB)
- **Response**:
```json
{
  "id": "db0c021d-728f-4453-be48-0aba9703893c",
  "scan_type": "deepfake_image",
  "status": "completed",
  "created_at": "2026-07-04T12:08:00Z",
  "result": {
    "confidence_score": 0.814,
    "verdict": "suspicious",
    "summary": "Noise spectrum indicates high jpeg artifact manipulation, indicative of AI facial swapping.",
    "detailed_analysis": {
      "noise_variance": 0.082,
      "manipulation_confidence": 0.814
    },
    "processing_time_ms": 110.2
  }
}
```

### 🎙️ Deepfake Voice clone forensics
- **Endpoint**: `POST /api/v1/scans/deepfake-audio`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Form Data**:
  - `file`: (Binary audio file e.g., WAV/MP3, limit <15MB)
- **Response**:
```json
{
  "id": "db0c021d-728f-4453-be48-0aba9703893f",
  "scan_type": "deepfake_audio",
  "status": "completed",
  "created_at": "2026-07-04T12:09:00Z",
  "result": {
    "confidence_score": 0.74,
    "verdict": "suspicious",
    "summary": "High pitch stability with robotic gaps found, indicating potential text-to-speech cloning.",
    "detailed_analysis": {
      "pitch_variance": 0.009,
      "robotic_breaks": 3
    },
    "processing_time_ms": 140.5
  }
}
```

### 💵 Currency Authenticity Verification Image scan
- **Endpoint**: `POST /api/v1/scans/currency-verify`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Form Data**:
  - `file`: (Binary currency note image, JPEG/PNG)
  - `denomination`: "500"
- **Response**:
```json
{
  "id": "eb0c021d-728f-4453-be48-0aba9703893g",
  "scan_type": "currency_verify",
  "status": "completed",
  "created_at": "2026-07-04T12:10:00Z",
  "result": {
    "confidence_score": 0.85,
    "verdict": "safe",
    "summary": "Security elements (RBI alignment, watermarks, paper ratios) match the ₹500 standard configuration registry.",
    "detailed_analysis": {
      "color_match_ratio": 0.91,
      "edge_sharpness": 0.85,
      "aligned_watermarks": true
    },
    "processing_time_ms": 320.0
  }
}
```

---

## ── 5. Analytics (Dashboard/LEO portal) ──────────────────

### 🗺️ Geospatial incident hotspots
- **Endpoint**: `GET /api/v1/analytics/geospatial`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Response**:
```json
{
  "hotspots": [
    {
      "latitude": 19.076,
      "longitude": 72.8777,
      "density": 0.75,
      "cases_count": 12,
      "primary_crime_type": "UPI Fraud",
      "city": "Mumbai",
      "state": "Maharashtra"
    }
  ]
}
```

### 🕸️ Fraud Transaction Networks graph mapping
- **Endpoint**: `GET /api/v1/analytics/fraud-network`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Query Params**:
  - `centrality_threshold=0.01`
- **Response**:
```json
{
  "nodes": [
    {
      "id": "node_9876543210",
      "label": "9876543210",
      "type": "upi",
      "centrality": 0.124,
      "risk_score": 0.85,
      "metadata": {
        "reports_count": 5,
        "is_blacklisted": true
      }
    }
  ],
  "edges": [
    {
      "source": "node_9876543210",
      "target": "node_account_001",
      "amount": 250000,
      "timestamp": "2026-07-04T10:00:00Z",
      "risk_label": "High Velocity transfer"
    }
  ]
}
```

---

## ── 6. RAG Security Advisories ─────────────────────────

### 📚 RAG Advisory Query Search
- **Endpoint**: `POST /api/v1/rag/query`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Payload**:
```json
{
  "query": "What should I do if a fake customs officer demands money under digital arrest threat on Skype?"
}
```
- **Response**:
```json
{
  "query": "What should I do if a fake customs officer demands money under digital arrest threat on Skype?",
  "answer": "Per official guidelines from the **Ministry of Home Affairs (MHA) / National Cyber Crime Reporting Portal (NCRP)** regarding 'Explosion in Digital Arrest Scam Networks', please be advised that no government agency, court, or law enforcement division (CBI, Police, Customs, NCB, etc.) is legally authorized to execute 'digital custody' or 'digital arrest' over video applications such as Skype or Zoom. They will never demand deposits, online statement reviews, or personal password verifications.",
  "key_actions": [
    "Disconnect Skype or WhatsApp video caller immediately",
    "Do NOT transfer payment, cash bonds, or safety deposits under pressure",
    "Report incident details to Cyber Crime helpline by calling 1930",
    "File official logs on the national portal at cybercrime.gov.in"
  ],
  "retrieved_sources": [
    {
      "title": "Explosion in Digital Arrest Scam Networks",
      "source": "Ministry of Home Affairs (MHA) / National Cyber Crime Reporting Portal (NCRP)",
      "document_type": "Advisory",
      "relevance_score": 0.7189,
      "url": "https://cybercrime.gov.in/Webform/Advisory.aspx"
    }
  ]
}
```
