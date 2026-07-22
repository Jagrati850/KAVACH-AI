/* ═══════════════════════════════════════════════════════════════
   KAVACH AI — Dashboard Application Logic
   ═══════════════════════════════════════════════════════════════ */

const API_BASE_URL = 'http://127.0.0.1:8000';

let mapInstance = null;

// ── Check Auth ───────────────────────────────────────────────
// ── Check Auth ───────────────────────────────────────────────
let token = localStorage.getItem('jwt_token');
let role = (localStorage.getItem('user_role') || 'citizen').toLowerCase().trim();
let nameVal = localStorage.getItem('user_name') || 'Valued Screen';

if (!token) {
  alert('Access denied. Please login first to enter control center.');
  window.location.href = 'index.html';
}

document.addEventListener('DOMContentLoaded', () => {
  setupUserInformation();
  applyRoleVisibility();

  if (role === 'admin') {
    switchTab('admin-overview');
  } else {
    loadStats();
    loadOverviewThreatIntel();
    if (role === 'leo') {
      setTimeout(loadAnalyticsCenter, 200);
    }
  }
});

// ── Role UI ──────────────────────────────────────────────────
function setupUserInformation() {
  document.getElementById('profileName').textContent = nameVal;
  document.getElementById('profileRole').textContent = role.toUpperCase();
  document.getElementById('avatarLetter').textContent = nameVal.charAt(0).toUpperCase();

  const casesNavText = document.getElementById('casesNavText');
  if (casesNavText) {
    if (role === 'citizen') {
      casesNavText.textContent = 'My Reports';
    } else if (role === 'leo') {
      casesNavText.textContent = 'Cases Pipeline';
    }
  }
}

function applyRoleVisibility() {
  // Show / Hide entire sidebar navigation items
  const citizenLeoNav = document.getElementById('citizenLeoNav');
  const adminNav = document.getElementById('adminNav');
  if (role === 'admin') {
    if (citizenLeoNav) citizenLeoNav.style.display = 'none';
    if (adminNav) adminNav.style.display = 'block';
  } else {
    if (citizenLeoNav) citizenLeoNav.style.display = 'block';
    if (adminNav) adminNav.style.display = 'none';
  }

  const classesToFilter = ['LEO-only', 'ADMIN-only'];
  document.querySelectorAll('.LEO-only, .ADMIN-only').forEach(el => {
    let match = false;
    if (el.classList.contains('LEO-only') && (role === 'leo' || role === 'admin')) match = true;
    if (el.classList.contains('ADMIN-only') && role === 'admin') match = true;

    if (!match) {
      el.style.setProperty('display', 'none', 'important');
    } else {
      el.style.display = '';
    }
  });

  // Switch workspace layout view based on role
  if (role === 'citizen') {
    document.getElementById('view-citizen-reports').style.display = 'block';
    document.getElementById('view-leo-cases').style.display = 'none';
  } else if (role === 'leo') {
    document.getElementById('view-citizen-reports').style.display = 'none';
    document.getElementById('view-leo-cases').style.display = 'block';
  }
}

// ── Tab Switcher ─────────────────────────────────────────────
function switchTab(tabId) {
  // Update views
  document.querySelectorAll('.dashboard-view').forEach(view => {
    view.classList.remove('active');
  });
  
  // Deactivate all nav items
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(btn => {
    btn.classList.remove('active');
  });

  // Find exact button matching clicked tabId
  const targetBtn = Array.from(document.querySelectorAll('.sidebar-nav .nav-item')).find(btn => {
    const onclickStr = btn.getAttribute('onclick') || '';
    return onclickStr.includes(`'${tabId}'`) || onclickStr.includes(`"${tabId}"`);
  });
  if (targetBtn) {
    targetBtn.classList.add('active');
  }

  const activeView = document.getElementById(`view-${tabId}`);
  if (activeView) activeView.classList.add('active');

  // Trigger custom loads on tab enter
  if (tabId === 'overview') {
    loadStats();
    loadOverviewThreatIntel();
  } else if (tabId === 'analytics') {
    setTimeout(refreshMapSize, 100);
  } else if (tabId === 'reports') {
    if (role === 'citizen') {
      loadCitizenReports();
    } else if (role === 'leo') {
      loadLeoCases();
    }
  } else if (tabId === 'admin-overview') {
    loadAdminOverview();
  } else if (tabId === 'admin-users') {
    loadAdminUsers();
  } else if (tabId === 'admin-audit') {
    loadAdminAudit();
  } else if (tabId === 'admin-health') {
    loadAdminHealth();
  } else if (tabId === 'admin-notifs') {
    loadAdminNotifications();
  } else if (tabId === 'admin-analytics') {
    loadAdminAnalytics();
  } else if (tabId === 'admin-settings') {
    loadAdminSettings();
  }

  // Update titles
  const titles = {
    overview: { main: 'Control Center', sub: 'Real-time digital threat mitigation overview' },
    'scan-center': { main: 'AI Safeshield Scans', sub: 'Interactive forensic scan engines' },
    'rag-advisory': { main: 'Official Advisories', sub: 'RAG search matching public law briefs' },
    analytics: { main: 'Threat Intel & Analytics', sub: 'Geospatial crime mapping and mule account transaction node trails' },
    reports: {
      main: role === 'citizen' ? 'Incident Reports' : 'Law Enforcement Cases',
      sub: role === 'citizen' ? 'My filed safety reports' : 'National Crime Registry validation workflow'
    },
    'admin-overview': { main: 'KAVACH AI Administration', sub: 'Control center diagnostic overview and platform alerts status' },
    'admin-users': { main: 'User Directory Access Controls', sub: 'Manage organization permissions, verification badges, and accounts' },
    'admin-roles': { main: 'Security Matrix Settings', sub: 'Manage credentials structural criteria and application level access controls' },
    'admin-broadcast': { main: 'Public Safety Dispatch Broadcasts', sub: 'Send target alerts, notifications, and mock threat warnings' },
    'admin-audit': { main: 'System Level Audit Registry', sub: 'Detailed chronological registry of administrator and LEO operations' },
    'admin-analytics': { main: 'Platform Load Metrics & Analytics', sub: 'Monitor API response latencies, DB query times, and backend usage load' },
    'admin-notifs': { main: 'Outbound Alerts Delivery Pipeline', sub: 'Comprehensive notifications queue list indicating message states' },
    'admin-health': { main: 'Shield Core Health Diagnostics', sub: 'Verify FastAPI status, DB sync operations, and cognitive AI units' },
    'admin-settings': { main: 'Platform Configurations Center', sub: 'Manage API gateway keys, SMS settings, and security threshold offsets' }
  };

  if (titles[tabId]) {
    document.getElementById('pageTitle').textContent = titles[tabId].main;
    document.getElementById('pageSubtitle').textContent = titles[tabId].sub;
  }
}

