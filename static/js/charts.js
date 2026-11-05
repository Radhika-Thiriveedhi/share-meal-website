/* ShareMeal Lightweight SVG / CSS Data Visualizer
   Zero external API or CDN dependencies. Renders directly in pure vanilla JS.
*/

window.renderBarChart = function(containerId, data, options = {}) {
  const container = document.getElementById(containerId);
  if (!container || !data || data.length === 0) return;

  const maxValue = Math.max(...data.map(d => d.value), 1);
  const chartHeight = options.height || 180;

  let html = `<div style="display:flex;align-items:flex-end;gap:1rem;height:${chartHeight}px;padding-top:1.5rem;border-bottom:1px solid var(--color-border);">`;

  data.forEach((item) => {
    const heightPercent = Math.round((item.value / maxValue) * 100);
    const color = item.color || "var(--color-primary)";
    html += `
      <div style="flex:1;display:flex;flex-direction:column;align-items:center;height:100%;justify-content:flex-end;">
        <span style="font-size:0.75rem;font-weight:600;margin-bottom:4px;color:var(--color-text-main);">${item.value}</span>
        <div style="width:100%;max-width:40px;height:${heightPercent}%;background-color:${color};border-radius:4px 4px 0 0;transition:height 0.4s ease;" title="${item.label}: ${item.value}"></div>
        <span style="font-size:0.75rem;color:var(--color-text-muted);margin-top:6px;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:60px;">${item.label}</span>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
};
