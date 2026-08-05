/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   RepoLens — Application Logic
   Single-page application with hash-based routing.
   â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */

// ─── Constants ──────────────────────────────────────────────────

const Icons = {
  folder: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg>`,
  file: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>`,
  cloud: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>`,
  settings: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>`,
  repo: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>`,
  plus: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>`,
  search: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>`,
  chat: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/></svg>`,
  home: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
  chevronRight: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>`,
chevronLeft: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>`,
  chevronDown: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>`,
  copy: `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>`,
  info: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>`,
  check: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>`,
  x: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="M6 6l12 12"/></svg>`
};

const API = '';  // Same origin
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
const el = (tag, attrs = {}, ...children) => {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') node.className = v;
    else if (k === 'style' && typeof v === 'object') Object.assign(node.style, v);
    else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2).toLowerCase(), v);
    else if (k === 'html') node.innerHTML = v;
    else node.setAttribute(k, v);
  }
  for (const c of children) {
    if (typeof c === 'string') node.appendChild(document.createTextNode(c));
    else if (c) node.appendChild(c);
  }
  return node;
};

// ─── State ──────────────────────────────────────────────────────
const state = {
  view: 'splash',
  config: null,
  repos: [],
  activeRepo: null,   // { owner, name, path }
  structure: null,
  nodes: null,
  conversations: [],
  activeConversation: null,
  chatMessages: [],
  pipelineStage: -1,
  pipelineError: null,
  searchOpen: false,
  modalOpen: null,
  expandedNodes: new Set(),
selectedId: null,
  explorerSearch: '',
};

// ─── API Layer ──────────────────────────────────────────────────
async function api(path, opts = {}) {
  const { method = 'GET', body } = opts;
  const headers = {};
  if (body) headers['Content-Type'] = 'application/json';
  try {
    const res = await fetch(`${API}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    return data;
  } catch (err) {
    if (err.message.includes('Failed to fetch')) {
      throw new Error('Backend disconnected. Is the server running?');
    }
    throw err;
  }
}

// ─── Toast ──────────────────────────────────────────────────────
function toast(message, type = 'info') {
  const icons = { success: Icons.check, error: Icons.x, info: Icons.info };
  const container = document.getElementById('toast-container');
  const t = el('div', { class: `toast toast-${type}` },
    el('span', { html: icons[type] || Icons.info }),
    el('span', {}, message),
  );
  container.appendChild(t);
  setTimeout(() => { t.classList.add('toast-exit'); setTimeout(() => t.remove(), 300); }, 4000);
}

// ─── Router ─────────────────────────────────────────────────────
function navigate(view, skipHash = false) {
  state.view = view;
  if (!skipHash) window.location.hash = view;
  render();
}

window.addEventListener('hashchange', () => {
  const hash = window.location.hash.slice(1) || 'home';
  if (hash !== state.view) {
    state.view = hash;
    render();
  }
});

// ─── Render ─────────────────────────────────────────────────────
function render() {
  const app = document.getElementById('app');
  app.innerHTML = '';

  switch (state.view) {
    case 'splash': app.appendChild(renderSplash()); break;
    case 'setup': app.appendChild(renderSetup()); break;
    case 'setup-cloud': app.appendChild(renderSetupCloud()); break;
    case 'setup-local': app.appendChild(renderSetupLocal()); break;
    case 'home': app.appendChild(renderLayout('home')); break;
    case 'pipeline': app.appendChild(renderLayout('pipeline')); break;
    case 'completion': app.appendChild(renderLayout('completion')); break;
    case 'explorer': app.appendChild(renderLayout('explorer')); break;
case 'graph': app.appendChild(renderLayout('graph')); break;
    case 'chat': app.appendChild(renderLayout('chat')); break;
    case 'settings': app.appendChild(renderLayout('settings')); break;
    default: app.appendChild(renderLayout('home')); break;
  }

  if (state.searchOpen) app.appendChild(renderSearch());
}

// ─── Splash ─────────────────────────────────────────────────────
function renderSplash() {
  const splash = el('div', { class: 'splash', id: 'splash-screen' });

  // Background nodes
  const nodesContainer = el('div', { class: 'splash-nodes' });
  for (let i = 0; i < 12; i++) {
    const x = 10 + Math.random() * 80;
    const y = 10 + Math.random() * 80;
    const node = el('div', {
      class: 'splash-node',
      style: { left: `${x}%`, top: `${y}%`, animationDelay: `${0.3 + Math.random() * 1.2}s` },
    });
    nodesContainer.appendChild(node);
  }
  for (let i = 0; i < 6; i++) {
    const y = 20 + Math.random() * 60;
    const w = 60 + Math.random() * 200;
    const line = el('div', {
      class: 'splash-line',
      style: { left: `${10 + Math.random() * 40}%`, top: `${y}%`, width: `${w}px`, animationDelay: `${0.5 + Math.random() * 1.5}s` },
    });
    nodesContainer.appendChild(line);
  }
  splash.appendChild(nodesContainer);

  splash.appendChild(el('img', { class: 'splash-logo', src: '/static/lens_image.png', alt: 'RepoLens' }));
  splash.appendChild(el('div', { class: 'splash-title' }, 'RepoLens'));
  splash.appendChild(el('div', { class: 'splash-subtitle' }, 'Optical Repository Analyzer'));

  setTimeout(async () => {
    splash.classList.add('splash-exit');
    setTimeout(async () => {
      try {
        const health = await api('/health');
        state.config = await api('/config');
        if (!health.gemini_key_set) {
          navigate('setup');
        } else {
          await loadRepos();
          navigate('home');
        }
      } catch {
        navigate('setup');
      }
    }, 500);
  }, 1800);

  return splash;
}

// ─── Setup: Choose ──────────────────────────────────────────────
function renderSetup() {
  const container = el('div', { class: 'setup' });
  const inner = el('div', { class: 'setup-container' });

  // Step indicator
  const steps = el('div', { class: 'setup-step-indicator' },
    el('div', { class: 'setup-step-dot active' }),
    el('div', { class: 'setup-step-dot' }),
  );
  inner.appendChild(steps);

  const header = el('div', { class: 'setup-header' });
  header.appendChild(el('img', { src: '/static/lens_image.png', alt: 'RepoLens' }));
  header.appendChild(el('h1', {}, 'Welcome to RepoLens'));
  header.appendChild(el('p', {}, 'Choose how you want to power your AI analysis'));
  inner.appendChild(header);

  const options = el('div', { class: 'setup-options' });

  const cloudOption = el('div', {
    class: 'setup-option',
    onClick: () => navigate('setup-cloud'),
  },
    el('div', { class: 'setup-option-icon', html: Icons.cloud }),
    el('div', { class: 'setup-option-title' }, 'Cloud AI'),
    el('div', { class: 'setup-option-desc' }, 'Use Gemini API. Fast, reliable, no local setup required.'),
  );

  const localOption = el('div', {
    class: 'setup-option',
    onClick: () => navigate('setup-local'),
  },
    el('div', { class: 'setup-option-icon', html: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>` }),
    el('div', { class: 'setup-option-title' }, 'Local AI'),
    el('div', { class: 'setup-option-desc' }, 'Run models locally with Ollama. Private, offline-capable.'),
  );

  options.appendChild(cloudOption);
  options.appendChild(localOption);
  inner.appendChild(options);
  container.appendChild(inner);
  return container;
}

// ─── Setup: Cloud ───────────────────────────────────────────────
function renderSetupCloud() {
  const container = el('div', { class: 'setup' });
  const inner = el('div', { class: 'setup-container' });

  const steps = el('div', { class: 'setup-step-indicator' },
    el('div', { class: 'setup-step-dot' }),
    el('div', { class: 'setup-step-dot active' }),
  );
  inner.appendChild(steps);

  const header = el('div', { class: 'setup-header' });
  header.appendChild(el('h1', {}, 'Connect Gemini API'));
  header.appendChild(el('p', {}, 'Enter your Google AI API key to get started'));
  inner.appendChild(header);

  const form = el('div', { class: 'setup-form' });

  const inputGroup = el('div', { class: 'input-group' });
  inputGroup.appendChild(el('label', { for: 'api-key-input' }, 'API Key'));
  const input = el('input', {
    class: 'input input-lg',
    id: 'api-key-input',
    type: 'password',
    placeholder: 'AIza...',
    autocomplete: 'off',
  });
  inputGroup.appendChild(input);
  form.appendChild(inputGroup);

  const validationMsg = el('div', { class: 'validation-msg', id: 'validation-msg' });
  form.appendChild(validationMsg);

  const actions = el('div', { class: 'modal-actions', style: { justifyContent: 'space-between' } });

  const backBtn = el('button', {
    class: 'btn btn-ghost',
    onClick: () => navigate('setup'),
  }, 'Back');

  const saveBtn = el('button', {
    class: 'btn btn-primary btn-lg',
    id: 'save-key-btn',
    onClick: async () => {
      const key = input.value.trim();
      if (!key) { toast('Please enter an API key', 'error'); return; }
      saveBtn.disabled = true;
      saveBtn.textContent = 'Validating...';
      validationMsg.innerHTML = '';
      try {
        await api('/config', { method: 'POST', body: { gemini_api_key: key, provider: 'cloud' } });
        const health = await api('/health');
        if (health.gemini_key_set) {
          validationMsg.innerHTML = '<span class="validation-success">✓ Connected successfully</span>';
          toast('API key saved', 'success');
          await loadRepos();
          setTimeout(() => navigate('home'), 600);
        } else {
          throw new Error('Key was not accepted');
        }
      } catch (err) {
        validationMsg.innerHTML = `<span class="validation-error">✕ ${err.message}</span>`;
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save & Continue';
      }
    },
  }, 'Save & Continue');

  actions.appendChild(backBtn);
  actions.appendChild(saveBtn);
  form.appendChild(actions);

  inner.appendChild(form);
  container.appendChild(inner);
  return container;
}

