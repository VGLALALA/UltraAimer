const form = document.querySelector('#configForm');
const toast = document.querySelector('#toast');
const runButton = document.querySelector('#runButton');
let original = null;
let running = false;

const notify = (message, error = false) => {
  toast.textContent = message;
  toast.style.background = error ? 'var(--red)' : 'var(--text)';
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2800);
};

const api = async (path, options = {}) => {
  const response = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...options });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed');
  return data;
};

const setPath = (target, path, value) => {
  const [section, key] = path.split('.');
  target[section] ||= {};
  target[section][key] = value;
};

const fillForm = (config) => {
  document.querySelectorAll('[data-path]').forEach((field) => {
    const [section, key] = field.dataset.path.split('.');
    const value = config[section]?.[key] ?? '';
    if (field.type === 'checkbox') field.checked = String(value).toLowerCase() === 'true';
    else field.value = value;
  });
  document.querySelector('#offsetOut').value = document.querySelector('[data-path="Mouse.offset"]').value;
  document.querySelector('#speedOut').value = document.querySelector('[data-path="Mouse.mouse_moving_speed"]').value;
  updateModeVisibility();
};

const collectForm = () => {
  const config = {};
  document.querySelectorAll('[data-path]').forEach((field) => {
    setPath(config, field.dataset.path, field.type === 'checkbox' ? field.checked : field.value.trim());
  });
  return config;
};

const updateModeVisibility = () => {
  const mode = document.querySelector('[data-path="Mode.aim"]').value.toLowerCase();
  document.querySelectorAll('[data-mode-value]').forEach((button) => {
    const active = button.dataset.modeValue.toLowerCase() === mode;
    button.classList.toggle('active', active);
    button.setAttribute('aria-selected', String(active));
  });
  document.querySelectorAll('[data-mode]').forEach((element) => {
    element.hidden = element.dataset.mode !== mode;
  });
};

document.querySelectorAll('[data-mode-value]').forEach((button) => button.addEventListener('click', () => {
  const source = document.querySelector('[data-path="Mode.aim"]');
  source.value = button.dataset.modeValue;
  source.dispatchEvent(new Event('input', { bubbles: true }));
}));

document.querySelectorAll('.key-capture').forEach((field) => {
  let previous = '';
  field.addEventListener('focus', () => {
    previous = field.value;
    field.value = 'Press any key…';
    field.classList.add('listening');
  });
  field.addEventListener('keydown', (event) => {
    event.preventDefault();
    if (event.key === 'Escape') {
      field.value = previous;
    } else {
      const code = event.keyCode || event.which;
      if (!code) return;
      field.value = `0x${code.toString(16).toUpperCase().padStart(2, '0')}`;
      field.dispatchEvent(new Event('input', { bubbles: true }));
    }
    field.classList.remove('listening');
    field.blur();
  });
  field.addEventListener('blur', () => {
    if (field.classList.contains('listening')) field.value = previous;
    field.classList.remove('listening');
  });
});

const markDirty = () => { document.querySelector('#saveState').textContent = 'Unsaved changes'; };
form.addEventListener('input', (event) => {
  markDirty();
  if (event.target.dataset.path === 'Mode.aim') updateModeVisibility();
  if (event.target.dataset.path === 'Mouse.offset') document.querySelector('#offsetOut').value = event.target.value;
  if (event.target.dataset.path === 'Mouse.mouse_moving_speed') document.querySelector('#speedOut').value = event.target.value;
});

document.querySelectorAll('.tabs button').forEach((button) => button.addEventListener('click', () => {
  document.querySelectorAll('.tabs button,.panel').forEach((item) => item.classList.remove('active'));
  button.classList.add('active');
  document.querySelector(`[data-panel="${button.dataset.tab}"]`).classList.add('active');
}));

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const result = await api('/api/config', { method: 'PUT', body: JSON.stringify(collectForm()) });
    original = result.config;
    fillForm(original);
    document.querySelector('#saveState').textContent = 'Configuration saved';
    notify('Configuration saved');
  } catch (error) { notify(error.message, true); }
});

document.querySelector('#resetButton').addEventListener('click', () => {
  if (original) fillForm(original);
  document.querySelector('#saveState').textContent = 'Changes discarded';
});

const paintStatus = (status) => {
  running = status.running;
  document.querySelector('#statusDot').classList.toggle('live', running);
  document.querySelector('#statusLabel').textContent = running ? `Running · PID ${status.pid}` : 'Engine idle';
  document.querySelector('#runText').textContent = running ? 'Stop engine' : 'Start engine';
  document.querySelector('#runIcon').textContent = running ? '■' : '▶';
  runButton.classList.toggle('stop', running);
  runButton.disabled = false;
};

runButton.addEventListener('click', async () => {
  runButton.disabled = true;
  try { paintStatus(await api(running ? '/api/stop' : '/api/start', { method: 'POST' })); }
  catch (error) { notify(error.message, true); runButton.disabled = false; }
});

document.querySelector('#themeButton').addEventListener('click', () => document.body.classList.toggle('light'));

Promise.all([api('/api/config'), api('/api/status')]).then(([config, status]) => {
  original = config;
  fillForm(config);
  paintStatus(status);
}).catch((error) => notify(error.message, true));
setInterval(() => api('/api/status').then(paintStatus).catch(() => {}), 2500);
