// =====================================================
// EKKLESIA - FRONTEND APPLICATION
// =====================================================

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:6076/api'
  : '/api';
// Modo demo: usar tenant por query cuando estamos en localhost sin subdominio
const DEMO_TENANT = 'comunidad-de-fe';

function getCurrentTenant() {
  const params = new URLSearchParams(window.location.search);
  if (params.get('tenant')) return params.get('tenant');
  // TODO: si hubiera subdominio, se podría inferir aquí
  return DEMO_TENANT;
}

function publicUrl(path) {
  const isLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);
  if (!isLocal) return `${API_BASE}${path}`;
  const sep = path.includes('?') ? '&' : '?';
  return `${API_BASE}${path}${sep}tenant=${getCurrentTenant()}`;
}

// =====================================================
// STATE
// =====================================================
const state = {
  accessToken: localStorage.getItem('accessToken') || null,
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  currentPage: 'home',
  currentSection: 'dashboard',
};

// =====================================================
// UTILITY FUNCTIONS
// =====================================================
function $(selector) {
  return document.querySelector(selector);
}

function $$(selector) {
  return document.querySelectorAll(selector);
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
  }).format(amount || 0);
}

function formatDate(dateString) {
  if (!dateString) return '—';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
}

function formatDateShort(dateString) {
  if (!dateString) return { day: '—', month: '' };
  const date = new Date(dateString);
  return {
    day: date.getDate(),
    month: new Intl.DateTimeFormat('es-CO', { month: 'short' }).format(date).toUpperCase()
  };
}

