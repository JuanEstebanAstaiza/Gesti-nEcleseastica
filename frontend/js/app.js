/**
 * EKKLESIA - Sistema de Gestión Eclesiástica
 * Frontend JavaScript Module
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

  setTimeout(() => {
    toast.remove();
  }, 5000);
}

// ========================================
// API UTILITIES
// ========================================

async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    ...options.headers,
  };

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

function showAuthModal() {
  document.getElementById('auth-modal').classList.remove('hidden');
  document.getElementById('app').classList.add('hidden');
}

function hideAuthModal() {
  document.getElementById('auth-modal').classList.add('hidden');
  document.getElementById('app').classList.remove('hidden');
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

  showAuthModal();
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
      loadEvents();
      break;
    case 'reports':
      loadReports();
      break;
  }
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
        
        // Render breakdown chart
        renderBreakdownChart(data.by_type);
      }
    }

    // Load events count
    const eventsRes = await apiRequest('/events');
    if (eventsRes.ok) {
      const events = await eventsRes.json();
      document.getElementById('stat-events-count').textContent = events.length;
    }

    // Load documents count (admin only)
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
    showToast('Error al cargar el dashboard', 'error');
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

  const colors = {
    diezmo: '#8b5cf6',
    ofrenda: '#22c55e',
    misiones: '#06b6d4',
    especial: '#f59e0b',
  };

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
        <div class="activity-title">${d.donation_type} - ${formatCurrency(d.amount)}</div>
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
        <td colspan="5">
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
      <td><span class="badge badge-primary">${d.donation_type}</span></td>
      <td><strong>${formatCurrency(d.amount)}</strong></td>
      <td>${d.payment_method}</td>
      <td>${formatDate(d.donation_date)}</td>
      <td>${d.note || '—'}</td>
    </tr>
  `).join('');
}

async function handleDonationSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  
  const payload = {
    donor_name: state.user?.full_name || 'Anónimo',
    donation_type: formData.get('donation_type'),
    amount: parseFloat(formData.get('amount')),
    payment_method: formData.get('payment_method'),
    donation_date: formData.get('donation_date'),
    note: formData.get('note') || null,
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
    const response = await apiRequest('/reports/export');
    if (response.ok) {
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'donaciones_export.csv';
      a.click();
      URL.revokeObjectURL(url);
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
        <p>Solo administradores pueden ver todos los documentos</p>
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
    showToast('Error al cargar documentos', 'error');
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
    'image/jpg': 'ri-image-line',
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
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } else {
      throw new Error('Error al descargar');
    }
  } catch (error) {
    showToast(error.message, 'error');
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
    resetFileUpload();
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
    showToast('Error al cargar eventos', 'error');
  }
}

function renderEventsGrid(events) {
  const container = document.getElementById('events-container');
  
  if (!events || events.length === 0) {
    container.innerHTML = `
      <div class="empty-state-full">
        <i class="ri-calendar-todo-line"></i>
        <h3>No hay eventos programados</h3>
        <p>Crea tu primer evento para comenzar</p>
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
              <span>Capacidad: ${event.capacity} personas</span>
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
              <span>Ver inscritos</span>
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
    const response = await apiRequest('/events', {
      method: 'POST',
      body: payload,
    });

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
      
      const message = registrations.length > 0
        ? `Inscritos (${registrations.length}):\n${registrations.map(r => `• ${r.attendee_name} (${r.attendee_email})`).join('\n')}`
        : 'No hay inscripciones aún';
      
      alert(message); // TODO: Replace with a proper modal
    }
  } catch (error) {
    showToast('Error al cargar inscripciones', 'error');
  }
}

// ========================================
// REPORTS
// ========================================

async function loadReports() {
  if (state.user?.role !== 'admin') {
    showToast('Solo administradores pueden ver reportes', 'warning');
    navigateTo('dashboard');
    return;
  }

  // Set default dates
  const today = new Date();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
  
  document.getElementById('report-from').valueAsDate = firstDay;
  document.getElementById('report-to').valueAsDate = today;
  
  await fetchReportData();
}

async function fetchReportData() {
  const form = document.getElementById('report-filters');
  const formData = new FormData(form);
  
  const params = new URLSearchParams();
  if (formData.get('from_date')) params.append('start_date', formData.get('from_date'));
  if (formData.get('to_date')) params.append('end_date', formData.get('to_date'));
  if (formData.get('donation_type')) params.append('donation_type', formData.get('donation_type'));

  try {
    const response = await apiRequest(`/reports/summary?${params.toString()}`);
    if (response.ok) {
      const data = await response.json();
      
      document.getElementById('report-total-count').textContent = data.total_donations;
      document.getElementById('report-total-amount').textContent = formatCurrency(data.total_amount);
      
      const avg = data.total_donations > 0 
        ? data.total_amount / data.total_donations 
        : 0;
      document.getElementById('report-average').textContent = formatCurrency(avg);
      
      renderReportBreakdown(data.by_type);
    }
  } catch (error) {
    console.error('Failed to load reports:', error);
    showToast('Error al cargar reportes', 'error');
  }
}

function renderReportBreakdown(byType) {
  const container = document.getElementById('report-breakdown');
  
  if (!byType || Object.keys(byType).length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <i class="ri-pie-chart-line"></i>
        <p>No hay datos para el período seleccionado</p>
      </div>
    `;
    return;
  }

  container.innerHTML = Object.entries(byType).map(([type, count]) => `
    <div class="breakdown-item">
      <div class="breakdown-type">${type}</div>
      <div class="breakdown-value">${count}</div>
      <div class="breakdown-count">donaciones</div>
    </div>
  `).join('');
}

async function handleReportFilter(event) {
  event.preventDefault();
  await fetchReportData();
}

async function exportReportCSV() {
  const form = document.getElementById('report-filters');
  const formData = new FormData(form);
  
  const params = new URLSearchParams();
  if (formData.get('from_date')) params.append('start_date', formData.get('from_date'));
  if (formData.get('to_date')) params.append('end_date', formData.get('to_date'));
  if (formData.get('donation_type')) params.append('donation_type', formData.get('donation_type'));

  try {
    const response = await apiRequest(`/reports/export?${params.toString()}`);
    if (response.ok) {
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'reporte_donaciones.csv';
      a.click();
      URL.revokeObjectURL(url);
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

    state.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    state.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    };

    state.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    state.ws.onclose = () => {
      console.log('WebSocket closed');
      // Reconnect after 5 seconds
      setTimeout(() => {
        if (state.accessToken) {
          connectWebSocket();
        }
      }, 5000);
    };
  } catch (error) {
    console.error('WebSocket connection failed:', error);
  }
}

function handleWebSocketMessage(data) {
  switch (data.type) {
    case 'donation.created':
      showToast(`Nueva donación: ${formatCurrency(data.amount)} (${data.donation_type})`, 'info');
      if (document.getElementById('section-dashboard').classList.contains('active')) {
        loadDashboard();
      }
      if (document.getElementById('section-donations').classList.contains('active')) {
        loadDonations();
      }
      break;
    case 'event.created':
      showToast(`Nuevo evento: ${data.name}`, 'info');
      if (document.getElementById('section-events').classList.contains('active')) {
        loadEvents();
      }
      break;
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
  }).format(amount);
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

function toggleFormCard(cardId, show) {
  const card = document.getElementById(cardId);
  if (show === undefined) {
    card.classList.toggle('hidden');
  } else {
    card.classList.toggle('hidden', !show);
  }
}

function resetFileUpload() {
  const fileInput = document.getElementById('doc-file');
  const preview = document.getElementById('file-preview');
  const dropZone = document.getElementById('file-drop-zone');
  
  fileInput.value = '';
  preview.classList.add('hidden');
  dropZone.classList.remove('dragover');
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

  // Logout
  document.getElementById('logout-btn').addEventListener('click', logout);

  // Navigation
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo(item.dataset.section);
    });
  });

  // Section links
  document.querySelectorAll('[data-section]').forEach(link => {
    if (!link.classList.contains('nav-item')) {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo(link.dataset.section);
      });
    }
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
  document.getElementById('new-document-btn').addEventListener('click', () => {
    toggleFormCard('document-form-card', true);
  });
  document.getElementById('document-form').addEventListener('submit', handleDocumentUpload);

  // File upload
  const fileDropZone = document.getElementById('file-drop-zone');
  const fileInput = document.getElementById('doc-file');
  const filePreview = document.getElementById('file-preview');

  fileDropZone.addEventListener('click', () => fileInput.click());
  
  fileDropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileDropZone.classList.add('dragover');
  });

  fileDropZone.addEventListener('dragleave', () => {
    fileDropZone.classList.remove('dragover');
  });

  fileDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    fileDropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      updateFilePreview(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
      updateFilePreview(fileInput.files[0]);
    }
  });

  document.getElementById('remove-file').addEventListener('click', (e) => {
    e.stopPropagation();
    resetFileUpload();
  });

  // Event form
  document.getElementById('new-event-btn').addEventListener('click', () => {
    toggleFormCard('event-form-card', true);
  });
  document.getElementById('event-form').addEventListener('submit', handleEventSubmit);

  // Registration form
  document.getElementById('registration-form').addEventListener('submit', handleRegistrationSubmit);
  document.querySelectorAll('.modal-close-btn').forEach(btn => {
    btn.addEventListener('click', closeRegistrationModal);
  });
  document.querySelector('#registration-modal .modal-backdrop').addEventListener('click', closeRegistrationModal);

  // Report filters
  document.getElementById('report-filters').addEventListener('submit', handleReportFilter);
  document.getElementById('export-report-btn').addEventListener('click', exportReportCSV);

  // Close form buttons
  document.querySelectorAll('.close-form-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const card = btn.closest('.form-card');
      if (card) card.classList.add('hidden');
    });
  });
}

function updateFilePreview(file) {
  const preview = document.getElementById('file-preview');
  const fileName = document.getElementById('file-name');
  
  fileName.textContent = file.name;
  preview.classList.remove('hidden');
}

// ========================================
// INITIALIZATION
// ========================================

function initializeApp() {
  if (state.accessToken && state.user) {
    hideAuthModal();
    updateUserUI();
    navigateTo('dashboard');
    connectWebSocket();
  } else if (state.accessToken) {
    fetchCurrentUser().then(() => {
      if (state.user) {
        hideAuthModal();
        navigateTo('dashboard');
        connectWebSocket();
      } else {
        showAuthModal();
      }
    });
  } else {
    showAuthModal();
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
