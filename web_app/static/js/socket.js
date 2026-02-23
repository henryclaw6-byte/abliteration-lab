(() => {
  const socket = io();
  const chatLog = document.getElementById('chat-log');
  const promptInput = document.getElementById('prompt-input');
  const sendBtn = document.getElementById('send-btn');
  const modelSelect = document.getElementById('model-select');
  const status = document.getElementById('connection-status');
  const typing = document.getElementById('typing-indicator');
  const toast = document.getElementById('toast');
  const presets = structuredClone(window.__INITIAL_PRESETS__);
  let streamEl = null;
  let batchResults = [];

  function notify(message) {
    toast.textContent = message;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 1800);
  }

  Object.keys(presets).forEach(model => {
    const option = document.createElement('option');
    option.value = model;
    option.textContent = model;
    modelSelect.appendChild(option);
    document.getElementById('settings-model').appendChild(option.cloneNode(true));
  });

  function appendMessage(role, text) {
    const d = document.createElement('div');
    d.className = `msg ${role}`;
    d.textContent = text;
    chatLog.appendChild(d);
    chatLog.scrollTop = chatLog.scrollHeight;
    return d;
  }

  socket.on('connect', () => { status.textContent = 'Connected'; });
  socket.on('disconnect', () => { status.textContent = 'Disconnected'; notify('Socket disconnected. Retrying...'); });
  socket.on('typing', data => typing.classList.toggle('hidden', !data.status));
  socket.on('chat_token', data => {
    if (!streamEl) streamEl = appendMessage('assistant', '');
    streamEl.textContent += data.token;
  });
  socket.on('chat_done', () => { streamEl = null; });
  socket.on('chat_error', data => notify(data.error));
  socket.on('analytics_update', data => window.LiberationCharts.updateAnalytics(data));

  sendBtn.addEventListener('click', () => {
    const prompt = promptInput.value.trim();
    if (!prompt) return notify('Prompt is required.');
    appendMessage('user', prompt);
    socket.emit('chat_message', { prompt, model: modelSelect.value });
    promptInput.value = '';
  });

  document.getElementById('export-trend').addEventListener('click', () => window.LiberationCharts.exportTrend());
  document.getElementById('export-comparison').addEventListener('click', () => window.LiberationCharts.exportComparison());

  const modal = document.getElementById('settings-modal');
  const settingsBtn = document.getElementById('settings-btn');
  const closeSettings = document.getElementById('close-settings');
  const settingsModel = document.getElementById('settings-model');
  const fields = ['temperature', 'top_p', 'max_tokens', 'system_prompt'];

  const renderSettings = () => {
    const cfg = presets[settingsModel.value];
    fields.forEach(f => document.getElementById(f).value = cfg[f]);
    document.getElementById('temp-value').textContent = Number(cfg.temperature).toFixed(2);
    document.getElementById('top-p-value').textContent = Number(cfg.top_p).toFixed(2);
  };

  settingsBtn.onclick = () => { modal.classList.remove('hidden'); renderSettings(); };
  closeSettings.onclick = () => modal.classList.add('hidden');
  settingsModel.onchange = renderSettings;

  document.getElementById('temperature').oninput = (e) => {
    presets[settingsModel.value].temperature = parseFloat(e.target.value);
    document.getElementById('temp-value').textContent = parseFloat(e.target.value).toFixed(2);
  };
  document.getElementById('top_p').oninput = (e) => {
    presets[settingsModel.value].top_p = parseFloat(e.target.value);
    document.getElementById('top-p-value').textContent = parseFloat(e.target.value).toFixed(2);
  };
  document.getElementById('max_tokens').oninput = e => presets[settingsModel.value].max_tokens = parseInt(e.target.value || '1', 10);
  document.getElementById('system_prompt').oninput = e => presets[settingsModel.value].system_prompt = e.target.value;

  document.getElementById('save-presets').onclick = async () => {
    const msg = document.getElementById('validation-msg');
    msg.textContent = '';
    const res = await fetch('/api/presets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(presets)
    });
    const data = await res.json();
    if (!res.ok) { msg.textContent = data.error; return; }
    notify('Presets saved');
    modal.classList.add('hidden');
  };

  socket.on('batch_progress', ({ done, total }) => {
    document.getElementById('batch-progress').style.width = `${Math.round((done / total) * 100)}%`;
  });

  const parseBatchPrompts = () => document.getElementById('batch-input').value.split('\n').map(x => x.trim()).filter(Boolean);

  document.getElementById('run-batch').onclick = async () => {
    const prompts = parseBatchPrompts();
    if (!prompts.length) return notify('No prompts entered.');
    const res = await fetch('/api/batch/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompts, models: Object.keys(presets) })
    });
    const data = await res.json();
    batchResults = data.results || [];
    const container = document.getElementById('batch-results');
    container.innerHTML = batchResults.map(r => `<div><b>${r.model}</b> | ${r.prompt}<br/>${r.response}</div><hr/></div>`).join('');
  };

  async function exportBatch(format) {
    if (!batchResults.length) return notify('Run batch first.');
    const res = await fetch('/api/batch/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ results: batchResults, format })
    });
    const blob = await res.blob();
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = format === 'csv' ? 'batch_results.csv' : 'batch_results.json';
    link.click();
  }

  document.getElementById('export-json').onclick = () => exportBatch('json');
  document.getElementById('export-csv').onclick = () => exportBatch('csv');

  document.getElementById('download-sample').onclick = () => {
    const sample = ['Prompt A', 'Prompt B', 'Prompt C'];
    const blob = new Blob([JSON.stringify(sample, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'sample_prompts.json';
    a.click();
  };

  document.getElementById('batch-file').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const text = await file.text();
    if (file.name.endsWith('.json')) {
      const prompts = JSON.parse(text);
      document.getElementById('batch-input').value = prompts.join('\n');
    } else if (file.name.endsWith('.csv')) {
      const lines = text.split('\n').slice(1).map(l => l.split(',')[0]).filter(Boolean);
      document.getElementById('batch-input').value = lines.join('\n');
    }
  });
})();
