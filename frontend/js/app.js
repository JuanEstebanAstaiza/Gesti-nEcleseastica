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
  document.getElementById('auth-modal')?.classList.remove('hidden');
}

function hideAuthModal() {
  document.getElementById('auth-modal')?.classList.add('hidden');
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
    
    // Check for pending event registration
    if (state.pendingEventRegistration) {
      const { eventId, eventName } = state.pendingEventRegistration;
      state.pendingEventRegistration = null;
      await registerToEvent(eventId, eventName);
    }
    
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

    showToast('Cuenta creada exitosamente', 'success');
    
    // Auto-login after registration
    const loginResponse = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    
    if (loginResponse.ok) {
      const data = await loginResponse.json();
      state.accessToken = data.access_token;
      state.refreshToken = data.refresh_token;
      localStorage.setItem('accessToken', data.access_token);
      localStorage.setItem('refreshToken', data.refresh_token);
      
      await fetchCurrentUser();
      hideAuthModal();
      
      // Check for pending event registration
      if (state.pendingEventRegistration) {
        const { eventId, eventName } = state.pendingEventRegistration;
        state.pendingEventRegistration = null;
        await registerToEvent(eventId, eventName);
      }
      
      initializeApp();
    } else {
      switchAuthTab('login');
    }
    
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
    
    const roleLabels = {
      admin: 'Administrador',
      member: 'Miembro',
      public: 'Visitante'
    };
    document.getElementById('user-role').textContent = roleLabels[state.user.role] || state.user.role;
    
    // Show/hide admin sections based on role
    const isAdmin = state.user.role === 'admin';
    
    const adminElements = [
      'admin-divider', 'admin-label',
      'nav-admin-donations', 'nav-admin-events', 'nav-admin-expenses',
      'nav-admin-announcements', 'nav-admin-documents', 'nav-admin-config', 'nav-admin-reports'
    ];
    
    adminElements.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = isAdmin ? '' : 'none';
    });

    // Show admin dashboard stats
    const adminStats = document.getElementById('admin-stats');
    if (adminStats) adminStats.style.display = isAdmin ? '' : 'none';
    
    const chartCard = document.getElementById('chart-card');
    if (chartCard) chartCard.style.display = isAdmin ? '' : 'none';
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
  console.log('Navigating to:', section);
  
  // Remove active from sidebar items only within sidebar-nav
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => item.classList.remove('active'));
  
  // Remove active from all user-app sections
  document.querySelectorAll('#user-app .section').forEach(s => s.classList.remove('active'));
  
  // Add active to the clicked nav item
  const navItem = document.querySelector(`.sidebar-nav [data-section="${section}"]`);
  if (navItem) navItem.classList.add('active');
  
  // Show the target section
  const targetSection = document.getElementById(`section-${section}`);
  if (targetSection) {
    targetSection.classList.add('active');
    console.log('Section found and activated:', `section-${section}`);
  } else {
    console.warn('Section not found:', `section-${section}`);
  }

  // Load section data
  switch (section) {
    case 'dashboard':
      loadDashboard();
      break;
    case 'donations':
    case 'my-donations':
      loadDonations();
      break;
    case 'documents':
      loadDocuments();
      break;
    case 'events':
    case 'my-events':
      loadEvents();
      break;
    case 'reports':
      loadReports();
      break;
    // Admin sections
    case 'admin-donations':
      loadAdminDonations();
      break;
    case 'admin-events':
      loadAdminEvents();
      break;
    case 'admin-expenses':
      loadAdminExpenses();
      break;
    case 'admin-announcements':
      loadAdminAnnouncements();
      break;
    case 'admin-documents':
      loadAdminDocuments();
      break;
    case 'admin-config':
      loadAdminConfig();
      break;
    case 'admin-reports':
      loadAdminReports();
      break;
  }
}

// ========================================
// DASHBOARD
// ========================================

async function loadDashboard() {
  try {
    const isAdmin = state.user?.role === 'admin';

    // Load summary for admins
    if (isAdmin) {
      const response = await apiRequest('/reports/summary');
      if (response.ok) {
        const data = await response.json();
        const countEl = document.getElementById('stat-donations-count');
        const amountEl = document.getElementById('stat-total-amount');
        
        if (countEl) countEl.textContent = data.total_donations || 0;
        if (amountEl) amountEl.textContent = formatCurrency(data.total_amount || 0);
        
        // Render breakdown chart
        renderBreakdownChart(data.by_type);
      }

      // Load events count
      const eventsRes = await apiRequest('/events');
      if (eventsRes.ok) {
        const events = await eventsRes.json();
        const eventsEl = document.getElementById('stat-events-count');
        if (eventsEl) eventsEl.textContent = events.length;
      }

      // Load documents count
      const docsRes = await apiRequest('/documents');
      if (docsRes.ok) {
        const docs = await docsRes.json();
        const docsEl = document.getElementById('stat-documents-count');
        if (docsEl) docsEl.textContent = docs.length;
      }
    }

    // Load recent donations for current user
    const endpoint = isAdmin ? '/donations' : '/donations/me';
    const myDonationsRes = await apiRequest(endpoint);
    if (myDonationsRes.ok) {
      const donations = await myDonationsRes.json();
      renderRecentActivity(donations.slice(0, 5));
    }

    // Set welcome name
    const welcomeEl = document.getElementById('welcome-name');
    if (welcomeEl && state.user) {
      welcomeEl.textContent = `¡Hola, ${state.user.full_name || 'Usuario'}!`;
    }

  } catch (error) {
    console.error('Failed to load dashboard:', error);
  }
}

function renderBreakdownChart(byType) {
  const container = document.getElementById('chart-by-type');
  if (!container) return;
  
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
      ${Object.entries(byType).map(([type, amount]) => `
        <div class="breakdown-item" style="border-left: 3px solid ${colors[type] || '#71717a'}">
          <div class="breakdown-type">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
          <div class="breakdown-value">${formatCurrency(amount)}</div>
          <div class="breakdown-count">${((amount / total) * 100).toFixed(1)}%</div>
        </div>
      `).join('')}
    </div>
  `;
}

function renderRecentActivity(donations) {
  const container = document.getElementById('recent-activity');
  if (!container) return;
  
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
        <div class="activity-meta">${formatDate(d.donation_date)} ${d.donor_name ? '- ' + d.donor_name : ''}</div>
      </div>
    </div>
  `).join('');
}

// ========================================
// DONATIONS
// ========================================

async function loadDonations() {
  try {
    const response = await apiRequest('/donations/me');
    
    if (response.ok) {
      const donations = await response.json();
      renderMyDonationsTable(donations);
    }
  } catch (error) {
    console.error('Failed to load donations:', error);
  }
}

function renderMyDonationsTable(donations) {
  const container = document.getElementById('my-donations-list');
  if (!container) return;
  
  if (!donations || donations.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <i class="ri-inbox-line"></i>
        <p>No tienes donaciones registradas</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>Tipo</th>
          <th>Monto</th>
          <th>Método</th>
          <th>Fecha</th>
          <th>Nota</th>
        </tr>
      </thead>
      <tbody>
        ${donations.map(d => `
          <tr>
            <td><span class="badge badge-primary">${d.donation_type}</span></td>
            <td><strong>${formatCurrency(d.amount)}</strong></td>
            <td>${d.payment_method}</td>
            <td>${formatDate(d.donation_date)}</td>
            <td>${d.note || '—'}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
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
  // Try multiple possible containers
  const container = document.getElementById('events-list') || 
                   document.getElementById('my-events-list') ||
                   document.getElementById('events-container');
  
  if (!container) return;
  
  if (!events || events.length === 0) {
    container.innerHTML = `
      <div class="empty-state-full">
        <i class="ri-calendar-todo-line"></i>
        <h3>No hay eventos programados</h3>
        <p>Próximamente más información</p>
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
  // Helper function to safely add event listeners
  function addEvent(selector, event, handler) {
    const el = typeof selector === 'string' ? document.getElementById(selector) : selector;
    if (el) el.addEventListener(event, handler);
  }
  
  function addEventQuery(selector, event, handler) {
    const el = document.querySelector(selector);
    if (el) el.addEventListener(event, handler);
  }

  // ========== LANDING PAGE EVENTS ==========
  
  // Login button on landing page
  addEvent('btn-login', 'click', () => {
    showAuthModal();
  });
  
  // Landing page navigation (data-page)
  document.querySelectorAll('[data-page]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const page = link.dataset.page;
      
      // Hide all public pages
      document.querySelectorAll('.public-page').forEach(p => p.classList.remove('active'));
      // Show selected page
      const targetPage = document.getElementById(`page-${page}`);
      if (targetPage) targetPage.classList.add('active');
      
      // Update nav links
      document.querySelectorAll('.header-nav .nav-link').forEach(l => l.classList.remove('active'));
      document.querySelector(`.header-nav [data-page="${page}"]`)?.classList.add('active');
      
      // Load content for the page
      loadPublicPageContent(page);
    });
  });

  // ========== AUTH MODAL EVENTS ==========
  
  // Auth tabs
  document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', () => switchAuthTab(tab.dataset.tab));
  });

  // Auth forms
  addEvent('login-form', 'submit', handleLogin);
  addEvent('register-form', 'submit', handleRegister);
  
  // Modal close buttons
  document.querySelectorAll('.modal-close-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal');
      if (modal) modal.classList.add('hidden');
    });
  });
  
  // Modal backdrop clicks
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', () => {
      const modal = backdrop.closest('.modal');
      if (modal) modal.classList.add('hidden');
    });
  });

  // ========== APP EVENTS (only if logged in) ==========
  
  // Logout
  addEvent('logout-btn', 'click', logout);
  
  // Back to site button
  addEvent('btn-back-to-site', 'click', () => {
    document.getElementById('user-app')?.classList.add('hidden');
    document.getElementById('landing-page')?.classList.remove('hidden');
  });

  // Navigation in app (sidebar)
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      const section = this.dataset.section;
      if (section) {
        console.log('Sidebar click:', section);
        navigateTo(section);
      }
      return false;
    });
  });

  // Section links
  document.querySelectorAll('[data-section]').forEach(link => {
    if (!link.classList.contains('nav-item')) {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        if (link.dataset.section) {
          navigateTo(link.dataset.section);
        }
      });
    }
  });

  // Dashboard refresh
  addEvent('refresh-dashboard', 'click', loadDashboard);

  // Donation form
  addEvent('new-donation-btn', 'click', () => {
    toggleFormCard('donation-form-card', true);
    const dateInput = document.getElementById('donation-date');
    if (dateInput) dateInput.valueAsDate = new Date();
  });
  addEvent('donation-form', 'submit', handleDonationSubmit);
  addEvent('export-donations-btn', 'click', exportDonationsCSV);

  // Document form
  addEvent('new-document-btn', 'click', () => {
    toggleFormCard('document-form-card', true);
  });
  addEvent('document-form', 'submit', handleDocumentUpload);

  // File upload
  const fileDropZone = document.getElementById('file-drop-zone');
  const fileInput = document.getElementById('doc-file');

  if (fileDropZone && fileInput) {
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
  }

  addEvent('remove-file', 'click', (e) => {
    e.stopPropagation();
    resetFileUpload();
  });

  // Event form
  addEvent('new-event-btn', 'click', () => {
    toggleFormCard('event-form-card', true);
  });
  addEvent('event-form', 'submit', handleEventSubmit);

  // Registration form
  addEvent('registration-form', 'submit', handleRegistrationSubmit);
  addEventQuery('#registration-modal .modal-backdrop', 'click', closeRegistrationModal);

  // Report filters
  addEvent('report-filters', 'submit', handleReportFilter);
  addEvent('export-report-btn', 'click', exportReportCSV);

  // Close form buttons
  document.querySelectorAll('.close-form-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const card = btn.closest('.form-card');
      if (card) card.classList.add('hidden');
    });
  });
  
  // Setup admin event listeners
  setupAdminEventListeners();
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
  // Check if user is logged in
  if (state.accessToken && state.user) {
    // User is logged in, show app
    showUserApp();
    updateUserUI();
    navigateTo('dashboard');
    connectWebSocket();
  } else if (state.accessToken) {
    // Have token but no user, try to fetch
    fetchCurrentUser().then(() => {
      if (state.user) {
        showUserApp();
        updateUserUI();
        navigateTo('dashboard');
        connectWebSocket();
      } else {
        // Token invalid, show landing page
        showLandingPage();
      }
    }).catch(() => {
      showLandingPage();
    });
  } else {
    // Not logged in, show landing page
    showLandingPage();
  }
}