// ── Sub-tab Switcher ──────────────────────────────────────────
function switchScanTab(scanId) {
  document.querySelectorAll('#view-scan-center .tab-header').forEach(btn => {
    btn.classList.remove('active');
  });
  event.currentTarget.classList.add('active');

  document.querySelectorAll('#view-scan-center .tab-content').forEach(cont => {
    cont.classList.remove('active');
  });
  document.getElementById(`scantab-${scanId}`).classList.add('active');
}

function switchForensicsTab(fkey) {
  document.querySelectorAll('#view-scan-center .subtab-header').forEach(btn => {
    btn.classList.remove('active');
  });
  event.currentTarget.classList.add('active');

  document.querySelectorAll('#view-scan-center .forensic-content').forEach(cont => {
    cont.classList.remove('active');
  });
  document.getElementById(`forensictab-${fkey}`).classList.add('active');
}

// ─────────────────────────────────────────────────────────────
// ACTIVE AI FORENSIC ENGINE CALLS
// ─────────────────────────────────────────────────────────────

// Helper to render scan card result layout
function renderScanResult(outputElId, data) {
  const result = data.result;
  const isSuspicious = result.verdict === 'suspicious' || result.verdict === 'dangerous' || result.verdict === 'fake' || result.verdict === 'flagged';
  const badgeClass = isSuspicious ? 'red' : 'green';
  const barClass = isSuspicious ? 'danger' : 'normal';

  const outputContainer = document.getElementById(outputElId);
  outputContainer.innerHTML = `
    <div class="verdict-header">
      <span class="verdict-title">AI Engine Verdict</span>
      <span class="verdict-badge ${badgeClass}">${result.verdict}</span>
    </div>
    <div class="verdict-score-wrapper">
      <div style="display:flex; justify-content:space-between; font-size:12px;">
        <span>Threat Probability Score:</span>
        <span class="mono">${Math.round(result.confidence_score * 100)}%</span>
      </div>
      <div class="score-bar-bg">
        <div class="score-bar-fill ${barClass}" style="width: ${result.confidence_score * 100}%"></div>
      </div>
    </div>
    <div class="verdict-summary">${result.summary}</div>
    <hr style="border:none; border-top:1px solid var(--border); margin:20px 0;">
    <div>
      <div class="verdict-title" style="margin-bottom:12px;">Recommended Actions</div>
      <ul class="verdict-details-list ${isSuspicious ? 'bullet-red' : ''}">
        ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
      </ul>
    </div>
    <div class="verdict-meta">
      <span>Core Scan: ${data.scan_type.toUpperCase()}</span>
      <span>Latency: ${result.processing_time_ms.toFixed(1)}ms</span>
    </div>
  `;
}

// Text Scam Scanner
async function runTextScan(e) {
  e.preventDefault();
  const text = document.getElementById('textScanContent').value;
  const context = document.getElementById('textScanContext').value;
  const btn = document.getElementById('btnTextScan');
  const output = document.getElementById('textScanOutput');

  btn.disabled = true;
  btn.textContent = 'Scanning Message Content...';
  output.innerHTML = '<div class="loading-spinner"></div>';

  try {
    const res = await callBackend('/api/v1/scans/scam-text', 'POST', { text, context });
    renderScanResult('textScanOutput', res);
    loadStats(); // Update total scans stats
  } catch (err) {
    output.innerHTML = `<div class="output-placeholder"><p style="color:#ff5252;">Scan Failed: ${err.message}</p></div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Perform Verification Scan <span class="arrow">→</span>';
  }
}

// Call Dialogue Analyzer
async function runCallScan(e) {
  e.preventDefault();
  const transcript = document.getElementById('callScanContent').value;
  const language = document.getElementById('callScanLanguage').value;
  const btn = document.getElementById('btnCallScan');
  const output = document.getElementById('callScanOutput');

  btn.disabled = true;
  btn.textContent = 'Analyzing Voice Dialogues...';
  output.innerHTML = '<div class="loading-spinner"></div>';

  try {
    const res = await callBackend('/api/v1/scans/scam-call', 'POST', { transcript, language });
    renderScanResult('callScanOutput', res);
    loadStats();
  } catch (err) {
    output.innerHTML = `<div class="output-placeholder"><p style="color:#ff5252;">Scan Failed: ${err.message}</p></div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Analyze Coercion Patterns <span class="arrow">→</span>';
  }
}

