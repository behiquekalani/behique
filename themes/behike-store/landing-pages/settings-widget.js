// Behike Settings Widget - Font size, color themes
// Inject into any landing page

(function() {
  // ── Theme definitions ──
  const themes = {
    midnight: {
      name: 'Midnight',
      icon: '🌙',
      black: '#000000',
      accent: '#0A84FF',
      light: '#F5F5F7',
      secondaryBg: '#1D1D1F',
      gray: '#86868B',
      navBg: 'rgba(0,0,0,0.8)',
      cardBg: 'rgba(29,29,31,0.6)',
      border: 'rgba(245,245,247,0.08)',
    },
    snow: {
      name: 'Snow',
      icon: '☀️',
      black: '#FFFFFF',
      accent: '#0066CC',
      light: '#1D1D1F',
      secondaryBg: '#F5F5F7',
      gray: '#6E6E73',
      navBg: 'rgba(255,255,255,0.85)',
      cardBg: 'rgba(245,245,247,0.8)',
      border: 'rgba(0,0,0,0.08)',
    },
    ocean: {
      name: 'Ocean',
      icon: '🌊',
      black: '#0A1628',
      accent: '#00D4AA',
      light: '#E0F7F0',
      secondaryBg: '#112240',
      gray: '#8892B0',
      navBg: 'rgba(10,22,40,0.9)',
      cardBg: 'rgba(17,34,64,0.7)',
      border: 'rgba(0,212,170,0.12)',
    },
    sunset: {
      name: 'Sunset',
      icon: '🌅',
      black: '#1A0A1E',
      accent: '#FF6B6B',
      light: '#FFF0EC',
      secondaryBg: '#2D1233',
      gray: '#B08EA8',
      navBg: 'rgba(26,10,30,0.9)',
      cardBg: 'rgba(45,18,51,0.7)',
      border: 'rgba(255,107,107,0.12)',
    },
    forest: {
      name: 'Forest',
      icon: '🌿',
      black: '#0B1A0B',
      accent: '#4ADE80',
      light: '#E8F5E8',
      secondaryBg: '#132613',
      gray: '#7DA67D',
      navBg: 'rgba(11,26,11,0.9)',
      cardBg: 'rgba(19,38,19,0.7)',
      border: 'rgba(74,222,128,0.12)',
    },
    royal: {
      name: 'Royal',
      icon: '👑',
      black: '#0D0A1A',
      accent: '#A78BFA',
      light: '#EDE9FE',
      secondaryBg: '#1E1635',
      gray: '#9B8EC4',
      navBg: 'rgba(13,10,26,0.9)',
      cardBg: 'rgba(30,22,53,0.7)',
      border: 'rgba(167,139,250,0.12)',
    },
    ember: {
      name: 'Ember',
      icon: '🔥',
      black: '#1A0C00',
      accent: '#FF9F43',
      light: '#FFF4E6',
      secondaryBg: '#2D1800',
      gray: '#C4956D',
      navBg: 'rgba(26,12,0,0.9)',
      cardBg: 'rgba(45,24,0,0.7)',
      border: 'rgba(255,159,67,0.12)',
    },
    candy: {
      name: 'Candy',
      icon: '🍬',
      black: '#FFF0F5',
      accent: '#FF1493',
      light: '#2D0A1E',
      secondaryBg: '#FFE0EB',
      gray: '#9B5072',
      navBg: 'rgba(255,240,245,0.9)',
      cardBg: 'rgba(255,224,235,0.7)',
      border: 'rgba(255,20,147,0.12)',
    },
  };

  // ── Font sizes ──
  const fontSizes = {
    small: { label: 'S', scale: 0.85 },
    medium: { label: 'M', scale: 1.0 },
    large: { label: 'L', scale: 1.15 },
    xl: { label: 'XL', scale: 1.3 },
  };

  // ── Load saved preferences ──
  const savedTheme = localStorage.getItem('behike-theme') || 'midnight';
  const savedSize = localStorage.getItem('behike-fontsize') || 'medium';

  // ── Apply theme ──
  function applyTheme(key) {
    const t = themes[key];
    if (!t) return;
    const r = document.documentElement.style;
    r.setProperty('--black', t.black);
    r.setProperty('--blue', t.accent);
    r.setProperty('--light', t.light);
    r.setProperty('--secondary-bg', t.secondaryBg);
    r.setProperty('--gray', t.gray);

    // Update nav background
    const nav = document.querySelector('nav');
    if (nav) nav.style.background = t.navBg;

    // Update card backgrounds
    document.querySelectorAll('.chapter-group, .stat-card, .faq-item, .pricing-card, .feature-card, .theme-card, .compare-table').forEach(el => {
      el.style.background = t.cardBg;
      el.style.borderColor = t.border;
    });

    // Update body
    document.body.style.background = t.black;
    document.body.style.color = t.light;

    // Update nav border
    if (nav) nav.style.borderBottomColor = t.border;

    // Update CTA buttons
    document.querySelectorAll('.nav-cta, .hero-cta, .pricing-cta, .cta-button').forEach(el => {
      el.style.background = t.accent;
    });

    // Update accent-colored text
    document.querySelectorAll('.hero h1 span, .hero-badge, .section-label, .price').forEach(el => {
      el.style.color = t.accent;
    });

    // Update hero badge border
    document.querySelectorAll('.hero-badge').forEach(el => {
      el.style.borderColor = t.accent + '4D';
    });

    // Mark active in panel
    document.querySelectorAll('.theme-dot').forEach(d => d.classList.remove('active'));
    const activeDot = document.querySelector(`.theme-dot[data-theme="${key}"]`);
    if (activeDot) activeDot.classList.add('active');

    localStorage.setItem('behike-theme', key);
  }

  // ── Apply font size ──
  function applyFontSize(key) {
    const s = fontSizes[key];
    if (!s) return;

    // Remove old size classes
    document.body.classList.remove('font-small', 'font-medium', 'font-large', 'font-xl');
    document.body.classList.add('font-' + key);

    // Apply zoom to scale everything proportionally (works with px values)
    document.body.style.zoom = s.scale;
    // Firefox doesn't support zoom, use transform as fallback
    if (!('zoom' in document.body.style)) {
      document.body.style.transform = 'scale(' + s.scale + ')';
      document.body.style.transformOrigin = 'top center';
    }

    document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
    const activeBtn = document.querySelector(`.size-btn[data-size="${key}"]`);
    if (activeBtn) activeBtn.classList.add('active');

    localStorage.setItem('behike-fontsize', key);
  }

  // ── Build widget HTML ──
  function createWidget() {
    const widget = document.createElement('div');
    widget.id = 'behike-settings';
    widget.innerHTML = `
      <style>
        #behike-settings-toggle {
          position: fixed;
          bottom: 24px;
          right: 24px;
          z-index: 9999;
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: var(--blue, #0A84FF);
          border: none;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.4);
          transition: transform 0.2s, box-shadow 0.2s;
        }
        #behike-settings-toggle:hover {
          transform: scale(1.1);
          box-shadow: 0 6px 28px rgba(0,0,0,0.5);
        }
        #behike-settings-panel {
          position: fixed;
          bottom: 84px;
          right: 24px;
          z-index: 9998;
          background: rgba(20,20,20,0.95);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border-radius: 16px;
          padding: 20px;
          width: 280px;
          border: 1px solid rgba(255,255,255,0.1);
          box-shadow: 0 8px 40px rgba(0,0,0,0.6);
          display: none;
          animation: slideUp 0.25s ease-out;
        }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        #behike-settings-panel.open { display: block; }
        .settings-title {
          font-size: 13px;
          font-weight: 600;
          color: #F5F5F7;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          margin-bottom: 12px;
        }
        .settings-section {
          margin-bottom: 16px;
        }
        .settings-label {
          font-size: 11px;
          color: #86868B;
          text-transform: uppercase;
          letter-spacing: 0.06em;
          margin-bottom: 8px;
        }
        .theme-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 8px;
        }
        .theme-dot {
          width: 100%;
          aspect-ratio: 1;
          border-radius: 10px;
          border: 2px solid transparent;
          cursor: pointer;
          transition: transform 0.15s, border-color 0.15s;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
          position: relative;
        }
        .theme-dot:hover { transform: scale(1.1); }
        .theme-dot.active { border-color: #F5F5F7; }
        .theme-dot::after {
          content: attr(data-name);
          position: absolute;
          bottom: -16px;
          font-size: 9px;
          color: #86868B;
          white-space: nowrap;
        }
        .size-row {
          display: flex;
          gap: 8px;
        }
        .size-btn {
          flex: 1;
          padding: 8px 0;
          border-radius: 8px;
          border: 1px solid rgba(255,255,255,0.15);
          background: transparent;
          color: #F5F5F7;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.15s, border-color 0.15s;
        }
        .size-btn:hover { background: rgba(255,255,255,0.08); }
        .size-btn.active {
          background: var(--blue, #0A84FF);
          border-color: var(--blue, #0A84FF);
          color: #fff;
        }
      </style>
      <button id="behike-settings-toggle" aria-label="Settings">⚙️</button>
      <div id="behike-settings-panel">
        <div class="settings-title">Settings</div>
        <div class="settings-section">
          <div class="settings-label">Theme</div>
          <div class="theme-grid">
            ${Object.entries(themes).map(([key, t]) =>
              `<div class="theme-dot" data-theme="${key}" data-name="${t.name}" style="background: ${t.black}; box-shadow: inset 0 0 0 4px ${t.accent};" title="${t.name}">${t.icon}</div>`
            ).join('')}
          </div>
        </div>
        <div class="settings-section" style="margin-top: 28px;">
          <div class="settings-label">Font Size</div>
          <div class="size-row">
            ${Object.entries(fontSizes).map(([key, s]) =>
              `<button class="size-btn" data-size="${key}">${s.label}</button>`
            ).join('')}
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(widget);

    // Toggle panel
    document.getElementById('behike-settings-toggle').addEventListener('click', () => {
      document.getElementById('behike-settings-panel').classList.toggle('open');
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      const panel = document.getElementById('behike-settings-panel');
      const toggle = document.getElementById('behike-settings-toggle');
      if (!panel.contains(e.target) && !toggle.contains(e.target)) {
        panel.classList.remove('open');
      }
    });

    // Theme dots
    document.querySelectorAll('.theme-dot').forEach(dot => {
      dot.addEventListener('click', () => applyTheme(dot.dataset.theme));
    });

    // Size buttons
    document.querySelectorAll('.size-btn').forEach(btn => {
      btn.addEventListener('click', () => applyFontSize(btn.dataset.size));
    });
  }

  // ── Init ──
  document.addEventListener('DOMContentLoaded', () => {
    createWidget();
    applyTheme(savedTheme);
    applyFontSize(savedSize);
  });
})();