function showLandingPage() {
  document.getElementById('landing-page')?.classList.remove('hidden');
  document.getElementById('user-app')?.classList.add('hidden');
  document.getElementById('auth-modal')?.classList.add('hidden');
}

function showUserApp() {
  document.getElementById('landing-page')?.classList.add('hidden');
  document.getElementById('user-app')?.classList.remove('hidden');
  document.getElementById('auth-modal')?.classList.add('hidden');
}

// Start app
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  loadPublicConfig(); // Cargar configuración de la iglesia
  loadFeaturedEvents(); // Cargar eventos destacados en landing
  loadPublicAnnouncements(); // Cargar anuncios públicos
  initializeApp();
});

// Cargar eventos destacados en la landing page
async function loadFeaturedEvents() {
  const container = document.getElementById('featured-events');
  if (!container) return;
  
  try {
    const response = await fetch(`${API_BASE}/public/events?limit=3`);
    if (!response.ok) throw new Error('Error al cargar eventos');
    
    const events = await response.json();
    
    if (!events || events.length === 0) {
      container.innerHTML = `
        <div class="event-preview-card">
          <div class="event-info">
            <h3>No hay eventos próximos</h3>
            <p>Pronto anunciaremos nuevos eventos</p>
          </div>
        </div>
      `;
      return;
    }
    
    container.innerHTML = events.slice(0, 3).map(e => {
      const date = e.start_date ? new Date(e.start_date) : null;
      const day = date ? date.getDate() : '--';
      const month = date ? date.toLocaleDateString('es-CO', { month: 'short' }).toUpperCase() : '---';
      
      return `
        <div class="event-preview-card" data-event-id="${e.id}">
          <div class="event-date">
            <span class="day">${day}</span>
            <span class="month">${month}</span>
          </div>
          <div class="event-info">
            <h3>${e.name}</h3>
            <p>${e.description || e.location || 'Próximamente más información'}</p>
          </div>
        </div>
      `;
    }).join('');
  } catch (error) {
    console.error('Error loading featured events:', error);
  }
}

// Cargar anuncios públicos en la landing page
async function loadPublicAnnouncements() {
  const container = document.getElementById('announcements-list');
  const section = document.getElementById('announcements-section');
  
  if (!container) return;
  
  try {
    const response = await fetch(`${API_BASE}/public/announcements?limit=4`);
    if (!response.ok) return;
    
    const announcements = await response.json();
    
    if (!announcements || announcements.length === 0) {
      // Keep section hidden if no announcements
      return;
    }
    
    // Show section if we have announcements
    if (section) section.style.display = 'block';
    
    container.innerHTML = announcements.map(a => `
      <div class="announcement-card">
        <div class="announcement-icon"><i class="ri-megaphone-line"></i></div>
        <div class="announcement-content">
          <h3>${a.title}</h3>
          <p>${a.content || ''}</p>
        </div>
      </div>
    `).join('');
  } catch (error) {
    console.error('Error loading announcements:', error);
  }
}

// Cargar configuración pública de la iglesia
async function loadPublicConfig() {
  try {
    const response = await fetch(`${API_BASE}/public/config`);
    if (!response.ok) return;
    
    const config = await response.json();
    state.churchConfig = config;
    
    // Actualizar nombre de la iglesia en todos los lugares
    const churchNameElements = [
      'church-name-header',
      'church-name-hero',
      'app-church-name'
    ];
    
    churchNameElements.forEach(id => {
      const el = document.getElementById(id);
      if (el && config.church_name) el.textContent = config.church_name;
    });
    
    // Actualizar eslogan
    const sloganEl = document.getElementById('church-slogan');
    if (sloganEl && config.slogan) sloganEl.textContent = config.slogan;
    
    // Actualizar logo en header público
    const headerLogo = document.getElementById('church-logo');
    if (headerLogo && config.logo_url) {
      headerLogo.innerHTML = `<img src="${config.logo_url}" alt="${config.church_name}" style="max-height: 40px; max-width: 40px; border-radius: 8px;" />`;
    }
    
    // Actualizar logo en sidebar del panel de usuario
    const sidebarLogo = document.querySelector('.sidebar-logo');
    if (sidebarLogo && config.logo_url) {
      sidebarLogo.innerHTML = `<img src="${config.logo_url}" alt="${config.church_name}" style="max-height: 48px; max-width: 48px; border-radius: 8px;" />`;
    }
    
    // Actualizar imagen de portada en el hero
    if (config.cover_image_url) {
      const heroSection = document.getElementById('hero-section');
      if (heroSection) {
        heroSection.style.setProperty('--hero-bg-image', `url(${config.cover_image_url})`);
      }
    }
    
    // Actualizar colores de marca
    if (config.primary_color) {
      document.documentElement.style.setProperty('--accent-primary', config.primary_color);
    }
    if (config.secondary_color) {
      document.documentElement.style.setProperty('--accent-secondary', config.secondary_color);
    }
    
    // Actualizar horarios de servicio
    if (config.service_schedule && Array.isArray(config.service_schedule)) {
      renderPublicSchedule(config.service_schedule);
    }
    
    // Actualizar sección "Quiénes Somos"
    if (config.about_us) {
      const historyEl = document.getElementById('about-history');
      if (historyEl) historyEl.textContent = config.about_us;
    }
    if (config.mission) {
      const missionEl = document.getElementById('about-mission');
      if (missionEl) missionEl.textContent = config.mission;
    }
    if (config.vision) {
      const visionEl = document.getElementById('about-vision');
      if (visionEl) visionEl.textContent = config.vision;
    }
    if (config.values) {
      const valuesEl = document.getElementById('about-values');
      if (valuesEl) valuesEl.textContent = config.values;
    }
    
    // Actualizar información de contacto
    if (config.address) {
      const addrEl = document.getElementById('contact-address');
      if (addrEl) addrEl.textContent = `${config.address}${config.city ? ', ' + config.city : ''}${config.country ? ', ' + config.country : ''}`;
    }
    if (config.phone) {
      const phoneEl = document.getElementById('contact-phone');
      if (phoneEl) phoneEl.textContent = config.phone;
    }
    if (config.email) {
      const emailEl = document.getElementById('contact-email');
      if (emailEl) emailEl.textContent = config.email;
    }
    
    // Actualizar redes sociales
    updateSocialLinks(config);
    
  } catch (error) {
    console.log('Could not load public config');
  }
}

function renderPublicSchedule(schedules) {
  const container = document.getElementById('service-schedule');
  if (!container || !schedules.length) return;
  
  // Agrupar por día
  const byDay = {};
  schedules.forEach(s => {
    if (!byDay[s.day]) byDay[s.day] = [];
    byDay[s.day].push(s);
  });
  
  const dayIcons = {
    'Domingo': 'ri-sun-line',
    'Lunes': 'ri-moon-line',
    'Martes': 'ri-moon-line',
    'Miércoles': 'ri-moon-line',
    'Jueves': 'ri-moon-line',
    'Viernes': 'ri-group-line',
    'Sábado': 'ri-group-line'
  };
  
  container.innerHTML = Object.entries(byDay).map(([day, services]) => `
    <div class="service-card">
      <i class="${dayIcons[day] || 'ri-calendar-line'}"></i>
      <h3>${day}</h3>
      ${services.map(s => `<p>${s.time || ''} ${s.time ? '-' : ''} ${s.name}</p>`).join('')}
    </div>
  `).join('');
}

function updateSocialLinks(config) {
  const container = document.getElementById('social-links');
  if (!container) return;
  
  const links = [];
  if (config.social_facebook) links.push({ url: config.social_facebook, icon: 'ri-facebook-fill', name: 'Facebook' });
  if (config.social_instagram) links.push({ url: config.social_instagram, icon: 'ri-instagram-line', name: 'Instagram' });
  if (config.social_youtube) links.push({ url: config.social_youtube, icon: 'ri-youtube-line', name: 'YouTube' });
  if (config.social_twitter) links.push({ url: config.social_twitter, icon: 'ri-twitter-x-line', name: 'Twitter' });
  if (config.social_tiktok) links.push({ url: config.social_tiktok, icon: 'ri-tiktok-line', name: 'TikTok' });
  
  if (links.length === 0) {
    container.innerHTML = '';
    return;
  }
  
  container.innerHTML = links.map(l => `
    <a href="${l.url}" target="_blank" rel="noopener" class="social-link" title="${l.name}">
      <i class="${l.icon}"></i>
    </a>
  `).join('');
}