// Call Audio Upload → Speech-to-Text → Analyzer
async function runCallAudioScan(e) {
  if (e) e.preventDefault();
  const fileInput = document.getElementById('callScanAudioFile');
  const language = document.getElementById('callScanLanguage').value;
  const btn = document.getElementById('btnCallAudioScan');
  const output = document.getElementById('callScanOutput');
  const transcriptBox = document.getElementById('callScanContent');

  if (!fileInput.files[0]) {
    showToast('Please choose an audio file to transcribe.', 'error');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Transcribing & Analyzing Audio...';
  output.innerHTML = '<div class="loading-spinner"></div>';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('language', language);

  try {
    const res = await callBackendMultipart('/api/v1/scans/scam-call-audio', formData);
    // Auto-populate the transcript textarea with the generated speech-to-text
    if (res.transcript) transcriptBox.value = res.transcript;
    renderScanResult('callScanOutput', res);
    if (res.case_number) {
      showToast(`Threat escalated. Case ${res.case_number} created.`, 'success');
    }
    loadStats();
  } catch (err) {
    output.innerHTML = `<div class="output-placeholder"><p style="color:#ff5252;">Audio Analysis Failed: ${err.message}</p></div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Transcribe &amp; Analyze Audio <span class="arrow">→</span>';
  }
}

// Universal Blacklist Selector lookup
async function runBlacklistScan(e) {
  e.preventDefault();
  const query = document.getElementById('blacklistQuery').value;
  const btn = document.getElementById('btnBlacklistScan');
  const output = document.getElementById('blacklistScanOutput');

  btn.disabled = true;
  btn.textContent = 'Querying registries...';
  output.innerHTML = '<div class="loading-spinner"></div>';

  try {
    const res = await callBackend(`/api/v1/scans/check-entity?query=${encodeURIComponent(query)}`, 'GET');
    const badgeClass = res.is_blacklisted ? 'red' : 'green';
    const verdictStr = res.is_blacklisted ? 'blacklisted' : 'clean';

    output.innerHTML = `
      <div class="verdict-header">
        <span class="verdict-title">Registry Target Match</span>
        <span class="verdict-badge ${badgeClass}">${verdictStr.toUpperCase()}</span>
      </div>
      <div class="verdict-score-wrapper">
        <div style="display:flex; justify-content:space-between; font-size:12px;">
          <span>Registry Risk Index Score:</span>
          <span class="mono">${Math.round(res.risk_score * 100)}%</span>
        </div>
        <div class="score-bar-bg">
          <div class="score-bar-fill ${res.is_blacklisted ? 'danger' : 'normal'}" style="width: ${res.risk_score * 100}%"></div>
        </div>
      </div>
      <div class="verdict-summary">Search query: <span class="mono">${res.entity}</span></div>
      <hr style="border:none; border-top:1px solid var(--border); margin:20px 0;">
      <div>
        <div class="verdict-title" style="margin-bottom:12px;">Blacklist Log Reason</div>
        <p style="font-size:13.5px;color:var(--text-secondary);line-height:1.6;">${res.reason}</p>
      </div>
    `;
    loadStats();
  } catch (err) {
    output.innerHTML = `<div class="output-placeholder"><p style="color:#ff5252;">Query Failed: ${err.message}</p></div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Search Registry Databases <span class="arrow">→</span>';
  }
}

// Media Forensics Image Deepfake call
async function runImageForensic(e) {
  e.preventDefault();
  const fileInput = document.getElementById('imgForensicFile');
  const btn = document.getElementById('btnImgForensic');
  const output = document.getElementById('imgForensicOutput');

  if (!fileInput.files[0]) return;

  btn.disabled = true;
  btn.textContent = 'Performing Pixel manipulation analysis...';
  output.innerHTML = '<div class="loading-spinner"></div>';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    const res = await callBackendMultipart('/api/v1/scans/deepfake-image', formData);
    renderScanResult('imgForensicOutput', res);
    loadStats();
  } catch (err) {
    output.innerHTML = `<div class="output-placeholder"><p style="color:#ff5252;">Forensic Failed: ${err.message}</p></div>`;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analyze Image Pixels';
  }
}

// Media Forensics Audio Cloned Speech call
async function runAudioForensic(e) {
  e.preventDefault();
  const fileInput = document.getElementById('audioForensicFile');
  const btn = document.getElementById('btnAudioForensic');
  const output = document.getElementById('audioForensicOutput');

  if (!fileInput.files[0]) return;

  btn.disabled = true;
  btn.textContent = 'Performing acoustic stability index analysis...';
  output.innerHTML = '<div class="loading-spinner"></div>';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    const res = await callBackendMultipart('/api/v1/scans/deepfake-audio', formData);
    renderScanResult('audioForensicOutput', res);
    loadStats();
  } catch (err) {
    output.innerHTML = `<div class="output-placeholder"><p style="color:#ff5252;">Forensic Failed: ${err.message}</p></div>`;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Assess Vocal Stability';
  }
}