// ─── Setup: Local AI ────────────────────────────────────────────
function renderSetupLocal() {
  const container = el('div', { class: 'setup' });
  const inner = el('div', { class: 'setup-container' });

  const steps = el('div', { class: 'setup-step-indicator' },
    el('div', { class: 'setup-step-dot' }),
    el('div', { class: 'setup-step-dot active' }),
  );
  inner.appendChild(steps);

  const header = el('div', { class: 'setup-header' });
  header.appendChild(el('h1', {}, 'Local AI Setup'));
  header.appendChild(el('p', {}, 'Run models locally with Ollama'));
  inner.appendChild(header);

  const reqs = el('div', { class: 'requirements-list' });
  const requirements = [
    { icon: Icons.settings, text: 'Dedicated GPU with minimum 6 GB VRAM', status: 'info' },
    { icon: Icons.folder, text: 'Ollama installed and on PATH', status: 'info' },
    { icon: Icons.plus, text: 'Ollama server running (ollama serve)', status: 'info' },
    { icon: Icons.repo, text: 'At least one model pulled (e.g. llama3)', status: 'info' },
  ];

  for (const r of requirements) {
    reqs.appendChild(el('div', { class: 'requirement-item' },
      el('span', { class: 'requirement-icon', html: r.icon }),
      el('span', {}, r.text),
    ));
  }
  inner.appendChild(reqs);

  const notice = el('div', { class: 'warning-banner', style: { marginTop: '24px' } },
    el('span', { html: Icons.info }),
    el('span', {}, 'Local AI backend integration is coming soon. For now, please use Cloud AI with a Gemini API key.'),
  );
  inner.appendChild(notice);

  const actions = el('div', { class: 'modal-actions', style: { justifyContent: 'space-between', marginTop: '24px' } });
  actions.appendChild(el('button', { class: 'btn btn-ghost', onClick: () => navigate('setup') }, 'Back'));
  actions.appendChild(el('button', { class: 'btn btn-primary btn-lg', onClick: () => navigate('setup-cloud') }, 'Use Cloud AI Instead'));
  inner.appendChild(actions);

  container.appendChild(inner);
  return container;
}

// ─── Layout Shell ───────────────────────────────────────────────
function renderLayout(contentView) {
  const layout = el('div', { class: 'layout' });
  layout.appendChild(renderSidebar(contentView));

  const main = el('div', { class: 'main' });
  main.appendChild(renderMainHeader(contentView));

  const content = el('div', { class: 'main-content' });
  switch (contentView) {
    case 'home': content.appendChild(renderHome()); break;
    case 'pipeline': content.appendChild(renderPipeline()); break;
    case 'completion': content.appendChild(renderCompletion()); break;
    case 'explorer': content.appendChild(renderExplorer()); break;
    case 'graph': content.appendChild(renderGraphView()); break;
    case 'chat': content.appendChild(renderChat()); break;
    case 'settings': content.appendChild(renderSettings()); break;
  }
  main.appendChild(content);
  layout.appendChild(main);
  return layout;
}

// ─── Sidebar ────────────────────────────────────────────────────
function renderSidebar(activeView) {
  const sidebar = el('div', { class: 'sidebar' + (state.sidebarCollapsed ? ' collapsed' : '') });

  // Header
  const header = el('div', { class: 'sidebar-header' });
  const logo = el('img', { src: '/static/lens_image.png', alt: 'RepoLens' });
  const title = el('span', { class: 'sidebar-header-title' }, 'RepoLens');
  
  const toggleBtn = el('button', { 
      class: 'btn-icon', 
      style: { background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '4px', marginLeft: 'auto' },
      html: Icons.menu || '☰'
  });
  toggleBtn.onclick = () => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
      sidebar.classList.toggle('collapsed', state.sidebarCollapsed);
  };

  header.appendChild(logo);
  header.appendChild(title);
  header.appendChild(toggleBtn);
  sidebar.appendChild(header);

  const nav = el('div', { class: 'sidebar-nav' });

  // Main nav
  const navItems = [
    { icon: Icons.home, label: 'Home', view: 'home' },
    { icon: Icons.plus, label: 'Add Repository', action: () => openAddRepoModal() },
  ];
  for (const item of navItems) {
    nav.appendChild(el('button', {
      class: `sidebar-item ${activeView === item.view ? 'active' : ''}`,
      onClick: item.action || (() => navigate(item.view)),
    },
      el('span', { class: 'sidebar-item-icon', html: item.icon }),
      el('span', { class: 'sidebar-item-label' }, item.label),
    ));
  }

  // Repos section
  if (state.repos.length > 0) {
    const repoSection = el('div', { class: 'sidebar-section' });
    repoSection.appendChild(el('div', { class: 'sidebar-section-title' }, 'Repositories'));
    for (const repo of state.repos) {
      const isActive = state.activeRepo && state.activeRepo.name === repo.name && state.activeRepo.owner === repo.owner;
      repoSection.appendChild(el('button', {
        class: `sidebar-item ${isActive ? 'active' : ''}`,
        onClick: () => openRepo(repo),
      },
        el('span', { class: 'sidebar-item-icon', html: Icons.repo }),
        el('span', { class: 'sidebar-item-label' }, repo.name),
      ));
    }
    nav.appendChild(repoSection);
  }

  // Active repo actions
  if (state.activeRepo) {
    const repoActions = el('div', { class: 'sidebar-section' });
    repoActions.appendChild(el('div', { class: 'sidebar-section-title' }, state.activeRepo.name));
    const items = [
      { icon: Icons.search, label: 'Summaries', view: 'explorer' },
      { icon: Icons.cloud, label: 'Graph View', view: 'graph' },
      { icon: Icons.chat, label: 'Chat', view: 'chat' },
    ];
    for (const item of items) {
      repoActions.appendChild(el('button', {
        class: `sidebar-item ${activeView === item.view ? 'active' : ''}`,
        onClick: () => navigate(item.view),
      },
        el('span', { class: 'sidebar-item-icon', html: item.icon }),
        el('span', { class: 'sidebar-item-label' }, item.label),
      ));
    }
    nav.appendChild(repoActions);
  }

  sidebar.appendChild(nav);

  // Footer
  const footer = el('div', { class: 'sidebar-footer' });
  footer.appendChild(el('button', {
    class: `sidebar-item ${activeView === 'settings' ? 'active' : ''}`,
    onClick: () => navigate('settings'),
  },
    el('span', { class: 'sidebar-item-icon', html: Icons.settings }),
    el('span', { class: 'sidebar-item-label' }, 'Settings'),
  ));
  const searchBtn = el('button', {
    class: 'sidebar-item',
    onClick: () => { state.searchOpen = true; render(); },
  },
    el('span', { class: 'sidebar-item-icon', html: Icons.search }),
    el('span', { class: 'sidebar-item-label' }, 'Search'),
    el('kbd', { class: 'sidebar-item-label', style: { marginLeft: 'auto', fontSize: '11px', padding: '1px 4px', background: 'var(--bg-input)', border: '1px solid var(--border-default)', borderRadius: '3px', color: 'var(--text-tertiary)' } }, '⌘K'),
  );
  footer.appendChild(searchBtn);
  sidebar.appendChild(footer);

  return sidebar;
}

// ─── Main Header ────────────────────────────────────────────────
function renderMainHeader(view) {
  const header = el('div', { class: 'main-header' });
  const left = el('div', { class: 'main-header-left' });

  const breadcrumb = el('div', { class: 'breadcrumb' });
  const labels = {
    home: 'Home', pipeline: 'Parsing', completion: 'Complete',
    explorer: 'Summaries', chat: 'Chat', settings: 'Settings',
  };

  if (state.activeRepo && ['explorer', 'chat', 'pipeline', 'completion'].includes(view)) {
    breadcrumb.appendChild(el('span', {}, state.activeRepo.owner));
    breadcrumb.appendChild(el('span', { class: 'breadcrumb-separator' }, '/'));
    breadcrumb.appendChild(el('span', {}, state.activeRepo.name));
    breadcrumb.appendChild(el('span', { class: 'breadcrumb-separator', html: Icons.chevronRight }));
  }
  breadcrumb.appendChild(el('span', { class: 'breadcrumb-current' }, labels[view] || view));
  left.appendChild(breadcrumb);
  header.appendChild(left);

  const right = el('div', { class: 'main-header-right' });
  if (state.config) {
    right.appendChild(el('span', { class: 'badge badge-default' }, state.config.model));
  }
  header.appendChild(right);
  return header;
}