// Expose functions for inline handlers
window.downloadDocument = downloadDocument;
window.openRegistrationModal = openRegistrationModal;
window.viewRegistrations = viewRegistrations;

// ========================================
// PUBLIC PAGE CONTENT
// ========================================

async function loadPublicPageContent(page) {
  switch (page) {
    case 'events':
      await loadPublicEvents();
      break;
    case 'about':
      await loadPublicAbout();
      break;
    case 'donate':
      await loadPublicDonateInfo();
      break;
    case 'live':
      await loadPublicLiveStreams();
      break;
    case 'home':
    default:
      // Home ya se carga con loadPublicConfig
      break;
  }
}

async function loadPublicEvents() {
  const container = document.getElementById('events-list');
  if (!container) return;
  
  try {
    const response = await fetch(`${API_BASE}/public/events`);
    if (!response.ok) throw new Error('Error al cargar eventos');
    
    const events = await response.json();
    
    if (!events || events.length === 0) {
      container.innerHTML = `
        <div class="empty-state-full">
          <i class="ri-calendar-todo-line"></i>
          <h3>No hay eventos programados</h3>
          <p>Pronto anunciaremos nuevos eventos</p>
        </div>
      `;
      return;
    }
    
    container.innerHTML = `
      <div class="events-grid">
        ${events.map(e => `
          <div class="event-card public-event-card" data-event-id="${e.id}">
            ${e.image_url ? `<div class="event-image"><img src="${e.image_url}" alt="${e.name}"></div>` : `
              <div class="event-image event-image-placeholder">
                <i class="ri-calendar-event-fill"></i>
              </div>
            `}
            <div class="event-content">
              <div class="event-date">
                <i class="ri-calendar-line"></i>
                ${e.start_date ? new Date(e.start_date).toLocaleDateString('es-CO', {weekday: 'long', day: 'numeric', month: 'long'}) : 'Próximamente'}
              </div>
              <h3>${e.name}</h3>
              <p>${e.description || ''}</p>
              <div class="event-meta">
                ${e.location ? `<div class="event-location"><i class="ri-map-pin-line"></i> ${e.location}</div>` : ''}
                ${e.start_time ? `<div class="event-time"><i class="ri-time-line"></i> ${e.start_time}</div>` : ''}
              </div>
              <button class="btn btn-primary btn-register-event" data-event-id="${e.id}" data-event-name="${e.name}">
                <i class="ri-user-add-line"></i>
                <span>Inscribirse</span>
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    `;
    
    // Add event listeners for registration buttons
    container.querySelectorAll('.btn-register-event').forEach(btn => {
      btn.addEventListener('click', () => {
        const eventId = btn.dataset.eventId;
        const eventName = btn.dataset.eventName;
        handlePublicEventRegistration(eventId, eventName);
      });
    });
  } catch (error) {
    console.error('Error loading public events:', error);
    container.innerHTML = `
      <div class="empty-state-full">
        <i class="ri-error-warning-line"></i>
        <h3>Error al cargar eventos</h3>
        <p>Intenta nuevamente más tarde</p>
      </div>
    `;
  }
}

function handlePublicEventRegistration(eventId, eventName) {
  // Check if user is logged in
  if (state.accessToken && state.user) {
    // User is logged in, proceed with registration
    registerToEvent(eventId, eventName);
  } else {
    // User not logged in, save event info and show auth modal
    state.pendingEventRegistration = { eventId, eventName };
    showAuthModal();
    showToast('Inicia sesión o regístrate para inscribirte al evento', 'info');
  }
}

async function registerToEvent(eventId, eventName) {
  try {
    const response = await apiRequest(`/events/${eventId}/registrations`, {
      method: 'POST',
      body: {
        attendee_name: state.user.full_name || state.user.email,
        attendee_email: state.user.email
      }
    });
    
    if (response.ok) {
      showToast(`¡Te has inscrito a "${eventName}"!`, 'success');
      // Update button state
      const btn = document.querySelector(`.btn-register-event[data-event-id="${eventId}"]`);
      if (btn) {
        btn.innerHTML = '<i class="ri-check-line"></i><span>Inscrito</span>';
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-success');
        btn.disabled = true;
      }
    } else {
      const error = await response.json();
      throw new Error(error.detail || 'Error al inscribirse');
    }
  } catch (error) {
    console.error('Registration error:', error);
    if (error.message.includes('already registered')) {
      showToast('Ya estás inscrito en este evento', 'info');
    } else {
      showToast(error.message || 'Error al inscribirse al evento', 'error');
    }
  }
}

async function loadPublicAbout() {
  if (!state.churchConfig) {
    await loadPublicConfig();
  }
  
  const config = state.churchConfig;
  if (!config) return;
  
  // Update About section with church info
  const historyEl = document.getElementById('about-history');
  const missionEl = document.getElementById('about-mission');
  const visionEl = document.getElementById('about-vision');
  const valuesEl = document.getElementById('about-values');
  
  if (historyEl) historyEl.textContent = config.history || config.about_us || 'Información no disponible';
  if (missionEl) missionEl.textContent = config.mission || 'Información no disponible';
  if (visionEl) visionEl.textContent = config.vision || 'Información no disponible';
  if (valuesEl) valuesEl.textContent = config.values || 'Información no disponible';
  
  // Update contact info
  const addressEl = document.getElementById('contact-address');
  const phoneEl = document.getElementById('contact-phone');
  const emailEl = document.getElementById('contact-email');
  
  if (addressEl) addressEl.textContent = config.address ? `${config.address}${config.city ? `, ${config.city}` : ''}` : 'Dirección no disponible';
  if (phoneEl) phoneEl.textContent = config.phone || 'Teléfono no disponible';
  if (emailEl) emailEl.textContent = config.email || 'Email no disponible';
  
  // Update social links
  const socialLinksEl = document.getElementById('social-links');
  if (socialLinksEl) {
    let socialHtml = '';
    if (config.social_facebook) socialHtml += `<a href="${config.social_facebook}" target="_blank" class="social-link"><i class="ri-facebook-fill"></i></a>`;
    if (config.social_instagram) socialHtml += `<a href="${config.social_instagram}" target="_blank" class="social-link"><i class="ri-instagram-fill"></i></a>`;
    if (config.social_youtube) socialHtml += `<a href="${config.social_youtube}" target="_blank" class="social-link"><i class="ri-youtube-fill"></i></a>`;
    if (config.social_twitter) socialHtml += `<a href="${config.social_twitter}" target="_blank" class="social-link"><i class="ri-twitter-x-fill"></i></a>`;
    if (config.social_tiktok) socialHtml += `<a href="${config.social_tiktok}" target="_blank" class="social-link"><i class="ri-tiktok-fill"></i></a>`;
    socialLinksEl.innerHTML = socialHtml || '<p>No hay redes sociales configuradas</p>';
  }
}

async function loadPublicDonateInfo() {
  if (!state.churchConfig) return;
  
  const config = state.churchConfig;
  
  const donateIntro = document.getElementById('donate-intro');
  if (donateIntro && config.donation_info) {
    donateIntro.innerHTML = `<p>${config.donation_info}</p>`;
  }
  
  const bankInfoEl = document.getElementById('bank-info');
  if (bankInfoEl && config.bank_info) {
    const bankInfo = typeof config.bank_info === 'string' ? JSON.parse(config.bank_info) : config.bank_info;
    bankInfoEl.innerHTML = `
      <h3>Información Bancaria</h3>
      ${bankInfo.bank_name ? `<p><strong>Banco:</strong> ${bankInfo.bank_name}</p>` : ''}
      ${bankInfo.account_number ? `<p><strong>Cuenta:</strong> ${bankInfo.account_number}</p>` : ''}
      ${bankInfo.account_type ? `<p><strong>Tipo:</strong> ${bankInfo.account_type}</p>` : ''}
      ${bankInfo.account_holder ? `<p><strong>Titular:</strong> ${bankInfo.account_holder}</p>` : ''}
    `;
  }
  
  if (config.donation_link) {
    const donateBtn = document.getElementById('donate-btn');
    if (donateBtn) {
      donateBtn.href = config.donation_link;
    }
  }
}

async function loadPublicLiveStreams() {
  const noLiveState = document.getElementById('no-live-state');
  const livePlayer = document.getElementById('live-player');
  const liveIframe = document.getElementById('live-iframe');
  const liveTitle = document.getElementById('live-title');
  const liveDescription = document.getElementById('live-description');
  
  if (!noLiveState || !livePlayer) return;
  
  try {
    const response = await fetch(`${API_BASE}/public/streams`);
    if (!response.ok) throw new Error('Error');
    
    const streams = await response.json();
    
    const activeStream = streams.find(s => s.is_live) || streams.find(s => s.is_featured);
    
    if (activeStream) {
      let embedUrl = '';
      if (activeStream.youtube_video_id) {
        embedUrl = `https://www.youtube.com/embed/${activeStream.youtube_video_id}?autoplay=1`;
      } else if (activeStream.stream_url) {
        embedUrl = activeStream.stream_url;
      }
      
      if (embedUrl && liveIframe) {
        liveIframe.src = embedUrl;
        if (liveTitle) liveTitle.textContent = activeStream.title;
        if (liveDescription) liveDescription.textContent = activeStream.description || '';
        
        noLiveState.style.display = 'none';
        livePlayer.style.display = 'block';
      } else {
        noLiveState.style.display = 'flex';
        livePlayer.style.display = 'none';
      }
    } else {
      noLiveState.style.display = 'flex';
      livePlayer.style.display = 'none';
    }
  } catch (error) {
    console.error('Error loading streams:', error);
    noLiveState.style.display = 'flex';
    livePlayer.style.display = 'none';
  }
}

// ========================================
// ADMIN FUNCTIONS
// ========================================