// =====================================================
// TOAST NOTIFICATIONS
// =====================================================
function showToast(message, type = 'info') {
  const container = $('#toast-container');
  if (!container) return;
  
  const icons = {
    success: 'ri-check-line',
    error: 'ri-close-circle-line',
    warning: 'ri-alert-line',
    info: 'ri-information-line',
  };
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <i class="${icons[type]}"></i>
    <span>${message}</span>
  `;
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// =====================================================
// API REQUESTS
// =====================================================
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (state.accessToken) {
    headers['Authorization'] = `Bearer ${state.accessToken}`;
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
    
    if (response.status === 401) {
      logout();
      return null;
    }
    
    return response;
  } catch (error) {
    console.error('API Error:', error);
    showToast('Error de conexión', 'error');
    return null;
  }
}

// =====================================================
// PUBLIC PAGE NAVIGATION
// =====================================================
function navigateToPage(page) {
  state.currentPage = page;
  
  // Update nav links
  $$('.header-nav .nav-link').forEach(link => {
    link.classList.toggle('active', link.dataset.page === page);
  });
  
  // Show correct page
  $$('.public-page').forEach(p => {
    p.classList.remove('active');
  });
  
  const targetPage = $(`#page-${page}`);
  if (targetPage) {
    targetPage.classList.add('active');
  }
  
  // Load page data
  switch (page) {
    case 'home':
      loadFeaturedEvents();
      loadChurchConfig();
      loadPublicAnnouncements();
      break;
    case 'about':
      loadAboutContent();
      break;
    case 'events':
      loadPublicEvents();
      break;
    case 'donate':
      loadDonationInfo();
      break;
  }
  
  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// =====================================================
// LOAD CHURCH CONFIG
// =====================================================
async function loadChurchConfig() {
  try {
    const response = await fetch(publicUrl('/public/config'));
    if (response.ok) {
      const config = await response.json();
      
      // Update hero
      if (config.church_name) {
        const heroTitle = $('.hero-content h1');
        if (heroTitle) {
          heroTitle.textContent = `Bienvenido a ${config.church_name}`;
        }
      }
      
      if (config.slogan) {
        const heroSlogan = $('.hero-slogan');
        if (heroSlogan) {
          heroSlogan.textContent = config.slogan;
        }
      }
      
      // Update service schedule
      if (config.service_schedule && Array.isArray(config.service_schedule)) {
        updateServiceSchedule(config.service_schedule);
      }
      
      // Store config for later use
      state.churchConfig = config;
    }
  } catch (error) {
    console.error('Error loading church config:', error);
  }
}

function updateServiceSchedule(schedule) {
  const grid = $('.services-grid');
  if (!grid || !schedule.length) return;
  
  // Group by day
  const byDay = {};
  schedule.forEach(s => {
    if (!byDay[s.day]) byDay[s.day] = [];
    byDay[s.day].push(s);
  });
  
  const icons = {
    'Domingo': 'ri-sun-line',
    'Lunes': 'ri-calendar-line',
    'Martes': 'ri-calendar-line',
    'Miércoles': 'ri-moon-line',
    'Miercoles': 'ri-moon-line',
    'Jueves': 'ri-calendar-line',
    'Viernes': 'ri-group-line',
    'Sábado': 'ri-calendar-line',
    'Sabado': 'ri-calendar-line',
  };
  
  grid.innerHTML = Object.entries(byDay).map(([day, services]) => `
    <div class="service-card">
      <i class="${icons[day] || 'ri-calendar-line'}"></i>
      <h3>${day}</h3>
      ${services.map(s => `<p>${s.time} - ${s.name}</p>`).join('')}
    </div>
  `).join('');
}

// =====================================================
// LOAD FEATURED EVENTS
// =====================================================
async function loadFeaturedEvents() {
  const container = $('#featured-events');
  if (!container) return;
  
  try {
    const response = await fetch(publicUrl('/public/events?limit=3'));
    if (response.ok) {
      const events = await response.json();
      
      if (!events.length) {
        container.innerHTML = `
          <div class="empty-message">
            <i class="ri-calendar-line" style="font-size: 48px; opacity: 0.3;"></i>
            <p>No hay eventos próximos</p>
          </div>
        `;
        return;
      }
      
      container.innerHTML = events.map(event => {
        const date = formatDateShort(event.start_date);
        return `
          <div class="event-preview-card">
            <div class="event-preview-image">
              <i class="ri-calendar-event-line"></i>
            </div>
            <div class="event-preview-content">
              <span class="event-preview-date">
                <i class="ri-calendar-line"></i>
                ${event.start_date ? formatDate(event.start_date) : 'Fecha por confirmar'}
              </span>
              <h3>${event.name}</h3>
              <p>${event.description || 'Sin descripción'}</p>
            </div>
          </div>
        `;
      }).join('');
    }
  } catch (error) {
    console.error('Error loading events:', error);
    container.innerHTML = '<p class="empty-message">Error al cargar eventos</p>';
  }
}

// =====================================================
// LOAD ABOUT CONTENT
// =====================================================
async function loadAboutContent() {
  const container = $('.about-content');
  if (!container) return;
  
  try {
    // Try to load church config for about info
    const response = await fetch(publicUrl('/public/config'));
    if (response.ok) {
      const config = await response.json();
      
      container.innerHTML = `
        ${config.mission ? `
          <h2>Nuestra Misión</h2>
          <p>${config.mission}</p>
        ` : ''}
        ${config.vision ? `
          <h2>Nuestra Visión</h2>
          <p>${config.vision}</p>
        ` : ''}
        ${config.about_us ? `
          <h2>Acerca de Nosotros</h2>
          <p>${config.about_us}</p>
        ` : ''}
        ${config.history ? `
          <h2>Nuestra Historia</h2>
          <p>${config.history}</p>
        ` : ''}
        ${!config.mission && !config.vision && !config.about_us && !config.history ? `
          <h2>Nuestra Misión</h2>
          <p>Predicar el evangelio de Jesucristo, formar discípulos y servir a nuestra comunidad con amor.</p>
          <h2>Nuestra Visión</h2>
          <p>Ser una iglesia que transforma vidas a través del poder del evangelio.</p>
        ` : ''}
      `;
    }
  } catch (error) {
    console.error('Error loading about content:', error);
  }
}

// =====================================================
// LOAD PUBLIC EVENTS
// =====================================================
async function loadPublicEvents() {
  const container = $('#public-events-list');
  if (!container) return;
  
  container.innerHTML = `
    <div class="loading-state">
      <i class="ri-loader-4-line spin"></i>
      <p>Cargando eventos...</p>
    </div>
  `;
  
  try {
    const response = await fetch(publicUrl('/public/events?limit=20&upcoming=false'));
    if (response.ok) {
      const events = await response.json();
      
      if (!events.length) {
        container.innerHTML = `
          <div class="empty-message">
            <i class="ri-calendar-line" style="font-size: 64px; opacity: 0.3; display: block; margin-bottom: 16px;"></i>
            <p>No hay eventos registrados</p>
          </div>
        `;
        return;
      }
      
      container.innerHTML = events.map(event => {
        const date = formatDateShort(event.start_date);
        return `
          <div class="event-list-card">
            <div class="event-date-badge">
              <span class="day">${date.day}</span>
              <span class="month">${date.month}</span>
            </div>
            <div class="event-info">
              <h3>${event.name}</h3>
              <p>${event.description || 'Sin descripción'}</p>
              <div class="event-meta">
                ${event.capacity ? `<span><i class="ri-group-line"></i> ${event.capacity} cupos</span>` : ''}
              </div>
            </div>
            <div class="event-actions">
              <button class="btn btn-primary btn-sm" onclick="openEventRegistration(${event.id}, '${event.name}')">
                <i class="ri-calendar-check-line"></i>
                Inscribirse
              </button>
            </div>
          </div>
        `;
      }).join('');
    }
  } catch (error) {
    console.error('Error loading events:', error);
    container.innerHTML = '<p class="empty-message">Error al cargar eventos</p>';
  }
}

// =====================================================
// LOAD DONATION INFO
// =====================================================
async function loadDonationInfo() {
  try {
    const response = await fetch(publicUrl('/public/donation-info'));
    if (response.ok) {
      const info = await response.json();
      
      // Update donation info if available
      if (info.payment_methods && info.payment_methods.length) {
        const methodsContainer = $('.payment-methods');
        if (methodsContainer) {
          methodsContainer.innerHTML = info.payment_methods.map(method => {
            if (method.type === 'bank') {
              return `
                <div class="payment-method-card">
                  <i class="ri-bank-line"></i>
                  <h4>Transferencia Bancaria</h4>
                  <p>
                    ${method.details.banco ? `Banco: ${method.details.banco}<br>` : ''}
                    ${method.details.numero ? `Cuenta: ${method.details.numero}<br>` : ''}
                    ${method.details.tipo_cuenta ? `Tipo: ${method.details.tipo_cuenta}<br>` : ''}
                    ${method.details.titular ? `Titular: ${method.details.titular}` : ''}
                  </p>
                </div>
              `;
            } else if (method.type === 'paypal') {
              return `
                <div class="payment-method-card">
                  <i class="ri-paypal-line"></i>
                  <h4>PayPal</h4>
                  <p>${method.email}</p>
                </div>
              `;
            } else if (method.type === 'online') {
              return `
                <div class="payment-method-card">
                  <i class="ri-global-line"></i>
                  <h4>Pago en Línea</h4>
                  <a href="${method.link}" target="_blank" class="btn btn-primary btn-sm">Donar Ahora</a>
                </div>
              `;
            }
            return '';
          }).join('') + `
            <div class="payment-method-card">
              <i class="ri-hand-coin-line"></i>
              <h4>Presencial</h4>
              <p>Durante los servicios dominicales</p>
            </div>
          `;
        }
      }
    }
  } catch (error) {
    console.error('Error loading donation info:', error);
  }
}

// =====================================================
// PUBLIC ANNOUNCEMENTS (landing)
// =====================================================
async function loadPublicAnnouncements() {
  const container = $('#public-announcements');
  if (!container) return;

  try {
    const response = await fetch(publicUrl('/public/announcements?limit=6'));
    if (response.ok) {
      const anns = await response.json();
      if (!anns.length) {
        container.innerHTML = `
          <p class="empty-message">No hay anuncios disponibles</p>
        `;
        return;
      }

      container.innerHTML = anns.map(a => `
        <div class="event-preview-card">
          <div class="event-preview-content">
            <span class="event-preview-date">
              <i class="ri-notification-3-line"></i>
              ${a.priority || 'Normal'}
            </span>
            <h3>${a.title || 'Anuncio'}</h3>
            <p>${a.content || ''}</p>
            <div class="event-meta" style="margin-top:8px;">
              ${a.start_date ? `<span><i class="ri-calendar-line"></i> ${formatDate(a.start_date)}</span>` : ''}
              ${a.end_date ? `<span><i class="ri-timer-line"></i> Hasta ${formatDate(a.end_date)}</span>` : ''}
            </div>
          </div>
        </div>
      `).join('');
    } else {
      container.innerHTML = `<p class="empty-message">Error al cargar anuncios</p>`;
    }
  } catch (error) {
    console.error('Error loading announcements:', error);
    container.innerHTML = `<p class="empty-message">Error de conexión</p>`;
  }
}

// =====================================================
// EVENT REGISTRATION
// =====================================================
function openEventRegistration(eventId, eventName) {
  if (!state.accessToken) {
    showToast('Debes iniciar sesión para inscribirte', 'warning');
    openAuthModal();
    return;
  }
  const modal = $('#registration-modal');
  if (modal) {
    $('#reg-event-id').value = eventId;
    modal.classList.remove('hidden');
  }
}

// =====================================================
// AUTH MODAL
// =====================================================
function openAuthModal() {
  const modal = $('#auth-modal');
  if (modal) {
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }
}

function closeAuthModal() {
  const modal = $('#auth-modal');
  if (modal) {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }
}

// =====================================================
// AUTH FUNCTIONS
// =====================================================
async function handleLogin(event) {
  event.preventDefault();
  
  const email = $('#login-email').value;
  const password = $('#login-password').value;
  
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    
    if (response.ok) {
      const data = await response.json();
      state.accessToken = data.access_token;
      localStorage.setItem('accessToken', data.access_token);
      
      // Get user info
      await loadUserProfile();
      
      closeAuthModal();
      showUserApp();
      showToast('¡Bienvenido!', 'success');
    } else {
      const error = await response.json();
      showToast(error.detail || 'Credenciales inválidas', 'error');
    }
  } catch (error) {
    showToast('Error de conexión', 'error');
  }
}

