import { api } from './api.js';
import { renderHeader, setBusy, showFormError, toast } from './ui.js';

export async function logout() {
  try { await api.auth.logout(); } catch { /* session already gone */ }
  window.location.href = 'login.html';
}

/** Call at the top of every private page. Redirects to login if not signed in. */
export async function initAppPage(active) {
  try {
    const { user } = await api.auth.me();
    renderHeader({ user, active, onLogout: logout });
    return user;
  } catch (err) {
    if (err.status !== 401) {
      renderHeader();
      toast(err.message, 'error');
    }
    return new Promise(() => {}); // stop the page script; we are redirecting or the server is down
  }
}

async function redirectIfSignedIn() {
  try { await api.auth.check(); window.location.href = 'dashboard.html'; } catch { /* not signed in */ }
}

export function initLogin() {
  renderHeader();
  redirectIfSignedIn();
  if (new URLSearchParams(location.search).get('registered')) toast('Account created. Log in to continue.', 'success');

  const form = document.getElementById('loginForm');
  const errorBox = document.getElementById('formError');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    showFormError(errorBox, '');
    const btn = form.querySelector('button[type=submit]');
    setBusy(btn, true, 'Logging in…');
    try {
      await api.auth.login({ identifier: form.identifier.value.trim(), password: form.password.value });
      window.location.href = 'dashboard.html';
    } catch (err) {
      showFormError(errorBox, err.message);
      setBusy(btn, false);
    }
  });
}

export function initRegister() {
  renderHeader();
  redirectIfSignedIn();
  const form = document.getElementById('registerForm');
  const errorBox = document.getElementById('formError');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    showFormError(errorBox, '');
    const username = form.username.value.trim();
    if (!/^[A-Za-z0-9_.-]{3,30}$/.test(username)) {
      return showFormError(errorBox, 'Username must be 3-30 characters: letters, numbers, dot, dash or underscore.');
    }
    if (form.password.value.length < 8) return showFormError(errorBox, 'Password must be at least 8 characters.');
    if (form.password.value !== form.confirm.value) return showFormError(errorBox, 'Passwords do not match.');

    const btn = form.querySelector('button[type=submit]');
    setBusy(btn, true, 'Creating account…');
    try {
      await api.auth.register({ username, email: form.email.value.trim(), password: form.password.value });
      window.location.href = 'login.html?registered=1';
    } catch (err) {
      showFormError(errorBox, err.message);
      setBusy(btn, false);
    }
  });
}
