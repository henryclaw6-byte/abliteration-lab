window.LiberationCharts = (() => {
  const trendCtx = document.getElementById('trend-chart');
  const comparisonCtx = document.getElementById('comparison-chart');

  const trendChart = new Chart(trendCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{ label: 'Benchmark', data: [], borderColor: '#e94560' }]
    },
    options: { animation: { duration: 250 }, responsive: true }
  });

  const comparisonChart = new Chart(comparisonCtx, {
    type: 'bar',
    data: {
      labels: ['GPT-4', 'Claude 3', 'Gemini 1.5'],
      datasets: [
        { label: 'Helpfulness', data: [0, 0, 0], backgroundColor: 'rgba(233,69,96,.8)' },
        { label: 'Safety', data: [0, 0, 0], backgroundColor: 'rgba(120,110,255,.8)' },
        { label: 'Latency', data: [0, 0, 0], backgroundColor: 'rgba(90,180,220,.8)' }
      ]
    },
    options: { responsive: true, animation: { duration: 250 } }
  });

  function renderGauges(refusalRates) {
    const gauges = document.getElementById('gauges');
    gauges.innerHTML = '';
    Object.entries(refusalRates).forEach(([model, value]) => {
      const d = document.createElement('div');
      d.className = 'gauge';
      d.innerHTML = `<canvas width="110" height="110"></canvas><div>${model}: ${(value * 100).toFixed(1)}%</div>`;
      gauges.appendChild(d);
      const ctx = d.querySelector('canvas').getContext('2d');
      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Refusal', 'Remaining'],
          datasets: [{ data: [value * 100, 100 - value * 100], backgroundColor: ['#e94560', 'rgba(180,180,200,.2)'] }]
        },
        options: {
          cutout: '70%',
          plugins: { legend: { display: false } },
          animation: { duration: 280 }
        }
      });
    });
  }

  function updateAnalytics(payload) {
    renderGauges(payload.refusal_rates);
    trendChart.data.labels = payload.benchmark_trends.map(x => x.t);
    trendChart.data.datasets[0].data = payload.benchmark_trends.map(x => x.value);
    trendChart.update('none');
    const models = ['GPT-4', 'Claude 3', 'Gemini 1.5'];
    comparisonChart.data.datasets[0].data = models.map(m => payload.comparison.helpfulness[m]);
    comparisonChart.data.datasets[1].data = models.map(m => payload.comparison.safety[m]);
    comparisonChart.data.datasets[2].data = models.map(m => payload.comparison.latency[m]);
    comparisonChart.update('none');
  }

  function exportChart(chart, name) {
    const link = document.createElement('a');
    link.download = `${name}.png`;
    link.href = chart.toBase64Image('image/png', 1);
    link.click();
  }

  return {
    updateAnalytics,
    exportTrend: () => exportChart(trendChart, 'trend-chart'),
    exportComparison: () => exportChart(comparisonChart, 'comparison-chart')
  };
})();
