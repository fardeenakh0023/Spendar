// Small shared helpers: theme, header, toasts, formatting.
const THEME_KEY = 'spendar-theme'; // only a light/dark preference is stored here

export function initTheme() {
  const saved = localStorage.getItem(THEME_KEY)
    || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.dataset.theme = saved;
}
initTheme();

function toggleTheme() {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem(THEME_KEY, next);
  document.dispatchEvent(new CustomEvent('themechange'));
  const btn = document.getElementById('themeBtn');
  if (btn) btn.textContent = next === 'dark' ? '☀️' : '🌙';
}

const BRAND = `
  <a href="index.html" class="brand" aria-label="Spendar home">
    <svg class="brand-icon" viewBox="0 0 48 48" aria-hidden="true">
      <defs><linearGradient id="spendarGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#14b8a6"/><stop offset="100%" stop-color="#6366f1"/>
      </linearGradient></defs>
      <rect width="48" height="48" rx="13" fill="url(#spendarGrad)"/>
      <rect x="11" y="27" width="6" height="11" rx="2" fill="#fff" opacity=".7"/>
      <rect x="21" y="20" width="6" height="18" rx="2" fill="#fff" opacity=".85"/>
      <rect x="31" y="11" width="6" height="27" rx="2" fill="#fff"/>
    </svg>
    <span class="brand-name">Spend<span class="brand-accent">ar</span></span>
  </a>`;

const APP_LINKS = [
  ['dashboard', 'Dashboard', 'dashboard.html'],
  ['expenses', 'Expenses', 'expenses.html'],
  ['categories', 'Categories', 'categories.html'],
  ['history', 'History', 'history.html'],
];

export function renderHeader({ user = null, active = '', onLogout = null } = {}) {
  const el = document.getElementById('site-header');
  if (!el) return;
  const themeIcon = document.documentElement.dataset.theme === 'dark' ? '☀️' : '🌙';
  const themeBtn = `<button id="themeBtn" class="icon-btn" aria-label="Toggle light or dark theme">${themeIcon}</button>`;
  let nav;
  if (user) {
    const links = APP_LINKS.map(([key, label, href]) =>
      `<a class="nav-link ${key === active ? 'active' : ''}" href="${href}">${label}</a>`).join('');
    nav = `${links}<span class="nav-user">${escapeHtml(user.username)}</span>
           ${themeBtn}<button id="logoutBtn" class="btn btn-ghost btn-sm">Log out</button>`;
  } else {
    nav = `<a class="nav-link" href="login.html">Log in</a>
           <a class="btn btn-primary btn-sm" href="register.html">Get started</a>${themeBtn}`;
  }
  el.className = 'site-header';
  el.innerHTML = `${BRAND}<nav class="site-nav">${nav}</nav>`;
  document.getElementById('themeBtn').addEventListener('click', toggleTheme);
  if (onLogout) document.getElementById('logoutBtn').addEventListener('click', onLogout);
}

export function toast(message, type = 'info') {
  let box = document.getElementById('toasts');
  if (!box) {
    box = document.createElement('div');
    box.id = 'toasts';
    document.body.appendChild(box);
  }
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.setAttribute('role', type === 'error' ? 'alert' : 'status');
  t.textContent = message;
  box.appendChild(t);
  setTimeout(() => t.remove(), 4500);
}

export function setBusy(button, busy, busyText = 'Please wait…') {
  if (busy) { button.dataset.label = button.textContent; button.textContent = busyText; }
  else if (button.dataset.label) button.textContent = button.dataset.label;
  button.disabled = busy;
}

export function showFormError(el, message) {
  el.textContent = message || '';
  el.classList.toggle('hidden', !message);
}

export function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

const money = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 });
export const formatMoney = (n) => money.format(Number(n));

export function parseISO(iso) {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d);
}
export function toISO(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
export const todayISO = () => toISO(new Date());
export const formatDate = (iso) =>
  parseISO(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