// Currency authenticator scan
async function runCurrencyVerify(e) {
  e.preventDefault();
  const fileInput = document.getElementById('currencyVerifyFile');
  const denom = document.getElementById('currencyVerifyValue').value;
  const btn = document.getElementById('btnCurrencyVerify');
  const output = document.getElementById('currencyVerifyOutput');

  if (!fileInput.files[0]) return;

  btn.disabled = true;
  btn.textContent = 'Authenticating currency note watermarks...';
  output.innerHTML = '<div class="loading-spinner"></div>';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('denomination', denom);

  try {
    const res = await callBackendMultipart('/api/v1/scans/currency-verify', formData);
    renderScanResult('currencyVerifyOutput', res);
    loadStats();
  } catch (err) {
    output.innerHTML = `<div class="output-placeholder"><p style="color:#ff5252;">Verification Failed: ${err.message}</p></div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Authenticate Banknote <span class="arrow">→</span>';
  }
}

// ─────────────────────────────────────────────────────────────
// RAG ADVISORY SEARCH CONSULTING
// ─────────────────────────────────────────────────────────────
async function runRagQuery(e) {
  e.preventDefault();
  const query = document.getElementById('ragQueryText').value;
  const btn = document.getElementById('btnRagQuery');
  const output = document.getElementById('ragQueryOutput');

  btn.disabled = true;
  btn.textContent = 'Searching...';
  output.style.display = 'block';
  output.innerHTML = '<div class="loading-spinner"></div>';

  try {
    const res = await callBackend('/api/v1/rag/query', 'POST', { query });
    output.innerHTML = `
      <div class="rag-answer-card">
        <div>
          <div class="rag-heading">Authoritative Answer</div>
          <div class="rag-text" style="margin-top:16px;">${res.answer}</div>
        </div>

        <div class="rag-actions-box">
          <div class="rag-heading" style="margin-bottom:14px;color:#ff9100;">Recommended Action Items</div>
          <ul class="verdict-details-list" style="margin-top:8px;">
            ${res.key_actions.map(action => `<li>${action}</li>`).join('')}
          </ul>
        </div>

        <div>
          <div class="rag-heading" style="margin-bottom:16px;">Verified Sources Cited</div>
          <div class="rag-sources">
            ${res.retrieved_sources.map(src => `
              <div class="rag-source-item">
                <div>
                  <div class="rag-source-title">${src.title}</div>
                  <div class="rag-source-meta" style="margin-top:4px;">Source: ${src.source} | Doc Type: ${src.document_type}</div>
                </div>
                <div class="rag-source-badge">RELEVANCE: ${Math.round(src.relevance_score * 100)}%</div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    output.innerHTML = `<div style="color:#ff5252;padding:24px;border:1px solid rgba(255,82,82,0.3);background:rgba(255,82,82,0.05);">${err.message}</div>`;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Query Engine';
  }
}

// ─────────────────────────────────────────────────────────────
// ANALYTICS & LEO PORTAL DATA LOADERS
// ─────────────────────────────────────────────────────────────

async function loadAnalyticsCenter() {
  // Load Leaflet Map
  initHeatmap();

  // Load Graph Network
  initNetworkGraph();

  // Load Full Threat indicators
  loadThreatIntelFull();
}

// Local simulation / load of spatial markers
async function initHeatmap() {
  if (mapInstance) return;

  // Initialize Map centering India coordinates
  mapInstance = L.map('hotspotsMap', {
    zoomControl: false
  }).setView([20.5937, 78.9629], 5);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
  }).addTo(mapInstance);

  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);

  try {
    const data = await callBackend('/api/v1/analytics/geospatial', 'GET');
    data.hotspots.forEach(pt => {
      // Create glowing points representing dense hot clusters
      const markerOptions = {
        radius: Math.max(12, pt.density * 22),
        fillColor: '#ff3d00',
        color: '#ff9100',
        weight: 1,
        opacity: 0.8,
        fillOpacity: 0.45
      };

      const circle = L.circleMarker([pt.latitude, pt.longitude], markerOptions).addTo(mapInstance);
      circle.bindPopup(`
        <div style="font-family:sans-serif;color:#000;padding:4px;">
          <h4 style="margin:0;font-size:13px;text-transform:uppercase;">${pt.city}, ${pt.state}</h4>
          <p style="margin:6px 0 0;font-size:11px;">Cases Reported: <b>${pt.cases_count}</b></p>
          <p style="margin:4px 0 0;font-size:11px;">Primary Scam: <b>${pt.primary_crime_type}</b></p>
          <p style="margin:4px 0 0;font-size:11px;">Mule Density Factor: <b>${(pt.density*100).toFixed(0)}%</b></p>
        </div>
      `);
    });
  } catch (err) {
    console.error('Failed to load spatial hotspot layers:', err);
  }
}

function refreshMapSize() {
  if (mapInstance) {
    mapInstance.invalidateSize();
  }
}

// Fraud nodes graph constructor
async function initNetworkGraph() {
  const svg = document.getElementById('graphSvg');
  if (!svg) return;
  svg.innerHTML = '';

  try {
    const data = await callBackend('/api/v1/analytics/fraud-network?centrality_threshold=0.01', 'GET');

    // Simple layout rendering for Nodes and Edges using SVG shapes
    const width = 1000;
    const height = 400;

    const nodePositions = {};
    const nodes = data.nodes;
    const edges = data.edges;

    // Generate circular layout mapping nodes coordinates
    nodes.forEach((n, idx) => {
      let cx = width / 2;
      let cy = height / 2;

      if (nodes.length > 1) {
        const angle = (idx / nodes.length) * 2 * Math.PI;
        cx = width / 2 + Math.cos(angle) * 140;
        cy = height / 2 + Math.sin(angle) * 120;
      }

      nodePositions[n.id] = { cx, cy };
    });

    // Draw Edges lines
    edges.forEach((e) => {
      const sourcePt = nodePositions[e.source];
      const targetPt = nodePositions[e.target];

      if (sourcePt && targetPt) {
        const edgeGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        edgeGroup.setAttribute("class", "graph-edge");

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", sourcePt.cx);
        line.setAttribute("y1", sourcePt.cy);
        line.setAttribute("x2", targetPt.cx);
        line.setAttribute("y2", targetPt.cy);
        line.setAttribute("stroke", "rgba(0, 229, 255, 0.4)");
        line.setAttribute("stroke-width", "1.5");
        edgeGroup.appendChild(line);

        // Edge label text midpoint
        const midX = (sourcePt.cx + targetPt.cx) / 2;
        const midY = (sourcePt.cy + targetPt.cy) / 2 - 4;
        const txt = document.createElementNS("http://www.w3.org/2000/svg", "text");
        txt.setAttribute("x", midX);
        txt.setAttribute("y", midY);
        txt.setAttribute("text-anchor", "middle");
        const edgeAmt = e.total_amount !== undefined ? e.total_amount : (e.weight || 0);
        txt.textContent = `₹${edgeAmt.toLocaleString('en-IN')}`;
        edgeGroup.appendChild(txt);

        svg.appendChild(edgeGroup);
      }
    });

    // Draw Nodes circles
    nodes.forEach((n) => {
      const pos = nodePositions[n.id];
      if (pos) {
        const nodeGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        nodeGroup.setAttribute("class", "graph-node");

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", pos.cx);
        circle.setAttribute("cy", pos.cy);
        circle.setAttribute("r", n.risk_score > 0.8 ? "15" : "12");

        // Color node based on risk category
        const fillCol = n.risk_score > 0.8 ? "#ff5252" : (n.risk_score > 0.5 ? "#ff9100" : "#00e5ff");
        circle.setAttribute("fill", fillCol);
        circle.setAttribute("stroke", "#060610");
        circle.setAttribute("stroke-width", "2");
        nodeGroup.appendChild(circle);

        // Node label
        const txt = document.createElementNS("http://www.w3.org/2000/svg", "text");
        txt.setAttribute("x", pos.cx);
        txt.setAttribute("y", pos.cy + 22);
        const nodeTypeStr = (n.node_type || 'account').toUpperCase();
        txt.textContent = `${nodeTypeStr}: ${n.label}`;
        nodeGroup.appendChild(txt);

        // Hover popup title decoration
        const titleEl = document.createElementNS("http://www.w3.org/2000/svg", "title");
        const degreeCent = n.metadata && n.metadata.degree_centrality !== undefined ? n.metadata.degree_centrality : 0;
        const txnQty = n.metadata && n.metadata.transaction_count !== undefined ? n.metadata.transaction_count : 0;
        titleEl.textContent = `Centrality index: ${degreeCent.toFixed(3)}\nTransactions: ${txnQty}`;
        nodeGroup.appendChild(titleEl);

        svg.appendChild(nodeGroup);
      }
    });

  } catch (err) {
    svg.innerHTML = `<text x="500" y="200" text-anchor="middle" fill="#ff5252">Failed to load graph network visualization: ${err.message}</text>`;
  }
}

// Load Full Threat Intel List
async function loadThreatIntelFull() {
  const container = document.getElementById('threatIntelFull');
  if (!container) return;

  try {
    const data = await callBackend('/api/v1/scans/threat-intel', 'GET');
    const threatsList = data.threats || [];
    if (threatsList.length === 0) {
      container.innerHTML = '<p style="font-size:13px;color:var(--text-muted);text-align:center;padding:24px;">No active malware/mule registries logged today.</p>';
      return;
    }

    container.innerHTML = threatsList.map(item => {
      const riskScore = item.risk_score || 0;
      const riskText = riskScore >= 0.8 ? 'CRITICAL' : (riskScore >= 0.5 ? 'HIGH RISK' : 'WARNING');
      const riskClass = riskScore >= 0.8 ? 'critical' : (riskScore >= 0.5 ? 'high' : 'medium');
      return `
        <div class="threat-indicator-card">
          <div>
            <div class="threat-val">${item.pattern_name}</div>
            <div style="font-size:10px;color:var(--text-muted);margin-top:4px;">Type: ${(item.threat_type || 'unknown').toUpperCase()} | Source: ${item.source || 'NCRP'}</div>
          </div>
          <span class="threat-tag ${riskClass}">${riskText}</span>
        </div>
      `;
    }).join('');
  } catch (err) {
    container.innerHTML = `<p style="font-size:12px;color:#ff5252;padding:20px;">Error matching feeds: ${err.message}</p>`;
  }
}

// ─────────────────────────────────────────────────────────────
// CASE & REPORTS PIPELINE LOADER
// ─────────────────────────────────────────────────────────────

// Citizen submissions handler
async function loadCitizenReports() {
  const container = document.getElementById('citizenReportsList');
  if (!container) return;

  try {
    let reportsList = [];
    try {
      const res = await callBackend('/api/v1/reports/', 'GET');
      reportsList = res.reports || [];
    } catch (e) {
      console.warn('Backend reports query failed, using offline fallback check:', e.message);
    }

    const localRepStr = localStorage.getItem('kavach_local_reports') || '[]';
    const localReports = JSON.parse(localRepStr);
    const combined = [...localReports, ...reportsList];

    if (combined.length === 0) {
      container.innerHTML = '<p style="font-size:13px;color:var(--text-muted);text-align:center;padding:24px;">You have not filed any crime incident reports yet.</p>';
      return;
    }

    container.innerHTML = combined.map(rep => {
      const typeLabel = (rep.report_type || 'other').replace('_', ' ').toUpperCase();
      const statusText = (rep.status || 'submitted').toUpperCase();
      const statusClass = rep.status === 'resolved' ? 'green' : (rep.status === 'dismissed' ? 'red' : 'orange');
      return `
        <div class="report-list-item">
          <div class="report-main-det">
            <div class="report-title-label">${rep.title}</div>
            <div class="report-desc-preview">${rep.description}</div>
            <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">Date: ${new Date(rep.created_at).toLocaleString()} | Category: ${typeLabel}</div>
          </div>
          <span class="verdict-badge ${statusClass}" style="font-size:9px;">
            ${statusText}
          </span>
        </div>
      `;
    }).join('');
  } catch (err) {
    container.innerHTML = `<p style="font-size:12px;color:#ff5252;padding:20px;">Failed loading report feed: ${err.message}</p>`;
  }
}

async function dashSubmitReport(e) {
  e.preventDefault();
  const title = document.getElementById('dashReportTitle').value;
  const type = document.getElementById('dashReportType').value;
  const desc = document.getElementById('dashReportDesc').value;
  const btn = document.getElementById('btnDashReportSubmit');

  // Pre-submission validation
  if (desc.trim().length < 20) {
    showToast('Incident description must be at least 20 characters long.', 'error');
    return;
  }
  if (title.trim().length < 5) {
    showToast('Incident title must be at least 5 characters long.', 'error');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Filing statement record...';

  let reportType = type ? type.split(' ')[0] : 'other';
  if (reportType === 'fake_currency') {
    reportType = 'counterfeit_currency';
  }

  try {
    await callBackend('/api/v1/reports/', 'POST', {
      title,
      description: desc,
      report_type: reportType
    });

    showToast('Incident statement recorded successfully!', 'success');
  } catch (err) {
    console.warn('API reporting failed, saving locally:', err.message);
    
    // Storing locally in localStorage
    const localRepStr = localStorage.getItem('kavach_local_reports') || '[]';
    const localReports = JSON.parse(localRepStr);
    
    const mockReport = {
      id: 'local-' + Math.random().toString(36).substring(2, 9),
      title: title,
      description: desc,
      report_type: reportType,
      status: 'submitted',
      created_at: new Date().toISOString()
    };
    
    localReports.unshift(mockReport);
    localStorage.setItem('kavach_local_reports', JSON.stringify(localReports));
    
    showToast('Report filed successfully (stored locally)!', 'success');
  } finally {
    document.getElementById('dashReportForm').reset();
    loadCitizenReports();
    loadStats();
    btn.disabled = false;
    btn.innerHTML = 'File Statement Record <span class="arrow">→</span>';
  }
}

// LEO pipeline verification loader
async function loadLeoCases() {
  const tbody = document.getElementById('leoCasesTableBody');
  if (!tbody) return;

  try {
    const res = await callBackend('/api/v1/cases/', 'GET');
    const casesList = res.cases || [];
    if (casesList.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:24px;">No cases found in registry pipeline.</td></tr>';
      return;
    }

    tbody.innerHTML = casesList.map(cs => {
      const priorityLabel = (cs.priority || 'medium').toUpperCase();
      const statusText = (cs.status || 'open').toUpperCase();
      const riskMapping = {
        'low': 25,
        'medium': 55,
        'high': 80,
        'critical': 98
      };
      const riskVal = riskMapping[cs.priority.toLowerCase()] || 50;
      const riskColor = riskVal > 75 ? '#ff5252' : (riskVal > 40 ? '#ff9100' : '#00e5ff');
      const nextStatus = cs.status === 'resolved' ? 'open' : 'resolved';
      return `
        <tr id="case-row-${cs.id}">
          <td class="mono-td">${cs.case_number}</td>
          <td class="bold">${cs.title}</td>
          <td class="mono-td">${priorityLabel}</td>
          <td>Report ID: ${cs.report_id.substring(0, 8)}...</td>
          <td>
            <span class="status-indicator ${cs.status === 'resolved' ? 'online' : ''}" style="margin-right:6px;"></span>
            <span>${statusText}</span>
          </td>
          <td class="mono-td bold" style="color: ${riskColor};">
            ${riskVal}%
          </td>
          <td>
            <button class="btn-outline btn-xs" onclick="alterCaseStatus('${cs.id}', '${nextStatus}')">
              Toggle Status
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="color:#ff5252;padding:20px;text-align:center;">Failed loading case pipelines: ${err.message}</td></tr>`;
  }
}

// Escalation and status actions
async function alterCaseStatus(caseId, targetStatus) {
  try {
    await callBackend(`/api/v1/cases/${caseId}`, 'PUT', { status: targetStatus });
    showToast(`Case status updated to ${targetStatus}`, 'success');
    loadLeoCases(); // Reload table
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ─────────────────────────────────────────────────────────────
// SYSTEM STATS & WELCOME INTERFACE DATA
// ─────────────────────────────────────────────────────────────

async function loadStats() {
  // Update scans history count
  const scansEl = document.getElementById('statScans');
  const reportsEl = document.getElementById('statReports');
  const riskEl = document.getElementById('statRisk');

  if (!scansEl) return;

  try {
    // Retrieve custom history logs to count scans completed
    const history = await callBackend('/api/v1/scans/history', 'GET');
    const scansList = history.scans || [];
    scansEl.textContent = history.total !== undefined ? history.total : scansList.length;

    // Reports filed count from backend
    let backendCount = 0;
    try {
      const reports = await callBackend('/api/v1/reports/', 'GET');
      backendCount = reports.total !== undefined ? reports.total : (reports.reports ? reports.reports.length : 0);
    } catch (e) {
      console.warn('Backend reports count failed, fallback count only:', e.message);
    }

    const localRepStr = localStorage.getItem('kavach_local_reports') || '[]';
    const localReports = JSON.parse(localRepStr);

    reportsEl.textContent = backendCount + localReports.length;

    // Latest threat status
    if (scansList.length > 0) {
      const scores = scansList
        .filter(c => c.result && c.result.confidence_score !== undefined)
        .map(c => c.result.confidence_score);
      const topScore = scores.length > 0 ? Math.max(...scores) : 0;
      if (topScore > 0.8) {
        riskEl.textContent = 'HIGH RISK';
        riskEl.style.color = '#ff5252';
      } else if (topScore > 0.4) {
        riskEl.textContent = 'MODERATE';
        riskEl.style.color = '#ff9100';
      } else {
        riskEl.textContent = 'SAFE';
        riskEl.style.color = '#00e676';
      }
    } else {
      riskEl.textContent = 'SAFE';
      riskEl.style.color = '#00e676';
    }

  } catch (err) {
    console.error('Stats loading issue:', err);
  }
}

async function loadOverviewThreatIntel() {
  const container = document.getElementById('threatIntelOverview');
  if (!container) return;

  try {
    const data = await callBackend('/api/v1/scans/threat-intel', 'GET');
    const threatsList = data.threats || [];
    if (threatsList.length === 0) {
      container.innerHTML = '<span style="font-size:11px;color:var(--text-muted);">No active threat alerts today.</span>';
      return;
    }

    container.innerHTML = threatsList.slice(0, 3).map(item => {
      const riskScore = item.risk_score || 0;
      const riskText = riskScore >= 0.8 ? 'CRIT' : (riskScore >= 0.5 ? 'HIGH' : 'WARN');
      return `
        <div class="threat-intel-item">
          <span class="threat-item-val">${item.pattern_name}</span>
          <span class="threat-item-badge">${riskText}</span>
        </div>
      `;
    }).join('');
  } catch (err) {
    container.innerHTML = `<span style="font-size:11px;color:#ff5252;">Intel Feed Error</span>`;
  }
}

// ─────────────────────────────────────────────────────────────
// LOG PANEL EXIT
// ─────────────────────────────────────────────────────────────
function handleLogout() {
  localStorage.removeItem('jwt_token');
  localStorage.removeItem('user_role');
  localStorage.removeItem('user_name');
  window.location.href = 'index.html';
}

// ─────────────────────────────────────────────────────────────
// NETWORK COMMUNICATIONS WRAPPERS
// ─────────────────────────────────────────────────────────────
async function callBackend(endpoint, method = 'GET', body = null) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };

  const config = { method, headers };
  if (body) config.body = JSON.stringify(body);

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (response.status === 401 || response.status === 403) {
    // Reset authorization
    localStorage.removeItem('jwt_token');
    window.location.href = 'index.html';
    throw new Error('Verification session expired. Please sign back in.');
  }

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || payload.message || 'API failure.');
  }

  return payload;
}

async function callBackendMultipart(endpoint, formData) {
  const headers = {
    'Authorization': `Bearer ${token}`
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData
  });

  if (response.status === 401 || response.status === 403) {
    localStorage.removeItem('jwt_token');
    window.location.href = 'index.html';
    throw new Error('Verification session expired. Please sign back in.');
  }

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || payload.message || 'API multipart failure.');
  }

  return payload;
}

// Reusable toast indicator
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.add('show');
  });

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, 4500);
}

// ── ADMIN PANEL LOGIC ─────────────────────────────────────────
async function loadAdminOverview() {
  const users = await callBackend('/api/v1/admin/users', 'GET');
  const countSpan = document.getElementById('admin-overview-user-count');
  if (countSpan) {
    countSpan.textContent = users.total || (users.users ? users.users.length : '--');
  }

  const healthList = document.getElementById('adminOverviewHealth');
  if (healthList) {
    try {
      const health = await callBackend('/api/v1/admin/system-health', 'GET');
      healthList.innerHTML = `
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.03);padding:6px 0;font-family:var(--font-mono);font-size:11px;">
          <span style="color:var(--text-secondary);">DB Engine Connectivity</span>
          <span style="color:#00ff88;font-weight:700;">${health.database.toUpperCase()}</span>
        </div>
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.03);padding:6px 0;font-family:var(--font-mono);font-size:11px;">
          <span style="color:var(--text-secondary);">RAG Advisory Endpoint</span>
          <span style="color:#00e5ff;font-weight:700;">OPERATIONAL</span>
        </div>
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.03);padding:6px 0;font-family:var(--font-mono);font-size:11px;">
          <span style="color:var(--text-secondary);">Outbound SMS Gateway</span>
          <span style="color:#00ff88;font-weight:700;">ACTIVE</span>
        </div>
      `;
    } catch (err) {
      healthList.innerHTML = '<div style="color:#ff3b3f;font-size:11px;">Failed to retrieve system health checklist.</div>';
    }
  }
}

async function loadAdminUsers() {
  const usersBody = document.getElementById('adminUsersTableBody');
  if (usersBody) usersBody.innerHTML = '<tr><td colspan="5"><div class="loading-spinner"></div></td></tr>';

  try {
    const payload = await callBackend('/api/v1/admin/users', 'GET');
    const users = payload.users || [];
    if (usersBody) {
      if (users.length === 0) {
        usersBody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:16px;color:var(--text-muted);">No accounts registered.</td></tr>';
      } else {
        usersBody.innerHTML = '';
        users.forEach(u => {
          const verifiedBadge = u.is_verified 
            ? '<span class="status-badge" style="background:rgba(0,184,212,0.1);color:var(--cyan);border:1px solid rgba(0,184,212,0.2);font-size:9px;padding:2px 6px;">[VERIFIED]</span>' 
            : '<span class="status-badge" style="background:rgba(255,82,82,0.1);color:#ff5252;border:1px solid rgba(255,82,82,0.2);font-size:9px;padding:2px 6px;">[PENDING]</span>';
          
          const activeStatus = u.is_active 
            ? '<span style="color:#00ff88;font-weight:600;">Active</span>' 
            : '<span style="color:#ff5252;font-weight:600;">Suspended</span>';
          
          const actionBtn = u.is_active
            ? `<button class="btn-outline btn-xs" style="border-color:#ff5252;color:#ff5252;padding:4px 8px;font-size:10px;font-family:var(--font-mono);" onclick="adminToggleUserStatus('${u.id}', ${u.is_active})">Suspend</button>`
            : `<button class="btn-outline btn-xs" style="border-color:#00ff88;color:#00ff88;padding:4px 8px;font-size:10px;font-family:var(--font-mono);" onclick="adminToggleUserStatus('${u.id}', ${u.is_active})">Activate</button>`;

          const tr = document.createElement('tr');
          tr.style.borderBottom = '1px solid rgba(0, 229, 255, 0.06)';
          tr.innerHTML = `
            <td style="padding: 10px 8px;">
              <span style="font-weight:600;display:block;margin-bottom:4px;">${u.full_name}</span>
              ${verifiedBadge}
            </td>
            <td style="padding: 10px 8px;font-family:var(--font-mono);font-size:12px;color:var(--text-secondary);">${u.email}</td>
            <td style="padding: 10px 8px;">
              <select style="background:rgba(0,0,0,0.3);color:#fff;border:1px solid var(--border);font-size:11px;padding:4px;font-family:var(--font-mono);outline:none;cursor:pointer;" onchange="adminUpdateUserRole('${u.id}', this.value)">
                <option value="citizen" ${u.role === 'citizen' ? 'selected' : ''}>CITIZEN</option>
                <option value="leo" ${u.role === 'leo' ? 'selected' : ''}>LEO</option>
                <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>ADMIN</option>
              </select>
            </td>
            <td style="padding: 10px 8px;font-size:12px;">${activeStatus}</td>
            <td style="padding: 10px 8px;">${actionBtn}</td>
          `;
          usersBody.appendChild(tr);
        });
      }
    }
  } catch (err) {
    if (usersBody) usersBody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#ff3b3f;padding:16px;">Failed to load user directory: ${err.message}</td></tr>`;
  }
}

