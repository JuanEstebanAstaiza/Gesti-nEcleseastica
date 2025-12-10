/**
 * EKKLESIA - Sistema de Gestión Eclesiástica
 * Frontend JavaScript Module v2.0
 */

// ========================================
// CONFIGURATION
// ========================================
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:6076/api'
  : '/api';

const WS_BASE = API_BASE.replace(/^http/, 'ws').replace('/api', '');

// ========================================
// STATE
// ========================================
const state = {
  accessToken: localStorage.getItem('accessToken') || null,
  refreshToken: localStorage.getItem('refreshToken') || null,
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  ws: null,
  expenseCategories: [],
};

// ========================================
// TOAST NOTIFICATIONS
// ========================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
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
    <span class="toast-message">${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}

// ========================================
// API UTILITIES
// ========================================
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = { ...options.headers };

  if (state.accessToken && !options.skipAuth) {
    headers['Authorization'] = `Bearer ${state.accessToken}`;
  }

  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  try {
    const response = await fetch(url, { ...options, headers });

    if (response.status === 401 && state.refreshToken) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        headers['Authorization'] = `Bearer ${state.accessToken}`;
        return fetch(url, { ...options, headers });
      }
    }

    return response;
  } catch (error) {
    console.error('API Request Error:', error);
    throw error;
  }
}

async function refreshAccessToken() {
  try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: state.refreshToken }),
    });

    if (response.ok) {
      const data = await response.json();
      state.accessToken = data.access_token;
      state.refreshToken = data.refresh_token;
      localStorage.setItem('accessToken', data.access_token);
      localStorage.setItem('refreshToken', data.refresh_token);
      return true;
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
  }

  logout();
  return false;
}

// ========================================
// AUTH
// ========================================
function showLandingPage() {
  document.getElementById('landing-page').classList.remove('hidden');
  document.getElementById('user-app').classList.add('hidden');
  document.getElementById('auth-modal').classList.add('hidden');
}

function showAuthModal() {
  document.getElementById('auth-modal').classList.remove('hidden');
}

function hideAuthModal() {
  document.getElementById('auth-modal').classList.add('hidden');
}

function showUserApp() {
  document.getElementById('landing-page').classList.add('hidden');
  document.getElementById('user-app').classList.remove('hidden');
  document.getElementById('auth-modal').classList.add('hidden');
}

function logout() {
  state.accessToken = null;
  state.refreshToken = null;
  state.user = null;
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');

  if (state.ws) {
    state.ws.close();
    state.ws = null;
  }

  showLandingPage();
  showToast('Sesión cerrada', 'info');
}

async function handleLogin(event) {
  event.preventDefault();
  const form = event.target;
  const email = form.querySelector('[name="email"]').value;
  const password = form.querySelector('[name="password"]').value;

  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Credenciales inválidas');
    }

    const data = await response.json();
    state.accessToken = data.access_token;
    state.refreshToken = data.refresh_token;
    localStorage.setItem('accessToken', data.access_token);
    localStorage.setItem('refreshToken', data.refresh_token);

    await fetchCurrentUser();
    hideAuthModal();
    showUserApp();
    initializeApp();
    showToast('¡Bienvenido!', 'success');
  } catch (error) {
    showToast(error.message, 'error');
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const form = event.target;
  const full_name = form.querySelector('[name="full_name"]').value;
  const email = form.querySelector('[name="email"]').value;
  const password = form.querySelector('[name="password"]').value;

  try {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ full_name, email, password, role: 'member' }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al registrar');
    }

    showToast('Cuenta creada exitosamente. Inicia sesión.', 'success');
    switchAuthTab('login');
    form.reset();
  } catch (error) {
    showToast(error.message, 'error');
  }
}

async function fetchCurrentUser() {
  try {
    const response = await apiRequest('/users/me');
    if (response.ok) {
      state.user = await response.json();
      localStorage.setItem('user', JSON.stringify(state.user));
      updateUserUI();
    }
  } catch (error) {
    console.error('Failed to fetch user:', error);
  }
}

function updateUserUI() {
  if (state.user) {
    document.getElementById('user-name').textContent = state.user.full_name || state.user.email;
    document.getElementById('user-role').textContent = state.user.role;

    // Show admin elements
    const isAdmin = state.user.role === 'admin';
    document.querySelectorAll('.admin-only').forEach(el => {
      el.style.display = isAdmin ? '' : 'none';
    });
  }
}

