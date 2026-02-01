const API_BASE = process.env.REACT_APP_API_URL || '';

export function getToken() {
  return localStorage.getItem('accessToken');
}

export async function api(path, options = {}) {
  const headers = { ...options.headers };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(API_BASE + path, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || data.message || 'Request failed');
  return data;
}

export async function register(email, password, fullName) {
  return api('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
}

export async function login(email, password) {
  return api('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
}

export async function me() {
  return api('/api/auth/me');
}

export async function resolveLocation(latitude, longitude, accuracy) {
  return api('/api/location/resolve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latitude, longitude, accuracy_m: accuracy }),
  });
}
export async function extractTicket(file) {
  const form = new FormData();
  form.append('ticket', file);
  return api('/api/ticket/extract', { method: 'POST', body: form });
}
export async function submitComplaint(formData) {
  return api('/api/complaint/submit', { method: 'POST', body: formData });
}
export async function getMyComplaints() {
  return api('/api/complaint/my');
}
export async function getComplaint(id) {
  return api(`/api/complaint/${id}`);
}
export async function adminComplaints(params = {}) {
  const q = new URLSearchParams(params).toString();
  return api('/api/admin/complaints' + (q ? '?' + q : ''));
}
export async function adminComplaintsMap() {
  return api('/api/admin/complaints/map');
}
export async function adminSetStatus(complaintId, status) {
  return api(`/api/admin/complaints/${complaintId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
}

export async function adminAssign(complaintId, department) {
  return api(`/api/admin/complaints/${complaintId}/assign`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ department }),
  });
}

export async function adminInsights() {
  return api('/api/admin/insights');
}