async function handleRegister(event) {
  event.preventDefault();
  
  const full_name = $('#register-name').value;
  const email = $('#register-email').value;
  const password = $('#register-password').value;
  
  try {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name }),
    });
    
    if (response.ok) {
      showToast('Cuenta creada. Ahora puedes iniciar sesión.', 'success');
      // Switch to login tab
      switchAuthTab('login');
    } else {
      const error = await response.json();
      showToast(error.detail || 'Error al crear cuenta', 'error');
    }
  } catch (error) {
    showToast('Error de conexión', 'error');
  }
}

function switchAuthTab(tab) {
  $$('.auth-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  $$('.auth-form').forEach(f => f.classList.toggle('active', f.id === `${tab}-form`));
}

async function loadUserProfile() {
  try {
    const response = await apiRequest('/auth/me');
    if (response && response.ok) {
      state.user = await response.json();
      localStorage.setItem('user', JSON.stringify(state.user));
      updateUserUI();
    }
  } catch (error) {
    console.error('Error loading profile:', error);
  }
}

function updateUserUI() {
  if (state.user) {
    $('#user-name').textContent = state.user.full_name || state.user.email;
    const roleLabel = {
      admin: 'Administrador',
      superadmin: 'Super Administrador',
      member: 'Miembro',
    }[state.user.role] || state.user.role || 'Miembro';
    $('#user-role').textContent = roleLabel;
    
    // Mostrar/ocultar secciones según rol
    const isAdmin = state.user.role === 'admin' || state.user.role === 'superadmin';
    $$('.admin-only').forEach(el => el.style.display = isAdmin ? '' : 'none');
    // Mostrar botones de comunidad (anuncios) si admin
    if (isAdmin) {
      $('#announcement-form-card')?.classList.add('hidden');
    }
    // Ocultar donaciones y documentos para miembros
    if (!isAdmin) {
      const hideIds = ['section-donations', 'section-documents', 'section-expenses', 'section-reports'];
      hideIds.forEach(id => {
        const sec = document.getElementById(id);
        if (sec) sec.classList.remove('active');
      });
      // Ajustar navegación: desactivar items que no aplican
      $$('.sidebar-nav .nav-item').forEach(item => {
        const disallowed = ['donations', 'documents', 'expenses', 'reports'];
        if (disallowed.includes(item.dataset.section)) {
          item.style.display = 'none';
          item.classList.remove('active');
        }
      });
      // Enfocar en eventos
      navigateToSection('events');
    } else {
      // Restaurar visibilidad para admin
      $$('.sidebar-nav .nav-item').forEach(item => {
        item.style.display = '';
      });
    }
  }
}

function logout() {
  state.accessToken = null;
  state.user = null;
  localStorage.removeItem('accessToken');
  localStorage.removeItem('user');
  showLandingPage();
  showToast('Sesión cerrada', 'info');
}

// =====================================================
// VIEW SWITCHING
// =====================================================
function showLandingPage() {
  $('#landing-page').classList.remove('hidden');
  $('#user-app').classList.add('hidden');
  navigateToPage('home');
}

function showUserApp() {
  $('#landing-page').classList.add('hidden');
  $('#user-app').classList.remove('hidden');
  navigateToSection('dashboard');
  loadDashboard();
}

function navigateToSection(section) {
  state.currentSection = section;
  
  // Update nav
  $$('.sidebar-nav .nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.section === section);
  });
  
  // Show section
  $$('.app .section').forEach(s => s.classList.remove('active'));
  const targetSection = $(`#section-${section}`);
  if (targetSection) {
    targetSection.classList.add('active');
  }
  
  // Load section data
  const isAdmin = state.user?.role === 'admin' || state.user?.role === 'superadmin';
  const disallowedForMember = ['donations', 'documents', 'expenses', 'reports'];
  if (!isAdmin && disallowedForMember.includes(section)) {
    // Reenviar a eventos si la sección no es permitida
    state.currentSection = 'events';
    return navigateToSection('events');
  }

  switch (section) {
    case 'dashboard':
      loadDashboard();
      break;
    case 'donations':
      loadDonations();
      break;
    case 'documents':
      loadDocuments();
      break;
    case 'events':
      loadUserEvents();
      break;
    case 'community':
      loadAnnouncements();
      break;
    case 'expenses':
      loadExpenses();
      break;
    case 'reports':
      initReports();
      break;
  }
}