function switchAuthTab(tab) {
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
  
  document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
  document.getElementById(`${tab}-form`).classList.add('active');
}

// ========================================
// NAVIGATION
// ========================================
function navigateTo(section) {
  document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  
  document.querySelector(`[data-section="${section}"]`)?.classList.add('active');
  document.getElementById(`section-${section}`)?.classList.add('active');

  // Load section data
  switch (section) {
    case 'dashboard': loadDashboard(); break;
    case 'donations': loadDonations(); break;
    case 'documents': loadDocuments(); break;
    case 'events': loadEvents(); break;
    case 'expenses': loadExpenses(); break;
    case 'reports': loadReports(); break;
  }
}

function navigatePublicPage(page) {
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.querySelectorAll('.public-page').forEach(p => p.classList.remove('active'));
  
  document.querySelector(`.nav-link[data-page="${page}"]`)?.classList.add('active');
  document.getElementById(`page-${page}`)?.classList.add('active');

  if (page === 'events') loadPublicEvents();
}

// ========================================
// DASHBOARD
// ========================================
async function loadDashboard() {
  try {
    // Load summary for admins
    if (state.user?.role === 'admin') {
      const response = await apiRequest('/reports/summary');
      if (response.ok) {
        const data = await response.json();
        document.getElementById('stat-donations-count').textContent = data.total_donations;
        document.getElementById('stat-total-amount').textContent = formatCurrency(data.total_amount);
        renderBreakdownChart(data.by_type);
      }
    }

    // Load events count
    const eventsRes = await apiRequest('/events', { skipAuth: true });
    if (eventsRes.ok) {
      const events = await eventsRes.json();
      document.getElementById('stat-events-count').textContent = events.length;
    }

    // Load documents count
    if (state.user?.role === 'admin') {
      const docsRes = await apiRequest('/documents');
      if (docsRes.ok) {
        const docs = await docsRes.json();
        document.getElementById('stat-documents-count').textContent = docs.length;
      }
    }

    // Load recent donations
    const myDonationsRes = await apiRequest('/donations/me');
    if (myDonationsRes.ok) {
      const donations = await myDonationsRes.json();
      renderRecentActivity(donations.slice(0, 5));
    }

  } catch (error) {
    console.error('Failed to load dashboard:', error);
  }
}

function renderBreakdownChart(byType) {
  const container = document.getElementById('chart-by-type');
  if (!byType || Object.keys(byType).length === 0) {
    container.innerHTML = `
      <div class="chart-placeholder">
        <i class="ri-pie-chart-2-line"></i>
        <p>No hay datos para mostrar</p>
      </div>
    `;
    return;
  }

  const colors = { diezmo: '#8b5cf6', ofrenda: '#22c55e', misiones: '#06b6d4', especial: '#f59e0b' };
  const total = Object.values(byType).reduce((a, b) => a + b, 0);
  
  container.innerHTML = `
    <div class="breakdown-grid">
      ${Object.entries(byType).map(([type, count]) => `
        <div class="breakdown-item" style="border-left: 3px solid ${colors[type] || '#71717a'}">
          <div class="breakdown-type">${type}</div>
          <div class="breakdown-value">${count}</div>
          <div class="breakdown-count">${((count / total) * 100).toFixed(1)}%</div>
        </div>
      `).join('')}
    </div>
  `;
}

function renderRecentActivity(donations) {
  const container = document.getElementById('recent-activity');
  
  if (!donations || donations.length === 0) {
    container.innerHTML = `
      <div class="activity-empty">
        <i class="ri-inbox-line"></i>
        <p>No hay actividad reciente</p>
      </div>
    `;
    return;
  }

  container.innerHTML = donations.map(d => `
    <div class="activity-item">
      <div class="activity-icon donation">
        <i class="ri-heart-3-line"></i>
      </div>
      <div class="activity-content">
        <div class="activity-title">${formatCurrency(d.amount_total || d.amount)}</div>
        <div class="activity-meta">${formatDate(d.donation_date)}</div>
      </div>
    </div>
  `).join('');
}