// Admin Donations
async function loadAdminDonations() {
  try {
    const response = await apiRequest('/donations');
    if (!response.ok) throw new Error('Error al cargar donaciones');
    
    const donations = await response.json();
    const container = document.getElementById('admin-donations-list');
    
    if (!donations.length) {
      container.innerHTML = '<p class="empty-message">No hay donaciones registradas</p>';
      return;
    }
    
    container.innerHTML = `
      <table class="data-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Donante</th>
            <th>Tipo</th>
            <th>Monto</th>
            <th>Método</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          ${donations.map(d => `
            <tr>
              <td>${new Date(d.donation_date).toLocaleDateString()}</td>
              <td>${d.donor_name}</td>
              <td><span class="badge">${d.donation_type}</span></td>
              <td class="text-right">$${parseFloat(d.amount).toLocaleString()}</td>
              <td>${d.payment_method}</td>
              <td>
                <button class="btn btn-ghost btn-sm" onclick="viewDonation(${d.id})">
                  <i class="ri-eye-line"></i>
                </button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  } catch (error) {
    console.error('Error loading donations:', error);
    showToast('Error al cargar donaciones', 'error');
  }
}

// Admin Events
async function loadAdminEvents() {
  try {
    const response = await apiRequest('/admin/events');
    if (!response.ok) throw new Error('Error al cargar eventos');
    
    const events = await response.json();
    const container = document.getElementById('admin-events-list');
    
    if (!events.length) {
      container.innerHTML = '<p class="empty-message">No hay eventos creados</p>';
      return;
    }
    
    container.innerHTML = `
      <table class="data-table">
        <thead>
          <tr>
            <th>Evento</th>
            <th>Fecha</th>
            <th>Ubicación</th>
            <th>Registrados</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          ${events.map(e => {
            const registered = e.registered_count || 0;
            const capacity = e.capacity;
            const capacityText = capacity ? `${registered}/${capacity}` : `${registered} (sin límite)`;
            const isFull = capacity && registered >= capacity;
            return `
            <tr>
              <td><strong>${e.name}</strong></td>
              <td>${e.start_date ? new Date(e.start_date).toLocaleDateString() : '-'}</td>
              <td>${e.location || '-'}</td>
              <td>
                <span class="badge ${isFull ? 'badge-danger' : 'badge-info'}">
                  ${capacityText}
                </span>
              </td>
              <td>
                <span class="badge ${e.is_public ? 'badge-success' : 'badge-warning'}">
                  ${e.is_public ? 'Público' : 'Privado'}
                </span>
              </td>
              <td>
                <button class="btn btn-ghost btn-sm btn-edit-event" data-event-id="${e.id}" title="Editar">
                  <i class="ri-edit-line"></i>
                </button>
                <button class="btn btn-ghost btn-sm text-danger btn-delete-event" data-event-id="${e.id}" title="Eliminar">
                  <i class="ri-delete-bin-line"></i>
                </button>
              </td>
            </tr>
          `}).join('')}
        </tbody>
      </table>
    `;
    
    // Add event listeners for edit and delete buttons
    container.querySelectorAll('.btn-edit-event').forEach(btn => {
      btn.addEventListener('click', () => editEvent(parseInt(btn.dataset.eventId)));
    });
    container.querySelectorAll('.btn-delete-event').forEach(btn => {
      btn.addEventListener('click', () => deleteEvent(parseInt(btn.dataset.eventId)));
    });
  } catch (error) {
    console.error('Error loading events:', error);
    showToast('Error al cargar eventos', 'error');
  }
}

async function editEvent(eventId) {
  try {
    // Fetch event data
    const response = await apiRequest(`/admin/events`);
    if (!response.ok) throw new Error('Error al cargar evento');
    
    const events = await response.json();
    const event = events.find(e => e.id === eventId);
    
    if (!event) {
      showToast('Evento no encontrado', 'error');
      return;
    }
    
    // Show form
    const formCard = document.getElementById('admin-event-form');
    const form = document.getElementById('admin-event-form-el');
    const formTitle = formCard.querySelector('.card-header h3');
    
    if (formCard) formCard.classList.remove('hidden');
    if (formTitle) formTitle.textContent = 'Editar Evento';
    
    // Populate form fields
    if (form) {
      form.querySelector('[name="event_id"]').value = event.id;
      form.querySelector('[name="name"]').value = event.name || '';
      form.querySelector('[name="description"]').value = event.description || '';
      form.querySelector('[name="start_date"]').value = event.start_date ? event.start_date.split('T')[0] : '';
      form.querySelector('[name="end_date"]').value = event.end_date ? event.end_date.split('T')[0] : '';
      form.querySelector('[name="start_time"]').value = event.start_time || '';
      form.querySelector('[name="end_time"]').value = event.end_time || '';
      form.querySelector('[name="location"]').value = event.location || '';
      form.querySelector('[name="capacity"]').value = event.capacity || '';
      form.querySelector('[name="is_public"]').checked = event.is_public !== false;
      form.querySelector('[name="is_featured"]').checked = event.is_featured === true;
      const imageInput = form.querySelector('[name="image_url"]');
      if (imageInput) imageInput.value = event.image_url || '';
    }
    
    // Scroll to form
    formCard.scrollIntoView({ behavior: 'smooth' });
  } catch (error) {
    console.error('Error editing event:', error);
    showToast('Error al cargar datos del evento', 'error');
  }
}

async function deleteEvent(eventId) {
  if (!confirm('¿Eliminar este evento?')) return;
  
  try {
    const response = await apiRequest(`/admin/events/${eventId}`, { method: 'DELETE' });
    if (!response.ok) throw new Error('Error al eliminar');
    showToast('Evento eliminado', 'success');
    loadAdminEvents();
  } catch (error) {
    showToast('Error al eliminar evento', 'error');
  }
}

// Admin Expenses
async function loadAdminExpenses() {
  try {
    const [expensesRes, categoriesRes] = await Promise.all([
      apiRequest('/expenses'),
      apiRequest('/expenses/categories')
    ]);
    
    if (!expensesRes.ok) throw new Error('Error al cargar gastos');
    
    const expenses = await expensesRes.json();
    const categories = categoriesRes.ok ? await categoriesRes.json() : [];
    
    // Update category select
    const categorySelect = document.getElementById('expense-category-select');
    if (categorySelect) {
      categorySelect.innerHTML = '<option value="">Sin categoría</option>' +
        categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    }
    
    // Update summary
    const pending = expenses.filter(e => e.status === 'pending').length;
    const approved = expenses.filter(e => e.status === 'approved').length;
    const paid = expenses.filter(e => e.status === 'paid').length;
    
    document.getElementById('expenses-pending').textContent = pending;
    document.getElementById('expenses-approved').textContent = approved;
    document.getElementById('expenses-paid').textContent = paid;
    
    const container = document.getElementById('admin-expenses-list');
    
    if (!expenses.length) {
      container.innerHTML = '<p class="empty-message">No hay gastos registrados</p>';
      return;
    }
    
    const statusLabels = {
      pending: 'Pendiente',
      approved: 'Aprobado',
      paid: 'Pagado',
      rejected: 'Rechazado'
    };
    
    const statusClasses = {
      pending: 'badge-warning',
      approved: 'badge-info',
      paid: 'badge-success',
      rejected: 'badge-danger'
    };
    
    container.innerHTML = `
      <table class="data-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Descripción</th>
            <th>Categoría</th>
            <th>Monto</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          ${expenses.map(e => `
            <tr>
              <td>${new Date(e.expense_date).toLocaleDateString()}</td>
              <td>${e.description}</td>
              <td>${e.category_name || '-'}</td>
              <td class="text-right">$${parseFloat(e.amount).toLocaleString()}</td>
              <td><span class="badge ${statusClasses[e.status]}">${statusLabels[e.status]}</span></td>
              <td>
                ${e.status === 'pending' ? `
                  <button class="btn btn-ghost btn-sm text-success" onclick="approveExpense(${e.id})" title="Aprobar">
                    <i class="ri-check-line"></i>
                  </button>
                  <button class="btn btn-ghost btn-sm text-danger" onclick="rejectExpense(${e.id})" title="Rechazar">
                    <i class="ri-close-line"></i>
                  </button>
                ` : ''}
                ${e.status === 'approved' ? `
                  <button class="btn btn-ghost btn-sm text-primary" onclick="payExpense(${e.id})" title="Marcar pagado">
                    <i class="ri-money-dollar-circle-line"></i>
                  </button>
                ` : ''}
                ${e.status === 'pending' ? `
                  <button class="btn btn-ghost btn-sm text-danger" onclick="deleteExpense(${e.id})" title="Eliminar">
                    <i class="ri-delete-bin-line"></i>
                  </button>
                ` : ''}
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  } catch (error) {
    console.error('Error loading expenses:', error);
    showToast('Error al cargar gastos', 'error');
  }
}

async function approveExpense(id) {
  try {
    const response = await apiRequest(`/expenses/${id}/approve`, { method: 'PATCH' });
    if (!response.ok) throw new Error('Error');
    showToast('Gasto aprobado', 'success');
    loadAdminExpenses();
  } catch (error) {
    showToast('Error al aprobar gasto', 'error');
  }
}

async function rejectExpense(id) {
  if (!confirm('¿Rechazar este gasto?')) return;
  try {
    const response = await apiRequest(`/expenses/${id}/reject`, { method: 'PATCH' });
    if (!response.ok) throw new Error('Error');
    showToast('Gasto rechazado', 'success');
    loadAdminExpenses();
  } catch (error) {
    showToast('Error al rechazar gasto', 'error');
  }
}

async function payExpense(id) {
  try {
    const response = await apiRequest(`/expenses/${id}/pay`, { method: 'PATCH' });
    if (!response.ok) throw new Error('Error');
    showToast('Gasto marcado como pagado', 'success');
    loadAdminExpenses();
  } catch (error) {
    showToast('Error al marcar como pagado', 'error');
  }
}

async function deleteExpense(id) {
  if (!confirm('¿Eliminar este gasto?')) return;
  try {
    const response = await apiRequest(`/expenses/${id}`, { method: 'DELETE' });
    if (!response.ok) throw new Error('Error');
    showToast('Gasto eliminado', 'success');
    loadAdminExpenses();
  } catch (error) {
    showToast('Error al eliminar gasto', 'error');
  }
}