// =====================================================
// DASHBOARD
// =====================================================
async function loadDashboard() {
  try {
    const response = await apiRequest('/reports/dashboard');
    if (response && response.ok) {
      const data = await response.json();
      
      $('#stat-donations-count').textContent = data.donations_count || 0;
      $('#stat-total-amount').textContent = formatCurrency(data.total_amount || 0);
      $('#stat-events-count').textContent = data.events_count || 0;
      $('#stat-documents-count').textContent = data.documents_count || 0;
    }
  } catch (error) {
    console.error('Error loading dashboard:', error);
  }
}

// =====================================================
// DONATIONS
// =====================================================
async function loadDonations() {
  try {
    const response = await apiRequest('/donations');
    if (response && response.ok) {
      const donations = await response.json();
      renderDonationsTable(donations);
    }
  } catch (error) {
    console.error('Error loading donations:', error);
  }
}

function renderDonationsTable(donations) {
  const tbody = $('#donations-tbody');
  if (!tbody) return;
  
  if (!donations.length) {
    tbody.innerHTML = `
      <tr class="empty-row">
        <td colspan="7">
          <div class="empty-state">
            <i class="ri-inbox-line"></i>
            <p>No hay donaciones registradas</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }
  
  tbody.innerHTML = donations.map(d => `
    <tr>
      <td>${formatDate(d.donation_date)}</td>
      <td>${d.donor_name}${d.is_anonymous ? ' (Anónimo)' : ''}</td>
      <td>${formatCurrency(d.amount_tithe || 0)}</td>
      <td>${formatCurrency(d.amount_offering || 0)}</td>
      <td>${formatCurrency(d.amount_missions || 0)}</td>
      <td><strong>${formatCurrency(d.amount_total || 0)}</strong></td>
      <td>
        <span class="badge ${d.is_cash ? 'badge-success' : 'badge-info'}">
          ${d.is_cash ? 'Efectivo' : 'Transferencia'}
        </span>
      </td>
    </tr>
  `).join('');
}

// =====================================================
// DOCUMENTS
// =====================================================
async function loadDocuments() {
  const container = $('#documents-list');
  if (!container) return;
  
  try {
    const endpoint = state.user?.role === 'admin' ? '/documents' : '/documents/me';
    const response = await apiRequest(endpoint);
    if (response && response.ok) {
      const docs = await response.json();
      
      if (!docs.length) {
        container.innerHTML = `
          <div class="empty-state">
            <i class="ri-folder-line"></i>
            <p>No hay documentos subidos</p>
          </div>
        `;
        return;
      }
      
      container.innerHTML = docs.map(doc => `
        <div class="document-card">
          <i class="ri-file-line"></i>
          <span>${doc.file_name}</span>
          <small>${formatDate(doc.uploaded_at)}</small>
        </div>
      `).join('');
    }
  } catch (error) {
    console.error('Error loading documents:', error);
  }
}

// -----------------------------------------------------
// Document upload handlers
// -----------------------------------------------------
function initDocumentUpload() {
  const formCard = $('#document-form-card');
  const form = $('#document-form');
  const newBtn = $('#new-document-btn');
  const fileInput = $('#doc-file');
  const dropZone = $('#file-drop-zone');
  const preview = $('#file-preview');
  const fileNameLabel = $('#file-name');
  const removeFileBtn = $('#remove-file');

  if (newBtn) {
    newBtn.addEventListener('click', () => {
      formCard?.classList.toggle('hidden');
    });
  }

  if (dropZone && fileInput) {
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer?.files?.length) {
        fileInput.files = e.dataTransfer.files;
        updateFilePreview();
      }
    });
  }

  if (fileInput) {
    fileInput.addEventListener('change', updateFilePreview);
  }

  if (removeFileBtn) {
    removeFileBtn.addEventListener('click', () => {
      if (fileInput) fileInput.value = '';
      preview?.classList.add('hidden');
    });
  }

  if (form) {
    form.addEventListener('submit', handleDocumentSubmit);
  }

  function updateFilePreview() {
    if (!fileInput?.files?.length) {
      preview?.classList.add('hidden');
      return;
    }
    const file = fileInput.files[0];
    if (fileNameLabel) fileNameLabel.textContent = file.name;
    preview?.classList.remove('hidden');
  }
}

async function handleDocumentSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const fileInput = $('#doc-file');
  if (!fileInput?.files?.length) {
    showToast('Selecciona un archivo primero', 'warning');
    return;
  }

  const fd = new FormData(form);
  const file = fileInput.files[0];
  fd.append('file', file);

  try {
    const response = await fetch(`${API_BASE}/documents`, {
      method: 'POST',
      headers: state.accessToken ? { Authorization: `Bearer ${state.accessToken}` } : undefined,
      body: fd,
    });

    if (response.ok) {
      showToast('Documento subido', 'success');
      form.reset();
      $('#document-form-card')?.classList.add('hidden');
      $('#file-preview')?.classList.add('hidden');
      await loadDocuments();
    } else {
      const err = await response.json();
      showToast(err.detail || 'Error al subir documento', 'error');
    }
  } catch (error) {
    console.error(error);
    showToast('Error de conexión', 'error');
  }
}

async function handleAnnouncementSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const fd = new FormData(form);
  const payload = {
    title: fd.get('title'),
    content: fd.get('content') || null,
    announcement_type: fd.get('announcement_type') || 'general',
    priority: parseInt(fd.get('priority') || '1', 10),
    is_public: fd.get('is_public') === 'on',
    start_date: fd.get('start_date') || null,
    end_date: fd.get('end_date') || null,
  };

  try {
    const response = await apiRequest('/admin/announcements', { method: 'POST', body: payload });
    if (response?.ok) {
      showToast('Anuncio publicado', 'success');
      form.reset();
      $('#announcement-form-card')?.classList.add('hidden');
      loadAnnouncements(); // refresca panel
      loadPublicAnnouncements(); // refresca landing
    } else {
      const err = await response.json();
      showToast(err.detail || 'Error al publicar', 'error');
    }
  } catch (err) {
    showToast('Error de conexión', 'error');
  }
}

async function handleCreateTag(event) {
  event.preventDefault();
  const name = $('#expense-tag-name')?.value?.trim();
  if (!name) {
    showToast('Nombre de etiqueta requerido', 'warning');
    return;
  }
  try {
    const response = await apiRequest('/expenses/tags', {
      method: 'POST',
      body: { name },
    });
    if (response?.ok) {
      showToast('Etiqueta creada', 'success');
      $('#expense-tag-name').value = '';
    } else {
      const err = await response.json();
      showToast(err.detail || 'Error al crear etiqueta', 'error');
    }
  } catch (err) {
    showToast('Error de conexión', 'error');
  }
}

async function approveExpense(id) {
  try {
    const response = await apiRequest(`/expenses/${id}/approve`, { method: 'POST' });
    if (response?.ok) {
      showToast('Gasto aprobado', 'success');
      loadExpenses();
    } else {
      const err = await response.json();
      showToast(err.detail || 'No se pudo aprobar', 'error');
    }
  } catch (err) {
    showToast('Error de conexión', 'error');
  }
}

async function payExpense(id) {
  try {
    const response = await apiRequest(`/expenses/${id}/pay`, { method: 'POST' });
    if (response?.ok) {
      showToast('Gasto pagado', 'success');
      loadExpenses();
    } else {
      const err = await response.json();
      showToast(err.detail || 'No se pudo pagar', 'error');
    }
  } catch (err) {
    showToast('Error de conexión', 'error');
  }
}

// =====================================================
// USER EVENTS
// =====================================================
async function loadUserEvents() {
  const container = $('#events-container');
  if (!container) return;
  
  try {
    const endpoint = state.user?.role === 'admin' || state.user?.role === 'superadmin'
      ? '/admin/events'
      : '/events/';
    const response = await apiRequest(endpoint);
    if (response && response.ok) {
      const events = await response.json();
      
      if (!events.length) {
        container.innerHTML = `
          <div class="empty-state-full">
            <i class="ri-calendar-todo-line"></i>
            <h3>No hay eventos</h3>
            <p>Crea tu primer evento</p>
          </div>
        `;
        return;
      }
      
      container.innerHTML = events.map(event => `
        <div class="event-card">
          <h3>${event.name}</h3>
          <p>${event.description || ''}</p>
          <div class="event-meta">
            <span><i class="ri-calendar-line"></i> ${formatDate(event.start_date)}</span>
            ${event.capacity ? `<span><i class="ri-group-line"></i> ${event.capacity}</span>` : ''}
          </div>
          ${ (state.user?.role === 'admin' || state.user?.role === 'superadmin') ? `
          <div style="margin-top:8px;">
            <button class="btn btn-secondary btn-sm" onclick="editEvent(${event.id})" disabled>
              <i class="ri-edit-line"></i> Editar
            </button>
            <button class="btn btn-ghost btn-sm" onclick="deleteEvent(${event.id})">
              <i class="ri-delete-bin-line"></i> Eliminar
            </button>
          </div>` : '' }
        </div>
      `).join('');
    }
  } catch (error) {
    console.error('Error loading events:', error);
  }
}

async function handleEventSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  const payload = {
    name: formData.get('name'),
    description: formData.get('description') || null,
    start_date: formData.get('start_date') || null,
    end_date: formData.get('end_date') || null,
    capacity: formData.get('capacity') ? parseInt(formData.get('capacity'), 10) : null,
  };
  try {
    const response = await apiRequest('/admin/events', { method: 'POST', body: payload });
    if (response?.ok) {
      showToast('Evento creado', 'success');
      form.reset();
      $('#event-form-card')?.classList.add('hidden');
      loadUserEvents();
    } else {
      const err = await response.json();
      showToast(err.detail || 'Error al crear evento', 'error');
    }
  } catch (err) {
    showToast('Error de conexión', 'error');
  }
}

async function deleteEvent(eventId) {
  if (!confirm('¿Eliminar evento?')) return;
  try {
    const response = await apiRequest(`/admin/events/${eventId}`, { method: 'DELETE' });
    if (response?.ok || response?.status === 204) {
      showToast('Evento eliminado', 'success');
      loadUserEvents();
    } else {
      const err = await response.json();
      showToast(err.detail || 'No se pudo eliminar', 'error');
    }
  } catch (err) {
    showToast('Error de conexión', 'error');
  }
}

// =====================================================
// ANNOUNCEMENTS (Comunidad)
// =====================================================
async function loadAnnouncements() {
  const container = $('#announcements-list');
  if (!container) return;

  container.innerHTML = `
    <div class="empty-state-full">
      <i class="ri-loader-4-line spin"></i>
      <h3>Cargando anuncios...</h3>
    </div>
  `;

  try {
    const response = await fetch(publicUrl('/public/announcements?limit=20'));
    if (response.ok) {
      const anns = await response.json();
      if (!anns.length) {
        container.innerHTML = `
          <div class="empty-state-full">
            <i class="ri-notification-off-line"></i>
            <h3>No hay anuncios</h3>
            <p>Cuando haya anuncios, aparecerán aquí.</p>
          </div>
        `;
        return;
      }

      container.innerHTML = anns.map(a => `
        <div class="event-card">
          <div class="event-meta" style="margin-bottom:8px;">
            <span><i class="ri-alarm-warning-line"></i> ${a.priority || 'Normal'}</span>
            ${a.is_public ? '<span><i class="ri-eye-line"></i> Público</span>' : ''}
          </div>
          <h3>${a.title || 'Anuncio'}</h3>
          <p>${a.content || ''}</p>
          <div class="event-meta">
            ${a.start_date ? `<span><i class="ri-calendar-line"></i> ${formatDate(a.start_date)}</span>` : ''}
            ${a.end_date ? `<span><i class="ri-timer-line"></i> Hasta ${formatDate(a.end_date)}</span>` : ''}
          </div>
        </div>
      `).join('');
    } else {
      container.innerHTML = `
        <div class="empty-state-full">
          <i class="ri-alert-line"></i>
          <h3>Error al cargar anuncios</h3>
        </div>
      `;
    }
  } catch (error) {
    console.error('Error loading announcements:', error);
    container.innerHTML = `
      <div class="empty-state-full">
        <i class="ri-alert-line"></i>
        <h3>Error de conexión</h3>
      </div>
    `;
  }
}

// =====================================================
// EXPENSES
// =====================================================
async function loadExpenses() {
  try {
    const response = await apiRequest('/expenses/');
    if (response && response.ok) {
      const expenses = await response.json();
      renderExpensesTable(expenses);
    }
  } catch (error) {
    console.error('Error loading expenses:', error);
  }
}

function renderExpensesTable(expenses) {
  const tbody = $('#expenses-tbody');
  if (!tbody) return;
  
  if (!expenses.length) {
    tbody.innerHTML = `
      <tr class="empty-row">
        <td colspan="6">
          <div class="empty-state">
            <i class="ri-inbox-line"></i>
            <p>No hay gastos registrados</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }
  
  tbody.innerHTML = expenses.map(e => `
    <tr>
      <td>${formatDate(e.expense_date)}</td>
      <td>${e.category?.name || '—'}</td>
      <td>${e.description}</td>
      <td>${formatCurrency(e.amount)}</td>
      <td><span class="badge badge-${e.status}">${e.status}</span></td>
      <td>
        <button class="btn btn-ghost btn-sm" onclick="viewExpense(${e.id})">
          <i class="ri-eye-line"></i>
        </button>
        ${(state.user?.role === 'admin' || state.user?.role === 'superadmin') ? `
          <button class="btn btn-ghost btn-sm" onclick="approveExpense(${e.id})" ${e.status !== 'pendiente' ? 'disabled' : ''}>
            <i class="ri-checkbox-circle-line"></i>
          </button>
          <button class="btn btn-ghost btn-sm" onclick="payExpense(${e.id})" ${e.status !== 'aprobado' ? 'disabled' : ''}>
            <i class="ri-bank-card-line"></i>
          </button>
        ` : ''}
      </td>
    </tr>
  `).join('');
}

