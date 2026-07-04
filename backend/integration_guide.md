# KAVACH AI — Frontend Integration Guide

This guide ensures proper configuration and execution flow for integrating a client-side frontend application with the frozen **KAVACH AI** backend service.

---

## 🚀 1. Local Server Configurations

Start the FastAPI application locally by configuring your shell environment:

### Executing python server
Run the following commands inside the backend project path:
```bash
# Activate virtual environment
venv\Scripts\activate

# Launch development server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🌐 2. CORS Allowance & Origins

By default, the backend limits connections to recognized origins inside `app/config.py`:
- `http://localhost:3000` (React/Next.js default)
- `http://localhost:5173` (Vite default)
- `http://127.0.0.1:5500` (Live Server extensions)

If your local server uses custom port alignments, configure them inside the `.env` settings block:
```ini
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:5173
```

---

## 🔑 3. Authentication & JWT Storage

### User Login & Token Retrieval
To access restricted APIs (Scans, Analytics, RAG), the frontend must fetch a JWT signature using `/api/v1/auth/login`.

Example fetch sequence:
```javascript
async function loginUser(email, password) {
  const response = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new Error(errorBody.detail || "Authentication Succeeded but failed payload query.");
  }

  const data = await response.json();
  
  // Save credentials securely in sessionStorage or localStorage
  localStorage.setItem("jwt_token", data.access_token);
  localStorage.setItem("user_role", data.role);
  
  return data;
}
```

### Attaching Authorization Headers
All secured routes (such as checking entities or executing RAG queries) demand a `Bearer` token inside the header map:
```javascript
const token = localStorage.getItem("jwt_token");

const headers = {
  "Authorization": `Bearer ${token}`,
  "Content-Type": "application/json"
};
```

---

## 📸 4. Media Uploads & Form-Data formatting

Endpoints handling image or audio uploads (such as deepfake scanning & currency validation) demand raw multipart form wrapping:

### Example File Upload Snippet (JavaScript)
```javascript
async function uploadDeepfakeImage(fileObject) {
  const token = localStorage.getItem("jwt_token");
  
  const formData = new FormData();
  formData.append("file", fileObject); // Field name must match "file" key in API

  const response = await fetch("http://127.0.0.1:8000/api/v1/scans/deepfake-image", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`
      // Note: Do NOT set Content-Type header manually here; 
      // the browser will automatically compute the multipart boundary setting.
    },
    body: formData
  });

  return await response.json();
}
```

---

## 🕸️ 5. Visualizing Network graphs & Maps

### Geospatial Analytics (`GET /api/v1/analytics/geospatial`)
- Returns a list of coordinate records mapping coordinates, density indices, and crime categories.
- Best mapped using React components linking **OpenStreetMap** (via `react-leaflet`) or standard Mapbox markers.

### Fraud Centrality Graphs (`GET /api/v1/analytics/fraud-network`)
- Returns node/edge schemas computed with NetworkX (eigenvector centrality).
- Map visually inside your canvas using **Vis.js**, **D3.js**, or visual canvas rendering engines to paint nodes (colored by `risk_score` parameter) and connecting arrow paths.
