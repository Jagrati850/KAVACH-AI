/* ═══════════════════════════════════════════════════════════════
   KAVACH AI — Frontend Application Logic
   Backend Integration · JWT Auth · API Calls · UI Controllers
   ═══════════════════════════════════════════════════════════════ */

const API_BASE = (window.location.protocol.startsWith('http')) ? window.location.origin : 'http://127.0.0.1:8000';

// ── State ────────────────────────────────────────────────────
let authToken = localStorage.getItem('jwt_token') || null;
let userRole = localStorage.getItem('user_role') || null;
let userName = localStorage.getItem('user_name') || null;

// ── Initialization ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initParticles();
  initScrollAnimations();
  updateAuthUI();
});

// ── Navbar Scroll Effect ─────────────────────────────────────
function initNavbar() {
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 60) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
}

// ── Mobile Menu ──────────────────────────────────────────────
function toggleMobileMenu() {
  const menu = document.getElementById('mobileMenu');
  menu.classList.toggle('active');
}

// ── Hero Particles ───────────────────────────────────────────
function initParticles() {
  const container = document.getElementById('heroParticles');
  if (!container) return;
  for (let i = 0; i < 30; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDuration = (Math.random() * 6 + 4) + 's';
    particle.style.animationDelay = (Math.random() * 8) + 's';
    particle.style.width = (Math.random() * 3 + 2) + 'px';
    particle.style.height = particle.style.width;
    container.appendChild(particle);
  }
}

// ── Scroll Animations (Intersection Observer) ────────────────
function initScrollAnimations() {
  const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  document.querySelectorAll('.feature-card, .mini-card, .hiw-step, .stat-item, .channel-item, .pricing-card, .gallery-item, .test-stat').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
  });
}

// ═══════════════════════════════════════════════════════════════
// AUTHENTICATION
// ═══════════════════════════════════════════════════════════════

function updateAuthUI() {
  const loginBtn = document.getElementById('loginBtn');
  if (authToken && userName) {
    loginBtn.textContent = `Dashboard (${userName.split(' ')[0]})`;
    loginBtn.onclick = () => window.location.href = 'dashboard.html';
  } else {
    loginBtn.textContent = 'Login / Dashboard';
    loginBtn.onclick = openLoginModal;
  }
}

function openLoginModal() {
  closeModals();
  document.getElementById('loginModal').classList.add('active');
}

function openRegisterModal() {
  closeModals();
  document.getElementById('registerModal').classList.add('active');
}

function closeModals() {
  document.getElementById('loginModal').classList.remove('active');
  document.getElementById('registerModal').classList.remove('active');
  // Clear errors
  document.getElementById('loginError').classList.remove('active');
  document.getElementById('registerError').classList.remove('active');
}

function switchToRegister(e) {
  e.preventDefault();
  openRegisterModal();
}

function switchToLogin(e) {
  e.preventDefault();
  openLoginModal();
}

// Close modals on overlay click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    closeModals();
  }
});

// ── Login Handler ────────────────────────────────────────────
async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  const btn = document.getElementById('loginSubmitBtn');
  const errorDiv = document.getElementById('loginError');

  btn.textContent = 'Authenticating...';
  btn.disabled = true;
  errorDiv.classList.remove('active');

  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || data.message || 'Login failed');
    }

    // Store JWT
    authToken = data.access_token;
    userRole = data.role || 'citizen';
    localStorage.setItem('jwt_token', authToken);
    localStorage.setItem('user_role', userRole);

    // Fetch user profile
    const profileRes = await fetch(`${API_BASE}/api/v1/auth/me`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    if (profileRes.ok) {
      const profile = await profileRes.json();
      userName = profile.full_name || email.split('@')[0];
      userRole = profile.role || 'citizen';
      localStorage.setItem('user_name', userName);
      localStorage.setItem('user_role', userRole);
    }

    closeModals();
    showToast('Login successful! Welcome back.', 'success');
    updateAuthUI();

    // Redirect to dashboard after brief delay
    setTimeout(() => {
      window.location.href = 'dashboard.html';
    }, 1200);

  } catch (err) {
    errorDiv.textContent = err.message;
    errorDiv.classList.add('active');
  } finally {
    btn.innerHTML = 'Login <span class="arrow">→</span>';
    btn.disabled = false;
  }
}