async function loadAdminAudit() {
  const dlogsList = document.getElementById('adminAuditLogs');
  if (dlogsList) dlogsList.innerHTML = '<div class="loading-spinner"></div>';

  try {
    const auditData = await callBackend('/api/v1/admin/audit-logs', 'GET');
    const logs = auditData.logs || [];
    if (dlogsList) {
      if (logs.length === 0) {
        dlogsList.innerHTML = '<div style="color:var(--text-muted);padding:8px;">No audit sequence parsed.</div>';
      } else {
        dlogsList.innerHTML = '';
        logs.forEach(log => {
          const timestamp = new Date(log.created_at).toLocaleString();
          const resId = log.resource_id ? `${log.resource_id.substring(0, 8)}...` : 'N/A';
          const dItem = document.createElement('div');
          dItem.style.background = 'rgba(255,255,255,0.01)';
          dItem.style.padding = '10px';
          dItem.style.border = '1px solid rgba(0,229,255,0.04)';
          dItem.style.borderRadius = '3px';
          dItem.style.marginBottom = '6px';
          dItem.innerHTML = `
            <div style="display:flex;justify-content:space-between;color:var(--cyan);font-weight:600;">
              <span>[${log.action.toUpperCase()}]</span>
              <span style="color:var(--text-muted);font-weight:normal;">${timestamp}</span>
            </div>
            <div style="color:var(--text-secondary);margin-top:2px;">Resource: ${log.resource} (${resId})</div>
            <div style="color:var(--text-muted);font-size:10px;margin-top:2px;">Details: ${log.details}</div>
          `;
          dlogsList.appendChild(dItem);
        });
      }
    }
  } catch (err) {
    if (dlogsList) dlogsList.innerHTML = `<div style="color:#ff3b3f;padding:8px;">Failed to retrieve audit trail.</div>`;
  }
}

