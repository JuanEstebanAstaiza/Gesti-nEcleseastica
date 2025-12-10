const API_BASE = "/api";

const loginForm = document.getElementById("login-form");
const donationForm = document.getElementById("donation-form");
const documentForm = document.getElementById("document-form");
const languageToggle = document.getElementById("language-toggle");
const eventForm = document.getElementById("event-form");
const registrationForm = document.getElementById("registration-form");
const refreshDashboardBtn = document.getElementById("refresh-dashboard");
const metricCount = document.getElementById("metric-count");
const metricAmount = document.getElementById("metric-amount");
const metricByType = document.getElementById("metric-by-type");

function notify(message, type = "info") {
  // Lugar para integrar notificaciones; por ahora usa alert mínimo.
  // eslint-disable-next-line no-alert
  alert(`${type.toUpperCase()}: ${message}`);
}

let accessToken = null;

async function postForm(url, formData, token) {
  const headers = token ? { Authorization: `Bearer ${token}` } : accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
  const res = await fetch(url, {
    method: "POST",
    body: formData,
    headers,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Error al procesar la solicitud");
  }
  return res.json();
}

loginForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(loginForm);
  const payload = Object.fromEntries(formData.entries());
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Credenciales inválidas");
    const data = await res.json();
    accessToken = data.access_token;
    notify("Sesión iniciada.");
  } catch (err) {
    notify(err.message, "error");
  }
});

donationForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(donationForm);
  try {
    await postForm(`${API_BASE}/donations`, formData);
    notify("Donación registrada.");
    donationForm.reset();
  } catch (err) {
    notify(err.message, "error");
  }
});

documentForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(documentForm);
  try {
    await postForm(`${API_BASE}/documents`, formData);
    notify("Documento cargado.");
    documentForm.reset();
  } catch (err) {
    notify(err.message, "error");
  }
});

languageToggle?.addEventListener("click", () => {
  notify("Selector de idioma en construcción (ES/EN).", "info");
});

if (window.feather) {
  window.feather.replace();
}

eventForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(eventForm).entries());
  try {
    const res = await fetch(`${API_BASE}/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(await res.text());
    notify("Evento creado.");
    eventForm.reset();
  } catch (err) {
    notify(err.message, "error");
  }
});

registrationForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(registrationForm).entries());
  try {
    const res = await fetch(`${API_BASE}/events/${data.event_id}/registrations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(await res.text());
    notify("Registro guardado.");
    registrationForm.reset();
  } catch (err) {
    notify(err.message, "error");
  }
});

async function loadDashboard() {
  if (!accessToken) {
    metricCount.textContent = "-";
    metricAmount.textContent = "-";
    metricByType.innerHTML = "";
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/reports/summary`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    metricCount.textContent = data.total_donations;
    metricAmount.textContent = `$ ${data.total_amount.toFixed(2)}`;
    metricByType.innerHTML = "";
    Object.entries(data.by_type || {}).forEach(([k, v]) => {
      const li = document.createElement("li");
      li.textContent = `${k}: ${v}`;
      metricByType.appendChild(li);
    });
  } catch (err) {
    notify(err.message, "error");
  }
}

refreshDashboardBtn?.addEventListener("click", () => loadDashboard());

