// Chart.js is loaded from a CDN <script> tag, so `Chart` is a global.
const PALETTE = ['#14b8a6', '#6366f1', '#f59e0b', '#ef4444', '#06b6d4', '#8b5cf6', '#84cc16', '#ec4899', '#64748b'];
export const colorFor = (i) => PALETTE[i % PALETTE.length];

let chart = null;

export function renderCategoryChart(canvas, categories) {
  if (chart) { chart.destroy(); chart = null; }
  if (!categories.length) return;
  const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text').trim();
  chart = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: categories.map((c) => c.category_name),
      datasets: [{
        data: categories.map((c) => Number(c.total)),
        backgroundColor: categories.map((_, i) => colorFor(i)),
        borderWidth: 0,
      }],
    },
    options: {
      maintainAspectRatio: false,
      cutout: '62%',
      plugins: { legend: { position: 'bottom', labels: { color: textColor, boxWidth: 12 } } },
    },
  });
}