// ========================================
// DONATIONS
// ========================================
async function loadDonations() {
  try {
    const endpoint = state.user?.role === 'admin' ? '/donations' : '/donations/me';
    const response = await apiRequest(endpoint);
    
    if (response.ok) {
      const donations = await response.json();
      renderDonationsTable(donations);
    }
  } catch (error) {
    console.error('Failed to load donations:', error);
    showToast('Error al cargar donaciones', 'error');
  }
}

function renderDonationsTable(donations) {
  const tbody = document.getElementById('donations-tbody');
  
  if (!donations || donations.length === 0) {
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

  tbody.innerHTML = donations.map(d => {
    const tithe = d.amount_tithe || 0;
    const offering = d.amount_offering || 0;
    const missions = d.amount_missions || 0;
    const total = d.amount_total || d.amount || 0;
    const method = d.is_cash && d.is_transfer ? 'Mixto' : (d.is_cash ? 'Efectivo' : (d.is_transfer ? 'Transferencia' : d.payment_method));
    
    return `
      <tr>
        <td>${formatDate(d.donation_date)}</td>
        <td>${d.is_anonymous ? '<span class="badge">OSI</span>' : d.donor_name}</td>
        <td>${tithe > 0 ? formatCurrency(tithe) : '—'}</td>
        <td>${offering > 0 ? formatCurrency(offering) : '—'}</td>
        <td>${missions > 0 ? formatCurrency(missions) : '—'}</td>
        <td><strong>${formatCurrency(total)}</strong></td>
        <td><span class="badge badge-primary">${method}</span></td>
      </tr>
    `;
  }).join('');
}

async function handleDonationSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  
  const tithe = parseFloat(formData.get('amount_tithe')) || 0;
  const offering = parseFloat(formData.get('amount_offering')) || 0;
  const missions = parseFloat(formData.get('amount_missions')) || 0;
  const special = parseFloat(formData.get('amount_special')) || 0;

  const payload = {
    donor_name: formData.get('donor_name'),
    donor_document: formData.get('donor_document') || null,
    donor_address: formData.get('donor_address') || null,
    donor_phone: formData.get('donor_phone') || null,
    amount_tithe: tithe,
    amount_offering: offering,
    amount_missions: missions,
    amount_special: special,
    cash_amount: tithe + offering + missions + special,
    transfer_amount: 0,
    donation_date: formData.get('donation_date'),
    envelope_number: formData.get('envelope_number') || null,
    note: formData.get('note') || null,
    is_anonymous: form.querySelector('[name="is_anonymous"]')?.checked || false,
  };

  try {
    const response = await apiRequest('/donations', {
      method: 'POST',
      body: payload,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al crear donación');
    }

    showToast('Donación registrada exitosamente', 'success');
    form.reset();
    document.getElementById('donation-date').valueAsDate = new Date();
    toggleFormCard('donation-form-card', false);
    loadDonations();
    loadDashboard();
  } catch (error) {
    showToast(error.message, 'error');
  }
}

async function exportDonationsCSV() {
  try {
    const month = document.getElementById('report-month')?.value || new Date().getMonth() + 1;
    const year = document.getElementById('report-year')?.value || new Date().getFullYear();
    
    const response = await apiRequest(`/reports/donations/monthly/csv?month=${month}&year=${year}`);
    if (response.ok) {
      const blob = await response.blob();
      downloadBlob(blob, `donaciones_${year}_${month}.csv`);
      showToast('Exportación completada', 'success');
    } else {
      throw new Error('Error al exportar');
    }
  } catch (error) {
    showToast(error.message, 'error');
  }
}

// ========================================
// DOCUMENTS
// ========================================
async function loadDocuments() {
  if (state.user?.role !== 'admin') {
    document.getElementById('documents-list').innerHTML = `
      <div class="empty-state">
        <i class="ri-lock-line"></i>
        <p>Solo administradores pueden ver documentos</p>
      </div>
    `;
    return;
  }

  try {
    const response = await apiRequest('/documents');
    if (response.ok) {
      const documents = await response.json();
      renderDocumentsGrid(documents);
    }
  } catch (error) {
    console.error('Failed to load documents:', error);
  }
}

function renderDocumentsGrid(documents) {
  const container = document.getElementById('documents-list');
  
  if (!documents || documents.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <i class="ri-folder-line"></i>
        <p>No hay documentos subidos</p>
      </div>
    `;
    return;
  }

  const icons = {
    'application/pdf': 'ri-file-pdf-2-line',
    'image/png': 'ri-image-line',
    'image/jpeg': 'ri-image-line',
  };

  container.innerHTML = documents.map(doc => `
    <div class="document-card" onclick="downloadDocument(${doc.id})">
      <div class="document-icon">
        <i class="${icons[doc.mime_type] || 'ri-file-line'}"></i>
      </div>
      <div class="document-name">${doc.file_name}</div>
      <div class="document-meta">${formatFileSize(doc.size_bytes)}</div>
    </div>
  `).join('');
}

async function downloadDocument(docId) {
  try {
    const response = await apiRequest(`/documents/${docId}`);
    if (response.ok) {
      const blob = await response.blob();
      const contentDisposition = response.headers.get('content-disposition');
      let filename = 'document';
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match) filename = match[1];
      }
      downloadBlob(blob, filename);
    }
  } catch (error) {
    showToast('Error al descargar', 'error');
  }
}

async function handleDocumentUpload(event) {
  event.preventDefault();
  const form = event.target;
  const fileInput = document.getElementById('doc-file');
  const file = fileInput.files[0];
  
  if (!file) {
    showToast('Por favor selecciona un archivo', 'warning');
    return;
  }

  if (file.size > 10 * 1024 * 1024) {
    showToast('El archivo excede el tamaño máximo de 10MB', 'error');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  formData.append('link_type', form.querySelector('[name="link_type"]').value);
  formData.append('ref_id', form.querySelector('[name="ref_id"]').value || '');
  formData.append('description', form.querySelector('[name="description"]').value || '');
  formData.append('is_public', 'false');

  try {
    const response = await apiRequest('/documents', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al subir documento');
    }

    showToast('Documento subido exitosamente', 'success');
    form.reset();
    toggleFormCard('document-form-card', false);
    loadDocuments();
  } catch (error) {
    showToast(error.message, 'error');
  }
}

// ========================================
// EVENTS
// ========================================
async function loadEvents() {
  try {
    const response = await apiRequest('/events', { skipAuth: true });
    if (response.ok) {
      const events = await response.json();
      renderEventsGrid(events);
    }
  } catch (error) {
    console.error('Failed to load events:', error);
  }
}

async function loadPublicEvents() {
  try {
    const response = await fetch(`${API_BASE}/events`);
    if (response.ok) {
      const events = await response.json();
      const container = document.getElementById('public-events-list');
      
      if (!events || events.length === 0) {
        container.innerHTML = '<p class="empty-message">No hay eventos programados</p>';
        return;
      }

      container.innerHTML = events.map(event => `
        <div class="event-card">
          <div class="event-header">
            <h4>${event.name}</h4>
            ${event.description ? `<p>${event.description}</p>` : ''}
          </div>
          <div class="event-body">
            <div class="event-meta">
              ${event.start_date ? `
                <div class="event-meta-item">
                  <i class="ri-calendar-line"></i>
                  <span>${formatDate(event.start_date)}</span>
                </div>
              ` : ''}
              ${event.capacity ? `
                <div class="event-meta-item">
                  <i class="ri-group-line"></i>
                  <span>Capacidad: ${event.capacity}</span>
                </div>
              ` : ''}
            </div>
            <div class="event-actions">
              <button class="btn btn-primary btn-sm" onclick="openRegistrationModal(${event.id}, '${event.name.replace(/'/g, "\\'")}')">
                <i class="ri-user-add-line"></i>
                <span>Inscribirse</span>
              </button>
            </div>
          </div>
        </div>
      `).join('');
    }
  } catch (error) {
    console.error('Failed to load public events:', error);
  }
}

function renderEventsGrid(events) {
  const container = document.getElementById('events-container');
  
  if (!events || events.length === 0) {
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
      <div class="event-header">
        <h4>${event.name}</h4>
        ${event.description ? `<p>${event.description}</p>` : ''}
      </div>
      <div class="event-body">
        <div class="event-meta">
          ${event.start_date ? `
            <div class="event-meta-item">
              <i class="ri-calendar-line"></i>
              <span>${formatDate(event.start_date)}${event.end_date ? ` — ${formatDate(event.end_date)}` : ''}</span>
            </div>
          ` : ''}
          ${event.capacity ? `
            <div class="event-meta-item">
              <i class="ri-group-line"></i>
              <span>Capacidad: ${event.capacity}</span>
            </div>
          ` : ''}
        </div>
        <div class="event-actions">
          <button class="btn btn-primary btn-sm" onclick="openRegistrationModal(${event.id}, '${event.name.replace(/'/g, "\\'")}')">
            <i class="ri-user-add-line"></i>
            <span>Inscribirse</span>
          </button>
          ${state.user?.role === 'admin' ? `
            <button class="btn btn-ghost btn-sm" onclick="viewRegistrations(${event.id})">
              <i class="ri-list-check"></i>
            </button>
          ` : ''}
        </div>
      </div>
    </div>
  `).join('');
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
    capacity: formData.get('capacity') ? parseInt(formData.get('capacity')) : null,
  };

  try {
    const response = await apiRequest('/events', { method: 'POST', body: payload });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al crear evento');
    }

    showToast('Evento creado exitosamente', 'success');
    form.reset();
    toggleFormCard('event-form-card', false);
    loadEvents();
  } catch (error) {
    showToast(error.message, 'error');
  }
}

