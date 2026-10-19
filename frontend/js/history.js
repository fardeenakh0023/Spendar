import { api } from './api.js';
import { initAppPage } from './auth.js';
import { escapeHtml, formatDate, formatMoney, parseISO, toast, todayISO } from './ui.js';

await initAppPage('history');

const $ = (id) => document.getElementById(id);
const state = { page: 1, pageSize: 15 };

function query() {
  const period = $('period').value;
  const base = { page: state.page, page_size: state.pageSize, period };
  if (period === 'custom') return { ...base, start_date: $('startDate').value, end_date: $('endDate').value };
  return { ...base, ref_date: $('refDate').value || todayISO() };
}

async function load() {
  const q = query();
  if (q.period === 'custom') {
    if (!q.start_date || !q.end_date) return toast('Choose both a start and an end date.', 'error');
    if (parseISO(q.start_date) > parseISO(q.end_date)) return toast('Start date must not be after end date.', 'error');
  }
  $('tableBody').innerHTML = '<tr><td colspan="4" class="loading"><span class="spinner"></span> Loading…</td></tr>';
  try {
    const data = await api.dashboard.history(q);
    $('rangeLabel').textContent = `${formatDate(data.period.start_date)} – ${formatDate(data.period.end_date)}`;
    $('totalSpent').textContent = formatMoney(data.total_spent);
    $('expenseCount').textContent = data.expense_count;
    const pages = Math.max(1, Math.ceil(data.expense_count / state.pageSize));
    $('emptyState').classList.toggle('hidden', data.items.length > 0);
    $('tableWrap').classList.toggle('hidden', data.items.length === 0);
    $('tableBody').innerHTML = data.items.map((e) => `
      <tr><td>${formatDate(e.expense_date)}</td><td>${escapeHtml(e.description)}</td>
      <td><span class="badge">${escapeHtml(e.category_name)}</span></td>
      <td class="num">${formatMoney(e.amount)}</td></tr>`).join('');
    $('pageInfo').textContent = `Page ${state.page} of ${pages}`;
    $('prevPage').disabled = state.page <= 1;
    $('nextPage').disabled = state.page >= pages;
  } catch (err) {
    $('tableBody').innerHTML = '';
    toast(err.message, 'error');
  }
}

function syncControls() {
  const custom = $('period').value === 'custom';
  $('customFields').classList.toggle('hidden', !custom);
  $('refField').classList.toggle('hidden', custom);
}

$('period').addEventListener('change', () => { syncControls(); state.page = 1; if ($('period').value !== 'custom') load(); });
$('refDate').addEventListener('change', () => { state.page = 1; load(); });
$('applyRange').addEventListener('click', () => { state.page = 1; load(); });
$('prevPage').addEventListener('click', () => { state.page -= 1; load(); });
$('nextPage').addEventListener('click', () => { state.page += 1; load(); });

$('refDate').value = todayISO();
syncControls();
load();