// ─── Home ───────────────────────────────────────────────────────
function renderHome() {
  const home = el('div', { class: 'home content-centered' });

  // Greeting
  const greeting = el('div', { class: 'home-greeting' });
  greeting.appendChild(el('h1', {}, 'Dashboard'));
  greeting.appendChild(el('p', { class: 'text-secondary' }, 'Parse repositories, explore summaries, and query your codebase.'));
  home.appendChild(greeting);

  // Quick actions
  const actions = el('div', { class: 'home-actions' });
  actions.appendChild(makeAction(Icons.plus, 'Add Repository', 'GitHub or local folder', () => openAddRepoModal()));
  actions.appendChild(makeAction(Icons.settings, 'Settings', 'AI provider & config', () => navigate('settings')));
  if (state.activeRepo) {
    actions.appendChild(makeAction(Icons.search, 'Summaries', state.activeRepo.name, () => navigate('explorer')));
    actions.appendChild(makeAction(Icons.chat, 'Chat', 'Query your code', () => navigate('chat')));
  }
  home.appendChild(actions);

  // Repo list
  const repoSection = el('div', { class: 'home-section' });
  const repoHeader = el('div', { class: 'home-section-header' });
  repoHeader.appendChild(el('span', { class: 'home-section-title' }, 'Repositories'));
  repoHeader.appendChild(el('button', { class: 'btn btn-ghost', onClick: loadRepos }, '↻ Refresh'));
  repoSection.appendChild(repoHeader);

  if (state.repos.length === 0) {
    repoSection.appendChild(renderEmptyState(Icons.folder, 'No repositories yet', 'Add a GitHub repository or local folder to get started.', 'Add Repository', () => openAddRepoModal()));
  } else {
    const list = el('div', { class: 'repo-list' });
    for (const repo of state.repos) {
      list.appendChild(renderRepoCard(repo));
    }
    repoSection.appendChild(list);
  }
  home.appendChild(repoSection);

  // Append modal if open
  if (state.modalOpen === 'addRepo') {
    home.appendChild(renderAddRepoModal());
  }

  return home;
}

function makeAction(icon, title, desc, onClick) {
  return el('div', { class: 'home-action', onClick },
    el('div', { class: 'home-action-icon', html: icon }),
    el('div', { class: 'home-action-text' },
      el('div', { class: 'home-action-title' }, title),
      el('div', { class: 'home-action-desc' }, desc),
    ),
  );
}

function renderRepoCard(repo) {
  const isActive = state.activeRepo && state.activeRepo.name === repo.name;
  return el('div', { class: 'repo-card', onClick: () => openRepo(repo) },
    el('div', { class: 'repo-card-left' },
      el('div', { class: 'repo-card-icon', html: Icons.repo }),
      el('div', { class: 'repo-card-info' },
        el('h3', {}, `${repo.owner}/${repo.name}`),
        el('div', { class: 'repo-card-meta' },
          el('span', {}, `${repo.file_count} files`),
          el('span', {}, `${repo.node_count} nodes`),
          repo.has_summaries ? el('span', { class: 'badge badge-success' }, 'Summarized') : el('span', { class: 'badge badge-default' }, 'Not summarized'),
        ),
      ),
    ),
    el('div', { class: 'repo-card-right' },
      isActive ? el('span', { class: 'badge badge-accent' }, 'Active') : null,
      el('span', { style: { color: 'var(--text-tertiary)' }, html: Icons.chevronRight }),
    ),
  );
}

// ─── Add Repo Modal ─────────────────────────────────────────────
function openAddRepoModal() {
  state.modalOpen = 'addRepo';
  render();
}

function closeModal() {
  state.modalOpen = null;
  render();
}

function renderAddRepoModal() {
  let activeTab = 'github';

  const overlay = el('div', { class: 'modal-overlay', onClick: (e) => { if (e.target === overlay) closeModal(); } });
  const modal = el('div', { class: 'modal' });

  const header = el('div', { class: 'modal-header' });
  header.appendChild(el('span', { class: 'modal-title' }, 'Add Repository'));
  header.appendChild(el('button', { class: 'modal-close', onClick: closeModal, html: Icons.x }));
  modal.appendChild(header);

  // Tabs
  const tabs = el('div', { class: 'modal-tabs' });
  const githubTab = el('button', { class: 'modal-tab active', onClick: () => switchTab('github') }, 'GitHub');
  const localTab = el('button', { class: 'modal-tab', onClick: () => switchTab('local') }, 'Local Folder');
  tabs.appendChild(githubTab);
  tabs.appendChild(localTab);
  modal.appendChild(tabs);

  // Tab content
  const content = el('div', { id: 'modal-tab-content' });
  content.appendChild(renderGitHubTab());
  modal.appendChild(content);

  function switchTab(tab) {
    activeTab = tab;
    githubTab.className = `modal-tab ${tab === 'github' ? 'active' : ''}`;
    localTab.className = `modal-tab ${tab === 'local' ? 'active' : ''}`;
    content.innerHTML = '';
    content.appendChild(tab === 'github' ? renderGitHubTab() : renderLocalTab());
  }

  overlay.appendChild(modal);
  return overlay;
}

function renderGitHubTab() {
  const frag = el('div', {});

  const inputGroup = el('div', { class: 'input-group' });
  inputGroup.appendChild(el('label', {}, 'Repository URL'));
  const input = el('input', {
    class: 'input',
    id: 'github-url-input',
    placeholder: 'https://github.com/owner/repo',
    type: 'url',
  });
  inputGroup.appendChild(input);
  frag.appendChild(inputGroup);

  const validationMsg = el('div', { id: 'repo-validation', style: { minHeight: '20px', marginTop: '8px' } });
  frag.appendChild(validationMsg);

  // Live validation
  let validateTimer;
  input.addEventListener('input', () => {
    clearTimeout(validateTimer);
    validateTimer = setTimeout(() => {
      const url = input.value.trim();
      if (!url) { validationMsg.innerHTML = ''; return; }
      const match = url.match(/github\.com\/([^/]+)\/([^/]+)/);
      if (match) {
        validationMsg.innerHTML = `<span class="validation-msg validation-success">✓ ${match[1]}/${match[2]}</span>`;
      } else {
        validationMsg.innerHTML = '<span class="validation-msg validation-error">✕ Invalid GitHub URL</span>';
      }
    }, 300);
  });

  const actions = el('div', { class: 'modal-actions' });
  actions.appendChild(el('button', { class: 'btn btn-secondary', onClick: closeModal }, 'Cancel'));
  const cloneBtn = el('button', {
    class: 'btn btn-primary',
    onClick: async () => {
      const url = input.value.trim();
      if (!url || !url.includes('github.com')) {
        toast('Please enter a valid GitHub URL', 'error');
        return;
      }
      cloneBtn.disabled = true;
      cloneBtn.textContent = 'Cloning...';
      try {
        const match = url.match(/github\.com\/([^/]+)\/([^/\s?.]+)/);
        await api('/repo', { method: 'POST', body: { github_url: url } });
        state.activeRepo = { owner: match[1], name: match[2].replace(/\.git$/, ''), path: '' };
        closeModal();
        await loadRepos();
        startPipeline();
      } catch (err) {
        toast(err.message, 'error');
        cloneBtn.disabled = false;
        cloneBtn.textContent = 'Clone & Parse';
      }
    },
  }, 'Clone & Parse');
  actions.appendChild(cloneBtn);
  frag.appendChild(actions);

  return frag;
}

function renderLocalTab() {
  const frag = el('div', {});

  const inputGroup = el('div', { class: 'input-group' });
  inputGroup.appendChild(el('label', {}, 'Folder Path'));
  const input = el('input', {
    class: 'input',
    id: 'local-path-input',
    placeholder: 'C:\\Users\\you\\projects\\my-repo',
    type: 'text',
  });
  inputGroup.appendChild(input);
  frag.appendChild(inputGroup);

  const hint = el('p', { class: 'text-xs text-tertiary', style: { marginTop: '8px' } }, 'Enter the absolute path to a local repository folder.');
  frag.appendChild(hint);

  const actions = el('div', { class: 'modal-actions' });
  actions.appendChild(el('button', { class: 'btn btn-secondary', onClick: closeModal }, 'Cancel'));
  const openBtn = el('button', {
    class: 'btn btn-primary',
    onClick: async () => {
      const folderPath = input.value.trim();
      if (!folderPath) {
        toast('Please enter a folder path', 'error');
        return;
      }
      openBtn.disabled = true;
      openBtn.textContent = 'Opening...';
      try {
        await api('/repo/local', { method: 'POST', body: { folder_path: folderPath } });
        const parts = folderPath.replace(/\\/g, '/').split('/').filter(Boolean);
        const name = parts.pop() || 'local-repo';
        const owner = 'local';
        state.activeRepo = { owner, name, path: folderPath };
        closeModal();
        await loadRepos();
        startPipeline();
      } catch (err) {
        toast(err.message, 'error');
        openBtn.disabled = false;
        openBtn.textContent = 'Open & Parse';
      }
    },
  }, 'Open & Parse');
  actions.appendChild(openBtn);
  frag.appendChild(actions);

  return frag;
}

// ─── Pipeline ───────────────────────────────────────────────────

const PIPELINE_STAGES = [
  { id: 'parse', label: 'Parsing Codebase' },
  { id: 'summary', label: 'Generating AI Summaries' },
  { id: 'index', label: 'Building Vector Index' }
];

let pipelineStartTime = null;
let pipelinePoller = null;
let pipelineData = null;