// Admin Announcements
async function loadAdminAnnouncements() {
  try {
    const response = await apiRequest('/admin/announcements');
    if (!response.ok) throw new Error('Error al cargar anuncios');
    
    const announcements = await response.json();
    const container = document.getElementById('admin-announcements-list');
    
    if (!announcements.length) {
      container.innerHTML = '<p class="empty-message">No hay anuncios publicados</p>';
      return;
    }
    
    container.innerHTML = `
      <table class="data-table">
        <thead>
          <tr>
            <th>Título</th>
            <th>Tipo</th>
            <th>Prioridad</th>
            <th>Público</th>
            <th>Activo</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          ${announcements.map(a => `
            <tr>
              <td><strong>${a.title}</strong></td>
              <td>${a.announcement_type}</td>
              <td>${a.priority}</td>
              <td>${a.is_public ? '<i class="ri-check-line text-success"></i>' : '<i class="ri-close-line text-danger"></i>'}</td>
              <td>${a.is_active ? '<i class="ri-check-line text-success"></i>' : '<i class="ri-close-line text-danger"></i>'}</td>
              <td>
                <button class="btn btn-ghost btn-sm text-danger" onclick="deleteAnnouncement(${a.id})">
                  <i class="ri-delete-bin-line"></i>
                </button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  } catch (error) {
    console.error('Error loading announcements:', error);
    showToast('Error al cargar anuncios', 'error');
  }
}

async function deleteAnnouncement(id) {
  if (!confirm('¿Eliminar este anuncio?')) return;
  try {
    const response = await apiRequest(`/admin/announcements/${id}`, { method: 'DELETE' });
    if (!response.ok) throw new Error('Error');
    showToast('Anuncio eliminado', 'success');
    loadAdminAnnouncements();
  } catch (error) {
    showToast('Error al eliminar anuncio', 'error');
  }
}

// Admin Config
async function loadAdminConfig() {
  try {
    const response = await apiRequest('/admin/config');
    if (!response.ok) throw new Error('Error al cargar configuración');
    
    const config = await response.json();
    state.churchConfig = config;
    
    // Populate form fields
    const form = document.getElementById('admin-config-form');
    if (form) {
      Object.keys(config).forEach(key => {
        const input = form.querySelector(`[name="${key}"]`);
        if (input && config[key] !== null) {
          input.value = config[key];
        }
      });
    }
    
    // Load logo preview
    if (config.logo_url) {
      const logoImg = document.getElementById('current-logo');
      const logoPlaceholder = document.getElementById('logo-placeholder');
      if (logoImg && logoPlaceholder) {
        logoImg.src = config.logo_url;
        logoImg.style.display = 'block';
        logoPlaceholder.style.display = 'none';
      }
      const logoUrlInput = document.getElementById('config-logo-url');
      if (logoUrlInput) logoUrlInput.value = config.logo_url;
    }
    
    // Load cover preview
    if (config.cover_image_url) {
      const coverImg = document.getElementById('current-cover');
      const coverPlaceholder = document.getElementById('cover-placeholder');
      if (coverImg && coverPlaceholder) {
        coverImg.src = config.cover_image_url;
        coverImg.style.display = 'block';
        coverPlaceholder.style.display = 'none';
      }
      const coverUrlInput = document.getElementById('config-cover-url');
      if (coverUrlInput) coverUrlInput.value = config.cover_image_url;
    }
    
    // Load colors
    if (config.primary_color) {
      const colorInput = document.getElementById('config-primary-color');
      const colorText = document.getElementById('config-primary-color-text');
      if (colorInput) colorInput.value = config.primary_color;
      if (colorText) colorText.value = config.primary_color;
    }
    if (config.secondary_color) {
      const colorInput = document.getElementById('config-secondary-color');
      const colorText = document.getElementById('config-secondary-color-text');
      if (colorInput) colorInput.value = config.secondary_color;
      if (colorText) colorText.value = config.secondary_color;
    }
    
    // Load schedules
    if (config.service_schedule) {
      renderSchedulesList(config.service_schedule);
    } else {
      renderSchedulesList([]);
    }
    
    // Load live streams
    await loadLiveStreams();
    
    // Setup config event listeners
    setupConfigListeners();
    
  } catch (error) {
    console.error('Error loading config:', error);
    showToast('Error al cargar configuración', 'error');
  }
}

// Live Streams Management
async function loadLiveStreams() {
  try {
    const response = await apiRequest('/admin/streams');
    const container = document.getElementById('live-streams-list');
    
    if (!container) return;
    
    if (!response.ok) {
      container.innerHTML = '<p class="text-muted">No se pudieron cargar las transmisiones</p>';
      return;
    }
    
    const streams = await response.json();
    state.liveStreams = streams;
    
    if (!streams || streams.length === 0) {
      container.innerHTML = '<p class="text-muted">No hay transmisiones configuradas</p>';
      return;
    }
    
    container.innerHTML = streams.map(s => `
      <div class="stream-item" data-stream-id="${s.id}">
        <div class="stream-info">
          <span class="stream-platform ${s.platform}">
            <i class="${getPlatformIcon(s.platform)}"></i>
            ${getPlatformName(s.platform)}
          </span>
          <strong>${s.title}</strong>
          <a href="${s.stream_url}" target="_blank" class="stream-url">${s.stream_url}</a>
          ${s.is_live ? '<span class="badge badge-success"><i class="ri-live-fill"></i> En Vivo</span>' : '<span class="badge badge-muted">Inactivo</span>'}
        </div>
        <div class="stream-actions">
          <button type="button" class="btn btn-sm ${s.is_live ? 'btn-secondary' : 'btn-primary'}" onclick="toggleStream(${s.id}, ${!s.is_live})">
            <i class="${s.is_live ? 'ri-stop-circle-line' : 'ri-play-circle-line'}"></i>
            <span>${s.is_live ? 'Detener' : 'Iniciar'}</span>
          </button>
          <button type="button" class="btn btn-sm btn-ghost btn-danger" onclick="deleteStream(${s.id})">
            <i class="ri-delete-bin-line"></i>
          </button>
        </div>
      </div>
    `).join('');
  } catch (error) {
    console.error('Error loading streams:', error);
  }
}

function getPlatformIcon(platform) {
  const icons = {
    youtube: 'ri-youtube-line',
    facebook: 'ri-facebook-live-line',
    twitch: 'ri-twitch-line',
    other: 'ri-live-line'
  };
  return icons[platform] || icons.other;
}

function getPlatformName(platform) {
  const names = {
    youtube: 'YouTube',
    facebook: 'Facebook',
    twitch: 'Twitch',
    other: 'Otro'
  };
  return names[platform] || 'Otro';
}

async function addLiveStream() {
  const title = document.getElementById('new-stream-title').value.trim();
  const platform = document.getElementById('new-stream-platform').value;
  const url = document.getElementById('new-stream-url').value.trim();
  
  if (!title || !url) {
    showToast('Por favor completa el título y la URL', 'warning');
    return;
  }
  
  try {
    const response = await apiRequest('/admin/streams', {
      method: 'POST',
      body: {
        title,
        platform,
        stream_url: url,
        is_active: true
      }
    });
    
    if (response.ok) {
      showToast('Transmisión agregada', 'success');
      document.getElementById('new-stream-title').value = '';
      document.getElementById('new-stream-url').value = '';
      await loadLiveStreams();
    } else {
      throw new Error('Error al agregar transmisión');
    }
  } catch (error) {
    showToast(error.message, 'error');
  }
}

async function toggleStream(streamId, isLive) {
  try {
    // Use the go-live or end-live endpoint
    const endpoint = isLive ? `/admin/streams/${streamId}/go-live` : `/admin/streams/${streamId}/end-live`;
    const response = await apiRequest(endpoint, {
      method: 'POST'
    });
    
    if (response.ok) {
      showToast(isLive ? '¡Transmisión en vivo!' : 'Transmisión finalizada', 'success');
      await loadLiveStreams();
    }
  } catch (error) {
    showToast('Error al actualizar transmisión', 'error');
  }
}

async function deleteStream(streamId) {
  if (!confirm('¿Eliminar esta transmisión?')) return;
  
  try {
    const response = await apiRequest(`/admin/streams/${streamId}`, {
      method: 'DELETE'
    });
    
    if (response.ok) {
      showToast('Transmisión eliminada', 'success');
      await loadLiveStreams();
    }
  } catch (error) {
    showToast('Error al eliminar transmisión', 'error');
  }
}

function renderSchedulesList(schedules) {
  const container = document.getElementById('schedules-list');
  if (!container) return;
  
  if (!schedules || schedules.length === 0) {
    container.innerHTML = '<p class="empty-message">No hay horarios configurados</p>';
    return;
  }
  
  container.innerHTML = schedules.map((s, i) => `
    <div class="schedule-item" data-index="${i}">
      <select name="schedule_day_${i}">
        <option value="Domingo" ${s.day === 'Domingo' ? 'selected' : ''}>Domingo</option>
        <option value="Lunes" ${s.day === 'Lunes' ? 'selected' : ''}>Lunes</option>
        <option value="Martes" ${s.day === 'Martes' ? 'selected' : ''}>Martes</option>
        <option value="Miércoles" ${s.day === 'Miércoles' ? 'selected' : ''}>Miércoles</option>
        <option value="Jueves" ${s.day === 'Jueves' ? 'selected' : ''}>Jueves</option>
        <option value="Viernes" ${s.day === 'Viernes' ? 'selected' : ''}>Viernes</option>
        <option value="Sábado" ${s.day === 'Sábado' ? 'selected' : ''}>Sábado</option>
      </select>
      <input type="time" name="schedule_time_${i}" value="${s.time || ''}" placeholder="Hora" />
      <input type="text" name="schedule_name_${i}" value="${s.name || ''}" placeholder="Nombre del servicio" />
      <button type="button" class="btn btn-ghost btn-remove" onclick="removeSchedule(${i})">
        <i class="ri-delete-bin-line"></i>
      </button>
    </div>
  `).join('');
}

function addSchedule() {
  const container = document.getElementById('schedules-list');
  if (!container) return;
  
  // Si hay mensaje de vacío, limpiarlo
  if (container.querySelector('.empty-message')) {
    container.innerHTML = '';
  }
  
  const index = container.querySelectorAll('.schedule-item').length;
  const html = `
    <div class="schedule-item" data-index="${index}">
      <select name="schedule_day_${index}">
        <option value="Domingo">Domingo</option>
        <option value="Lunes">Lunes</option>
        <option value="Martes">Martes</option>
        <option value="Miércoles">Miércoles</option>
        <option value="Jueves">Jueves</option>
        <option value="Viernes">Viernes</option>
        <option value="Sábado">Sábado</option>
      </select>
      <input type="time" name="schedule_time_${index}" placeholder="Hora" />
      <input type="text" name="schedule_name_${index}" placeholder="Nombre del servicio" />
      <button type="button" class="btn btn-ghost btn-remove" onclick="removeSchedule(${index})">
        <i class="ri-delete-bin-line"></i>
      </button>
    </div>
  `;
  container.insertAdjacentHTML('beforeend', html);
}