// =====================================================
// REPORTS
// =====================================================
function initReports() {
  const now = new Date();
  $('#report-month').value = now.getMonth() + 1;
  $('#report-year').value = now.getFullYear();
  $('#expense-report-month').value = now.getMonth() + 1;
  $('#expense-report-year').value = now.getFullYear();
  
  const weekNumber = getWeekNumber(now);
  $('#accountant-week').value = weekNumber;
  $('#accountant-year').value = now.getFullYear();
}

function getWeekNumber(date) {
  const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
  const pastDaysOfYear = (date - firstDayOfYear) / 86400000;
  return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
}

// =====================================================
// EVENT LISTENERS
// =====================================================
function initEventListeners() {
  // Navigation links
  $$('.header-nav .nav-link, [data-page]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const page = link.dataset.page;
      if (page) navigateToPage(page);
    });
  });
  
  // Login button
  $('#btn-login')?.addEventListener('click', openAuthModal);
  
  // Close auth modal
  $('#auth-modal-close')?.addEventListener('click', closeAuthModal);
  $('.modal-backdrop')?.addEventListener('click', closeAuthModal);
  
  // Auth tabs
  $$('.auth-tab').forEach(tab => {
    tab.addEventListener('click', () => switchAuthTab(tab.dataset.tab));
  });
  
  // Auth forms
  $('#login-form')?.addEventListener('submit', handleLogin);
  $('#register-form')?.addEventListener('submit', handleRegister);
  
  // Logout
  $('#logout-btn')?.addEventListener('click', logout);
  
  // Back to site
  $('#btn-back-to-site')?.addEventListener('click', showLandingPage);
  
  // Sidebar navigation
  $$('.sidebar-nav .nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      navigateToSection(item.dataset.section);
    });
  });
  
  // Form toggles
  $('#new-donation-btn')?.addEventListener('click', () => {
    $('#donation-form-card')?.classList.toggle('hidden');
    // Set default date
    const today = new Date().toISOString().split('T')[0];
    $('#donation-date').value = today;
  });
  
  $$('.close-form-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.closest('.form-card')?.classList.add('hidden');
    });
  });
  
  // Donation form
  $('#donation-form')?.addEventListener('submit', handleDonationSubmit);
  $('#event-form')?.addEventListener('submit', handleEventSubmit);

  // Announcement form
  $('#new-announcement-btn')?.addEventListener('click', () => {
    $('#announcement-form-card')?.classList.toggle('hidden');
  });
  $('#announcement-form')?.addEventListener('submit', handleAnnouncementSubmit);

  // Expense tag
  $('#create-tag-btn')?.addEventListener('click', handleCreateTag);
  
  // Registration modal close
  $$('.modal-close-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.closest('.modal')?.classList.add('hidden');
    });
  });
  
  // Report tabs
  $$('.report-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      $$('.report-tab').forEach(t => t.classList.toggle('active', t === tab));
      $$('.report-panel').forEach(p => p.classList.toggle('active', p.id === `report-${tab.dataset.report}`));
    });
  });

  // Documents
  initDocumentUpload();
}