// ========================================
// REGISTRATIONS
// ========================================
function openRegistrationModal(eventId, eventName) {
  document.getElementById('reg-event-id').value = eventId;
  document.querySelector('#registration-modal .modal-header h3').textContent = `Inscribirse: ${eventName}`;
  document.getElementById('registration-modal').classList.remove('hidden');
}

function closeRegistrationModal() {
  document.getElementById('registration-modal').classList.add('hidden');
  document.getElementById('registration-form').reset();
}

async function handleRegistrationSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const eventId = form.querySelector('[name="event_id"]').value;
  
  const payload = {
    attendee_name: form.querySelector('[name="attendee_name"]').value,
    attendee_email: form.querySelector('[name="attendee_email"]').value,
    notes: form.querySelector('[name="notes"]').value || null,
  };

  try {
    const response = await fetch(`${API_BASE}/events/${eventId}/registrations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al inscribirse');
    }

    showToast('¡Inscripción exitosa!', 'success');
    closeRegistrationModal();
  } catch (error) {
    showToast(error.message, 'error');
  }
}

async function viewRegistrations(eventId) {
  try {
    const response = await apiRequest(`/events/${eventId}/registrations`);
    if (response.ok) {
      const registrations = await response.json();
      alert(registrations.length > 0
        ? `Inscritos (${registrations.length}):\n${registrations.map(r => `• ${r.attendee_name} (${r.attendee_email})`).join('\n')}`
        : 'No hay inscripciones aún');
    }
  } catch (error) {
    showToast('Error al cargar inscripciones', 'error');
  }
}

// ========================================
// EXPENSES
// ========================================
async function loadExpenses() {
  await loadExpenseCategories();
  await loadExpenseSummary();
  await loadExpensesList();
}

async function loadExpenseCategories() {
  try {
    const response = await apiRequest('/expenses/categories');
    if (response.ok) {
      state.expenseCategories = await response.json();
      const select = document.getElementById('expense-category');
      select.innerHTML = '<option value="">Seleccionar...</option>' +
        state.expenseCategories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    }
  } catch (error) {
    console.error('Failed to load categories:', error);
  }
}

async function loadExpenseSummary() {
  try {
    const response = await apiRequest('/expenses/reports/summary');
    if (response.ok) {
      const data = await response.json();
      document.getElementById('expense-pending').textContent = formatCurrency(data.pending);
      document.getElementById('expense-approved').textContent = formatCurrency(data.approved);
      document.getElementById('expense-paid').textContent = formatCurrency(data.paid);
    }
  } catch (error) {
    console.error('Failed to load expense summary:', error);
  }
}

async function loadExpensesList() {
  try {
    const response = await apiRequest('/expenses');
    if (response.ok) {
      const expenses = await response.json();
      renderExpensesTable(expenses);
    }
  } catch (error) {
    console.error('Failed to load expenses:', error);
  }
}

function renderExpensesTable(expenses) {
  const tbody = document.getElementById('expenses-tbody');
  
  if (!expenses || expenses.length === 0) {
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

  const statusColors = {
    pending: 'badge',
    approved: 'badge badge-primary',
    paid: 'badge badge-success',
    cancelled: 'badge',
  };

  tbody.innerHTML = expenses.map(e => `
    <tr>
      <td>${formatDate(e.expense_date)}</td>
      <td>${e.category?.name || 'Sin categoría'}</td>
      <td>${e.description}</td>
      <td><strong>${formatCurrency(e.amount)}</strong></td>
      <td><span class="${statusColors[e.status] || 'badge'}">${e.status}</span></td>
      <td>
        ${e.status === 'pending' ? `
          <button class="btn btn-ghost btn-xs" onclick="approveExpense(${e.id})">
            <i class="ri-check-line"></i>
          </button>
        ` : ''}
        ${e.status === 'approved' ? `
          <button class="btn btn-ghost btn-xs" onclick="payExpense(${e.id})">
            <i class="ri-money-dollar-circle-line"></i>
          </button>
        ` : ''}
      </td>
    </tr>
  `).join('');
}

async function handleExpenseSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);

  const payload = {
    category_id: parseInt(formData.get('category_id')),
    subcategory_id: formData.get('subcategory_id') ? parseInt(formData.get('subcategory_id')) : null,
    description: formData.get('description'),
    amount: parseFloat(formData.get('amount')),
    expense_date: formData.get('expense_date'),
    vendor_name: formData.get('vendor_name') || null,
    vendor_document: formData.get('vendor_document') || null,
    payment_method: formData.get('payment_method'),
    invoice_number: formData.get('invoice_number') || null,
    notes: formData.get('notes') || null,
  };

  try {
    const response = await apiRequest('/expenses', { method: 'POST', body: payload });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al crear gasto');
    }

    showToast('Gasto registrado exitosamente', 'success');
    form.reset();
    toggleFormCard('expense-form-card', false);
    loadExpenses();
  } catch (error) {
    showToast(error.message, 'error');
  }
}

async function approveExpense(id) {
  try {
    const response = await apiRequest(`/expenses/${id}/approve`, { method: 'POST' });
    if (response.ok) {
      showToast('Gasto aprobado', 'success');
      loadExpenses();
    }
  } catch (error) {
    showToast('Error al aprobar gasto', 'error');
  }
}

async function payExpense(id) {
  try {
    const response = await apiRequest(`/expenses/${id}/pay`, { method: 'POST' });
    if (response.ok) {
      showToast('Gasto marcado como pagado', 'success');
      loadExpenses();
    }
  } catch (error) {
    showToast('Error al marcar como pagado', 'error');
  }
}

// ========================================
// REPORTS
// ========================================
function loadReports() {
  const now = new Date();
  document.getElementById('report-month').value = now.getMonth() + 1;
  document.getElementById('report-year').value = now.getFullYear();
  document.getElementById('expense-report-month').value = now.getMonth() + 1;
  document.getElementById('expense-report-year').value = now.getFullYear();
  
  const weekNum = getWeekNumber(now);
  document.getElementById('accountant-week').value = weekNum;
  document.getElementById('accountant-year').value = now.getFullYear();
}

function switchReportTab(reportType) {
  document.querySelectorAll('.report-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.report-panel').forEach(p => p.classList.remove('active'));
  
  document.querySelector(`.report-tab[data-report="${reportType}"]`)?.classList.add('active');
  document.getElementById(`report-${reportType}`)?.classList.add('active');
}

async function handleDonationReportFilter(event) {
  event.preventDefault();
  const month = document.getElementById('report-month').value;
  const year = document.getElementById('report-year').value;

  try {
    const response = await apiRequest(`/reports/donations/monthly?month=${month}&year=${year}`);
    if (response.ok) {
      const data = await response.json();
      document.getElementById('report-total-tithe').textContent = formatCurrency(data.summary.total_diezmo);
      document.getElementById('report-total-offering').textContent = formatCurrency(data.summary.total_ofrenda);
      document.getElementById('report-total-missions').textContent = formatCurrency(data.summary.total_misiones);
      document.getElementById('report-grand-total').textContent = formatCurrency(data.summary.gran_total);
    }
  } catch (error) {
    showToast('Error al generar reporte', 'error');
  }
}

async function handleAccountantReportFilter(event) {
  event.preventDefault();
  const week = document.getElementById('accountant-week').value;
  const year = document.getElementById('accountant-year').value;

  try {
    const response = await apiRequest(`/reports/donations/weekly/${week}?year=${year}`);
    if (response.ok) {
      const data = await response.json();
      
      document.getElementById('acc-fecha').textContent = data.fecha;
      document.getElementById('acc-semana').textContent = data.semana;
      document.getElementById('acc-sobres').textContent = data.numero_sobres;
      
      document.getElementById('acc-diezmo-efectivo').textContent = formatCurrency(data.diezmos_efectivo);
      document.getElementById('acc-diezmo-transferencia').textContent = formatCurrency(data.diezmos_transferencia);
      document.getElementById('acc-diezmo-total').textContent = formatCurrency(data.diezmos_total);
      
      document.getElementById('acc-ofrenda-efectivo').textContent = formatCurrency(data.ofrendas_efectivo);
      document.getElementById('acc-ofrenda-transferencia').textContent = formatCurrency(data.ofrendas_transferencia);
      document.getElementById('acc-ofrenda-total').textContent = formatCurrency(data.ofrendas_total);
      
      document.getElementById('acc-misiones-efectivo').textContent = formatCurrency(data.misiones_efectivo);
      document.getElementById('acc-misiones-transferencia').textContent = formatCurrency(data.misiones_transferencia);
      document.getElementById('acc-misiones-total').textContent = formatCurrency(data.misiones_total);
      
      document.getElementById('acc-total-efectivo').textContent = formatCurrency(data.total_efectivo);
      document.getElementById('acc-total-transferencia').textContent = formatCurrency(data.total_transferencia);
      document.getElementById('acc-valor-total').textContent = formatCurrency(data.valor_total);
      
      document.getElementById('acc-diezmo-diezmos').textContent = formatCurrency(data.diezmo_de_diezmos);
      
      document.getElementById('accountant-report-preview').style.display = 'block';
    }
  } catch (error) {
    showToast('Error al generar reporte', 'error');
  }
}

async function exportAccountantCSV() {
  const week = document.getElementById('accountant-week').value;
  const year = document.getElementById('accountant-year').value;

  try {
    const response = await apiRequest(`/reports/donations/weekly/${week}/csv?year=${year}`);
    if (response.ok) {
      const blob = await response.blob();
      downloadBlob(blob, `reporte_contadora_semana_${week}_${year}.csv`);
      showToast('Exportación completada', 'success');
    }
  } catch (error) {
    showToast('Error al exportar', 'error');
  }
}

// ========================================
// WEBSOCKET
// ========================================
function connectWebSocket() {
  if (!state.accessToken) return;

  try {
    const wsUrl = `${WS_BASE}/api/ws/notifications?token=${state.accessToken}`;
    state.ws = new WebSocket(wsUrl);

    state.ws.onopen = () => console.log('WebSocket connected');

    state.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'donation.created') {
          showToast(`Nueva donación: ${formatCurrency(data.amount)}`, 'info');
          loadDashboard();
        }
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    };

    state.ws.onclose = () => {
      setTimeout(() => state.accessToken && connectWebSocket(), 5000);
    };
  } catch (error) {
    console.error('WebSocket connection failed:', error);
  }
}

// ========================================
// UTILITIES
// ========================================
function formatCurrency(amount) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
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

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function getWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

function toggleFormCard(cardId, show) {
  const card = document.getElementById(cardId);
  if (show === undefined) {
    card.classList.toggle('hidden');
  } else {
    card.classList.toggle('hidden', !show);
  }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ========================================
// EVENT LISTENERS
// ========================================
function setupEventListeners() {
  // Auth tabs
  document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', () => switchAuthTab(tab.dataset.tab));
  });

  // Auth forms
  document.getElementById('login-form').addEventListener('submit', handleLogin);
  document.getElementById('register-form').addEventListener('submit', handleRegister);

  // Login button
  document.getElementById('btn-login').addEventListener('click', showAuthModal);
  document.getElementById('auth-modal-close').addEventListener('click', hideAuthModal);
  document.querySelector('#auth-modal .modal-backdrop')?.addEventListener('click', hideAuthModal);

  // Logout
  document.getElementById('logout-btn').addEventListener('click', logout);

  // Back to site
  document.getElementById('btn-back-to-site').addEventListener('click', showLandingPage);

  // Navigation
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo(item.dataset.section);
    });
  });

  // Public page navigation
  document.querySelectorAll('.nav-link[data-page]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      navigatePublicPage(link.dataset.page);
    });
  });

  // Hero buttons
  document.querySelectorAll('.hero-buttons [data-page]').forEach(btn => {
    btn.addEventListener('click', () => navigatePublicPage(btn.dataset.page));
  });

  // Dashboard refresh
  document.getElementById('refresh-dashboard').addEventListener('click', loadDashboard);

  // Donation form
  document.getElementById('new-donation-btn').addEventListener('click', () => {
    toggleFormCard('donation-form-card', true);
    document.getElementById('donation-date').valueAsDate = new Date();
  });
  document.getElementById('donation-form').addEventListener('submit', handleDonationSubmit);
  document.getElementById('export-donations-btn').addEventListener('click', exportDonationsCSV);

  // Document form
  document.getElementById('new-document-btn').addEventListener('click', () => toggleFormCard('document-form-card', true));
  document.getElementById('document-form').addEventListener('submit', handleDocumentUpload);

  // File upload
  const fileDropZone = document.getElementById('file-drop-zone');
  const fileInput = document.getElementById('doc-file');
  
  fileDropZone?.addEventListener('click', () => fileInput?.click());
  fileDropZone?.addEventListener('dragover', (e) => { e.preventDefault(); fileDropZone.classList.add('dragover'); });
  fileDropZone?.addEventListener('dragleave', () => fileDropZone.classList.remove('dragover'));
  fileDropZone?.addEventListener('drop', (e) => {
    e.preventDefault();
    fileDropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      document.getElementById('file-name').textContent = e.dataTransfer.files[0].name;
      document.getElementById('file-preview').classList.remove('hidden');
    }
  });
  
  fileInput?.addEventListener('change', () => {
    if (fileInput.files.length) {
      document.getElementById('file-name').textContent = fileInput.files[0].name;
      document.getElementById('file-preview').classList.remove('hidden');
    }
  });
  
  document.getElementById('remove-file')?.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.value = '';
    document.getElementById('file-preview').classList.add('hidden');
  });

  // Event form
  document.getElementById('new-event-btn')?.addEventListener('click', () => toggleFormCard('event-form-card', true));
  document.getElementById('event-form')?.addEventListener('submit', handleEventSubmit);

  // Registration form
  document.getElementById('registration-form')?.addEventListener('submit', handleRegistrationSubmit);
  document.querySelectorAll('.modal-close-btn').forEach(btn => {
    btn.addEventListener('click', closeRegistrationModal);
  });
  document.querySelector('#registration-modal .modal-backdrop')?.addEventListener('click', closeRegistrationModal);

  // Expense form
  document.getElementById('new-expense-btn')?.addEventListener('click', () => {
    toggleFormCard('expense-form-card', true);
    document.querySelector('#expense-form [name="expense_date"]').valueAsDate = new Date();
  });
  document.getElementById('expense-form')?.addEventListener('submit', handleExpenseSubmit);

  // Report tabs
  document.querySelectorAll('.report-tab').forEach(tab => {
    tab.addEventListener('click', () => switchReportTab(tab.dataset.report));
  });

  // Report filters
  document.getElementById('report-filters')?.addEventListener('submit', handleDonationReportFilter);
  document.getElementById('export-monthly-csv')?.addEventListener('click', exportDonationsCSV);
  document.getElementById('accountant-report-filters')?.addEventListener('submit', handleAccountantReportFilter);
  document.getElementById('export-accountant-csv')?.addEventListener('click', exportAccountantCSV);

  // Close form buttons
  document.querySelectorAll('.close-form-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const card = btn.closest('.form-card');
      if (card) card.classList.add('hidden');
    });
  });
}

// ========================================
// INITIALIZATION
// ========================================
function initializeApp() {
  if (state.accessToken && state.user) {
    showUserApp();
    updateUserUI();
    navigateTo('dashboard');
    connectWebSocket();
  } else if (state.accessToken) {
    fetchCurrentUser().then(() => {
      if (state.user) {
        showUserApp();
        navigateTo('dashboard');
        connectWebSocket();
      } else {
        showLandingPage();
      }
    });
  } else {
    showLandingPage();
    loadPublicEvents();
  }
}

// Start app
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  initializeApp();
});

// Expose functions for inline handlers
window.downloadDocument = downloadDocument;
window.openRegistrationModal = openRegistrationModal;
window.viewRegistrations = viewRegistrations;
window.approveExpense = approveExpense;
window.payExpense = payExpense;