async function startPipeline() {
  pipelineStartTime = Date.now();
  pipelineData = { stage: 'tree', elapsed: 0, error: null, stage_index: 0, logs: [] };
  state.pipelineStage = 0;
  state.pipelineError = null;
  navigate('pipeline');

  if (pipelinePoller) clearInterval(pipelinePoller);
  pipelinePoller = setInterval(() => {
    if (pipelineData && !pipelineData.error && pipelineData.stage !== 'done') {
      pipelineData.elapsed = Math.floor((Date.now() - pipelineStartTime) / 1000);
      updatePipeline(pipelineData);
    }
  }, 1000);

  const log = (msg) => { 
    pipelineData.logs.push(msg); 
    const logContent = document.getElementById('pl-log-content');
    if (logContent) {
      logContent.appendChild(el('div', { class: 'pl-log-entry' }, msg));
      logContent.scrollTop = logContent.scrollHeight;
    }
  };

  try {
    pipelineData.stage_index = 0; pipelineData.stage = 'parse'; updatePipeline(pipelineData);
    log('Starting Tree Sitter parsing...');
    await api('/tree', { method: 'POST' });
    log('Extracting Nodes...');
    await api('/nodes', { method: 'POST' });
    log('Extracting Edges...');
    await api('/edges', { method: 'POST' });
    
    pipelineData.stage_index = 1; pipelineData.stage = 'summary'; updatePipeline(pipelineData);
    log('Generating AI Summaries...');
    await api('/summary', { method: 'POST' });
    
    pipelineData.stage_index = 2; pipelineData.stage = 'index'; updatePipeline(pipelineData);
    log('Building Vector Index...');
    await api('/index', { method: 'POST' });
    
    pipelineData.stage_index = 3; pipelineData.stage = 'done'; updatePipeline(pipelineData);
    log('Pipeline completed successfully!');
    
    clearInterval(pipelinePoller);
    pipelinePoller = null;
    
    try {
      state.structure = await api('/data/filestructure.json');
      state.nodes = await api('/data/nodes.json');
      state.edges = await api('/data/edges.json');
      await loadRepos();
    } catch(e) {
      console.error("Failed to load parsed data", e);
    }
    
    render();
    setTimeout(() => navigate('completion'), 600);
    
  } catch (err) {
    pipelineData.error = err.message;
    state.pipelineError = err.message;
    clearInterval(pipelinePoller);
    pipelinePoller = null;
    render();
    toast(`Pipeline failed: ${err.message}`, 'error');
  }
}

async function pollPipeline() {
  // Deprecated - using manual sequencing
}

