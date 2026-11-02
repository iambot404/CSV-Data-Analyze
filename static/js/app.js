/**
 * SynapseCSV - Frontend Application Logic
 */

(function () {
  'use strict';

  // Application State
  const state = {
    token: localStorage.getItem('synapse_token') || null,
    user: null,
    currentAnalysis: null,
    isAuthModeRegister: false
  };

  // DOM Elements
  const dropZone = document.getElementById('dropZone');
  const csvFileInput = document.getElementById('csvFileInput');
  const uploadSection = document.getElementById('uploadSection');
  const loadingSection = document.getElementById('loadingSection');
  const loadingSubtext = document.getElementById('loadingSubtext');
  const dashboardSection = document.getElementById('dashboardSection');
  
  // Dashboard Elements
  const dashFilename = document.getElementById('dashFilename');
  const dashFileMeta = document.getElementById('dashFileMeta');
  const kpiRows = document.getElementById('kpiRows');
  const kpiCols = document.getElementById('kpiCols');
  const kpiMemory = document.getElementById('kpiMemory');
  const kpiMissing = document.getElementById('kpiMissing');
  const kpiDuplicates = document.getElementById('kpiDuplicates');
  const kpiHealth = document.getElementById('kpiHealth');
  const kpiHealthBadge = document.getElementById('kpiHealthBadge');

  const chartCount = document.getElementById('chartCount');
  const columnCount = document.getElementById('columnCount');
  const chartsContainer = document.getElementById('chartsContainer');
  const columnsTableBody = document.getElementById('columnsTableBody');
  const previewTableHead = document.getElementById('previewTableHead');
  const previewTableBody = document.getElementById('previewTableBody');

  // AI Elements
  const modelTag = document.getElementById('modelTag');
  const aiExecutiveSummary = document.getElementById('aiExecutiveSummary');
  const aiKeyPatterns = document.getElementById('aiKeyPatterns');
  const aiAnomalies = document.getElementById('aiAnomalies');
  const aiRecommendations = document.getElementById('aiRecommendations');

  // Chat Elements
  const chatMessages = document.getElementById('chatMessages');
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const suggestedPromptsList = document.getElementById('suggestedPromptsList');

  // Auth & Modals
  const authModal = document.getElementById('authModal');
  const authContainer = document.getElementById('authContainer');
  const btnOpenAuth = document.getElementById('btnOpenAuth');
  const btnCloseAuth = document.getElementById('btnCloseAuth');
  const tabSignIn = document.getElementById('tabSignIn');
  const tabSignUp = document.getElementById('tabSignUp');
  const groupFullName = document.getElementById('groupFullName');
  const authForm = document.getElementById('authForm');
  const authFullName = document.getElementById('authFullName');
  const authEmail = document.getElementById('authEmail');
  const authPassword = document.getElementById('authPassword');
  const btnAuthSubmit = document.getElementById('btnAuthSubmit');
  const authError = document.getElementById('authError');

  // History Modal
  const historyModal = document.getElementById('historyModal');
  const btnOpenHistory = document.getElementById('btnOpenHistory');
  const btnCloseHistory = document.getElementById('btnCloseHistory');
  const historyList = document.getElementById('historyList');

  // Action Buttons
  const btnNewUpload = document.getElementById('btnNewUpload');
  const btnExportReport = document.getElementById('btnExportReport');

  // ==================== AUTHENTICATION ==================== //

  async function checkAuth() {
    if (!state.token) {
      renderAuthNav();
      return;
    }
    try {
      const res = await fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${state.token}` }
      });
      const data = await res.json();
      if (data.authenticated && data.user) {
        state.user = data.user;
      } else {
        logout();
      }
    } catch (e) {
      console.warn('Auth check failed:', e);
    }
    renderAuthNav();
  }

  function renderAuthNav() {
    if (state.user) {
      const initial = (state.user.name || state.user.email || 'U')[0].toUpperCase();
      authContainer.innerHTML = `
        <div class="user-pill">
          <div class="user-avatar">${initial}</div>
          <span>${state.user.email}</span>
          <button id="btnLogout" class="btn btn-ghost" style="padding: 4px 8px; font-size: 0.75rem;" title="Sign Out">✕</button>
        </div>
      `;
      document.getElementById('btnLogout').addEventListener('click', logout);
    } else {
      authContainer.innerHTML = `
        <button id="btnOpenAuth" class="btn btn-primary">
          <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          Sign In / Register
        </button>
      `;
      document.getElementById('btnOpenAuth').addEventListener('click', () => openAuthModal(false));
    }
  }

  function openAuthModal(isRegister = false) {
    state.isAuthModeRegister = isRegister;
    authError.style.display = 'none';
    if (isRegister) {
      tabSignUp.classList.add('active');
      tabSignIn.classList.remove('active');
      groupFullName.style.display = 'block';
      btnAuthSubmit.textContent = 'Create Account';
    } else {
      tabSignIn.classList.add('active');
      tabSignUp.classList.remove('active');
      groupFullName.style.display = 'none';
      btnAuthSubmit.textContent = 'Sign In';
    }
    authModal.classList.add('open');
  }

  function closeAuthModal() {
    authModal.classList.remove('open');
  }

  function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('synapse_token');
    renderAuthNav();
  }

  tabSignIn.addEventListener('click', () => openAuthModal(false));
  tabSignUp.addEventListener('click', () => openAuthModal(true));
  btnCloseAuth.addEventListener('click', closeAuthModal);

  authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    authError.style.display = 'none';
    const email = authEmail.value.trim();
    const password = authPassword.value;
    const fullName = authFullName.value.trim();

    const endpoint = state.isAuthModeRegister ? '/api/auth/register' : '/api/auth/login';
    const payload = state.isAuthModeRegister ? { email, password, full_name: fullName } : { email, password };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Authentication failed');
      }

      state.token = data.token;
      state.user = data.user;
      localStorage.setItem('synapse_token', data.token);
      renderAuthNav();
      closeAuthModal();
    } catch (err) {
      authError.textContent = err.message;
      authError.style.display = 'block';
    }
  });

  // ==================== UPLOAD & SAMPLES ==================== //

  dropZone.addEventListener('click', () => csvFileInput.click());

  ['dragenter', 'dragover'].forEach(event => {
    dropZone.addEventListener(event, (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(event => {
    dropZone.addEventListener(event, (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
    });
  });

  dropZone.addEventListener('drop', (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  csvFileInput.addEventListener('change', () => {
    if (csvFileInput.files && csvFileInput.files.length > 0) {
      handleFileUpload(csvFileInput.files[0]);
    }
  });

  // Sample Chips
  document.querySelectorAll('.sample-chip').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const sampleId = btn.getAttribute('data-sample');
      loadSample(sampleId);
    });
  });

  function showLoading(msg = 'Ingesting and computing distributions...') {
    uploadSection.style.display = 'none';
    dashboardSection.style.display = 'none';
    loadingSection.style.display = 'block';
    loadingSubtext.textContent = msg;
  }

  function hideLoading() {
    loadingSection.style.display = 'none';
  }

  async function handleFileUpload(file) {
    if (!file.name.match(/\.(csv|tsv|txt)$/i)) {
      alert('Please upload a valid CSV file (.csv, .tsv, .txt)');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert(`File is too large (${(file.size / (1024*1024)).toFixed(1)} MB). Maximum allowed size is 10 MB.`);
      return;
    }

    showLoading(`Ingesting ${file.name} in-memory & profiling...`);

    const formData = new FormData();
    formData.append('file', file);

    const headers = {};
    if (state.token) {
      headers['Authorization'] = `Bearer ${state.token}`;
    }

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        headers: headers,
        body: formData
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Failed to process CSV file.');
      }
      renderDashboard(data.analysis);
    } catch (err) {
      hideLoading();
      uploadSection.style.display = 'block';
      alert(`Upload error: ${err.message}`);
    }
  }

  async function loadSample(sampleId) {
    showLoading(`Loading preconfigured sample '${sampleId}'...`);
    const headers = {};
    if (state.token) {
      headers['Authorization'] = `Bearer ${state.token}`;
    }

    try {
      const res = await fetch(`/api/samples/${sampleId}/load`, {
        method: 'POST',
        headers: headers
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Failed to load sample dataset.');
      }
      renderDashboard(data.analysis);
    } catch (err) {
      hideLoading();
      uploadSection.style.display = 'block';
      alert(`Error loading sample: ${err.message}`);
    }
  }

  // ==================== DASHBOARD RENDERING ==================== //

  function formatBytes(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  function renderDashboard(analysis) {
    state.currentAnalysis = analysis;
    hideLoading();
    uploadSection.style.display = 'none';
    dashboardSection.style.display = 'block';

    // Header & Meta
    dashFilename.textContent = analysis.filename || 'dataset.csv';
    const sizeStr = formatBytes(analysis.file_size_bytes);
    dashFileMeta.textContent = `${analysis.row_count} rows &bull; ${analysis.column_count} columns &bull; ${sizeStr} in-memory`;

    // KPIs
    kpiRows.textContent = (analysis.row_count || 0).toLocaleString();
    kpiCols.textContent = (analysis.column_count || 0).toLocaleString();
    
    const summaryStats = analysis.summary_stats || {};
    kpiMemory.textContent = formatBytes(summaryStats.memory_usage_bytes || analysis.file_size_bytes);
    
    // Missing & Duplicates
    kpiDuplicates.textContent = (summaryStats.duplicate_rows || 0).toLocaleString();
    
    // Total missing cells
    let totalMissing = 0;
    (analysis.columns || []).forEach(c => totalMissing += (c.missing_count || 0));
    kpiMissing.textContent = totalMissing.toLocaleString();

    // Health Score
    const score = summaryStats.health_score || 85;
    kpiHealth.textContent = `${score}/100`;
    if (score >= 80) {
      kpiHealthBadge.textContent = 'Excellent Health';
      kpiHealthBadge.className = 'kpi-health-badge health-excellent';
    } else if (score >= 60) {
      kpiHealthBadge.textContent = 'Moderate Health';
      kpiHealthBadge.className = 'kpi-health-badge health-good';
    } else {
      kpiHealthBadge.textContent = 'Needs Cleaning';
      kpiHealthBadge.className = 'kpi-health-badge health-warning';
    }

    // Counts
    chartCount.textContent = (analysis.charts || []).length;
    columnCount.textContent = (analysis.columns || []).length;

    // Render Tabs
    renderAiInsights(analysis.ai_insights);
    renderCharts(analysis.charts);
    renderColumnsTable(analysis.columns);
    renderDataPreview(analysis.columns, analysis.data_sample);
    setupChatSuggestions(analysis.ai_insights);

    // Switch to first tab
    switchTab('tabInsights');
  }

  function renderAiInsights(ai) {
    if (!ai) return;
    modelTag.textContent = ai.model_used || 'Gemini 3.8 Flash';
    aiExecutiveSummary.textContent = ai.executive_summary || 'Executive summary generated.';

    // Key patterns
    aiKeyPatterns.innerHTML = (ai.key_patterns || []).map(p => `<li>${p}</li>`).join('');
    
    // Anomalies
    aiAnomalies.innerHTML = (ai.anomalies_and_risks || []).map(a => `<li>${a}</li>`).join('');

    // Recommendations
    aiRecommendations.innerHTML = (ai.strategic_recommendations || []).map(r => `<li>${r}</li>`).join('');
  }

  function renderCharts(charts) {
    if (!charts || charts.length === 0) {
      chartsContainer.innerHTML = `
        <div class="empty-state-card" style="grid-column: 1 / -1;">
          <img src="/static/img/empty-art.svg" alt="Empty Charts" class="empty-art">
          <h4>No numeric or categorical columns suitable for charts</h4>
        </div>
      `;
      return;
    }

    chartsContainer.innerHTML = charts.map(c => `
      <div class="chart-card">
        <h4 class="chart-title">${c.title}</h4>
        <img src="${c.image_data}" alt="${c.title}" class="chart-img">
      </div>
    `).join('');
  }

  function renderColumnsTable(columns) {
    if (!columns) return;
    columnsTableBody.innerHTML = columns.map(c => {
      let statsText = '-';
      if (c.stats) {
        if (c.type === 'numeric') {
          statsText = `Mean: <b>${c.stats.mean ?? '-'}</b> | Med: <b>${c.stats.median ?? '-'}</b> | Range: [${c.stats.min ?? '-'}, ${c.stats.max ?? '-'}]`;
        } else if (c.stats.top_categories) {
          statsText = c.stats.top_categories.slice(0, 2).map(cat => `${cat.value} (${cat.count})`).join(', ');
        }
      }

      const samples = (c.sample_values || []).slice(0, 3).map(v => `<span style="background:rgba(15,23,42,0.8); padding:2px 6px; border-radius:4px; font-size:0.75rem; border:1px solid #334155;">${v}</span>`).join(' ');

      return `
        <tr>
          <td><b>${c.name}</b></td>
          <td><span class="badge-type type-${c.type}">${c.type}</span></td>
          <td>${c.missing_count} (${c.missing_pct}%)</td>
          <td>${c.unique_count}</td>
          <td style="font-size:0.82rem;">${statsText}</td>
          <td>${samples || '-'}</td>
        </tr>
      `;
    }).join('');
  }

  function renderDataPreview(columns, dataSample) {
    if (!columns || !dataSample || dataSample.length === 0) {
      previewTableHead.innerHTML = '';
      previewTableBody.innerHTML = '<tr><td colspan="5">No data sample available</td></tr>';
      return;
    }

    // Headers
    previewTableHead.innerHTML = `
      <tr>
        <th style="width: 40px;">#</th>
        ${columns.map(c => `<th>${c.name}</th>`).join('')}
      </tr>
    `;

    // Rows
    previewTableBody.innerHTML = dataSample.map((row, idx) => `
      <tr>
        <td style="color: var(--text-faint); font-size: 0.75rem;">${idx + 1}</td>
        ${columns.map(c => `<td>${row[c.name] !== null ? row[c.name] : '<span style="color:#64748b; font-style:italic;">null</span>'}</td>`).join('')}
      </tr>
    `).join('');
  }

  function setupChatSuggestions(ai) {
    suggestedPromptsList.innerHTML = '';
    const questions = (ai && ai.suggested_questions) || [
      'What are the key statistical highlights?',
      'Which category represents the largest proportion?',
      'Are there notable outliers in the data?'
    ];

    questions.forEach(q => {
      const btn = document.createElement('button');
      btn.className = 'prompt-btn';
      btn.textContent = q;
      btn.addEventListener('click', () => {
        chatInput.value = q;
        chatForm.dispatchEvent(new Event('submit'));
      });
      suggestedPromptsList.appendChild(btn);
    });
  }

  // ==================== TABS SWITCHING ==================== //

  function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
    });
    document.querySelectorAll('.tab-content').forEach(panel => {
      panel.classList.toggle('active', panel.id === tabId);
    });
  }

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      switchTab(btn.getAttribute('data-tab'));
    });
  });

  // ==================== ASK AI CHAT ==================== //

  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query || !state.currentAnalysis) return;

    chatInput.value = '';

    // Append User Bubble
    appendChatMessage(query, 'user');

    // Append Typing Indicator
    const typingId = 'typing-' + Date.now();
    const typingElem = document.createElement('div');
    typingElem.id = typingId;
    typingElem.className = 'chat-bubble bubble-ai';
    typingElem.textContent = 'Thinking with Gemini AI...';
    chatMessages.appendChild(typingElem);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const headers = { 'Content-Type': 'application/json' };
    if (state.token) {
      headers['Authorization'] = `Bearer ${state.token}`;
    }

    try {
      const res = await fetch(`/api/analysis/${state.currentAnalysis.id}/query`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ question: query })
      });
      const data = await res.json();
      
      const typingNode = document.getElementById(typingId);
      if (typingNode) typingNode.remove();

      if (!res.ok) {
        throw new Error(data.error || 'Failed to answer query.');
      }

      appendChatMessage(data.answer, 'ai');
    } catch (err) {
      const typingNode = document.getElementById(typingId);
      if (typingNode) typingNode.remove();
      appendChatMessage(`Sorry, I couldn't process that: ${err.message}`, 'ai');
    }
  });

  function appendChatMessage(text, sender) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble bubble-${sender}`;
    bubble.textContent = text;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // ==================== HISTORY MODAL ==================== //

  btnOpenHistory.addEventListener('click', async () => {
    historyModal.classList.add('open');
    historyList.innerHTML = '<div style="color:var(--text-muted); font-size:0.85rem; padding:10px;">Loading past analyses...</div>';

    const headers = {};
    if (state.token) headers['Authorization'] = `Bearer ${state.token}`;

    try {
      const res = await fetch('/api/history', { headers });
      const data = await res.json();
      const list = data.history || [];

      if (list.length === 0) {
        historyList.innerHTML = `
          <div class="empty-state-card" style="padding: 20px;">
            <img src="/static/img/empty-art.svg" alt="Empty" style="width: 100px; height: auto; margin-bottom: 8px;">
            <p style="font-size: 0.85rem; color: var(--text-muted);">No saved analyses found in Supabase yet.</p>
          </div>
        `;
        return;
      }

      historyList.innerHTML = list.map(item => `
        <div style="background: rgba(30,41,59,0.7); border:1px solid var(--border-subtle); border-radius: var(--radius-sm); padding:12px; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-weight:700; font-size:0.92rem; color:#ffffff;">${item.filename}</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">${item.row_count} rows &bull; ${item.column_count} cols &bull; ${new Date(item.created_at).toLocaleDateString()}</div>
          </div>
          <button class="btn btn-outline btn-load-hist" data-id="${item.id}" style="padding: 6px 12px; font-size:0.8rem;">
            Open
          </button>
        </div>
      `).join('');

      document.querySelectorAll('.btn-load-hist').forEach(b => {
        b.addEventListener('click', () => loadSavedAnalysis(b.getAttribute('data-id')));
      });

    } catch (e) {
      historyList.innerHTML = `<div style="color:var(--rose-danger); font-size:0.85rem;">Failed to fetch history: ${e.message}</div>`;
    }
  });

  btnCloseHistory.addEventListener('click', () => historyModal.classList.remove('open'));

  async function loadSavedAnalysis(analysisId) {
    historyModal.classList.remove('open');
    showLoading('Loading saved report from Supabase...');

    const headers = {};
    if (state.token) headers['Authorization'] = `Bearer ${state.token}`;

    try {
      const res = await fetch(`/api/analysis/${analysisId}`, { headers });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to retrieve analysis.');
      renderDashboard(data.analysis);
    } catch (e) {
      hideLoading();
      alert(`Error loading analysis: ${e.message}`);
    }
  }

  // ==================== NEW UPLOAD & EXPORT ==================== //

  btnNewUpload.addEventListener('click', () => {
    dashboardSection.style.display = 'none';
    uploadSection.style.display = 'block';
    csvFileInput.value = '';
  });

  btnExportReport.addEventListener('click', () => {
    if (!state.currentAnalysis) return;
    const blob = new Blob([JSON.stringify(state.currentAnalysis, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${state.currentAnalysis.filename || 'dataset'}_analysis_report.json`;
    a.click();
    URL.revokeObjectURL(url);
  });

  // Init
  checkAuth();
})();
