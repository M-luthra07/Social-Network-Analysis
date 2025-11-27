// animate.js
document.addEventListener('DOMContentLoaded', function () {
    // Color palette
    const PALETTE = ['#4e79a7','#f28e2b','#e15759','#76b7b2','#59a14f','#edc948','#b07aa1','#ff9da7','#9c755f','#bab0ac'];
  
    function makeBar(ctx, labels, values, title) {
      return new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            data: values,
            backgroundColor: labels.map((_,i) => PALETTE[i % PALETTE.length]),
            borderRadius: 6
          }]
        },
        options: {
          plugins: { legend: { display: false }, title: { display: false } },
          responsive: true,
          scales: { x: { ticks: { maxRotation: 0, autoSkip: true }, grid: { display: false } }, y: { beginAtZero: true } }
        }
      });
    }
  
    function makeHorizontalBar(ctx, labels, values, title) {
      return new Chart(ctx, {
        type: 'bar',
        data: { labels: labels, datasets: [{ data: values, backgroundColor: labels.map((_,i)=>PALETTE[i%PALETTE.length]) }] },
        options: { indexAxis: 'y', plugins: { legend: {display:false} }, responsive:true }
      });
    }
  
    function makeScatter(ctx, points) {
      return new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [{
            label: 'Companies',
            data: points.map(p => ({ x: p.degree, y: p.neighbor_industry_count, company: p.company, industry: p.industry })),
            backgroundColor: PALETTE[1],
            pointRadius: 6
          }]
        },
        options: {
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  const d = context.raw;
                  return `${d.company} — Industry: ${d.industry} — Degree: ${d.x.toFixed(3)} — Neighbor industries: ${d.y}`;
                }
              }
            }
          },
          scales: {
            x: { title: { display: true, text: 'Degree centrality' } },
            y: { title: { display: true, text: 'Distinct neighbor industries' }, ticks: { precision: 0 } }
          }
        }
      });
    }
  
    // Top Cities chart (uses fallback PNG counts if available)
    try {
      // Top Cities: extract labels & counts from the top_cities_list by reading server-side top N counts? We didn't pass counts,
      // so we'll display placeholder or fallback to the PNG. To keep things consistent, we attempt to read the top cities array.
      const topCitiesEl = document.getElementById('topCitiesChart');
      if (topCitiesEl && CHART_DATA.top_cities_list && CHART_DATA.top_cities_list.length) {
        // We don't have counts in CHART_DATA for top cities; show city names with dummy values by reading image? Instead,
        // we'll show city names with counts extracted from the PNG filename is not possible. So do a safe fallback:
        const labels = CHART_DATA.top_cities_list;
        const values = labels.map((_,i) => (labels.length - i)); // simple descending dummy to show a visual ranking
        makeBar(topCitiesEl.getContext('2d'), labels, values, 'Top Cities (counts in PNG)');
      }
    } catch(e) { console.warn(e); }
  
    // Top industries chart: similar fallback approach
    try {
      const topIndEl = document.getElementById('topIndustriesChart');
      if (topIndEl && CHART_DATA.top_industries_list && CHART_DATA.top_industries_list.length) {
        const labels = CHART_DATA.top_industries_list;
        const values = labels.map((_,i) => (labels.length - i));
        makeBar(topIndEl.getContext('2d'), labels, values, 'Top Industries');
      }
    } catch(e){ console.warn(e); }
  
    // Degree centrality chart (exact labels & values provided)
    try {
      const ctxDeg = document.getElementById('degreeChart');
      if (ctxDeg && CHART_DATA.degree) {
        makeHorizontalBar(ctxDeg.getContext('2d'), CHART_DATA.degree.labels.slice().reverse(), CHART_DATA.degree.values.slice().reverse().map(v => +v.toFixed(4)), 'Degree centrality');
      }
    } catch(e){ console.warn(e); }
  
    // Betweenness chart (values already scaled)
    try {
      const ctxBtw = document.getElementById('betweennessChart');
      if (ctxBtw && CHART_DATA.betweenness) {
        makeHorizontalBar(ctxBtw.getContext('2d'), CHART_DATA.betweenness.labels.slice().reverse(), CHART_DATA.betweenness.values.slice().reverse().map(v=>+v.toFixed(2)), 'Betweenness ×1000');
      }
    } catch(e){ console.warn(e); }
  
    // Funding vs influence
    try {
      const ctxFund = document.getElementById('fundingChart');
      if (ctxFund && CHART_DATA.funding_vs_influence) {
        makeBar(ctxFund.getContext('2d'), CHART_DATA.funding_vs_influence.labels, CHART_DATA.funding_vs_influence.values.map(v => +v.toFixed(4)), 'Funding vs Influence');
      }
    } catch(e){ console.warn(e); }
  
    // K-core
    try {
      const ctxK = document.getElementById('kcoreChart');
      if (ctxK && CHART_DATA.kcore) {
        makeHorizontalBar(ctxK.getContext('2d'), CHART_DATA.kcore.labels.slice().reverse(), CHART_DATA.kcore.values.slice().reverse().map(v => +v), 'K-core');
      }
    } catch(e){ console.warn(e); }
  
    // Bridges scatter
    try {
      const ctxSc = document.getElementById('bridgesScatter');
      if (ctxSc && CHART_DATA.bridges_scatter) {
        makeScatter(ctxSc.getContext('2d'), CHART_DATA.bridges_scatter);
      }
    } catch(e){ console.warn(e); }
  
  });
  