function fmtElapsed(sec) {
  if (!sec || sec < 0) return '0s';
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

function renderPipeline() {
  const d = pipelineData || {};
  const root = el('div', { class: 'pipeline' });

  const top = el('div', { class: 'pipeline-top' });
  top.appendChild(el('span', { class: 'pipeline-top-title' }, 'Parsing Repository'));
  const elapsed = el('span', { class: 'pipeline-top-elapsed', id: 'pl-elapsed' }, fmtElapsed(d.elapsed));
  top.appendChild(elapsed);
  root.appendChild(top);

  const errBanner = el('div', { class: 'pl-error', id: 'pl-error', style: { display: d.error ? 'flex' : 'none' } });
  errBanner.appendChild(el('span', { html: Icons.x }));
  errBanner.appendChild(el('span', { id: 'pl-error-text' }, d.error || ''));
  errBanner.appendChild(el('button', { class: 'btn btn-secondary', style: { marginLeft: 'auto' }, onClick: () => startPipeline() }, 'Retry'));
  root.appendChild(errBanner);

  const body = el('div', { class: 'pipeline-body' });
  const timeline = el('div', { class: 'pl-timeline' });
  
  const stageIndex = d.stage_index ?? state.pipelineStage ?? 0;
  for (let i = 0; i < PIPELINE_STAGES.length; i++) {
    const s = PIPELINE_STAGES[i];
    let cls = 'pending';
    if (i < stageIndex) cls = 'completed';
    else if (i === stageIndex && !d.error) cls = 'active';

    const stage = el('div', { class: `pl-stage ${cls}`, id: `pl-stage-${i}` });
    const track = el('div', { class: 'pl-stage-track' });
    const dot = el('div', { class: 'pl-stage-dot', id: `pl-dot-${i}` });
    if (cls === 'completed') dot.innerHTML = Icons.check;
    track.appendChild(dot);
    track.appendChild(el('div', { class: 'pl-stage-wire' }));
    stage.appendChild(track);

    const cnt = el('div', { class: 'pl-stage-content' });
    cnt.appendChild(el('div', { class: 'pl-stage-label' }, s.label));

    const sub = el('div', { class: 'pl-stage-sub', id: `pl-sub-${i}` });
    if (cls === 'active') sub.textContent = 'processing...';
    cnt.appendChild(sub);
    stage.appendChild(cnt);
    timeline.appendChild(stage);
  }
  body.appendChild(timeline);

  const right = el('div', { class: 'pl-right' });
  const progressBars = el('div', { class: 'pl-progress-section' });

  // 1. Tree Parse Bar
  const treeGroup = el('div', { class: 'pl-progress-group' });
  const treeHeader = el('div', { class: 'pl-progress-header' });
  treeHeader.appendChild(el('span', {}, 'Tree Parsing'));
  treeHeader.appendChild(el('span', { id: 'pb-tree-pct' }, '0%'));
  treeGroup.appendChild(treeHeader);
  const treeBar = el('div', { class: 'pl-progress-track' });
  treeBar.appendChild(el('div', { class: 'pl-progress-fill', id: 'pb-tree-fill', style: { width: '0%', transition: 'width 0.3s ease' } }));
  treeGroup.appendChild(treeBar);
  progressBars.appendChild(treeGroup);

  // 2. Node & Edge Bar
  const nodeGroup = el('div', { class: 'pl-progress-group' });
  const nodeHeader = el('div', { class: 'pl-progress-header' });
  nodeHeader.appendChild(el('span', {}, 'Nodes & Edges'));
  nodeHeader.appendChild(el('span', { id: 'pb-node-pct' }, '0%'));
  nodeGroup.appendChild(nodeHeader);
  const nodeBar = el('div', { class: 'pl-progress-track' });
  nodeBar.appendChild(el('div', { class: 'pl-progress-fill pl-progress-fill-accent', id: 'pb-node-fill', style: { width: '0%', transition: 'width 0.3s ease' } }));
  nodeGroup.appendChild(nodeBar);
  progressBars.appendChild(nodeGroup);

  // 3. Summaries & Index Bar
  const sumGroup = el('div', { class: 'pl-progress-group' });
  const sumHeader = el('div', { class: 'pl-progress-header' });
  sumHeader.appendChild(el('span', {}, 'Summaries & Indexing'));
  sumHeader.appendChild(el('span', { id: 'pb-sum-pct' }, '0%'));
  sumGroup.appendChild(sumHeader);
  const sumBar = el('div', { class: 'pl-progress-track' });
  sumBar.appendChild(el('div', { class: 'pl-progress-fill pl-progress-fill-accent', id: 'pb-sum-fill', style: { width: '0%', transition: 'width 0.3s ease' } }));
  sumGroup.appendChild(sumBar);
  progressBars.appendChild(sumGroup);

  right.appendChild(progressBars);

  const logTerminal = el('div', { class: 'pl-logs' });
  logTerminal.appendChild(el('div', { class: 'pl-logs-title' }, 'ACTIVITY'));
  const logContent = el('div', { class: 'pl-logs-content', id: 'pl-log-content' });
  if (d.logs) {
    for (const msg of d.logs) {
      logContent.appendChild(el('div', { class: 'pl-log-entry' }, msg));
    }
  }
  logTerminal.appendChild(logContent);
  right.appendChild(logTerminal);

  body.appendChild(right);
  root.appendChild(body);

  setTimeout(() => updatePipeline(d), 10);
  return root;
}

function updatePipeline(d) {
  if (!d) return;
  const stageIndex = d.stage_index ?? state.pipelineStage ?? 0;

  const elElapsed = document.getElementById('pl-elapsed');
  if (elElapsed) elElapsed.textContent = fmtElapsed(d.elapsed);

  for (let i = 0; i < PIPELINE_STAGES.length; i++) {
    const stageEl = document.getElementById(`pl-stage-${i}`);
    const dot = document.getElementById(`pl-dot-${i}`);
    const sub = document.getElementById(`pl-sub-${i}`);
    if (!stageEl || !dot || !sub) continue;

    let cls = 'pending';
    if (i < stageIndex) cls = 'completed';
    else if (i === stageIndex && !d.error) cls = 'active';

    stageEl.className = `pl-stage ${cls}`;
    if (cls === 'completed') dot.innerHTML = Icons.check; else dot.innerHTML = '';
    if (cls === 'active') sub.textContent = 'processing...';
    else if (cls === 'completed') sub.textContent = 'done';
    else sub.textContent = '';
  }

  // Calculate percentages based on stage_index
  // stage_index 1 = tree (0->100)
  // stage_index 2 = nodes (0->100)
  // stage_index 3 = summaries (0->100)
  
  let treePct = stageIndex > 1 ? 100 : (stageIndex === 1 ? 50 : 0);
  let nodePct = stageIndex > 2 ? 100 : (stageIndex === 2 ? 50 : 0);
  let sumPct = stageIndex > 3 ? 100 : (stageIndex === 3 ? 50 : 0);

  const pbTreePct = document.getElementById('pb-tree-pct');
  const pbTreeFill = document.getElementById('pb-tree-fill');
  if (pbTreePct && pbTreeFill) { pbTreePct.textContent = `${treePct}%`; pbTreeFill.style.width = `${treePct}%`; }

  const pbNodePct = document.getElementById('pb-node-pct');
  const pbNodeFill = document.getElementById('pb-node-fill');
  if (pbNodePct && pbNodeFill) { pbNodePct.textContent = `${nodePct}%`; pbNodeFill.style.width = `${nodePct}%`; }

  const pbSumPct = document.getElementById('pb-sum-pct');
  const pbSumFill = document.getElementById('pb-sum-fill');
  if (pbSumPct && pbSumFill) { pbSumPct.textContent = `${sumPct}%`; pbSumFill.style.width = `${sumPct}%`; }
}

// ─── Completion ─────────────────────────────────────────────────
function renderCompletion() {
  const d = pipelineData || {};
  const comp = el('div', { class: 'completion content-centered' });

  comp.appendChild(el('div', { class: 'completion-icon' }, '\u2713'));
  comp.appendChild(el('h2', {}, 'Repository Ready'));
  comp.appendChild(el('p', {}, `${state.activeRepo?.owner}/${state.activeRepo?.name} has been fully parsed and summarized.`));

  const stats = el('div', { class: 'completion-stats' });
  const nodeCount = d.nodes_discovered || state.nodes?.nodes?.length || 0;
  const fileCount = d.files_processed || countFiles(state.structure);
  const summaryCount = d.summaries_completed || 0;
  const elapsed = d.elapsed ? fmtElapsed(d.elapsed) : (pipelineStartTime ? `${Math.round((Date.now() - pipelineStartTime) / 1000)}s` : '\u2014');

  stats.appendChild(makeStat(nodeCount, 'Code Nodes'));
  stats.appendChild(makeStat(fileCount, 'Files'));
  stats.appendChild(makeStat(summaryCount, 'Summaries'));
  stats.appendChild(makeStat(elapsed, 'Processing Time'));
  comp.appendChild(stats);

  const actions = el('div', { class: 'flex-center gap-3' });
  actions.appendChild(el('button', { class: 'btn btn-primary btn-lg', onClick: () => navigate('explorer') }, 'Explore Summaries'));
  actions.appendChild(el('button', { class: 'btn btn-secondary btn-lg', onClick: () => navigate('chat') }, 'Start Chatting'));
  comp.appendChild(actions);

  return comp;
}

function makeStat(value, label) {
  return el('div', { class: 'completion-stat' },
    el('div', { class: 'completion-stat-value' }, String(value)),
    el('div', { class: 'completion-stat-label' }, label),
  );
}

function countFiles(node) {
  if (!node) return 0;
  if (node.type === 'file') return 1;
  let count = 0;
  for (const c of (node.children || [])) count += countFiles(c);
  return count;
}

// ─── Explorer ───────────────────────────────────────────────────
function renderExplorer() {
  const explorer = el('div', { class: 'explorer content-centered' });

  if (!state.structure) {
    explorer.appendChild(renderEmptyState(Icons.folder, 'No summaries available', 'Parse a repository first to view its summaries.', 'Add Repository', () => openAddRepoModal()));
    return explorer;
  }

  // Search
  const searchDiv = el('div', { class: 'explorer-search' });
  searchDiv.appendChild(el('span', { class: 'explorer-search-icon', html: Icons.search }));
  const searchInput = el('input', {
    class: 'input',
    placeholder: 'Search summaries...',
    style: { paddingLeft: '32px' },
    value: state.explorerSearch,
  });
  searchInput.addEventListener('input', (e) => {
    state.explorerSearch = e.target.value;
    renderTreeInto(treeContainer, state.structure, state.explorerSearch);
  });
  searchDiv.appendChild(searchInput);
  explorer.appendChild(searchDiv);

  // Actions
  const actionsBar = el('div', { class: 'flex-between mb-4' });
  actionsBar.appendChild(el('span', { class: 'text-sm text-secondary' }, `${countFiles(state.structure)} files · ${state.nodes?.nodes?.length || 0} nodes`));
  const btns = el('div', { class: 'flex-center gap-2' });
  btns.appendChild(el('button', { class: 'btn btn-ghost', onClick: () => { state.expandedNodes.clear(); renderTreeInto(treeContainer, state.structure, state.explorerSearch); } }, 'Collapse All'));
  btns.appendChild(el('button', { class: 'btn btn-ghost', onClick: () => expandAll(state.structure) }, 'Expand All'));
  actionsBar.appendChild(btns);
  explorer.appendChild(actionsBar);

  // Tree
  const treeContainer = el('div', { id: 'tree-container' });
  renderTreeInto(treeContainer, state.structure, state.explorerSearch);
  explorer.appendChild(treeContainer);

  return explorer;
}

function expandAll(node) {
  if (!node) return;
  if (node.children?.length || node.node_ids?.length) state.expandedNodes.add(node.id);
  for (const c of (node.children || [])) expandAll(c);
  render();
}

function renderTreeInto(container, structure, search) {
  container.innerHTML = '';
  if (!structure) return;
  container.appendChild(renderTreeNode(structure, 0, search?.toLowerCase()));
}

function renderTreeNode(node, depth, search) {
  const frag = el('div', { class: depth > 0 ? 'tree-node' : '' });

  if (search && !nodeMatchesSearch(node, search)) return frag;

  const isExpanded = state.expandedNodes.has(node.id);
  const hasChildren = (node.children && node.children.length > 0);
  const isFile = node.type === 'file';
  const icon = node.type === 'repository' ? Icons.repo : node.type === 'folder' ? Icons.folder : Icons.file;

  const isSelected = state.selectedId === node.id;
const item = el('div', { class: `tree-item ${isSelected ? 'selected' : ''}`, onClick: () => toggleNode(node.id) });

  if (hasChildren || isFile) {
    const toggle = el('span', { class: `tree-toggle ${isExpanded ? 'expanded' : ''}`, html: Icons.chevronRight });
    item.appendChild(toggle);
  } else {
    item.appendChild(el('span', { class: 'tree-toggle' }, ' '));
  }

  item.appendChild(el('span', { class: 'tree-item-icon', html: icon }));

  const content = el('div', { class: 'tree-item-content' });
  content.appendChild(el('div', { class: 'tree-item-name' }, node.name));

  if (node.summary && !isExpanded) {
    const preview = node.summary.split('\n')[0].substring(0, 120);
    content.appendChild(el('div', { class: 'tree-item-summary' }, preview));
  }

  const meta = el('div', { class: 'tree-item-meta' });
  if (node.type === 'file' && node.node_ids) {
    meta.appendChild(el('span', { class: 'badge badge-default' }, `${node.node_ids.length} nodes`));
  }
  if (node.children?.length) {
    meta.appendChild(el('span', { class: 'badge badge-default' }, `${node.children.length} items`));
  }
  content.appendChild(meta);
  item.appendChild(content);
  frag.appendChild(item);

  // Expanded content
  if (isExpanded) {
    // Show full summary as a collapsible tree node
    if (node.summary) {
      const summaryItem = el('div', { class: 'tree-node' });
      const isSummaryExpanded = state.expandedNodes.has(node.id + '_summary');
      
      const si = el('div', { class: 'tree-item', onClick: (e) => { e.stopPropagation(); toggleNode(node.id + '_summary'); } });
      const toggle = el('span', { class: `tree-toggle ${isSummaryExpanded ? 'expanded' : ''}`, html: Icons.chevronRight });
      si.appendChild(toggle);
      si.appendChild(el('span', { class: 'tree-item-icon', style: { color: 'var(--accent)' }, html: Icons.info }));
      
      const sc = el('div', { class: 'tree-item-content' });
      sc.appendChild(el('div', { class: 'tree-item-name' }, 'Full Summary'));
      si.appendChild(sc);
      summaryItem.appendChild(si);
      
      if (isSummaryExpanded) {
        const detail = el('div', { class: 'summary-detail', style: { paddingLeft: '32px' } });
        const textContainer = el('div', { class: 'summary-detail-text', style: { whiteSpace: 'pre-wrap', lineHeight: '1.6', marginBottom: '8px' } });
        textContainer.textContent = node.summary;
        detail.appendChild(textContainer);
        const detailActions = el('div', { class: 'summary-detail-actions' });
        detailActions.appendChild(el('button', { class: 'btn btn-ghost', onClick: (e) => { e.stopPropagation(); copyText(node.summary); }, html: Icons.copy + '<span>Copy</span>' }));
        detail.appendChild(detailActions);
        summaryItem.appendChild(detail);
      }
      frag.appendChild(summaryItem);
    }

    // Show children
    if (hasChildren) {
      for (const child of node.children) {
        frag.appendChild(renderTreeNode(child, depth + 1, search));
      }
    }

    // Removed syntax nodes rendering inside files
  }

  return frag;
}

function toggleNode(id) {
  if (state.expandedNodes.has(id)) state.expandedNodes.delete(id);
  else state.expandedNodes.add(id);
  render();
}

function nodeMatchesSearch(node, search) {
  if (!search) return true;
  if (node.name?.toLowerCase().includes(search)) return true;
  if (node.summary?.toLowerCase().includes(search)) return true;
  if (node.children) return node.children.some(c => nodeMatchesSearch(c, search));
  if (node.nodes) return node.nodes.some(n => (n.title || '').toLowerCase().includes(search) || (n.summary || '').toLowerCase().includes(search));
  return false;
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => toast('Copied to clipboard', 'success'));
}

