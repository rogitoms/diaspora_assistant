// ============================================
// STATE
// ============================================
let allTasks = [];
let currentFilter = 'all';

// ============================================
// ON PAGE LOAD
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  loadTasks();
});

// ============================================
// FILL EXAMPLE INTO TEXTAREA
// ============================================
function fillExample(btn) {
  document.getElementById('userRequest').value = btn.textContent.trim();
  document.getElementById('userRequest').focus();
}

// ============================================
// SUBMIT REQUEST
// ============================================
async function submitRequest() {
  const input   = document.getElementById('userRequest').value.trim();
  const btn     = document.getElementById('submitBtn');
  const btnText = document.getElementById('submitText');
  const loader  = document.getElementById('submitLoader');

  if (!input) {
    showToast('Please describe your request first', 'error');
    return;
  }

  // Loading state
  btn.disabled    = true;
  btnText.style.display = 'none';
  loader.style.display  = 'inline-block';

  try {
    const res  = await fetch('/api/submit/', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ request: input }),
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      throw new Error(data.error || 'Something went wrong');
    }

    showResultCard(data.task);
    showToast(`Task ${data.task.task_code} created successfully!`);
    loadTasks();  // refresh dashboard

  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled          = false;
    btnText.style.display = 'inline';
    loader.style.display  = 'none';
  }
}

// ============================================
// SHOW RESULT CARD
// ============================================
function showResultCard(task) {
  const card = document.getElementById('resultCard');

  document.getElementById('resultCode').textContent = task.task_code;
  document.getElementById('resultTeam').textContent = task.employee_team;

  // Risk pill
  const riskEl = document.getElementById('resultRisk');
  riskEl.textContent  = `Risk: ${task.risk_score}/100 — ${task.risk_label}`;
  riskEl.className    = `result-risk risk-${task.risk_label.toLowerCase()}`;

  // Steps
  const stepsList = document.getElementById('resultSteps');
  stepsList.innerHTML = task.steps
    .map(s => `<li>${s.description}</li>`)
    .join('');

  // Messages
  document.getElementById('msgWhatsapp').textContent = task.messages.whatsapp || '—';
  document.getElementById('msgEmail').textContent    = task.messages.email    || '—';
  document.getElementById('msgSms').textContent      = task.messages.sms      || '—';

  // Reset to whatsapp tab
  document.querySelectorAll('.msg-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.msg-tab')[0].classList.add('active');
  document.getElementById('msgWhatsapp').style.display = 'block';
  document.getElementById('msgEmail').style.display    = 'none';
  document.getElementById('msgSms').style.display      = 'none';

  card.style.display = 'block';
  card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ============================================
// MESSAGE TABS
// ============================================
function showTab(btn, channel) {
  document.querySelectorAll('.msg-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');

  ['whatsapp', 'email', 'sms'].forEach(c => {
    const el = document.getElementById(`msg${c.charAt(0).toUpperCase() + c.slice(1)}`);
    el.style.display = c === channel ? 'block' : 'none';
  });
}

// ============================================
// LOAD ALL TASKS
// ============================================
async function loadTasks() {
  try {
    const res  = await fetch('/api/tasks/');
    const data = await res.json();
    if (!data.success) throw new Error(data.error);
    allTasks = data.tasks;
    renderTasks();
  } catch (err) {
    document.getElementById('taskList').innerHTML =
      `<div class="empty-state">Failed to load tasks: ${err.message}</div>`;
  }
}

// ============================================
// RENDER TASKS
// ============================================
function renderTasks() {
  const list = document.getElementById('taskList');

  const filtered = currentFilter === 'all'
    ? allTasks
    : allTasks.filter(t => t.status === currentFilter);

  if (filtered.length === 0) {
    list.innerHTML = `<div class="empty-state">No ${currentFilter === 'all' ? '' : currentFilter} tasks yet</div>`;
    return;
  }

  list.innerHTML = filtered.map(task => buildTaskCard(task)).join('');
}

// ============================================
// BUILD TASK CARD HTML
// ============================================
function buildTaskCard(task) {
  const statusClass = {
    'Pending':     'status-pending',
    'In Progress': 'status-in-progress',
    'Completed':   'status-completed',
  }[task.status] || '';

  const riskClass = {
    'Low':    'risk-low',
    'Medium': 'risk-medium',
    'High':   'risk-high',
  }[task.risk_label] || '';

  return `
    <div class="task-card" id="card-${task.task_code}">
      <div class="task-card-top">
        <span class="task-code-badge">${task.task_code}</span>
        <span class="task-intent-badge intent-${task.intent}">${task.intent.replace('_', ' ')}</span>
      </div>
      <p class="task-request">"${task.original_request}"</p>
      <div class="task-meta">
        <span class="task-meta-item">🕐 ${task.created_at}</span>
        <span class="task-risk-pill ${riskClass}">Risk ${task.risk_score}/100 · ${task.risk_label}</span>
      </div>
      <div class="task-card-bottom">
        <select
          class="status-select ${statusClass}"
          onchange="updateStatus('${task.task_code}', this)"
        >
          <option ${task.status === 'Pending'     ? 'selected' : ''}>Pending</option>
          <option ${task.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
          <option ${task.status === 'Completed'   ? 'selected' : ''}>Completed</option>
        </select>
        <span class="team-tag">👤 ${task.employee_team}</span>
        <span class="task-time">${task.created_at}</span>
      </div>
    </div>
  `;
}

// ============================================
// UPDATE TASK STATUS
// ============================================
async function updateStatus(taskCode, selectEl) {
  const newStatus = selectEl.value;

  try {
    const res  = await fetch(`/api/tasks/${taskCode}/status/`, {
      method:  'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ status: newStatus }),
    });
    const data = await res.json();
    if (!res.ok || !data.success) throw new Error(data.error);

    // Update local state
    const task = allTasks.find(t => t.task_code === taskCode);
    if (task) task.status = newStatus;

    // Update select color class
    selectEl.className = `status-select status-${newStatus.toLowerCase().replace(' ', '-')}`;

    showToast(`${taskCode} updated to ${newStatus}`);

  } catch (err) {
    showToast(err.message, 'error');
    loadTasks(); // reload to reset select to real value
  }
}

// ============================================
// FILTER TASKS
// ============================================
function filterTasks(btn, filter) {
  currentFilter = filter;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderTasks();
}

// ============================================
// TOAST NOTIFICATION
// ============================================
function showToast(message, type = 'success') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = `toast${type === 'error' ? ' error' : ''}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => toast.remove(), 3500);
}