# 🛡️ KAVACH AI — Next-Gen Multi-Agent Cyber Fraud Intelligence & Defense Platform

**KAVACH AI** is a state-of-the-art multi-agent AI ecosystem designed to detect, analyze, and mitigate cyber fraud, financial scams, deepfake threats, and counterfeit currency. Built for citizens, law enforcement agencies (LEO), and financial analysts, KAVACH AI provides real-time threat intelligence, automated incident reporting, geospatial fraud analytics, and visual network graph analysis.

---

## ✨ Key Features & Capability Modules

### 1. 💬 Text Message & Email Parser
- **SMS / WhatsApp / Email Phishing Detection**: Detects lottery scams, fake bank KYC update alerts, electricity bill disconnection threats, and UPI phishing.
- **Explainable AI Verifiers**: Extracts suspicious URLs, phone numbers, threat contexts, urgency markers, and financial extraction patterns.

### 2. 🗣️ Call Transcript Scam Tactic Analyzer
- **Digital Arrest & Authority Impersonation Detector**: Identifies impersonation tactics (CBI, Customs, TRAI, Police) and coercion signatures in call transcripts.
- **Risk Breakdown**: Highlights high-pressure psychological manipulation phrases and provides instant actionable recommendations.

### 3. 🕵️ Entity Risk Registry & Threat Intel
- **Instant Entity Checker**: Cross-checks UPI IDs, phone numbers, domain URLs, bank account numbers, and email addresses against blacklists.
- **Live Threat Intelligence Feed**: Aggregates verified indicators of compromise (IoCs) reported by CERT-In and citizen crime reports.

### 4. 📸 Media Forensics (Deepfake & Counterfeit Detection)
- **Deepfake Audio & Image Scanner**: Analyzes audio and image files for synthesized speech signatures, spectral anomalies, and facial distortion artifacts.
- **Currency Security Spec Checker**: Verifies security features (watermarks, color-shifting ink, microtext, security threads) for Indian Rupee banknotes (₹10 to ₹2000).

### 5. 🗺️ Geospatial Analytics & Crime Heatmaps
- **Spatial Incident Mapping**: Maps cybercrime reports across Indian cities (Delhi, Mumbai, Bengaluru, Hyderabad, etc.) with severity indexing.
- **Law Enforcement Command View**: Enables police cells to identify regional scam clusters and prioritize high-risk investigation cases.

### 6. 🕸️ Fraud Network Centrality Graphs
- **Graph Analytics (NetworkX)**: Identifies key scam syndicate nodes (mule bank accounts, spoofed UPI IDs, scam call nodes) using eigenvector and degree centrality algorithms.
- **Visual Graph Explorer**: Dynamic graph visualization for investigating interconnected financial fraud networks.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | Python 3.10+, FastAPI, Uvicorn, Pydantic |
| **Database & ORM** | SQLite / PostgreSQL, SQLAlchemy (AsyncIO) |
| **Security & Auth** | JWT (JSON Web Tokens), Passlib (Bcrypt), OAuth2 Bearer |
| **Data Analysis & Graphing** | NetworkX, NumPy, HTTPX |
| **Frontend UI** | HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), Tailwind CSS, JavaScript (ES6+), FontAwesome Icons |

---

## 📁 Repository Structure

```
.
├── backend/
│   ├── app/
│   │   ├── ai/                 # Multi-agent AI scan engines & analytics
│   │   ├── api/                # FastAPI v1 endpoints & authentication routes
│   │   ├── core/               # Security, JWT tokens, & app configuration
│   │   ├── models/             # SQLAlchemy ORM database models
│   │   ├── schemas/            # Pydantic validation schemas
│   │   ├── database.py         # Database engine session management
│   │   ├── main.py             # FastAPI entrypoint application
│   │   └── seed.py             # Comprehensive demo data seeder script
│   ├── data/                   # ML datasets & scam pattern dictionaries
│   ├── ml/                     # ML training scripts & dataset generators
│   ├── backend_api.md          # Complete API Endpoint Catalog
│   ├── integration_guide.md    # Frontend-to-Backend Integration Manual
│   ├── requirements.txt        # Python dependency specifications
│   └── run_server.py           # Backend startup runner script
├── css/                        # Shared style assets
├── frontend/
│   ├── index.html              # Landing Page & Public Information Portal
│   ├── dashboard.html          # Interactive Multi-Agent Security Dashboard
│   ├── index.css               # Modern Landing Page Stylesheet
│   ├── dashboard.css           # Futuristic High-Tech Cyber Dashboard CSS
│   ├── app.js                  # Landing Page JS & Navigation Scripts
│   └── dashboard.js            # Dashboard API Integration & Canvas Renderer
└── README.md                   # Project Documentation
```

---

## 🚀 Getting Started & Local Setup

### Prerequisites
- **Python**: Version 3.10 or higher
- **Web Browser**: Chrome, Edge, Firefox, or Safari

---

### 1. Backend Setup

1. **Navigate to the backend folder**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Seed Demo Data**:
   Populate the database with realistic citizen reports, investigation cases, and threat intelligence indicators:
   ```bash
   python -m app.seed
   ```

5. **Start the Development Server**:
   ```bash
   python run_server.py
   ```
   *The FastAPI server will be live at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.*

---

### 2. Frontend Setup

1. Simply open `frontend/index.html` or `frontend/dashboard.html` directly in your web browser, or launch using VS Code **Live Server** at `http://127.0.0.1:5500`.

---

## 🔑 Demo Access Credentials

The database seeder initializes ready-to-use accounts for presentation:

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Citizen User** | `priya.sharma@gmail.com` | `Demo@2026` | Public Scans, Report Submission, Personal History |
| **Law Enforcement Officer** | `inspector.rajesh@cybercell.gov.in` | `Demo@2026` | Full Case Management, Heatmaps, Graph Analysis |
| **System Administrator** | `admin@kavach.ai` | `Admin@2026` | Global Threat Intel & System Configuration |

---

## 🛡️ License & Acknowledgments

Developed as part of the **KAVACH AI Cyber Security Hackathon**. Designed to protect digital citizens and empower law enforcement agencies across India.