// =====================================================
// DONATION FORM HANDLER
// =====================================================
async function handleDonationSubmit(event) {
  event.preventDefault();
  
  const form = event.target;
  const formData = new FormData(form);
  
  const data = {
    donor_name: formData.get('donor_name'),
    donor_document: formData.get('donor_document') || null,
    donor_address: formData.get('donor_address') || null,
    donor_phone: formData.get('donor_phone') || null,
    amount_tithe: parseFloat(formData.get('amount_tithe')) || 0,
    amount_offering: parseFloat(formData.get('amount_offering')) || 0,
    amount_missions: parseFloat(formData.get('amount_missions')) || 0,
    amount_special: parseFloat(formData.get('amount_special')) || 0,
    is_cash: formData.get('is_cash') === 'on',
    is_transfer: formData.get('is_transfer') === 'on',
    payment_reference: formData.get('payment_reference') || null,
    donation_date: formData.get('donation_date'),
    envelope_number: formData.get('envelope_number') || null,
    is_anonymous: formData.get('is_anonymous') === 'on',
    note: formData.get('note') || null,
  };
  
  const supportFile = $('#donation-support-file')?.files?.[0];
  
  try {
    const response = await apiRequest('/donations', {
      method: 'POST',
      body: data,
    });
    
    if (response && response.ok) {
      const donation = await response.json();
      
      // Si hay soporte adjunto, subirlo ligado a la donación
      if (supportFile) {
        const uploaded = await uploadDonationSupport(donation.id, supportFile);
        if (uploaded) {
          showToast('Soporte adjuntado', 'success');
        }
      }
      
      showToast('Donación registrada exitosamente', 'success');
      form.reset();
      if ($('#donation-support-file')) $('#donation-support-file').value = '';
      $('#file-preview')?.classList.add('hidden');
      $('#donation-form-card')?.classList.add('hidden');
      loadDonations();
    } else {
      const error = await response?.json();
      showToast(error?.detail || 'Error al registrar donación', 'error');
    }
  } catch (error) {
    showToast('Error de conexión', 'error');
  }
}

async function uploadDonationSupport(donationId, file) {
  const fd = new FormData();
  fd.append('file', file);
  fd.append('link_type', 'donation');
  fd.append('ref_id', donationId);
  fd.append('is_public', false);

  try {
    const response = await fetch(`${API_BASE}/documents`, {
      method: 'POST',
      headers: state.accessToken ? { Authorization: `Bearer ${state.accessToken}` } : undefined,
      body: fd,
    });
    if (response.ok) return true;
    const err = await response.json();
    showToast(err.detail || 'No se pudo adjuntar el soporte', 'warning');
    return false;
  } catch (err) {
    console.error(err);
    showToast('Error de conexión al adjuntar soporte', 'warning');
    return false;
  }
}

// =====================================================
// INITIALIZATION
// =====================================================
function init() {
  initEventListeners();
  
  // Check if user is logged in
  if (state.accessToken) {
    loadUserProfile().then(() => {
      showUserApp();
    }).catch(() => {
      showLandingPage();
    });
  } else {
    showLandingPage();
  }
}

// Start app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Make functions available globally for onclick handlers
window.openEventRegistration = openEventRegistration;
window.viewExpense = (id) => console.log('View expense:', id);


