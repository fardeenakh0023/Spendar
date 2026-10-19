import { api } from './api.js';
import { initAppPage } from './auth.js';
import { escapeHtml, setBusy, showFormError, toast } from './ui.js';

await initAppPage('categories');

const $ = (id) => document.getElementById(id);
const form = $('categoryForm');
let categories = [];
let editingId = null;

function render() {
  const body = $('tableBody');
  $('emptyState').classList.toggle('hidden', categories.length > 0);
  $('tableWrap').classList.toggle('hidden', categories.length === 0);
  body.innerHTML = categories.map((c) => {
    if (c.id === editingId) {
      return `<tr><td colspan="2"><div class="inline-edit">
        <input id="renameInput" value="${escapeHtml(c.name)}" maxlength="50" aria-label="Category name">
        <button class="btn btn-primary btn-sm" data-action="save" data-id="${c.id}">Save</button>
        <button class="btn btn-ghost btn-sm" data-action="cancel">Cancel</button></div></td></tr>`;
    }
    return `<tr><td>${escapeHtml(c.name)}</td><td class="actions">
      <button class="btn btn-ghost btn-sm" data-action="rename" data-id="${c.id}">Rename</button>
      <button class="btn btn-danger btn-sm" data-action="delete" data-id="${c.id}">Delete</button></td></tr>`;
  }).join('');
  const input = $('renameInput');
  if (input) { input.focus(); input.select(); }
}

async function load() {
  try { categories = await api.categories.list(); render(); }
  catch (err) { toast(err.message, 'error'); }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const errorBox = $('formError');
  showFormError(errorBox, '');
  const name = form.name.value.trim();
  if (!name) return showFormError(errorBox, 'Enter a category name.');
  const btn = form.querySelector('button[type=submit]');
  setBusy(btn, true, 'Adding…');
  try {
    await api.categories.create(name);
    form.reset();
    toast('Category added.', 'success');
    await load();
  } catch (err) { showFormError(errorBox, err.message); }
  setBusy(btn, false);
});

$('tableBody').addEventListener('click', async (e) => {
  const btn = e.target.closest('button[data-action]');
  if (!btn) return;
  const id = Number(btn.dataset.id);
  const cat = categories.find((c) => c.id === id);
  try {
    switch (btn.dataset.action) {
      case 'rename': editingId = id; render(); break;
      case 'cancel': editingId = null; render(); break;
      case 'save': {
        const name = $('renameInput').value.trim();
        if (!name) return toast('Category name cannot be empty.', 'error');
        await api.categories.rename(id, name);
        editingId = null;
        toast('Category renamed.', 'success');
        await load();
        break;
      }
      case 'delete':
        if (confirm(`Delete the category "${cat.name}"?`)) {
          await api.categories.remove(id);
          toast('Category deleted.', 'success');
          await load();
        }
        break;
    }
  } catch (err) { toast(err.message, 'error'); }
});

load();
