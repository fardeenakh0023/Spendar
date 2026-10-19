import { api } from './api.js';
import { initAppPage } from './auth.js';
import { renderCategoryChart, colorFor } from './charts.js';
import { escapeHtml, formatDate, formatMoney, parseISO, toast, toISO } from './ui.js';

await initAppPage('dashboard');

const state = { period: 'month', ref: new Date(), start: '', end: '', cats: [] };
const $ = (id) => document.getElementById(id);

function query() {
  return state.period === 'custom'
    ? { period: 'custom', start_date: state.start, end_date: state.end }
    : { period: state.period, ref_date: toISO(state.ref) };
}

function shift(dir) {
  const d = new Date(state.ref.getFullYear(), state.ref.getMonth(), state.ref.getDate());
  if (state.period === 'week') d.setDate(d.getDate() + 7 * dir);
  if (state.period === 'month') { d.setDate(1); d.setMonth(d.getMonth() + dir); }
  if (state.period === 'year') { d.setMonth(0, 1); d.setFullYear(d.getFullYear() + dir); }
  state.ref = d;
  load();
}

function renderCategories() {
  const box = $('categoryList');
  if (!state.cats.length) {
    box.innerHTML = '<div class="empty"><strong>No spending in this period</strong>Add an expense to see it here.</div>';
    return;
  }
  box.innerHTML = state.cats.map((c, i) => `
    <div class="cat-row">
      <div class="top"><span>${escapeHtml(c.category_name)} <span class="muted">(${c.count})</span></span>
        <span><strong>${formatMoney(c.total)}</strong> <span class="muted">${c.percentage}%</span></span></div>
      <div class="bar"><span style="width:${c.percentage}%;background:${colorFor(i)}"></span></div>
    </div>`).join('');
}

async function load() {
  $('statsLoading').classList.remove('hidden');
  try {
    const q = query();
    const [summary, breakdown] = await Promise.all([api.dashboard.summary(q), api.dashboard.breakdown(q)]);
    const { start_date, end_date } = summary.period;
    $('rangeLabel').textContent = `${formatDate(start_date)} – ${formatDate(end_date)}`;
    $('statTotal').textContent = formatMoney(summary.total_spent);
    $('statCount').textContent = summary.expense_count;
    $('statAvg').textContent = formatMoney(summary.average_per_day);
    $('statTop').textContent = summary.top_category || '—';
    state.cats = breakdown.categories;
    renderCategoryChart($('categoryChart'), state.cats);
    $('chartEmpty').classList.toggle('hidden', state.cats.length > 0);
    $('categoryChart').classList.toggle('hidden', state.cats.length === 0);
    renderCategories();
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    $('statsLoading').classList.add('hidden');
  }
}

document.querySelectorAll('.tab').forEach((tab) =>
  tab.addEventListener('click', () => {
    state.period = tab.dataset.period;
    document.querySelectorAll('.tab').forEach((t) => t.classList.toggle('active', t === tab));
    const custom = state.period === 'custom';
    $('customRange').classList.toggle('hidden', !custom);
    $('rangeNav').classList.toggle('hidden', custom);
    if (!custom) load();
  }));

$('prevBtn').addEventListener('click', () => shift(-1));
$('nextBtn').addEventListener('click', () => shift(1));
$('applyRange').addEventListener('click', () => {
  state.start = $('startDate').value;
  state.end = $('endDate').value;
  if (!state.start || !state.end) return toast('Choose both a start and an end date.', 'error');
  if (parseISO(state.start) > parseISO(state.end)) return toast('Start date must not be after end date.', 'error');
  load();
});
document.addEventListener('themechange', () => renderCategoryChart($('categoryChart'), state.cats));

load();