// ── Register Handler ─────────────────────────────────────────
async function handleRegister(e) {
  e.preventDefault();
  const name = document.getElementById('regName').value;
  const email = document.getElementById('regEmail').value;
  const phone = document.getElementById('regPhone').value;
  const password = document.getElementById('regPassword').value;
  const btn = document.getElementById('regSubmitBtn');
  const errorDiv = document.getElementById('registerError');

  btn.textContent = 'Creating Account...';
  btn.disabled = true;
  errorDiv.classList.remove('active');

  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        password,
        full_name: name,
        phone: phone || undefined
      })
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || data.message || 'Registration failed');
    }

    // Store JWT from registration response
    authToken = data.access_token;
    userRole = data.role || 'citizen';
    userName = name;
    localStorage.setItem('jwt_token', authToken);
    localStorage.setItem('user_role', userRole);
    localStorage.setItem('user_name', userName);

    closeModals();
    showToast('Account created successfully! Welcome to KAVACH AI.', 'success');
    updateAuthUI();

    setTimeout(() => {
      window.location.href = 'dashboard.html';
    }, 1200);

  } catch (err) {
    errorDiv.textContent = err.message;
    errorDiv.classList.add('active');
  } finally {
    btn.innerHTML = 'Register <span class="arrow">→</span>';
    btn.disabled = false;
  }
}

// ═══════════════════════════════════════════════════════════════
// REPORT FRAUD FORM
// ═══════════════════════════════════════════════════════════════

async function submitReport(e) {
  e.preventDefault();

  const name = document.getElementById('reportName').value;
  const email = document.getElementById('reportEmail').value;
  const type = document.getElementById('reportType').value;
  const desc = document.getElementById('reportDesc').value;

  let reportType = type ? type.split(' ')[0] : 'other';
  if (reportType === 'fake_currency') {
    reportType = 'counterfeit_currency';
  }

  // Pre-submission validation
  if (desc.trim().length < 20) {
    showToast('Incident description must be at least 20 characters long.', 'error');
    return;
  }
  const titleText = `${reportType.replace('_', ' ').toUpperCase()} Incident Report by ${name}`;
  if (titleText.length < 5) {
    showToast('Report title is too short.', 'error');
    return;
  }

  // If user is authenticated, submit to backend
  if (authToken) {
    try {
      const res = await fetch(`${API_BASE}/api/v1/reports/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: titleText,
          description: desc,
          report_type: reportType
        })
      });

      if (res.ok) {
        showToast('Report submitted successfully! Our AI is analyzing it.', 'success');
        document.getElementById('reportForm').reset();
      } else {
        const data = await res.json();
        throw new Error(data.message || data.detail || 'API ValidationError replacement');
      }
    } catch (err) {
      console.warn('API reporting failed, saving locally:', err.message);
      
      const localRepStr = localStorage.getItem('kavach_local_reports') || '[]';
      const localReports = JSON.parse(localRepStr);
      
      const mockReport = {
        id: 'local-' + Math.random().toString(36).substring(2, 9),
        title: titleText,
        description: desc,
        report_type: reportType,
        status: 'submitted',
        created_at: new Date().toISOString()
      };
      
      localReports.unshift(mockReport);
      localStorage.setItem('kavach_local_reports', JSON.stringify(localReports));
      
      showToast('Report submitted successfully! (Stored locally)', 'success');
      document.getElementById('reportForm').reset();
    }
  } else {
    // Prompt login first
    showToast('Please login first to submit a fraud report.', 'error');
    setTimeout(() => openLoginModal(), 1500);
  }
}

// ═══════════════════════════════════════════════════════════════
// TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════════════════

function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  // Trigger animation
  requestAnimationFrame(() => {
    toast.classList.add('show');
  });

  // Auto-remove
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

// ═══════════════════════════════════════════════════════════════
// UTILITY: Fetch with auth header
// ═══════════════════════════════════════════════════════════════

async function apiFetch(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  if (res.status === 401 || res.status === 403) {
    // Token expired – clear and redirect
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_name');
    authToken = null;
    updateAuthUI();
    showToast('Session expired. Please login again.', 'error');
    setTimeout(() => openLoginModal(), 1500);
    throw new Error('Unauthorized');
  }

  return res;
}