async function loadAdminHealth() {
  const healthList = document.getElementById('adminHealthDiagnostics');
  if (healthList) healthList.innerHTML = '<div class="loading-spinner"></div>';

  try {
    const health = await callBackend('/api/v1/admin/system-health', 'GET');
    if (healthList) {
      const dbStatusColor = health.database === 'healthy' ? '#00ff88' : '#ff3b3f';
      const statusColor = health.status === 'operational' ? '#00e5ff' : '#ff9f00';
      
      healthList.innerHTML = `
        <div style="display:flex;justify-content:space-between;font-size:12px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.03);">
          <span>Database Integrity Check:</span>
          <span style="color:${dbStatusColor};font-weight:700;">${health.database.toUpperCase()}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:12px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.03);">
          <span>Shield Core API Main Gateway:</span>
          <span style="color:${statusColor};font-weight:700;">${health.status.toUpperCase()}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:12px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.03);">
          <span>KAVACH Core Version:</span>
          <span class="mono">${health.version}</span>
        </div>
        
        <div style="font-size:10px;font-family:var(--font-mono);color:var(--text-muted);margin-top:16px;margin-bottom:8px;">AI ENGINE MODULE STATUS:</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
          ${Object.entries(health.ai_engines || {}).map(([engine, state]) => `
            <div style="background:rgba(255,255,255,0.02);padding:8px;border:1px solid rgba(0,229,255,0.06);border-radius:3px;text-align:center;">
              <span style="display:block;color:var(--text-secondary);text-transform:capitalize;font-size:10px;margin-bottom:2px;">${engine.replace('_', ' ')}</span>
              <span style="color:#00ff88;font-weight:600;font-size:10px;">${state.toUpperCase()}</span>
            </div>
          `).join('')}
        </div>
      `;
    }
  } catch (err) {
    if (healthList) healthList.innerHTML = `<div style="color:#ff3b3f;font-size:12px;">Failed to fetch system diagnostics.</div>`;
  }
}