// ─── Chat ───────────────────────────────────────────────────────
function renderChat() {
  const chat = el('div', { class: 'chat' });

  if (!state.activeRepo) {
    chat.appendChild(renderEmptyState(Icons.chat, 'No repository selected', 'Add and parse a repository first to start chatting.', 'Add Repository', () => openAddRepoModal()));
    return chat;
  }

  // Messages
  const messagesDiv = el('div', { class: 'chat-messages', id: 'chat-messages' });

  if (state.chatMessages.length === 0) {
    const empty = el('div', { class: 'chat-empty' });
    empty.appendChild(el('img', { src: '/static/lens_image.png', alt: '' }));
    empty.appendChild(el('h3', {}, 'Ask about your code'));
    empty.appendChild(el('p', {}, `Query ${state.activeRepo.name} using natural language. Ask about functions, architecture, or how things work.`));

    const suggestions = el('div', { class: 'flex-center gap-2', style: { flexWrap: 'wrap', marginTop: '16px' } });
    const prompts = [
      'Explain the main entry point',
      'What does this project do?',
      'Find the database logic',
    ];
    for (const p of prompts) {
      suggestions.appendChild(el('button', { class: 'btn btn-secondary', onClick: () => sendChat(p) }, p));
    }
    empty.appendChild(suggestions);
    messagesDiv.appendChild(empty);
  } else {
    for (const msg of state.chatMessages) {
      messagesDiv.appendChild(renderChatMessage(msg));
    }
  }
  chat.appendChild(messagesDiv);

  // Input
  const inputArea = el('div', { class: 'chat-input-area' });
  const inputContainer = el('div', { class: 'chat-input-container' });

  const textarea = el('textarea', {
    id: 'chat-input',
    placeholder: 'Ask about your repository...',
    rows: '1',
  });

  textarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChat(textarea.value.trim());
    }
  });

  textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  });

  const sendBtn = el('button', {
    class: 'chat-send-btn',
    id: 'chat-send-btn',
    onClick: () => sendChat(textarea.value.trim()),
  }, '↑');

  inputContainer.appendChild(textarea);
  inputContainer.appendChild(sendBtn);
  inputArea.appendChild(inputContainer);
  chat.appendChild(inputArea);

  // Scroll to bottom
  requestAnimationFrame(() => {
    const msgs = document.getElementById('chat-messages');
    if (msgs) msgs.scrollTop = msgs.scrollHeight;
  });

  return chat;
}

function renderChatMessage(msg) {
  const wrapper = el('div', { class: `chat-message chat-message-${msg.role}` });
  const bubble = el('div', { class: 'chat-bubble' });

  // Simple markdown-ish rendering
  bubble.innerHTML = formatChatContent(msg.content);

  if (msg.references && msg.references.length > 0) {
    const refs = el('div', { class: 'chat-references' });
    for (const ref of msg.references) {
      const pathParts = (ref.path || '').replace(/\\/g, '/').split('/');
      const filename = pathParts.pop() || ref.title;
      refs.appendChild(el('span', {
        class: 'chat-reference',
        title: ref.path,
      }, `${ref.title || filename}:${ref.start_line || ''}`));
    }
    bubble.appendChild(refs);
  }

  wrapper.appendChild(bubble);
  return wrapper;
}

function formatChatContent(text) {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^---$/gm, '<hr>')
    .replace(/\n/g, '<br>');
}

async function sendChat(query) {
  if (!query || !state.activeRepo) return;

  const textarea = document.getElementById('chat-input');
  if (textarea) { textarea.value = ''; textarea.style.height = 'auto'; }

  state.chatMessages.push({ role: 'user', content: query });
  render();

  // Add typing indicator
  const msgs = document.getElementById('chat-messages');
  if (msgs) {
    const typing = el('div', { class: 'chat-message chat-message-assistant', id: 'typing-indicator' });
    const bubble = el('div', { class: 'chat-bubble' });
    const dots = el('div', { class: 'chat-typing' },
      el('div', { class: 'chat-typing-dot' }),
      el('div', { class: 'chat-typing-dot' }),
      el('div', { class: 'chat-typing-dot' }),
    );
    bubble.appendChild(dots);
    typing.appendChild(bubble);
    msgs.appendChild(typing);
    msgs.scrollTop = msgs.scrollHeight;
  }

  try {
    const res = await api('/ask', {
      method: 'POST',
      body: {
        query,
        repo_owner: state.activeRepo.owner,
        repo_name: state.activeRepo.name,
      },
    });

    state.chatMessages.push({
      role: 'assistant',
      content: res.answer,
      references: res.citations,
    });
  } catch (err) {
    state.chatMessages.push({ role: 'assistant', content: `Error: ${err.message}` });
    toast(err.message, 'error');
  }

  render();
}

// ─── Settings ───────────────────────────────────────────────────
function renderSettings() {
  const settings = el('div', { class: 'settings content-centered' });

  // AI Provider
  const aiSection = el('div', { class: 'settings-section' });
  aiSection.appendChild(el('div', { class: 'settings-section-title' }, 'AI Configuration'));

  aiSection.appendChild(makeSettingsRow('Provider', state.config?.provider === 'cloud' ? 'Cloud (Gemini)' : 'Local (Ollama)',
    el('span', { class: 'badge badge-accent' }, state.config?.provider || 'cloud'),
  ));

  aiSection.appendChild(makeSettingsRow('Model', state.config?.model || 'gemini-3.1-flash-lite',
    el('span', { class: 'text-sm font-mono' }, state.config?.model || '—'),
  ));

  aiSection.appendChild(makeSettingsRow('API Key', state.config?.api_key_set ? 'Configured' : 'Not set',
    el('div', { class: 'flex-center gap-2' },
      el('span', { class: state.config?.api_key_set ? 'badge badge-success' : 'badge badge-error' }, state.config?.api_key_set ? `${state.config.api_key_preview}` : 'Missing'),
      el('button', { class: 'btn btn-ghost', onClick: () => navigate('setup-cloud') }, 'Change'),
    ),
  ));
  settings.appendChild(aiSection);

  // Data
  const dataSection = el('div', { class: 'settings-section' });
  dataSection.appendChild(el('div', { class: 'settings-section-title' }, 'Data'));
  dataSection.appendChild(makeSettingsRow('Parsed Repositories', `${state.repos.length} repos`,
    el('button', { class: 'btn btn-ghost', onClick: loadRepos }, '↻ Refresh'),
  ));
  dataSection.appendChild(makeSettingsRow('Storage Location', 'out/', el('span', { class: 'font-mono text-sm' }, 'out/')));
  settings.appendChild(dataSection);

  // About
  const aboutSection = el('div', { class: 'settings-section' });
  aboutSection.appendChild(el('div', { class: 'settings-section-title' }, 'About'));
  aboutSection.appendChild(makeSettingsRow('RepoLens', 'v0.2.0', el('span', { class: 'text-sm text-secondary' }, 'v0.2.0')));
  aboutSection.appendChild(makeSettingsRow('Backend', 'FastAPI + Uvicorn', el('span', { class: 'text-sm text-secondary' }, 'FastAPI')));
  settings.appendChild(aboutSection);

  return settings;
}

function makeSettingsRow(label, desc, rightEl) {
  return el('div', { class: 'settings-row' },
    el('div', { class: 'settings-row-left' },
      el('div', { class: 'settings-row-label' }, label),
      el('div', { class: 'settings-row-desc' }, desc),
    ),
    el('div', { class: 'settings-row-right' }, rightEl),
  );
}

// ─── Global Search ──────────────────────────────────────────────
function renderSearch() {
  const overlay = el('div', {
    class: 'search-overlay',
    onClick: (e) => { if (e.target === overlay) { state.searchOpen = false; render(); } },
  });

  const modal = el('div', { class: 'search-modal' });

  const wrapper = el('div', { class: 'search-input-wrapper' });
  wrapper.appendChild(el('span', { class: 'search-icon', html: Icons.search }));
  const input = el('input', {
    placeholder: 'Search repositories, summaries, settings...',
    id: 'global-search-input',
    autocomplete: 'off',
  });
  wrapper.appendChild(input);
  wrapper.appendChild(el('kbd', {}, 'ESC'));
  modal.appendChild(wrapper);

  const results = el('div', { class: 'search-results', id: 'search-results' });

  // Default results
  const defaults = [
    { icon: Icons.home, text: 'Home', hint: 'Dashboard', action: () => { state.searchOpen = false; navigate('home'); } },
    { icon: Icons.plus, text: 'Add Repository', hint: 'GitHub or local', action: () => { state.searchOpen = false; openAddRepoModal(); navigate('home'); } },
    { icon: Icons.settings, text: 'Settings', hint: 'Configuration', action: () => { state.searchOpen = false; navigate('settings'); } },
  ];

  if (state.activeRepo) {
    defaults.push(
      { icon: Icons.search, text: 'Summaries', hint: state.activeRepo.name, action: () => { state.searchOpen = false; navigate('explorer'); } },
      { icon: Icons.chat, text: 'Chat', hint: state.activeRepo.name, action: () => { state.searchOpen = false; navigate('chat'); } },
    );
  }

  for (const r of state.repos) {
    defaults.push({ icon: Icons.repo, text: `${r.owner}/${r.name}`, hint: 'Repository', action: () => { state.searchOpen = false; openRepo(r); } });
  }

  function renderResults(items) {
    results.innerHTML = '';
    if (items.length === 0) {
      results.appendChild(el('div', { class: 'search-empty' }, 'No results found'));
      return;
    }
    for (const item of items) {
      results.appendChild(el('div', {
        class: 'search-result',
        onClick: item.action,
      },
        el('span', { class: 'search-result-icon', html: item.icon }),
        el('span', { class: 'search-result-text' }, item.text),
        el('span', { class: 'search-result-hint' }, item.hint),
      ));
    }
  }

  renderResults(defaults);

  let searchTimeout = null;

  input.addEventListener('input', () => {
    const q = input.value.trim();
    if (!q) { renderResults(defaults); return; }
    
    // Always include any defaults that match locally
    const filteredDefaults = defaults.filter(r => r.text.toLowerCase().includes(q.toLowerCase()) || r.hint.toLowerCase().includes(q.toLowerCase()));
    
    // Show a loading indicator
    renderResults([
      ...filteredDefaults,
      { icon: '↻', text: 'Searching...', hint: '', action: () => {} }
    ]);

    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
        try {
            const res = await api('/search?query=' + encodeURIComponent(q));
            const resultsData = res.results || [];
            
            const nodeResults = resultsData.map(n => {
                const pathParts = (n.path || '').replace(/\\/g, '/').split('/');
                const hintBase = pathParts.pop() || '';
                const scoreText = n.score ? ` (Score: ${n.score.toFixed(2)})` : '';
                return {
                    icon: n.node_type === 'file' ? Icons.file : 'ƒ',
                    text: n.title || n.id,
                    hint: hintBase + scoreText,
                    action: () => {
                        state.searchOpen = false;
                        state.expandedNodes.add(n.id);
                        navigate('explorer');
                        setTimeout(() => selectEntity(n.id), 150);
                    }
                };
            });
            
            renderResults([...filteredDefaults, ...nodeResults]);
        } catch (e) {
            console.error('Search error:', e);
            renderResults([...filteredDefaults, { icon: '⚠', text: 'Error searching nodes', hint: '', action: () => {} }]);
        }
    }, 300);
  });

  const footer = el('div', { class: 'search-footer' });
  footer.appendChild(el('span', {}, el('kbd', {}, '↑↓'), ' navigate'));
  footer.appendChild(el('span', {}, el('kbd', {}, '↵'), ' open'));
  footer.appendChild(el('span', {}, el('kbd', {}, 'esc'), ' close'));
  modal.appendChild(results);
  modal.appendChild(footer);
  overlay.appendChild(modal);

  // Auto-focus
  requestAnimationFrame(() => {
    const el = document.getElementById('global-search-input');
    if (el) el.focus();
  });

  return overlay;
}

