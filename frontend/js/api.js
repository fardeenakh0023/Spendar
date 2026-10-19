// All communication with the backend lives here.
// The host follows the page's host so the session cookie matches (localhost vs 127.0.0.1).
const API_BASE = `${location.protocol}//${location.hostname}:8000/api/v1`;

let csrfToken = null; // kept in memory only, never in localStorage

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, { method = 'GET', body, query, redirectOn401 = true } = {}) {
  const url = new URL(API_BASE + path);
  for (const [key, value] of Object.entries(query || {})) {
    if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, value);
  }
  const headers = {};
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (method !== 'GET' && csrfToken) headers['X-CSRF-Token'] = csrfToken;

  let res;
  try {
    res = await fetch(url, {
      method, headers, credentials: 'include',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError('Cannot reach the server. Check that the backend is running on port 8000.', 0);
  }

  if (res.status === 204) return null;
  let data = null;
  try { data = await res.json(); } catch { /* empty body */ }

  if (!res.ok) {
    if (res.status === 401 && redirectOn401) window.location.href = 'login.html';
    throw new ApiError(data?.detail || `Request failed (${res.status})`, res.status);
  }
  return data;
}

export const api = {
  auth: {
    register: (body) => request('/auth/register', { method: 'POST', body, redirectOn401: false }),
    async login(body) {
      const data = await request('/auth/login', { method: 'POST', body, redirectOn401: false });
      csrfToken = data.csrf_token;
      return data;
    },
    async logout() {
      await request('/auth/logout', { method: 'POST', redirectOn401: false });
      csrfToken = null;
    },
    async me() {
      const data = await request('/auth/me');
      csrfToken = data.csrf_token;
      return data;
    },
    async check() { // like me(), but never redirects
      const data = await request('/auth/me', { redirectOn401: false });
      csrfToken = data.csrf_token;
      return data;
    },
  },
  expenses: {
    list: (query) => request('/expenses', { query }),
    create: (body) => request('/expenses', { method: 'POST', body }),
    update: (id, body) => request(`/expenses/${id}`, { method: 'PATCH', body }),
    remove: (id) => request(`/expenses/${id}`, { method: 'DELETE' }),
  },
  categories: {
    list: () => request('/categories'),
    create: (name) => request('/categories', { method: 'POST', body: { name } }),
    rename: (id, name) => request(`/categories/${id}`, { method: 'PATCH', body: { name } }),
    remove: (id) => request(`/categories/${id}`, { method: 'DELETE' }),
  },
  dashboard: {
    summary: (query) => request('/dashboard/summary', { query }),
    breakdown: (query) => request('/dashboard/category-breakdown', { query }),
    history: (query) => request('/dashboard/history', { query }),
  },
};