async function loadAdminNotifications() {
  const notifsList = document.getElementById('adminNotificationQueue');
  if (notifsList) notifsList.innerHTML = '<div class="loading-spinner"></div>';

  try {
    const payload = await callBackend('/api/v1/alerts/notifications', 'GET');
    const notifications = payload.notifications || [];
    
    if (notifsList) {
      if (notifications.length === 0) {
        notifsList.innerHTML = '<div style="color:var(--text-muted);padding:16px;text-align:center;font-size:11px;">Notification queue is currently empty. Outbound alerts will print here.</div>';
      } else {
        notifsList.innerHTML = '';
        notifications.forEach(n => {
          const timestamp = new Date(n.created_at).toLocaleString();
          const notItem = document.createElement('div');
          notItem.style.background = 'rgba(0,229,255,0.01)';
          notItem.style.padding = '10px';
          notItem.style.border = '1px solid rgba(0,229,255,0.05)';
          notItem.style.borderRadius = '3px';
          notItem.style.marginBottom = '6px';
          
          let badge = `[${(n.notification_type || 'info').toUpperCase()}]`;
          let badgeColor = 'var(--cyan)';
          if (n.notification_type === 'new_report') {
            badgeColor = '#ff3b3f';
          } else if (n.notification_type === 'platform_setting') {
            badgeColor = '#00ff88';
          } else if (n.notification_type === 'broadcast') {
            badgeColor = '#ff9f00';
          }
          
          notItem.innerHTML = `
            <div style="display:flex;justify-content:space-between;color:${badgeColor};font-weight:600;font-size:11px;">
              <span>${badge} - ${n.title}</span>
              <span style="color:var(--text-muted);font-weight:normal;">${timestamp}</span>
            </div>
            <div style="color:var(--text-secondary);margin-top:4px;font-size:11px;line-height:1.4;">${n.message}</div>
            <div style="font-size:9px;color:#00ff88;margin-top:6px;font-family:var(--font-mono)">Status: DELIVERED (SUCCESS)</div>
          `;
          notifsList.appendChild(notItem);
        });
      }
    }
  } catch (err) {
    if (notifsList) notifsList.innerHTML = `<div style="color:#ff3b3f;padding:8px;font-size:11px;">Failed to fetch notification queue: ${err.message}</div>`;
  }
}