// ─── Empty State ────────────────────────────────────────────────
function renderEmptyState(icon, title, desc, actionLabel, actionFn) {
  const empty = el('div', { class: 'empty-state' });
  empty.appendChild(el('div', { class: 'empty-state-icon', html: icon }));
  empty.appendChild(el('h3', {}, title));
  empty.appendChild(el('p', {}, desc));
  if (actionLabel) {
    empty.appendChild(el('button', { class: 'btn btn-primary', onClick: actionFn }, actionLabel));
  }
  return empty;
}

// ─── Data Loaders ───────────────────────────────────────────────
async function loadRepos() {
  try {
    const data = await api('/repos');
    state.repos = data.repos || [];
  } catch {
    state.repos = [];
  }
}

async function openRepo(repo) {
  state.activeRepo = { owner: repo.owner, name: repo.name, path: repo.path };

  try {
    state.structure = await api('/structure');
  } catch { state.structure = null; }
  try {
    state.nodes = await api('/nodes');
  } catch { state.nodes = null; }

  state.chatMessages = [];

  // Load conversation history
  try {
    const convs = await api(`/chats/${repo.owner}/${repo.name}`);
    if (convs.conversations?.length > 0) {
      const latest = convs.conversations[0];
      const conv = await api(`/chat/${repo.owner}/${repo.name}/${latest.id}`);
      state.chatMessages = conv.messages || [];
    }
  } catch { }

  if (state.structure) {
    navigate('explorer');
  } else {
    navigate('home');
  }
}

// ─── Keyboard Shortcuts ────────────────────────────────────────
document.addEventListener('keydown', (e) => {
  // Ctrl+K or Cmd+K → search
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    state.searchOpen = !state.searchOpen;
    render();
  }
  // Escape → close search/modal
  if (e.key === 'Escape') {
    if (state.searchOpen) {
      state.searchOpen = false;
      render();
    } else if (state.modalOpen) {
      closeModal();
    }
  }
});

// ─── Boot ───────────────────────────────────────────────────────
render();