function removeSchedule(index) {
  const item = document.querySelector(`.schedule-item[data-index="${index}"]`);
  if (item) item.remove();
  
  // Si no quedan horarios, mostrar mensaje
  const container = document.getElementById('schedules-list');
  if (container && container.querySelectorAll('.schedule-item').length === 0) {
    container.innerHTML = '<p class="empty-message">No hay horarios configurados</p>';
  }
}

function getSchedulesFromForm() {
  const items = document.querySelectorAll('.schedule-item');
  const schedules = [];
  
  items.forEach((item, i) => {
    const day = item.querySelector(`[name^="schedule_day"]`)?.value;
    const time = item.querySelector(`[name^="schedule_time"]`)?.value;
    const name = item.querySelector(`[name^="schedule_name"]`)?.value;
    
    if (day && name) {
      schedules.push({ day, time, name });
    }
  });
  
  return schedules;
}

function setupConfigListeners() {
  // Color sync
  const primaryColor = document.getElementById('config-primary-color');
  const primaryText = document.getElementById('config-primary-color-text');
  const secondaryColor = document.getElementById('config-secondary-color');
  const secondaryText = document.getElementById('config-secondary-color-text');
  
  if (primaryColor && primaryText) {
    primaryColor.addEventListener('input', () => primaryText.value = primaryColor.value);
    primaryText.addEventListener('input', () => {
      if (/^#[0-9A-Fa-f]{6}$/.test(primaryText.value)) {
        primaryColor.value = primaryText.value;
      }
    });
  }
  
  if (secondaryColor && secondaryText) {
    secondaryColor.addEventListener('input', () => secondaryText.value = secondaryColor.value);
    secondaryText.addEventListener('input', () => {
      if (/^#[0-9A-Fa-f]{6}$/.test(secondaryText.value)) {
        secondaryColor.value = secondaryText.value;
      }
    });
  }
  
  // Logo upload
  const logoUpload = document.getElementById('logo-upload');
  if (logoUpload) {
    logoUpload.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (file) {
        await uploadConfigImage(file, 'logo');
      }
    });
  }
  
  // Cover upload
  const coverUpload = document.getElementById('cover-upload');
  if (coverUpload) {
    coverUpload.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (file) {
        await uploadConfigImage(file, 'cover');
      }
    });
  }
  
  // Add schedule button
  const btnAddSchedule = document.getElementById('btn-add-schedule');
  if (btnAddSchedule) {
    btnAddSchedule.addEventListener('click', addSchedule);
  }
  
  // Add stream button
  const btnAddStream = document.getElementById('btn-add-stream');
  if (btnAddStream) {
    btnAddStream.addEventListener('click', addLiveStream);
  }
}