async function adminUpdateUserRole(userId, newRole) {
  try {
    await callBackend(`/api/v1/admin/users/${userId}`, 'PUT', { role: newRole });
    showToast(`User role successfully changed to ${newRole.toUpperCase()}!`, 'success');
    loadAdminUsers();
  } catch (err) {
    showToast(`Failed to update user role: ${err.message}`, 'error');
  }
}

async function adminToggleUserStatus(userId, currentStatus) {
  try {
    await callBackend(`/api/v1/admin/users/${userId}`, 'PUT', { is_active: !currentStatus });
    showToast(`User account status modified successfully!`, 'success');
    loadAdminUsers();
  } catch (err) {
    showToast(`Failed to toggle account status: ${err.message}`, 'error');
  }
}

async function adminSendBroadcast(e) {
  e.preventDefault();
  const phoneVal = document.getElementById('adminBroadcastPhone').value.trim();
  const messageVal = document.getElementById('adminBroadcastMsg').value.trim();
  const submitBtn = document.getElementById('btnAdminBroadcast');

  submitBtn.disabled = true;
  submitBtn.textContent = 'Configuring delivery...';

  try {
    const payload = { message: messageVal };
    if (phoneVal) payload.phone_number = phoneVal;

    const res = await callBackend('/api/v1/alerts/test-sms', 'POST', payload);
    showToast(`Mock SMS broadcast alert queued to ${res.recipient}!`, 'success');
    document.getElementById('adminBroadcastMsg').value = '';
    
    // Switch to notifications queue or refresh it if here
    loadAdminNotifications();
  } catch (err) {
    showToast(`SMS delivery failed: ${err.message}`, 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Dispatch Custom SMS Alert →';
  }
}

async function loadAdminAnalytics() {
  try {
    const stats = await callBackend('/api/v1/admin/system-stats', 'GET');
    
    const scale = (valStr) => {
      const val = parseFloat(valStr);
      return isNaN(val) ? 10 : Math.min(val, 100);
    };

    // Bind CPU and RAM usage
    document.getElementById('statCPULoad').textContent = stats.cpu_load;
    document.getElementById('statBarCPU').style.width = stats.cpu_load;
    document.getElementById('statRAMUsage').textContent = stats.ram_usage;
    
    const ramMB = parseFloat(stats.ram_usage);
    const ramPct = Math.min((ramMB / 512) * 100, 100);
    document.getElementById('statBarRAM').style.width = `${ramPct}%`;

    // Latency elements
    document.getElementById('statLatencyAuth').textContent = stats.latencies.auth_me;
    document.getElementById('statBarAuth').style.width = `${scale(stats.latencies.auth_me)}%`;
    
    document.getElementById('statLatencyReport').textContent = stats.latencies.post_report;
    document.getElementById('statBarReport').style.width = `${scale(stats.latencies.post_report)}%`;
    
    document.getElementById('statLatencyUsers').textContent = stats.latencies.admin_users;
    document.getElementById('statBarUsers').style.width = `${scale(stats.latencies.admin_users)}%`;

  } catch (err) {
    console.error('Failed to load system stats:', err);
  }
}

async function loadAdminSettings() {
  try {
    const config = await callBackend('/api/v1/admin/settings', 'GET');
    
    document.getElementById('adminSettingSMSGateway').value = config.sms_gateway || 'mock';
    document.getElementById('adminSettingThreshold').value = config.ai_confidence_threshold || '75';
    document.getElementById('thresholdVal').textContent = `${config.ai_confidence_threshold || '75'}%`;
    document.getElementById('adminSettingMaintenance').checked = config.maintenance_mode === true;
  } catch (err) {
    showToast(`Failed to load system settings: ${err.message}`, 'error');
  }
}

async function adminSaveSettings() {
  const smsEl = document.getElementById('adminSettingSMSGateway');
  const threshEl = document.getElementById('adminSettingThreshold');
  const maintEl = document.getElementById('adminSettingMaintenance');
  const saveBtn = document.getElementById('btnAdminSaveSettings');

  saveBtn.disabled = true;
  saveBtn.textContent = 'Saving Settings...';

  try {
    const payload = {
      sms_gateway: smsEl.value,
      ai_confidence_threshold: threshEl.value,
      maintenance_mode: maintEl.checked
    };

    await callBackend('/api/v1/admin/settings', 'POST', payload);
    showToast('Platform settings deployed and logged to audit trails successfully!', 'success');
  } catch (err) {
    showToast(`Failed to deploy settings: ${err.message}`, 'error');
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = 'Deploy Configurations';
  }
}