// ─── Graph View ─────────────────────────────────────────────────
function createResizer(targetId, isLeft) {
    const resizer = el('div', { 
        style: { width: '4px', cursor: 'col-resize', background: 'transparent', flexShrink: 0, zIndex: 10, transition: 'background 0.2s' } 
    });
    resizer.onmouseenter = () => resizer.style.background = 'var(--accent)';
    resizer.onmouseleave = () => resizer.style.background = 'transparent';
    
    resizer.onmousedown = (e) => {
        e.preventDefault();
        const target = document.getElementById(targetId);
        if (!target) return;
        document.body.style.cursor = 'col-resize';
        const startX = e.clientX;
        const startWidth = parseInt(window.getComputedStyle(target).width, 10);
        
        const onMouseMove = (moveEvent) => {
            if (isLeft) {
                target.style.width = Math.max(150, startWidth + moveEvent.clientX - startX) + 'px';
            } else {
                target.style.width = Math.max(200, startWidth - (moveEvent.clientX - startX)) + 'px';
            }
        };
        const onMouseUp = () => {
            document.body.style.cursor = 'default';
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    };
    return resizer;
}

function renderGraphView() {
const container = el('div', { class: 'graph-3pane-layout', style: { display: 'flex', width: '100%', height: '100%' } });

if (!state.nodes || !state.nodes.nodes || state.nodes.nodes.length === 0) {
container.appendChild(renderEmptyState(Icons.cloud, 'No graph data', 'Parse a repository first to view its graph.', 'Add Repository', () => openAddRepoModal()));
return container;
}

// LEFT PANE (Tree)
const leftPane = el('div', { id: 'graph-left-pane', class: 'graph-left-pane', style: { width: '260px', borderRight: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', background: 'var(--bg-surface)', overflowY: 'auto' } });
const searchDiv = el('div', { class: 'explorer-search', style: { padding: '10px' } });
searchDiv.appendChild(el('span', { class: 'explorer-search-icon', html: Icons.search }));
const searchInput = el('input', {
class: 'input',
placeholder: 'Search summaries...',
style: { paddingLeft: '32px', cursor: 'pointer' },
value: '',
readOnly: true
});
searchInput.addEventListener('click', () => {
    state.searchOpen = true;
    render();
});
searchDiv.appendChild(searchInput);
leftPane.appendChild(searchDiv);
const treeContainer = el('div', { id: 'tree-container', style: { padding: '0 10px' } });
renderTreeInto(treeContainer, state.structure, state.explorerSearch);
leftPane.appendChild(treeContainer);

// CENTER PANE (Graph)
const centerPane = el('div', { class: 'graph-center-pane', style: { flex: 1, position: 'relative', background: 'var(--bg-root)' } });

// Add Graph Filters UI
if (!state.graphFilters) {
    state.graphFilters = { Folders: true, Files: true, Classes: true, Functions: true, Methods: true, Interfaces: true, Misc: true };
}
const filterContainer = el('div', {
    style: {
        position: 'absolute', top: '10px', left: '50%', transform: 'translateX(-50%)',
        background: 'var(--bg-surface)', border: '1px solid var(--border-color)',
        borderRadius: '6px', padding: '6px 12px', display: 'flex', gap: '12px', flexWrap: 'wrap',
        zIndex: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.5)', maxWidth: '90%', justifyContent: 'center'
    }
});

Object.keys(NODE_CATEGORIES).forEach(cat => {
    const isChecked = state.graphFilters[cat];
    const catColor = NODE_CATEGORIES[cat].color;
    
    const pill = el('div', {
        style: {
            display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer',
            opacity: isChecked ? 1 : 0.4, transition: 'opacity 0.2s',
            fontSize: '11px', fontWeight: '500', color: 'var(--text-primary)'
        },
        onClick: () => {
            state.graphFilters[cat] = !state.graphFilters[cat];
            render(); // re-render the whole graph view
        }
    });
    
    pill.appendChild(el('div', {
        style: { width: '10px', height: '10px', borderRadius: '2px', background: catColor }
    }));
    pill.appendChild(document.createTextNode(cat));
    filterContainer.appendChild(pill);
});
centerPane.appendChild(filterContainer);

const toggleLeftBtn = el('button', { 
    class: 'btn btn-icon', 
    style: { position: 'absolute', top: '10px', left: '10px', zIndex: 10, background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: '4px' },
    html: Icons.menu || '☰' 
});
toggleLeftBtn.onclick = () => {
    const pane = document.getElementById('graph-left-pane');
    if (pane) {
        pane.style.display = pane.style.display === 'none' ? 'flex' : 'none';
    }
};
centerPane.appendChild(toggleLeftBtn);

const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
svg.id = 'd3-svg-canvas';
svg.style.width = '100%';
svg.style.height = '100%';
centerPane.appendChild(svg);

// RIGHT PANE (Inspector)
const rightPane = el('div', { id: 'inspector-container', class: 'graph-right-pane', style: { width: '300px', borderLeft: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', background: 'var(--bg-surface)', padding: '16px', overflowY: 'auto' } });

container.appendChild(leftPane);
container.appendChild(createResizer('graph-left-pane', true));
container.appendChild(centerPane);
container.appendChild(createResizer('inspector-container', false));
container.appendChild(rightPane);

// Initialize D3 graph on next tick
setTimeout(() => {
    initD3Graph(svg);
    updateInspector();
}, 0);

return container;
}

function selectEntity(id) {
    state.selectedId = id;
    if (state.view === 'graph') {
        updateInspector();
        highlightNodeInGraph(id);
    }
}

function updateInspector() {
    const container = document.getElementById('inspector-container');
    if (!container) return;
    container.innerHTML = '';
    
    if (!state.selectedId) {
        container.appendChild(el('div', { class: 'text-secondary text-center', style: { marginTop: '50px' } }, 'Select a node to view details'));
        return;
    }
    
    // Find node in state
    let treeTarget = null;
    let nodeTarget = null;
    let isFile = false;
    
    // Try finding in structure
    const findInTree = (n) => {
        if (n.id === state.selectedId) return n;
        for (const c of (n.children || [])) {
            const found = findInTree(c);
            if (found) return found;
        }
        return null;
    };
    if (state.structure) {
        treeTarget = findInTree(state.structure);
    }
    
    // Try finding in nodes if not found
    if (state.nodes && state.nodes.nodes) {
        nodeTarget = state.nodes.nodes.find(n => n.id === state.selectedId);
    }
    
    const target = { ...(treeTarget || {}), ...(nodeTarget || {}) };
    
    if (!treeTarget && !nodeTarget) {
        container.appendChild(el('div', { class: 'text-secondary text-center', style: { marginTop: '50px' } }, 'Node not found'));
        return;
    }
    
    isFile = target.type === 'file' || target.node_type === 'file';
    
    container.appendChild(el('h3', { style: { marginBottom: '8px', wordBreak: 'break-all' } }, target.name || target.title || 'Unknown'));
    container.appendChild(el('div', { class: 'text-xs text-secondary', style: { marginBottom: '16px' } }, target.path || ''));
    
    container.appendChild(el('div', { class: 'text-sm mb-2' }, el('strong', {}, 'Type: '), el('span', {}, target.type || target.node_type || 'Unknown')));
    
    container.appendChild(el('h4', { style: { marginTop: '16px', marginBottom: '8px' } }, 'Summary'));
    if (target.summary) {
        container.appendChild(el('div', { class: 'text-sm text-secondary' }, target.summary));
    } else {
        container.appendChild(el('div', { class: 'text-sm text-secondary', style: { fontStyle: 'italic' } }, 'No summary available for this node.'));
    }
    
    // Dependencies
    if (isFile && state.edges && state.edges.edges) {
        const outEdges = state.edges.edges.filter(e => e.source_file_id === target.id);
        const inEdges = state.edges.edges.filter(e => e.target_file_id === target.id);
        
        if (outEdges.length > 0) {
            container.appendChild(el('h4', { style: { marginTop: '16px', marginBottom: '8px' } }, 'Imports'));
            outEdges.forEach(e => {
                container.appendChild(el('div', { class: 'text-xs text-secondary mb-1' }, e.target_path || e.target_file_id));
            });
        }
        if (inEdges.length > 0) {
            container.appendChild(el('h4', { style: { marginTop: '16px', marginBottom: '8px' } }, 'Imported by'));
            inEdges.forEach(e => {
                container.appendChild(el('div', { class: 'text-xs text-secondary mb-1' }, e.source_path || e.source_file_id));
            });
        }
    }
}

function highlightNodeInGraph(id) {
    if (typeof d3 === 'undefined') return;
    const svg = d3.select('#d3-svg-canvas');
    if (svg.empty()) return;
    svg.selectAll('circle').attr('stroke', '#000').attr('stroke-width', 1.5);
    svg.selectAll('circle').filter(d => d.id === id).attr('stroke', 'var(--c-primary)').attr('stroke-width', 4);
    
    // Auto-pan to the selected node
    const nodeData = svg.selectAll('g.node').data().find(d => d.id === id);
    const zoomBehavior = svg.node().__zoomBehavior;
    if (nodeData && zoomBehavior && typeof nodeData.x === 'number') {
        const svgEl = svg.node();
        const cw = svgEl.clientWidth || 800;
        const ch = svgEl.clientHeight || 600;
        const currentTransform = d3.zoomTransform(svgEl);
        
        const targetX = (cw / 2) - (nodeData.x * currentTransform.k);
        const targetY = (ch / 2) - (nodeData.y * currentTransform.k);
        
        svg.transition().duration(750).call(
            zoomBehavior.transform,
            d3.zoomIdentity.translate(targetX, targetY).scale(currentTransform.k)
        );
    }
}

const NODE_CATEGORIES = {
    Folders: { color: '#E59866', keys: ['folder', 'directory'] },
    Files: { color: '#85C1E9', keys: ['file', 'module', 'repository'] },
    Classes: { color: '#48C9B0', keys: ['class_definition', 'class_declaration', 'class'] },
    Functions: { color: '#58D68D', keys: ['function_definition', 'function_declaration', 'arrow_function', 'function'] },
    Methods: { color: '#52BE80', keys: ['method_definition', 'method_declaration', 'method'] },
    Interfaces: { color: '#EB984E', keys: ['interface_declaration', 'interface', 'struct_declaration', 'type_alias_declaration'] },
    Misc: { color: '#AF7AC5', keys: [] }
};

function getNodeCategory(group) {
    for (const [catName, catData] of Object.entries(NODE_CATEGORIES)) {
        if (catName === 'Misc') continue;
        if (catData.keys.includes(group)) return catName;
    }
    return 'Misc';
}

function initD3Graph(svgEl) {
if (typeof d3 === 'undefined') return;
const width = svgEl.clientWidth || 800;
const height = svgEl.clientHeight || 600;

const svg = d3.select(svgEl);
svg.selectAll('*').remove();

const g = svg.append('g');
const zoom = d3.zoom()
  .scaleExtent([0.1, 4])
  .on('zoom', (event) => {
      g.attr('transform', event.transform);
      const scale = event.transform.k;
      const opacity = scale < 0.9 ? 0 : Math.min(1, (scale - 0.9) * 2.5);
      g.selectAll('text').style('opacity', opacity);
  });
svg.call(zoom);
svg.node().__zoomBehavior = zoom; // Store for external panning

// Initial scale
svg.call(zoom.transform, d3.zoomIdentity.scale(0.8));

const nodesMap = new Map();
const nodes = [];

state.nodes.nodes.forEach(n => {
    const rawGroup = n.node_type || 'node';
    const cat = getNodeCategory(rawGroup);
    if (!state.graphFilters || !state.graphFilters[cat]) return;
    
    const nodeData = { id: n.id, title: n.title || n.node_type || 'Unknown', group: cat, radius: 8 };
    nodesMap.set(n.id, nodeData);
    nodes.push(nodeData);
});

const links = [];

const addTreeNodes = (n) => {
    if (!n) return;
    const rawGroup = n.type || 'folder';
    const cat = getNodeCategory(rawGroup);
    
    // Check if the current node is visible
    if (state.graphFilters && state.graphFilters[cat]) {
        const isFile = n.type === 'file';
        const nodeData = { id: n.id, title: n.name || n.id, group: cat, radius: isFile ? 10 : 14 };
        if (!nodesMap.has(n.id)) {
            nodesMap.set(n.id, nodeData);
            nodes.push(nodeData);
        }
    }
    
    // Always process children so we can render them even if parent is hidden,
    // though linking them requires the parent to be visible.
    (n.children || []).forEach(c => {
        addTreeNodes(c);
        if (nodesMap.has(n.id) && nodesMap.has(c.id)) {
            links.push({ source: n.id, target: c.id, value: 2 });
        }
    });
};
if (state.structure) {
    addTreeNodes(state.structure);
}

if (state.edges && state.edges.edges) {
    state.edges.edges.forEach(e => {
        if (nodesMap.has(e.source_file_id) && nodesMap.has(e.target_file_id)) {
            links.push({
                source: e.source_file_id,
                target: e.target_file_id,
                value: 1
            });
        }
    });
}

state.nodes.nodes.forEach(n => {
    if (n.parent_id && nodesMap.has(n.parent_id) && nodesMap.has(n.id)) {
        links.push({
            source: n.parent_id,
            target: n.id,
            value: 2
        });
    }
});

const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

const simulation = d3.forceSimulation(nodes)
.force('link', d3.forceLink(links).id(d => d.id).distance(80).strength(0.5))
.force('charge', d3.forceManyBody().strength(-300))
.force('center', d3.forceCenter(width / 2, height / 2))
.force('collide', d3.forceCollide().radius(20).iterations(3));

const link = g.append('g')
.attr('stroke', 'rgba(255, 255, 255, 0.35)')
.attr('stroke-opacity', 0.8)
.selectAll('line')
.data(links)
.join('line')
.attr('stroke-width', d => Math.max(1.5, Math.sqrt(d.value) * 1.5));

const node = g.append('g')
.selectAll('g.node')
.data(nodes)
.join('g')
.attr('class', 'node')
.call(drag(simulation))
.on('click', (event, d) => {
    selectEntity(d.id);
    const tc = document.getElementById('tree-container');
    if (tc) renderTreeInto(tc, state.structure, state.explorerSearch);
});

node.append('circle')
.attr('r', d => d.radius)
.attr('fill', d => NODE_CATEGORIES[d.group]?.color || NODE_CATEGORIES.Misc.color)
.attr('stroke', '#000')
.attr('stroke-width', 1.5);

node.append('text')
.text(d => {
    const s = d.title || d.name || '';
    return s.length > 25 ? s.substring(0, 24) + '...' : s;
})
.attr('dx', d => d.radius + 5)
.attr('dy', 4)
.style('font-size', '11px')
.style('fill', 'var(--text-secondary)')
.style('pointer-events', 'none')
.style('text-shadow', '0 1px 3px rgba(0,0,0,0.8)');

node.append('title').text(d => d.title);

simulation.on('tick', () => {
link.attr('x1', d => d.source.x)
    .attr('y1', d => d.source.y)
    .attr('x2', d => d.target.x)
    .attr('y2', d => d.target.y);
node.attr('transform', d => `translate(${d.x},${d.y})`);
});

function drag(simulation) {
function dragstarted(event) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  event.subject.fx = event.subject.x;
  event.subject.fy = event.subject.y;
}
function dragged(event) {
  event.subject.fx = event.x;
  event.subject.fy = event.y;
}
function dragended(event) {
  if (!event.active) simulation.alphaTarget(0);
  event.subject.fx = null;
  event.subject.fy = null;
}
return d3.drag()
  .on('start', dragstarted)
  .on('drag', dragged)
  .on('end', dragended);
}

if (state.selectedId) {
    highlightNodeInGraph(state.selectedId);
}
}
