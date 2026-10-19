import { api } from './api.js';
import { initAppPage } from './auth.js';
import { escapeHtml, formatDate, formatMoney, setBusy, showFormError, toast, todayISO } from './ui.js';

await initAppPage('expenses');

const $ = (id) => document.getElementById(id);
const form = $('expenseForm');
const state = { page: 1, pageSize: 10, total: 0, items: [], categoryFilter: '', editingId: null };

async function loadCategories() {
  const cats = await api.categories.list();
  const options = cats.map((c) => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join('');
  form.category_id.innerHTML = options;
  $('filterCategory').innerHTML = '<option value="">All categories</option>' + options;
}

async function loadExpenses() {
  $('tableBody').innerHTML = '<tr><td colspan="5" class="loading"><span class="spinner"></span> Loading…</td></tr>';
  try {
    const data = await api.expenses.list({
      page: state.page, page_size: state.pageSize, category_id: state.categoryFilter,
    });
    state.items = data.items;
    state.total = data.total;
    const pages = Math.max(1, Math.ceil(data.total / state.pageSize));
    if (state.page > pages) { state.page = pages; return loadExpenses(); }
    renderTable(pages);
  } catch (err) {
    $('tableBody').innerHTML = '';
    toast(err.message, 'error');
  }
}

function renderTable(pages) {
  const body = $('tableBody');
  $('emptyState').classList.toggle('hidden', state.items.length > 0);
  $('tableWrap').classList.toggle('hidden', state.items.length === 0);
  body.innerHTML = state.items.map((e) => `
    <tr>
      <td>${escapeHtml(e.description)}</td>
      <td class="num">${formatMoney(e.amount)}</td>
      <td><span class="badge">${escapeHtml(e.category_name)}</span></td>
      <td>${formatDate(e.expense_date)}</td>
      <td class="actions">
        <button class="btn btn-ghost btn-sm" data-action="edit" data-id="${e.id}">Edit</button>
        <button class="btn btn-danger btn-sm" data-action="delete" data-id="${e.id}">Delete</button>
      </td>
    </tr>`).join('');
  $('pageInfo').textContent = `Page ${state.page} of ${pages} · ${state.total} expense${state.total === 1 ? '' : 's'}`;
  $('prevPage').disabled = state.page <= 1;
  $('nextPage').disabled = state.page >= pages;
}

function resetForm() {
  state.editingId = null;
  form.reset();
  form.expense_date.value = todayISO();
  $('formTitle').textContent = 'Add expense';
  form.querySelector('button[type=submit]').textContent = 'Add expense';
  $('cancelEdit').classList.add('hidden');
  showFormError($('formError'), '');
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const errorBox = $('formError');
  showFormError(errorBox, '');
  const description = form.description.value.trim();
  const amount = form.amount.value.trim();
  if (!description) return showFormError(errorBox, 'Enter a description.');
  if (!(Number(amount) > 0)) return showFormError(errorBox, 'Amount must be greater than zero.');
  if (!/^\d+(\.\d{1,2})?$/.test(amount)) return showFormError(errorBox, 'Amount can have at most 2 decimal places.');
  if (!form.expense_date.value) return showFormError(errorBox, 'Choose a date.');

  const payload = {
    description, amount, category_id: Number(form.category_id.value), expense_date: form.expense_date.value,
  };
  const btn = form.querySelector('button[type=submit]');
  const editing = state.editingId !== null;
  setBusy(btn, true, 'Saving…');
  try {
    if (editing) await api.expenses.update(state.editingId, payload);
    else await api.expenses.create(payload);
    toast(editing ? 'Expense updated.' : 'Expense added.', 'success');
    setBusy(btn, false);
    resetForm();
    await loadExpenses();
  } catch (err) {
    setBusy(btn, false);
    showFormError(errorBox, err.message);
  }
});

$('tableBody').addEventListener('click', async (e) => {
  const btn = e.target.closest('button[data-action]');
  if (!btn) return;
  const id = Number(btn.dataset.id);
  const expense = state.items.find((x) => x.id === id);
  if (!expense) return;
  if (btn.dataset.action === 'edit') {
    state.editingId = id;
    form.description.value = expense.description;
    form.amount.value = expense.amount;
    form.category_id.value = expense.category_id;
    form.expense_date.value = expense.expense_date;
    $('formTitle').textContent = 'Edit expense';
    form.querySelector('button[type=submit]').textContent = 'Save changes';
    $('cancelEdit').classList.remove('hidden');
    form.description.focus();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else if (confirm(`Delete "${expense.description}" (${formatMoney(expense.amount)})? This cannot be undone.`)) {
    try {
      await api.expenses.remove(id);
      toast('Expense deleted.', 'success');
      if (state.editingId === id) resetForm();
      await loadExpenses();
    } catch (err) { toast(err.message, 'error'); }
  }
});

$('cancelEdit').addEventListener('click', resetForm);
$('prevPage').addEventListener('click', () => { state.page -= 1; loadExpenses(); });
$('nextPage').addEventListener('click', () => { state.page += 1; loadExpenses(); });
$('filterCategory').addEventListener('change', (e) => { state.categoryFilter = e.target.value; state.page = 1; loadExpenses(); });

try { await loadCategories(); } catch (err) { toast(err.message, 'error'); }
resetForm();
loadExpenses();