async function uploadConfigImage(file, type) {
  try {
    showToast('Subiendo imagen...', 'info');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('description', `${type === 'logo' ? 'Logo' : 'Portada'} de la iglesia`);
    formData.append('is_public', 'true');
    
    const response = await fetch(`${API_BASE}/documents`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${state.accessToken}` },
      body: formData
    });
    
    if (!response.ok) throw new Error('Error al subir');
    
    const doc = await response.json();
    const imageUrl = `${API_BASE}/documents/${doc.id}/download`;
    
    // Update preview
    if (type === 'logo') {
      const img = document.getElementById('current-logo');
      const placeholder = document.getElementById('logo-placeholder');
      const urlInput = document.getElementById('config-logo-url');
      if (img) { img.src = imageUrl; img.style.display = 'block'; }
      if (placeholder) placeholder.style.display = 'none';
      if (urlInput) urlInput.value = imageUrl;
    } else {
      const img = document.getElementById('current-cover');
      const placeholder = document.getElementById('cover-placeholder');
      const urlInput = document.getElementById('config-cover-url');
      if (img) { img.src = imageUrl; img.style.display = 'block'; }
      if (placeholder) placeholder.style.display = 'none';
      if (urlInput) urlInput.value = imageUrl;
    }
    
    showToast('Imagen subida', 'success');
  } catch (error) {
    showToast('Error al subir imagen', 'error');
  }
}

async function saveAdminConfig(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const data = {};
  
  // Get basic form data
  formData.forEach((value, key) => {
    // Skip schedule fields (handled separately)
    if (!key.startsWith('schedule_') && value) {
      data[key] = value;
    }
  });
  
  // Get schedules
  data.service_schedule = getSchedulesFromForm();
  
  try {
    const response = await apiRequest('/admin/config', {
      method: 'PATCH',
      body: data
    });
    
    if (!response.ok) throw new Error('Error al guardar');
    showToast('Configuración guardada exitosamente', 'success');
    
    // Reload public config to update UI
    loadPublicConfig();
    
  } catch (error) {
    showToast('Error al guardar configuración', 'error');
  }
}

// Admin Reports
async function loadAdminReports() {
  await loadAdminReportsFiltered();
}

async function loadAdminReportsFiltered() {
  try {
    // Get filter values
    const periodSelect = document.getElementById('report-period');
    const period = periodSelect?.value || 'month';
    
    let fromDate = null;
    let toDate = new Date().toISOString().split('T')[0];
    
    if (period === 'custom') {
      fromDate = document.getElementById('report-from-date')?.value;
      toDate = document.getElementById('report-to-date')?.value || toDate;
    } else {
      const now = new Date();
      switch (period) {
        case 'month':
          fromDate = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
          break;
        case 'quarter':
          const quarter = Math.floor(now.getMonth() / 3);
          fromDate = new Date(now.getFullYear(), quarter * 3, 1).toISOString().split('T')[0];
          break;
        case 'year':
          fromDate = new Date(now.getFullYear(), 0, 1).toISOString().split('T')[0];
          break;
      }
    }
    
    const [donationsRes, expensesRes, usersRes] = await Promise.all([
      apiRequest('/donations'),
      apiRequest('/expenses'),
      apiRequest('/users')
    ]);
    
    let allDonations = [];
    let allExpenses = [];
    let memberCount = 0;
    
    if (donationsRes.ok) {
      allDonations = await donationsRes.json();
    }
    
    if (expensesRes.ok) {
      allExpenses = await expensesRes.json();
    }

    if (usersRes.ok) {
      const users = await usersRes.json();
      memberCount = users.length;
    }
    
    // Filter by date
    const filteredDonations = allDonations.filter(d => {
      if (!d.donation_date) return true;
      const date = d.donation_date.split('T')[0];
      return (!fromDate || date >= fromDate) && (!toDate || date <= toDate);
    });
    
    const filteredExpenses = allExpenses.filter(e => {
      if (!e.expense_date && !e.created_at) return true;
      const date = (e.expense_date || e.created_at)?.split('T')[0];
      return (!fromDate || date >= fromDate) && (!toDate || date <= toDate);
    });
    
    // Calculate totals
    const totalDonations = filteredDonations.reduce((sum, d) => sum + parseFloat(d.amount || 0), 0);
    const approvedExpenses = filteredExpenses.filter(e => e.status === 'paid' || e.status === 'approved');
    const totalExpenses = approvedExpenses.reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
    
    // Update stats
    const donationsEl = document.getElementById('report-total-donations');
    const expensesEl = document.getElementById('report-total-expenses');
    const balanceEl = document.getElementById('report-balance');
    const membersEl = document.getElementById('report-members');
    
    if (donationsEl) donationsEl.textContent = formatCurrency(totalDonations);
    if (expensesEl) expensesEl.textContent = formatCurrency(totalExpenses);
    if (balanceEl) balanceEl.textContent = formatCurrency(totalDonations - totalExpenses);
    if (membersEl) membersEl.textContent = memberCount;
    
    // Render donations table (formato tipo Excel)
    renderDonationsReportTable(filteredDonations);
    
    // Render donations by type chart
    renderDonationsByTypeChart(filteredDonations);
    
    // Render expenses summary by status
    renderExpensesSummary(filteredExpenses);
    
    // Load expenses by category
    const byCategoryRes = await apiRequest('/expenses/summary/by-category');
    if (byCategoryRes.ok) {
      const byCategory = await byCategoryRes.json();
      const container = document.getElementById('expenses-by-category-chart');
      if (container) {
        if (!byCategory || byCategory.length === 0) {
          container.innerHTML = '<p class="empty-message">No hay datos de gastos</p>';
        } else {
          container.innerHTML = `
            <div class="breakdown-grid">
              ${byCategory.map(c => `
                <div class="breakdown-item" style="border-left: 3px solid ${c.color || '#6b7280'}">
                  <div class="breakdown-type">${c.category || 'Sin categoría'}</div>
                  <div class="breakdown-value">${formatCurrency(c.total || 0)}</div>
                </div>
              `).join('')}
            </div>
          `;
        }
      }
    }
  } catch (error) {
    console.error('Error loading reports:', error);
  }
}

function renderExpensesSummary(expenses) {
  const pending = expenses.filter(e => e.status === 'pending');
  const approved = expenses.filter(e => e.status === 'approved');
  const paid = expenses.filter(e => e.status === 'paid');
  const rejected = expenses.filter(e => e.status === 'rejected');
  
  const pendingTotal = pending.reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
  const approvedTotal = approved.reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
  const paidTotal = paid.reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
  
  // Update elements if they exist in the reports section
  const container = document.getElementById('expenses-summary-report');
  if (container) {
    container.innerHTML = `
      <div class="stats-row">
        <div class="stat-card mini">
          <div class="stat-value">${pending.length}</div>
          <div class="stat-label">Pendientes (${formatCurrency(pendingTotal)})</div>
        </div>
        <div class="stat-card mini">
          <div class="stat-value">${approved.length}</div>
          <div class="stat-label">Aprobados (${formatCurrency(approvedTotal)})</div>
        </div>
        <div class="stat-card mini">
          <div class="stat-value">${paid.length}</div>
          <div class="stat-label">Pagados (${formatCurrency(paidTotal)})</div>
        </div>
        <div class="stat-card mini">
          <div class="stat-value">${rejected.length}</div>
          <div class="stat-label">Rechazados</div>
        </div>
      </div>
    `;
  }
}

function renderDonationsReportTable(donations) {
  const tbody = document.getElementById('donations-report-tbody');
  if (!tbody) return;

  if (!donations || donations.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" class="empty-message">No hay donaciones</td></tr>';
    return;
  }

  let totals = { diezmo: 0, ofrenda: 0, misiones: 0, general: 0 };

  tbody.innerHTML = donations.map(d => {
    const amount = parseFloat(d.amount || 0);
    const type = d.donation_type || 'ofrenda';
    
    if (totals[type] !== undefined) totals[type] += amount;
    totals.general += amount;

    const isEfectivo = d.payment_method === 'efectivo';
    const isTransf = d.payment_method === 'transferencia';

    return `
      <tr>
        <td>${formatDate(d.donation_date)}</td>
        <td>${d.donor_name || 'Anónimo'}</td>
        <td class="text-right">${isEfectivo ? formatCurrency(amount) : ''}</td>
        <td class="text-right">${isTransf ? formatCurrency(amount) : ''}</td>
        <td>${d.donor_document || ''}</td>
        <td class="text-right">${type === 'diezmo' ? formatCurrency(amount) : ''}</td>
        <td class="text-right">${type === 'ofrenda' ? formatCurrency(amount) : ''}</td>
        <td class="text-right">${type === 'misiones' ? formatCurrency(amount) : ''}</td>
        <td class="text-right"><strong>${formatCurrency(amount)}</strong></td>
      </tr>
    `;
  }).join('');

  const el = (id, val) => { const e = document.getElementById(id); if (e) e.textContent = formatCurrency(val); };
  el('total-diezmo', totals.diezmo);
  el('total-ofrenda', totals.ofrenda);
  el('total-misiones', totals.misiones);
  el('total-general', totals.general);
}

function renderDonationsByTypeChart(donations) {
  const container = document.getElementById('donations-by-type-chart');
  if (!container) return;

  const byType = {};
  donations.forEach(d => {
    const type = d.donation_type || 'otro';
    if (!byType[type]) byType[type] = 0;
    byType[type] += parseFloat(d.amount || 0);
  });

  if (Object.keys(byType).length === 0) {
    container.innerHTML = '<p class="empty-message">No hay datos</p>';
    return;
  }

  const colors = { diezmo: '#8b5cf6', ofrenda: '#22c55e', misiones: '#06b6d4', especial: '#f59e0b' };
  const total = Object.values(byType).reduce((a, b) => a + b, 0);

  container.innerHTML = `
    <div class="breakdown-grid">
      ${Object.entries(byType).map(([type, amount]) => `
        <div class="breakdown-item" style="border-left: 3px solid ${colors[type] || '#6b7280'}">
          <div class="breakdown-type">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
          <div class="breakdown-value">${formatCurrency(amount)}</div>
          <div class="breakdown-count">${((amount / total) * 100).toFixed(1)}%</div>
        </div>
      `).join('')}
    </div>
  `;
}

// Admin Documents
async function loadAdminDocuments() {
  try {
    const response = await apiRequest('/documents');
    if (!response.ok) return;
    
    const documents = await response.json();
    
    // Categorize documents
    const systemDocs = [];
    const donationDocs = [];
    const expenseDocs = [];
    
    documents.forEach(doc => {
      const desc = (doc.description || '').toLowerCase();
      if (desc.includes('logo') || desc.includes('portada') || desc.includes('banner') || desc.includes('sistema')) {
        systemDocs.push(doc);
      } else if (desc.includes('donación') || desc.includes('donacion') || desc.includes('soporte donación') || doc.donation_id) {
        donationDocs.push(doc);
      } else if (desc.includes('gasto') || desc.includes('factura') || desc.includes('soporte gasto') || doc.expense_id) {
        expenseDocs.push(doc);
      } else {
        // Default to system files
        systemDocs.push(doc);
      }
    });
    
    // Render each folder
    renderDocumentFolder('docs-system', systemDocs);
    renderDocumentFolder('docs-donations', donationDocs);
    renderDocumentFolder('docs-expenses', expenseDocs);
    
    // Update folder counts
    updateFolderCount('count-system', systemDocs.length);
    updateFolderCount('count-donations', donationDocs.length);
    updateFolderCount('count-expenses', expenseDocs.length);
    
    // Setup folder toggles
    setupFolderToggles();
    
  } catch (error) {
    console.error('Error loading documents:', error);
  }
}

function renderDocumentFolder(containerId, documents) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  if (!documents.length) {
    container.innerHTML = '<p class="empty-message">No hay archivos en esta carpeta</p>';
    return;
  }
  
  container.innerHTML = documents.map(doc => `
    <div class="document-card">
      <div class="document-icon">
        <i class="${getDocIcon(doc.mime_type)}"></i>
      </div>
      <div class="document-info">
        <h4>${doc.file_name}</h4>
        <p>${doc.description || 'Sin descripción'}</p>
        <small>${formatDate(doc.uploaded_at)} • ${formatSize(doc.size_bytes)}</small>
      </div>
      <div class="document-actions">
        <button class="btn btn-ghost btn-sm" onclick="downloadDocument(${doc.id})">
          <i class="ri-download-line"></i>
        </button>
        <button class="btn btn-ghost btn-sm danger" onclick="deleteDocument(${doc.id})">
          <i class="ri-delete-bin-line"></i>
        </button>
      </div>
    </div>
  `).join('');
}

function updateFolderCount(elementId, count) {
  const el = document.getElementById(elementId);
  if (el) {
    el.textContent = count === 1 ? '1 archivo' : `${count} archivos`;
  }
}

function setupFolderToggles() {
  document.querySelectorAll('.folder-card').forEach(card => {
    const header = card.querySelector('.folder-header');
    const content = card.querySelector('.folder-content');
    
    if (!header || !content) return;
    
    // Remove existing listeners by cloning
    const newHeader = header.cloneNode(true);
    header.parentNode.replaceChild(newHeader, header);
    
    newHeader.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      // Toggle open state
      card.classList.toggle('open');
      content.classList.toggle('hidden');
      
      console.log('Folder toggled:', card.dataset.folder, 'open:', card.classList.contains('open'));
    });
  });
  
  // Open first folder by default if has content
  const firstFolder = document.querySelector('.folder-card[data-folder="system"]');
  if (firstFolder) {
    const content = firstFolder.querySelector('.folder-content');
    const docsContainer = firstFolder.querySelector('.documents-grid');
    if (docsContainer && !docsContainer.textContent.includes('No hay')) {
      firstFolder.classList.add('open');
      content?.classList.remove('hidden');
    }
  }
}

function openUploadModal(category) {
  const modal = document.getElementById('upload-document-modal');
  const categoryInput = document.getElementById('upload-category');
  const typeSelect = document.getElementById('upload-doc-type');
  
  if (categoryInput) categoryInput.value = category;
  
  // Update type options based on category
  if (typeSelect) {
    if (category === 'system') {
      typeSelect.innerHTML = `
        <option value="logo">Logo de la iglesia</option>
        <option value="cover">Portada de la iglesia</option>
        <option value="other">Otro archivo del sistema</option>
      `;
    } else {
      typeSelect.closest('.form-group').style.display = 'none';
    }
  }
  
  if (modal) modal.classList.remove('hidden');
}

function closeUploadModal() {
  const modal = document.getElementById('upload-document-modal');
  if (modal) modal.classList.add('hidden');
}

function getDocIcon(mime) {
  if (!mime) return 'ri-file-line';
  if (mime.includes('pdf')) return 'ri-file-pdf-line';
  if (mime.includes('image')) return 'ri-image-line';
  if (mime.includes('word')) return 'ri-file-word-line';
  if (mime.includes('excel') || mime.includes('spreadsheet')) return 'ri-file-excel-line';
  return 'ri-file-line';
}

function formatSize(bytes) {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

async function deleteDocument(id) {
  if (!confirm('¿Eliminar documento?')) return;
  try {
    const res = await apiRequest(`/documents/${id}`, { method: 'DELETE' });
    if (res.ok) {
      showToast('Documento eliminado', 'success');
      loadAdminDocuments();
    }
  } catch (e) {
    showToast('Error', 'error');
  }
}

// Export functions
function exportToExcel() {
  exportToCSV();
}

async function exportToCSV() {
  try {
    const res = await apiRequest('/donations');
    if (!res.ok) throw new Error();
    
    const donations = await res.json();
    const headers = ['Fecha', 'Nombre', 'Documento', 'Tipo', 'Método', 'Monto'];
    const rows = donations.map(d => [
      d.donation_date, d.donor_name || 'Anónimo', d.donor_document || '',
      d.donation_type, d.payment_method, d.amount
    ]);
    
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `donaciones_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    showToast('CSV descargado', 'success');
  } catch (e) {
    showToast('Error al exportar', 'error');
  }
}

function exportToPDF() {
  showToast('Usa Ctrl+P para imprimir/guardar como PDF', 'info');
  window.print();
}

// Setup admin event listeners
function setupAdminEventListeners() {
  // Admin donation form
  const btnRegisterDonation = document.getElementById('btn-register-donation');
  if (btnRegisterDonation) {
    btnRegisterDonation.addEventListener('click', () => {
      const form = document.getElementById('admin-donation-form');
      form.classList.toggle('hidden');
      const dateInput = form.querySelector('[name="donation_date"]');
      if (dateInput) dateInput.valueAsDate = new Date();
    });
  }
  
  const adminDonationForm = document.getElementById('admin-donation-form-el');
  if (adminDonationForm) {
    adminDonationForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      
      // Datos comunes
      const donorName = formData.get('donor_name');
      const donorDocument = formData.get('donor_document');
      const donationDate = formData.get('donation_date');
      const note = formData.get('note');
      const supportFile = formData.get('support_file');
      
      // Montos y métodos de pago por tipo
      const types = ['diezmo', 'ofrenda', 'misiones', 'especial'];
      const donations = [];
      
      for (const type of types) {
        const amount = parseFloat(formData.get(`amount_${type}`)) || 0;
        const method = formData.get(`method_${type}`) || 'efectivo';
        
        if (amount > 0) {
          donations.push({
            donor_name: donorName,
            donor_document: donorDocument,
            donation_type: type,
            amount: amount,
            payment_method: method,
            donation_date: donationDate,
            note: note
          });
        }
      }
      
      if (donations.length === 0) {
        showToast('Ingresa al menos un monto de donación', 'error');
        return;
      }
      
      try {
        let lastDonationId = null;
        let successCount = 0;
        
        for (const data of donations) {
          const response = await apiRequest('/donations', {
            method: 'POST',
            body: data
          });
          if (response.ok) {
            const result = await response.json();
            lastDonationId = result.id;
            successCount++;
          }
        }
        
        // Subir archivo de soporte si existe
        if (supportFile && supportFile.size > 0 && lastDonationId) {
          const fileForm = new FormData();
          fileForm.append('file', supportFile);
          fileForm.append('description', `Soporte donación ${donorName}`);
          fileForm.append('donation_id', lastDonationId);
          
          await fetch(`${API_BASE}/documents`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${state.accessToken}` },
            body: fileForm
          });
        }
        
        if (successCount > 0) {
          showToast(`${successCount} donación(es) registrada(s)`, 'success');
          e.target.reset();
          document.getElementById('admin-donation-form').classList.add('hidden');
          loadAdminDonations();
        } else {
          showToast('Error al registrar donaciones', 'error');
        }
      } catch (error) {
        showToast('Error al registrar donación', 'error');
      }
    });
  }
  
  // Admin event form
  const btnCreateEvent = document.getElementById('btn-create-event');
  if (btnCreateEvent) {
    btnCreateEvent.addEventListener('click', () => {
      const form = document.getElementById('admin-event-form');
      const formEl = document.getElementById('admin-event-form-el');
      const formTitle = form?.querySelector('.card-header h3');
      
      // Reset form for creating new event
      if (formEl) {
        formEl.reset();
        formEl.querySelector('[name="event_id"]').value = '';
      }
      if (formTitle) formTitle.textContent = 'Nuevo Evento';
      
      form.classList.toggle('hidden');
    });
  }
  
  const adminEventForm = document.getElementById('admin-event-form-el');
  if (adminEventForm) {
    adminEventForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const eventId = formData.get('event_id');
      const isEditing = eventId && eventId !== '';
      
      const data = {
        name: formData.get('name'),
        description: formData.get('description'),
        start_date: formData.get('start_date'),
        end_date: formData.get('end_date') || null,
        start_time: formData.get('start_time') || null,
        end_time: formData.get('end_time') || null,
        location: formData.get('location'),
        capacity: formData.get('capacity') ? parseInt(formData.get('capacity')) : null,
        is_public: formData.has('is_public'),
        is_featured: formData.has('is_featured')
      };
      
      try {
        const endpoint = isEditing ? `/admin/events/${eventId}` : '/admin/events';
        const method = isEditing ? 'PATCH' : 'POST';
        
        const response = await apiRequest(endpoint, {
          method: method,
          body: data
        });
        if (!response.ok) throw new Error('Error al guardar');
        showToast(isEditing ? 'Evento actualizado' : 'Evento creado', 'success');
        e.target.reset();
        // Reset hidden field
        e.target.querySelector('[name="event_id"]').value = '';
        // Reset form title
        const formTitle = document.querySelector('#admin-event-form .card-header h3');
        if (formTitle) formTitle.textContent = 'Nuevo Evento';
        document.getElementById('admin-event-form').classList.add('hidden');
        loadAdminEvents();
      } catch (error) {
        showToast('Error al guardar evento', 'error');
      }
    });
  }
  
  // Admin expense form
  const btnCreateExpense = document.getElementById('btn-create-expense');
  if (btnCreateExpense) {
    btnCreateExpense.addEventListener('click', () => {
      const form = document.getElementById('admin-expense-form');
      form.classList.toggle('hidden');
      const dateInput = form.querySelector('[name="expense_date"]');
      if (dateInput) dateInput.valueAsDate = new Date();
    });
  }
  
  const adminExpenseForm = document.getElementById('admin-expense-form-el');
  if (adminExpenseForm) {
    adminExpenseForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const fileInput = document.getElementById('expense-file-input');
      const file = fileInput?.files[0];
      
      // Prepare expense data (without the file)
      const data = {};
      formData.forEach((value, key) => {
        if (key !== 'support_file') {
          data[key] = value;
        }
      });
      if (data.category_id) data.category_id = parseInt(data.category_id);
      if (data.amount) data.amount = parseFloat(data.amount);
      
      try {
        // Create expense first
        const response = await apiRequest('/expenses', {
          method: 'POST',
          body: data
        });
        if (!response.ok) throw new Error('Error al registrar');
        
        const expense = await response.json();
        
        // Upload support file if provided
        if (file) {
          const fileFormData = new FormData();
          fileFormData.append('file', file);
          fileFormData.append('description', `Soporte gasto: ${data.description}`);
          fileFormData.append('expense_id', expense.id);
          
          await fetch(`${API_BASE}/documents`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${state.accessToken}`
            },
            body: fileFormData
          });
        }
        
        showToast('Gasto registrado', 'success');
        e.target.reset();
        resetExpenseFileInput();
        document.getElementById('admin-expense-form').classList.add('hidden');
        loadAdminExpenses();
      } catch (error) {
        showToast('Error al registrar gasto', 'error');
      }
    });
    
    // Handle file input for expenses
    const expenseFileInput = document.getElementById('expense-file-input');
    if (expenseFileInput) {
      expenseFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        const placeholder = document.querySelector('#expense-upload-area .file-upload-placeholder');
        const selected = document.querySelector('#expense-upload-area .file-selected');
        const fileName = document.getElementById('expense-file-name');
        
        if (file && placeholder && selected) {
          placeholder.classList.add('hidden');
          selected.classList.remove('hidden');
          if (fileName) fileName.textContent = file.name;
        }
      });
    }
    
    // Remove file button
    const btnRemoveExpenseFile = document.getElementById('btn-remove-expense-file');
    if (btnRemoveExpenseFile) {
      btnRemoveExpenseFile.addEventListener('click', resetExpenseFileInput);
    }
  }
  
  function resetExpenseFileInput() {
    const fileInput = document.getElementById('expense-file-input');
    const placeholder = document.querySelector('#expense-upload-area .file-upload-placeholder');
    const selected = document.querySelector('#expense-upload-area .file-selected');
    
    if (fileInput) fileInput.value = '';
    if (placeholder) placeholder.classList.remove('hidden');
    if (selected) selected.classList.add('hidden');
  }
  
  // Admin announcement form
  const btnCreateAnnouncement = document.getElementById('btn-create-announcement');
  if (btnCreateAnnouncement) {
    btnCreateAnnouncement.addEventListener('click', () => {
      document.getElementById('admin-announcement-form').classList.toggle('hidden');
    });
  }
  
  const adminAnnouncementForm = document.getElementById('admin-announcement-form-el');
  if (adminAnnouncementForm) {
    adminAnnouncementForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const data = {
        title: formData.get('title'),
        content: formData.get('content'),
        announcement_type: formData.get('announcement_type'),
        priority: parseInt(formData.get('priority') || '0'),
        is_public: formData.has('is_public'),
        start_date: formData.get('start_date') || null,
        end_date: formData.get('end_date') || null
      };
      
      try {
        const response = await apiRequest('/admin/announcements', {
          method: 'POST',
          body: data
        });
        if (!response.ok) throw new Error('Error al crear');
        showToast('Anuncio publicado', 'success');
        e.target.reset();
        document.getElementById('admin-announcement-form').classList.add('hidden');
        loadAdminAnnouncements();
      } catch (error) {
        showToast('Error al publicar anuncio', 'error');
      }
    });
  }
  
  // Admin config form
  const adminConfigForm = document.getElementById('admin-config-form');
  if (adminConfigForm) {
    adminConfigForm.addEventListener('submit', saveAdminConfig);
  }

  // Document upload modal
  const uploadModal = document.getElementById('upload-document-modal');
  if (uploadModal) {
    // Close modal buttons
    uploadModal.querySelectorAll('.modal-close-btn').forEach(btn => {
      btn.addEventListener('click', closeUploadModal);
    });
    
    // Close on overlay click
    const overlay = uploadModal.querySelector('.modal-overlay');
    if (overlay) {
      overlay.addEventListener('click', closeUploadModal);
    }
  }
  
  const docUploadForm = document.getElementById('document-upload-form');
  if (docUploadForm) {
    docUploadForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const category = formData.get('category');
      const docType = formData.get('document_type');
      
      // Add category info to description
      let description = formData.get('description') || '';
      if (category === 'system') {
        if (docType === 'logo') description = 'Logo de la iglesia';
        else if (docType === 'cover') description = 'Portada de la iglesia';
        else if (!description) description = 'Archivo del sistema';
      }
      
      // Update description in formData
      formData.set('description', description);
      
      try {
        const response = await fetch(`${API_BASE}/documents`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${state.accessToken}` },
          body: formData
        });
        if (!response.ok) throw new Error('Error');
        showToast('Documento subido', 'success');
        e.target.reset();
        closeUploadModal();
        loadAdminDocuments();
      } catch (error) {
        showToast('Error al subir documento', 'error');
      }
    });
  }

  // Export buttons
  const btnExportExcel = document.getElementById('btn-export-excel');
  if (btnExportExcel) {
    btnExportExcel.addEventListener('click', exportToExcel);
  }
  
  const btnExportPdf = document.getElementById('btn-export-pdf');
  if (btnExportPdf) {
    btnExportPdf.addEventListener('click', exportToPDF);
  }

  // Report period filter
  const reportPeriod = document.getElementById('report-period');
  if (reportPeriod) {
    reportPeriod.addEventListener('change', (e) => {
      const custom = e.target.value === 'custom';
      document.getElementById('custom-dates').style.display = custom ? '' : 'none';
      document.getElementById('custom-dates-end').style.display = custom ? '' : 'none';
    });
  }
  
  // Apply filter button
  const btnApplyFilter = document.getElementById('btn-apply-filter');
  if (btnApplyFilter) {
    btnApplyFilter.addEventListener('click', () => {
      loadAdminReportsFiltered();
    });
  }
}

// Expose admin functions
window.editEvent = editEvent;
window.deleteEvent = deleteEvent;
window.approveExpense = approveExpense;
window.rejectExpense = rejectExpense;
window.payExpense = payExpense;
window.deleteExpense = deleteExpense;
window.deleteAnnouncement = deleteAnnouncement;
window.deleteDocument = deleteDocument;
window.exportToExcel = exportToExcel;
window.exportToPDF = exportToPDF;
window.addSchedule = addSchedule;
window.removeSchedule = removeSchedule;
window.toggleStream = toggleStream;
window.deleteStream = deleteStream;
window.openUploadModal = openUploadModal;
window.closeUploadModal = closeUploadModal;


