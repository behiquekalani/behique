#!/usr/bin/env python3
"""
BEHIQUE BLUEPRINT GENERATOR V2
Generates multi-page business blueprint HTML documents.
Architectural schematic aesthetic. Dark, clean, dense, professional.

Usage:
    python3 blueprint_v2.py data.json                     # midnight theme (default)
    python3 blueprint_v2.py data.json --theme carbon      # specific theme
    python3 blueprint_v2.py data.json --all-themes        # generate all 4 themes
    python3 blueprint_v2.py data.json --section marketing  # single section only

No external dependencies. Pure Python. Self-contained HTML output.
"""

import json
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# TRANSLATIONS
# ---------------------------------------------------------------------------

TRANSLATIONS = {
    "en": {
        "overview": "OVERVIEW",
        "growth": "GROWTH",
        "offer": "OFFER",
        "retention": "RETENTION",
        "business_blueprint": "Business Blueprint",
        "version_generated": "Version {version} / Generated {date}",
        "rollout_phases": "ROLLOUT PHASES",
        "phase": "PHASE",
        "tools_software": "TOOLS &amp; SOFTWARE ASSETS",
        "dept_blueprints": "DEPARTMENT BLUEPRINTS",
        "sections_count": "{n} SECTIONS",
        "dept_blueprint": "DEPARTMENT BLUEPRINT",
        "the_north_star": "THE NORTH STAR",
        "the_framework": "THE FRAMEWORK",
        "the_workflow": "THE WORKFLOW",
        "key_metrics": "KEY METRICS",
        "the_tech_stack": "THE TECH STACK",
        "the_asset_library": "THE ASSET LIBRARY",
        "global_guardrails": "GLOBAL GUARDRAILS",
        "agent_roles": "AGENT ROLES",
        "the_prompt_library": "THE PROMPT LIBRARY",
        "memory_system": "MEMORY SYSTEM",
        "safety_rails": "SAFETY RAILS",
        "architecture": "ARCHITECTURE",
        "strategy": "STRATEGY",
        "content_growth_wheel": "Content Growth Wheel",
        "growth_wheel_subtitle": "The five forces that drive sustainable content growth",
        "spoke_details": "SPOKE DETAILS",
        "framework": "FRAMEWORK",
        "offer_framework": "Offer Framework",
        "offer_subtitle": "From target market to deliverables. The complete offer construction.",
        "offer_checklist": "OFFER CHECKLIST",
        "retention_hooks": "Retention Hooks",
        "retention_subtitle": "Systems that keep customers engaged and coming back",
        "hook": "HOOK",
        "generated": "GENERATED",
        "theme_label": "THEME",
        "blueprint_v": "BLUEPRINT V{version}",
        "font_small": "Small text",
        "font_medium": "Medium text (default)",
        "font_large": "Large text",
        "font_xl": "Extra large text (accessibility)",
    },
    "es": {
        "overview": "RESUMEN",
        "growth": "CRECIMIENTO",
        "offer": "OFERTA",
        "retention": "RETENCI\u00d3N",
        "business_blueprint": "Plan de Negocio",
        "version_generated": "Versi\u00f3n {version} / Generado {date}",
        "rollout_phases": "FASES DE IMPLEMENTACI\u00d3N",
        "phase": "FASE",
        "tools_software": "HERRAMIENTAS Y SOFTWARE",
        "dept_blueprints": "DEPARTAMENTOS",
        "sections_count": "{n} SECCIONES",
        "dept_blueprint": "PLAN DEPARTAMENTAL",
        "the_north_star": "LA ESTRELLA NORTE",
        "the_framework": "EL MARCO",
        "the_workflow": "EL FLUJO DE TRABAJO",
        "key_metrics": "M\u00c9TRICAS CLAVE",
        "the_tech_stack": "STACK TECNOL\u00d3GICO",
        "the_asset_library": "BIBLIOTECA DE RECURSOS",
        "global_guardrails": "L\u00cdMITES GLOBALES",
        "agent_roles": "ROLES DE AGENTES",
        "the_prompt_library": "BIBLIOTECA DE PROMPTS",
        "memory_system": "SISTEMA DE MEMORIA",
        "safety_rails": "BARRERAS DE SEGURIDAD",
        "architecture": "ARQUITECTURA",
        "strategy": "ESTRATEGIA",
        "content_growth_wheel": "Rueda de Crecimiento de Contenido",
        "growth_wheel_subtitle": "Las cinco fuerzas que impulsan el crecimiento sostenible del contenido",
        "spoke_details": "DETALLES POR EJE",
        "framework": "MARCO",
        "offer_framework": "Marco de Oferta",
        "offer_subtitle": "Del mercado objetivo a los entregables. La construcci\u00f3n completa de la oferta.",
        "offer_checklist": "CHECKLIST DE OFERTA",
        "retention_hooks": "Ganchos de Retenci\u00f3n",
        "retention_subtitle": "Sistemas que mantienen a los clientes comprometidos y regresando",
        "hook": "GANCHO",
        "generated": "GENERADO",
        "theme_label": "TEMA",
        "blueprint_v": "PLAN V{version}",
        "font_small": "Texto peque\u00f1o",
        "font_medium": "Texto mediano (por defecto)",
        "font_large": "Texto grande",
        "font_xl": "Texto extra grande (accesibilidad)",
    },
    "pt": {
        "overview": "VIS\u00c3O GERAL",
        "growth": "CRESCIMENTO",
        "offer": "OFERTA",
        "retention": "RETEN\u00c7\u00c3O",
        "business_blueprint": "Plano de Neg\u00f3cio",
        "version_generated": "Vers\u00e3o {version} / Gerado {date}",
        "rollout_phases": "FASES DE IMPLEMENTA\u00c7\u00c3O",
        "phase": "FASE",
        "tools_software": "FERRAMENTAS E SOFTWARE",
        "dept_blueprints": "DEPARTAMENTOS",
        "sections_count": "{n} SE\u00c7\u00d5ES",
        "dept_blueprint": "PLANO DEPARTAMENTAL",
        "the_north_star": "A ESTRELA NORTE",
        "the_framework": "O FRAMEWORK",
        "the_workflow": "O FLUXO DE TRABALHO",
        "key_metrics": "M\u00c9TRICAS CHAVE",
        "the_tech_stack": "STACK TECNOL\u00d3GICO",
        "the_asset_library": "BIBLIOTECA DE RECURSOS",
        "global_guardrails": "LIMITES GLOBAIS",
        "agent_roles": "FUN\u00c7\u00d5ES DOS AGENTES",
        "the_prompt_library": "BIBLIOTECA DE PROMPTS",
        "memory_system": "SISTEMA DE MEM\u00d3RIA",
        "safety_rails": "BARREIRAS DE SEGURAN\u00c7A",
        "architecture": "ARQUITETURA",
        "strategy": "ESTRAT\u00c9GIA",
        "content_growth_wheel": "Roda de Crescimento de Conte\u00fado",
        "growth_wheel_subtitle": "As cinco for\u00e7as que impulsionam o crescimento sustent\u00e1vel do conte\u00fado",
        "spoke_details": "DETALHES POR EIXO",
        "framework": "FRAMEWORK",
        "offer_framework": "Framework de Oferta",
        "offer_subtitle": "Do mercado-alvo \u00e0s entregas. A constru\u00e7\u00e3o completa da oferta.",
        "offer_checklist": "CHECKLIST DA OFERTA",
        "retention_hooks": "Ganchos de Reten\u00e7\u00e3o",
        "retention_subtitle": "Sistemas que mant\u00eam os clientes engajados e voltando",
        "hook": "GANCHO",
        "generated": "GERADO",
        "theme_label": "TEMA",
        "blueprint_v": "PLANO V{version}",
        "font_small": "Texto pequeno",
        "font_medium": "Texto m\u00e9dio (padr\u00e3o)",
        "font_large": "Texto grande",
        "font_xl": "Texto extra grande (acessibilidade)",
    },
}

SUPPORTED_LANGS = list(TRANSLATIONS.keys())


# ---------------------------------------------------------------------------
# THEMES
# ---------------------------------------------------------------------------

THEMES = {
    "midnight": {
        "bg": "#0a0a0a",
        "bg_secondary": "#111111",
        "text": "#ffffff",
        "text_secondary": "#a0a0a0",
        "text_muted": "#666666",
        "border": "#333333",
        "border_light": "#222222",
        "accent": "#f0c040",
        "accent_secondary": "#d4a017",
        "card_bg": "#0f0f0f",
        "nav_bg": "rgba(10,10,10,0.95)",
        "hover": "#1a1a1a",
        "success": "#22c55e",
        "info": "#3b82f6",
    },
    "clean": {
        "bg": "#ffffff",
        "bg_secondary": "#f8f9fa",
        "text": "#1a1a1a",
        "text_secondary": "#6b7280",
        "text_muted": "#9ca3af",
        "border": "#e5e7eb",
        "border_light": "#f3f4f6",
        "accent": "#2563eb",
        "accent_secondary": "#1d4ed8",
        "card_bg": "#ffffff",
        "nav_bg": "rgba(255,255,255,0.95)",
        "hover": "#f3f4f6",
        "success": "#16a34a",
        "info": "#2563eb",
    },
    "navy": {
        "bg": "#0f172a",
        "bg_secondary": "#1e293b",
        "text": "#e2e8f0",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "border": "#334155",
        "border_light": "#1e293b",
        "accent": "#f59e0b",
        "accent_secondary": "#d97706",
        "card_bg": "#1e293b",
        "nav_bg": "rgba(15,23,42,0.95)",
        "hover": "#334155",
        "success": "#22c55e",
        "info": "#38bdf8",
    },
    "carbon": {
        "bg": "#111111",
        "bg_secondary": "#1a1a1a",
        "text": "#d4d4d4",
        "text_secondary": "#a3a3a3",
        "text_muted": "#737373",
        "border": "#2a2a2a",
        "border_light": "#1f1f1f",
        "accent": "#10b981",
        "accent_secondary": "#059669",
        "card_bg": "#171717",
        "nav_bg": "rgba(17,17,17,0.95)",
        "hover": "#262626",
        "success": "#10b981",
        "info": "#06b6d4",
    },
    "amber": {
        "bg": "#0c0a06",
        "bg_secondary": "#141008",
        "text": "#f5e6c8",
        "text_secondary": "#c4a97d",
        "text_muted": "#7a6543",
        "border": "#2a2010",
        "border_light": "#1e1808",
        "accent": "#f59e0b",
        "accent_secondary": "#d97706",
        "card_bg": "#110e06",
        "nav_bg": "rgba(12,10,6,0.95)",
        "hover": "#1e1808",
        "success": "#84cc16",
        "info": "#f59e0b",
    },
    "rose": {
        "bg": "#0c0608",
        "bg_secondary": "#140a0e",
        "text": "#f5e0e8",
        "text_secondary": "#c49aaa",
        "text_muted": "#7a5565",
        "border": "#2a1520",
        "border_light": "#1e0e18",
        "accent": "#f43f5e",
        "accent_secondary": "#e11d48",
        "card_bg": "#110810",
        "nav_bg": "rgba(12,6,8,0.95)",
        "hover": "#1e0e18",
        "success": "#fb7185",
        "info": "#f43f5e",
    },
    "ocean": {
        "bg": "#060c10",
        "bg_secondary": "#0a1420",
        "text": "#e0eef5",
        "text_secondary": "#7ab0d4",
        "text_muted": "#456580",
        "border": "#102a3a",
        "border_light": "#081e2e",
        "accent": "#06b6d4",
        "accent_secondary": "#0891b2",
        "card_bg": "#081018",
        "nav_bg": "rgba(6,12,16,0.95)",
        "hover": "#0a1a28",
        "success": "#22d3ee",
        "info": "#06b6d4",
    },
    "purple": {
        "bg": "#080610",
        "bg_secondary": "#0e0a1a",
        "text": "#e8e0f5",
        "text_secondary": "#a090c4",
        "text_muted": "#65557a",
        "border": "#1e152a",
        "border_light": "#140e20",
        "accent": "#a855f7",
        "accent_secondary": "#9333ea",
        "card_bg": "#0c0814",
        "nav_bg": "rgba(8,6,16,0.95)",
        "hover": "#140e20",
        "success": "#c084fc",
        "info": "#a855f7",
    },
}


# ---------------------------------------------------------------------------
# CSS GENERATION
# ---------------------------------------------------------------------------

def generate_css():
    """Generate all CSS. Theme colors via custom properties."""
    return """
/* ========================================================================
   BLUEPRINT V2 - CORE STYLES
   ======================================================================== */

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg: #0a0a0a;
    --bg-secondary: #111111;
    --text: #ffffff;
    --text-secondary: #a0a0a0;
    --text-muted: #666666;
    --border: #333333;
    --border-light: #222222;
    --accent: #f0c040;
    --accent-secondary: #d4a017;
    --card-bg: #0f0f0f;
    --nav-bg: rgba(10,10,10,0.95);
    --hover: #1a1a1a;
    --success: #22c55e;
    --info: #3b82f6;
    --font-family: -apple-system, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    --font-mono: 'SF Mono', 'Fira Code', 'Cascadia Code', 'JetBrains Mono', Consolas, monospace;
}

html { scroll-behavior: smooth; font-size: 14px; transition: font-size 0.3s ease; }
html.fs-small { font-size: 12px; }
html.fs-medium { font-size: 14px; }
html.fs-large { font-size: 18px; }
html.fs-xl { font-size: 22px; }

body {
    font-family: var(--font-family);
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ---- NAVIGATION ---- */

.bp-nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    background: var(--nav-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    padding: 0 1.5rem;
    height: 48px;
    display: flex;
    align-items: center;
    gap: 0;
}

.bp-nav-brand {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-right: 1rem;
    white-space: nowrap;
    flex-shrink: 0;
}

.bp-nav-links {
    display: flex;
    align-items: center;
    gap: 0;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
    flex: 1;
    min-width: 0;
}

.bp-nav-links::-webkit-scrollbar { display: none; }

.bp-nav-link {
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-secondary);
    text-decoration: none;
    padding: 0.85rem 0.6rem;
    white-space: nowrap;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
}

/* ---- FONT SIZE CONTROLS ---- */

.bp-font-controls {
    display: flex;
    align-items: center;
    gap: 2px;
    margin-left: 0.5rem;
    padding-left: 0.5rem;
    border-left: 1px solid var(--border);
    flex-shrink: 0;
}

.bp-font-controls span {
    font-size: 0.55rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-right: 2px;
}

.bp-font-btn {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    width: 24px;
    height: 24px;
    border-radius: 3px;
    cursor: pointer;
    font-family: var(--font-family);
    font-weight: 600;
    font-size: 0.6rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.bp-font-btn:hover {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--hover);
}

.bp-font-btn.active {
    border-color: var(--accent);
    color: var(--bg);
    background: var(--accent);
}

.bp-nav-link:hover {
    color: var(--text);
    border-bottom-color: var(--accent);
}

.bp-nav-link.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
}

.bp-nav-version {
    font-size: 0.55rem;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    font-family: var(--font-mono);
    margin-left: 0.5rem;
    white-space: nowrap;
    flex-shrink: 0;
}

/* ---- MAIN CONTENT ---- */

.bp-main { padding-top: 48px; }

.bp-section {
    padding: 4rem 2rem;
    border-bottom: 1px solid var(--border-light);
    scroll-margin-top: 48px;
}

/* ---- SECTION HEADERS ---- */

.bp-section-header {
    text-align: center;
    margin-bottom: 3rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--border);
}

.bp-section-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
}

.bp-section-name {
    font-size: 2rem;
    font-weight: 300;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 0.5rem;
}

.bp-section-subtitle {
    font-size: 0.8rem;
    color: var(--text-secondary);
    letter-spacing: 0.05em;
    max-width: 600px;
    margin: 0 auto;
}

.bp-section-line {
    width: 60px;
    height: 1px;
    background: var(--accent);
    margin: 1.5rem auto 0;
}

/* ---- GRID LAYOUTS ---- */

.bp-grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    max-width: 1400px;
    margin: 0 auto;
}

.bp-grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    max-width: 1400px;
    margin: 0 auto;
}

.bp-grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    max-width: 1400px;
    margin: 0 auto;
}

.bp-grid-6 {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 1rem;
    max-width: 1400px;
    margin: 0 auto;
}

/* ---- CARDS ---- */

.bp-card {
    border: 1px solid var(--border);
    background: var(--card-bg);
    padding: 1.5rem;
    position: relative;
}

.bp-card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border-light);
}

.bp-card-icon {
    font-size: 1.2rem;
    width: 2rem;
    text-align: center;
    flex-shrink: 0;
}

.bp-card-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-secondary);
}

.bp-card-number {
    font-size: 0.55rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    color: var(--accent);
    font-family: var(--font-mono);
}

.bp-card-title {
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 0.5rem;
}

.bp-card-text {
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.7;
}

/* ---- LISTS ---- */

.bp-list {
    list-style: none;
    padding: 0;
}

.bp-list li {
    font-size: 0.8rem;
    color: var(--text-secondary);
    padding: 0.4rem 0;
    padding-left: 1rem;
    position: relative;
    line-height: 1.5;
}

.bp-list li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0.75rem;
    width: 4px;
    height: 4px;
    background: var(--accent);
}

.bp-list-numbered li {
    padding-left: 1.5rem;
    counter-increment: bp-counter;
}

.bp-list-numbered li::before {
    content: counter(bp-counter, decimal-leading-zero);
    background: none;
    width: auto;
    height: auto;
    top: 0.4rem;
    font-size: 0.6rem;
    color: var(--accent);
    font-family: var(--font-mono);
    font-weight: 600;
}

.bp-list-numbered { counter-reset: bp-counter; }

/* ---- KEY-VALUE PAIRS ---- */

.bp-kv {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border-light);
    font-size: 0.8rem;
}

.bp-kv:last-child { border-bottom: none; }

.bp-kv-key {
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: 0.65rem;
    font-weight: 600;
}

.bp-kv-value {
    color: var(--text);
    text-align: right;
    font-weight: 500;
}

/* ---- TAGS / BADGES ---- */

.bp-tags { display: flex; flex-wrap: wrap; gap: 0.5rem; }

.bp-tag {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.3rem 0.75rem;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    background: var(--bg-secondary);
}

.bp-tag-accent {
    border-color: var(--accent);
    color: var(--accent);
}

/* ---- FLOW DIAGRAM ---- */

.bp-flow {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    padding: 1.5rem 0;
    flex-wrap: wrap;
}

.bp-flow-node {
    border: 1px solid var(--border);
    padding: 1rem 1.5rem;
    text-align: center;
    min-width: 140px;
    background: var(--card-bg);
    position: relative;
}

.bp-flow-node-label {
    font-size: 0.55rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.25rem;
}

.bp-flow-node-title {
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text);
}

.bp-flow-arrow {
    width: 40px;
    height: 1px;
    background: var(--border);
    position: relative;
    flex-shrink: 0;
}

.bp-flow-arrow::after {
    content: '';
    position: absolute;
    right: 0;
    top: -4px;
    width: 0;
    height: 0;
    border-left: 6px solid var(--border);
    border-top: 4px solid transparent;
    border-bottom: 4px solid transparent;
}

.bp-flow-arrow-accent { background: var(--accent); }
.bp-flow-arrow-accent::after { border-left-color: var(--accent); }

/* ---- PHASE TIMELINE ---- */

.bp-phases {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0;
    max-width: 1200px;
    margin: 0 auto 3rem;
    border: 1px solid var(--border);
}

.bp-phase {
    padding: 2rem;
    border-right: 1px solid var(--border);
    position: relative;
}

.bp-phase:last-child { border-right: none; }

.bp-phase-number {
    font-size: 0.55rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    color: var(--accent);
    font-family: var(--font-mono);
    margin-bottom: 0.75rem;
}

.bp-phase-title {
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 0.5rem;
}

.bp-phase-desc {
    font-size: 0.75rem;
    color: var(--text-secondary);
    line-height: 1.7;
    margin-bottom: 1rem;
}

.bp-phase-timeline {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    font-family: var(--font-mono);
}

/* ---- TOOLS GRID ---- */

.bp-tool {
    border: 1px solid var(--border);
    padding: 1rem;
    text-align: center;
    background: var(--card-bg);
    transition: border-color 0.2s;
}

.bp-tool:hover { border-color: var(--accent); }

.bp-tool-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.bp-tool-name {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text);
}

.bp-tool-category {
    font-size: 0.55rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.25rem;
}

/* ---- DEPARTMENT NAV CARDS ---- */

.bp-dept-card {
    border: 1px solid var(--border);
    padding: 1.5rem;
    background: var(--card-bg);
    text-decoration: none;
    display: block;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
}

.bp-dept-card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
}

.bp-dept-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--accent);
    opacity: 0;
    transition: opacity 0.2s;
}

.bp-dept-card:hover::before { opacity: 1; }

.bp-dept-card-icon {
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
}

.bp-dept-card-title {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 0.5rem;
}

.bp-dept-card-desc {
    font-size: 0.7rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

.bp-dept-card-count {
    font-size: 0.55rem;
    color: var(--text-muted);
    font-family: var(--font-mono);
    letter-spacing: 0.1em;
    margin-top: 0.75rem;
}

/* ---- DEPARTMENT BLUEPRINT LAYOUT ---- */

.bp-dept-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    max-width: 1400px;
    margin: 0 auto;
}

.bp-dept-col { display: flex; flex-direction: column; gap: 1.5rem; }

/* ---- GROWTH WHEEL ---- */

.bp-wheel {
    width: 500px;
    height: 500px;
    margin: 2rem auto;
    position: relative;
}

.bp-wheel-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 120px;
    height: 120px;
    border: 2px solid var(--accent);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg);
    z-index: 2;
}

.bp-wheel-center-text {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--accent);
}

.bp-wheel-spoke {
    position: absolute;
    width: 160px;
    text-align: center;
    z-index: 2;
}

.bp-wheel-spoke-title {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 0.25rem;
}

.bp-wheel-spoke-desc {
    font-size: 0.6rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

.bp-wheel-line {
    position: absolute;
    background: var(--border);
    transform-origin: center center;
    z-index: 1;
}

/* Spoke positions (5 spokes, evenly distributed) */
.bp-wheel-spoke:nth-child(2) { top: -10px; left: 50%; transform: translateX(-50%); }
.bp-wheel-spoke:nth-child(3) { top: 25%; right: -40px; }
.bp-wheel-spoke:nth-child(4) { bottom: 5%; right: -20px; }
.bp-wheel-spoke:nth-child(5) { bottom: 5%; left: -20px; }
.bp-wheel-spoke:nth-child(6) { top: 25%; left: -40px; }

/* Connecting lines */
.bp-wheel-line:nth-child(7) { top: 50%; left: 50%; width: 130px; height: 1px; transform: translateX(-50%) rotate(-90deg) translateY(-65px); }
.bp-wheel-line:nth-child(8) { top: 50%; left: 50%; width: 130px; height: 1px; transform: translateX(-50%) rotate(-18deg) translateY(-65px); }
.bp-wheel-line:nth-child(9) { top: 50%; left: 50%; width: 130px; height: 1px; transform: translateX(-50%) rotate(54deg) translateY(-65px); }
.bp-wheel-line:nth-child(10) { top: 50%; left: 50%; width: 130px; height: 1px; transform: translateX(-50%) rotate(126deg) translateY(-65px); }
.bp-wheel-line:nth-child(11) { top: 50%; left: 50%; width: 130px; height: 1px; transform: translateX(-50%) rotate(198deg) translateY(-65px); }

/* ---- FUNNEL ---- */

.bp-funnel {
    max-width: 700px;
    margin: 2rem auto;
}

.bp-funnel-step {
    border: 1px solid var(--border);
    padding: 1.25rem 2rem;
    margin-bottom: -1px;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    position: relative;
    background: var(--card-bg);
}

.bp-funnel-step::before {
    content: '';
    position: absolute;
    left: -1px;
    top: 0;
    bottom: 0;
    width: 3px;
    background: var(--accent);
}

.bp-funnel-num {
    font-size: 1.5rem;
    font-weight: 200;
    color: var(--accent);
    font-family: var(--font-mono);
    min-width: 2rem;
}

.bp-funnel-content { flex: 1; }

.bp-funnel-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.15rem;
}

.bp-funnel-text {
    font-size: 0.85rem;
    color: var(--text);
    font-weight: 500;
}

/* ---- ARCHITECTURE DIAGRAM ---- */

.bp-arch {
    max-width: 1000px;
    margin: 2rem auto;
}

.bp-arch-layer {
    border: 1px solid var(--border);
    padding: 1.5rem;
    margin-bottom: 0.75rem;
    position: relative;
}

.bp-arch-layer::after {
    content: '';
    position: absolute;
    bottom: -12px;
    left: 50%;
    transform: translateX(-50%);
    width: 1px;
    height: 12px;
    background: var(--border);
}

.bp-arch-layer:last-child::after { display: none; }

.bp-arch-layer-title {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.75rem;
}

.bp-arch-nodes {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.bp-arch-node {
    border: 1px solid var(--border);
    padding: 0.6rem 1rem;
    font-size: 0.7rem;
    color: var(--text-secondary);
    background: var(--bg);
}

/* ---- STAT BOX ---- */

.bp-stat {
    text-align: center;
    padding: 1.5rem;
    border: 1px solid var(--border);
    background: var(--card-bg);
}

.bp-stat-value {
    font-size: 2rem;
    font-weight: 200;
    color: var(--accent);
    font-family: var(--font-mono);
    margin-bottom: 0.25rem;
}

.bp-stat-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* ---- SEPARATOR ---- */

.bp-sep {
    border: none;
    border-top: 1px solid var(--border-light);
    margin: 2rem 0;
}

/* ---- CONTAINER ---- */

.bp-container {
    max-width: 1400px;
    margin: 0 auto;
}

/* ---- SECTION LABEL (inline) ---- */

.bp-label {
    font-size: 0.55rem;
    font-weight: 700;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.bp-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ---- FOOTER ---- */

.bp-footer {
    text-align: center;
    padding: 3rem 2rem;
    border-top: 1px solid var(--border);
}

.bp-footer-text {
    font-size: 0.6rem;
    color: var(--text-muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.bp-footer-brand {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--accent);
    margin-top: 0.5rem;
}

/* ---- RESPONSIVE ---- */

@media (max-width: 1200px) {
    .bp-grid-6 { grid-template-columns: repeat(3, 1fr); }
    .bp-dept-layout { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
    .bp-phases { grid-template-columns: 1fr; }
    .bp-phase { border-right: none; border-bottom: 1px solid var(--border); }
    .bp-phase:last-child { border-bottom: none; }
    .bp-grid-2, .bp-grid-3, .bp-grid-4 { grid-template-columns: 1fr; }
    .bp-nav { padding: 0 0.75rem; }
    .bp-nav-brand { margin-right: 0.5rem; font-size: 0.6rem; }
    .bp-nav-link { padding: 0.85rem 0.4rem; font-size: 0.55rem; }
    .bp-nav-version { display: none; }
    .bp-section { padding: 2rem 1rem; }
    .bp-flow { flex-direction: column; }
    .bp-flow-arrow { width: 1px; height: 30px; }
    .bp-flow-arrow::after {
        right: -4px;
        top: auto;
        bottom: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid var(--border);
        border-bottom: none;
    }
    .bp-wheel { width: 300px; height: 300px; }
}

@media (max-width: 480px) {
    .bp-font-controls span { display: none; }
    .bp-nav-brand { letter-spacing: 0.1em; }
}

/* ---- PRINT ---- */

@media print {
    .bp-nav { display: none; }
    .bp-main { padding-top: 0; }
    .bp-section {
        min-height: auto;
        page-break-after: always;
        page-break-inside: avoid;
        border-bottom: none;
        padding: 1.5rem;
    }
    .bp-section:last-child { page-break-after: auto; }
    body { background: white; color: #1a1a1a; font-size: 10pt; }
    .bp-card, .bp-tool, .bp-dept-card, .bp-flow-node, .bp-arch-node, .bp-funnel-step, .bp-stat {
        border-color: #ccc;
        background: white;
    }
    .bp-section-name, .bp-card-title, .bp-flow-node-title, .bp-dept-card-title { color: #1a1a1a; }
    .bp-nav-link, .bp-tag, .bp-card-text, .bp-list li, .bp-kv-key, .bp-kv-value { color: #333; }
    .bp-accent-print { color: #333 !important; border-color: #333 !important; }
}
"""


# ---------------------------------------------------------------------------
# HTML BUILDER
# ---------------------------------------------------------------------------

class BlueprintBuilder:
    """Builds multi-page business blueprint HTML from JSON data."""

    def __init__(self, data, theme_name="midnight", lang="en"):
        self.data = data
        self.theme_name = theme_name
        self.theme = THEMES.get(theme_name, THEMES["midnight"])
        self.company = data.get("company", "COMPANY")
        self.version = data.get("version", "1.0")
        self.lang = lang
        self.t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    def _theme_vars(self):
        """Generate CSS custom property overrides for the selected theme."""
        lines = [":root {"]
        mapping = {
            "bg": "--bg", "bg_secondary": "--bg-secondary",
            "text": "--text", "text_secondary": "--text-secondary",
            "text_muted": "--text-muted", "border": "--border",
            "border_light": "--border-light", "accent": "--accent",
            "accent_secondary": "--accent-secondary", "card_bg": "--card-bg",
            "nav_bg": "--nav-bg", "hover": "--hover",
            "success": "--success", "info": "--info",
        }
        for key, var in mapping.items():
            if key in self.theme:
                lines.append(f"    {var}: {self.theme[key]};")
        lines.append("}")
        return "\n".join(lines)

    # --- Navigation ---

    def _build_nav(self, sections_only=None):
        t = self.t
        dept_keys = list(self.data.get("departments", {}).keys())
        links = [f'<a class="bp-nav-link" href="#overview">{t["overview"]}</a>']
        for key in dept_keys:
            if sections_only and key != sections_only:
                continue
            dept = self.data["departments"][key]
            label = dept.get("short_name", dept.get("title", key)).upper()
            links.append(f'<a class="bp-nav-link" href="#dept-{key}">{label}</a>')

        if not sections_only:
            if self.data.get("growth_wheel"):
                links.append(f'<a class="bp-nav-link" href="#growth-wheel">{t["growth"]}</a>')
            if self.data.get("offer_framework"):
                links.append(f'<a class="bp-nav-link" href="#offer">{t["offer"]}</a>')
            if self.data.get("retention_hooks"):
                links.append(f'<a class="bp-nav-link" href="#retention">{t["retention"]}</a>')

        return f"""
<nav class="bp-nav">
    <span class="bp-nav-brand">{self.company}</span>
    <div class="bp-nav-links">{''.join(links)}</div>
    <div class="bp-font-controls">
        <span>Aa</span>
        <button class="bp-font-btn" data-size="fs-small" title="{t['font_small']}">S</button>
        <button class="bp-font-btn active" data-size="fs-medium" title="{t['font_medium']}">M</button>
        <button class="bp-font-btn" data-size="fs-large" title="{t['font_large']}">L</button>
        <button class="bp-font-btn" data-size="fs-xl" title="{t['font_xl']}">XL</button>
    </div>
    <span class="bp-nav-version">V{self.version} / {self.theme_name.upper()}</span>
</nav>"""

    # --- Overview Page ---

    def _build_overview(self):
        t = self.t
        parts = []

        # Header
        version_line = t["version_generated"].format(version=self.version, date=datetime.now().strftime('%Y-%m-%d'))
        parts.append(f"""
<section class="bp-section" id="overview">
    <div class="bp-section-header">
        <div class="bp-section-title">{self.company}</div>
        <div class="bp-section-name">{t['business_blueprint']}</div>
        <div class="bp-section-subtitle">{version_line}</div>
        <div class="bp-section-line"></div>
    </div>""")

        # Phases
        phases = self.data.get("phases", [])
        if phases:
            parts.append(f'    <div class="bp-label">{t["rollout_phases"]}</div>')
            parts.append('    <div class="bp-phases">')
            for i, phase in enumerate(phases, 1):
                parts.append(f"""
        <div class="bp-phase">
            <div class="bp-phase-number">{t['phase']} {i:02d}</div>
            <div class="bp-phase-title">{_esc(phase.get('name', ''))}</div>
            <div class="bp-phase-desc">{_esc(phase.get('description', ''))}</div>
            <div class="bp-phase-timeline">{_esc(phase.get('timeline', ''))}</div>
        </div>""")
            parts.append('    </div>')

        # Tools
        tools = self.data.get("tools", [])
        if tools:
            parts.append('    <hr class="bp-sep">')
            parts.append(f'    <div class="bp-label">{t["tools_software"]}</div>')
            parts.append('    <div class="bp-grid-6">')
            for tool in tools:
                parts.append(f"""
        <div class="bp-tool">
            <div class="bp-tool-icon">{_esc(tool.get('icon', ''))}</div>
            <div class="bp-tool-name">{_esc(tool.get('name', ''))}</div>
            <div class="bp-tool-category">{_esc(tool.get('category', ''))}</div>
        </div>""")
            parts.append('    </div>')

        # Department navigation cards
        departments = self.data.get("departments", {})
        if departments:
            parts.append('    <hr class="bp-sep">')
            parts.append(f'    <div class="bp-label">{t["dept_blueprints"]}</div>')
            parts.append('    <div class="bp-grid-3">')
            dept_icons = {
                "marketing": "M", "sales": "S", "operations": "O",
                "finance": "F", "ai_automations": "A", "content": "C"
            }
            for key, dept in departments.items():
                icon = dept.get("icon", dept_icons.get(key, ""))
                sections_count = sum(1 for k in ["north_star", "framework", "tech_stack", "assets", "guardrails", "workflow"] if dept.get(k))
                count_label = t["sections_count"].format(n=sections_count)
                parts.append(f"""
        <a class="bp-dept-card" href="#dept-{key}">
            <div class="bp-dept-card-icon">{_esc(icon)}</div>
            <div class="bp-dept-card-title">{_esc(dept.get('title', key))}</div>
            <div class="bp-dept-card-desc">{_esc(dept.get('objective', ''))}</div>
            <div class="bp-dept-card-count">{count_label}</div>
        </a>""")
            parts.append('    </div>')

        # Stats row
        stats = self.data.get("stats", [])
        if stats:
            parts.append('    <hr class="bp-sep">')
            parts.append(f'    <div class="bp-grid-{min(len(stats), 4)}">')
            for stat in stats:
                parts.append(f"""
        <div class="bp-stat">
            <div class="bp-stat-value">{_esc(stat.get('value', ''))}</div>
            <div class="bp-stat-label">{_esc(stat.get('label', ''))}</div>
        </div>""")
            parts.append('    </div>')

        parts.append('</section>')
        return '\n'.join(parts)

    # --- Department Blueprint ---

    def _build_department(self, key, dept):
        t = self.t
        parts = []
        parts.append(f"""
<section class="bp-section" id="dept-{key}">
    <div class="bp-section-header">
        <div class="bp-section-title">{self.company} / {t['dept_blueprint']}</div>
        <div class="bp-section-name">{_esc(dept.get('title', key))}</div>
        <div class="bp-section-subtitle">{_esc(dept.get('objective', ''))}</div>
        <div class="bp-section-line"></div>
    </div>
    <div class="bp-dept-layout">
        <div class="bp-dept-col">""")

        # LEFT COLUMN: North Star + Framework/Workflow

        # North Star
        ns = dept.get("north_star")
        if ns:
            parts.append(self._card(
                "01", t["the_north_star"], ns.get("icon", ""),
                self._render_north_star(ns)
            ))

        # Framework
        fw = dept.get("framework")
        if fw:
            parts.append(self._card(
                "02", t["the_framework"], fw.get("icon", ""),
                self._render_framework(fw)
            ))

        # Workflow (if separate from framework)
        wf = dept.get("workflow")
        if wf:
            parts.append(self._card(
                "03", t["the_workflow"], wf.get("icon", ""),
                self._render_workflow(wf)
            ))

        # KPIs
        kpis = dept.get("kpis")
        if kpis:
            parts.append(self._card(
                "04", t["key_metrics"], "",
                self._render_kpis(kpis)
            ))

        parts.append('        </div>')
        parts.append('        <div class="bp-dept-col">')

        # RIGHT COLUMN: Tech Stack, Assets, Guardrails

        # Tech Stack
        ts = dept.get("tech_stack")
        if ts:
            parts.append(self._card(
                "05", t["the_tech_stack"], "",
                self._render_tech_stack(ts)
            ))

        # Assets
        assets = dept.get("assets")
        if assets:
            parts.append(self._card(
                "06", t["the_asset_library"], "",
                self._render_assets(assets)
            ))

        # Guardrails
        gr = dept.get("guardrails")
        if gr:
            parts.append(self._card(
                "07", t["global_guardrails"], "",
                self._render_list(gr)
            ))

        # Agent Roles (for AI section)
        agents = dept.get("agent_roles")
        if agents:
            parts.append(self._card(
                "08", t["agent_roles"], "",
                self._render_agents(agents)
            ))

        # Prompt Library (for AI section)
        prompts = dept.get("prompt_library")
        if prompts:
            parts.append(self._card(
                "09", t["the_prompt_library"], "",
                self._render_prompt_library(prompts)
            ))

        # Memory System (for AI section)
        memory = dept.get("memory_system")
        if memory:
            parts.append(self._card(
                "10", t["memory_system"], "",
                self._render_memory_system(memory)
            ))

        # Safety Rails (for AI section)
        safety = dept.get("safety_rails")
        if safety:
            parts.append(self._card(
                "11", t["safety_rails"], "",
                self._render_list(safety)
            ))

        parts.append('        </div>')
        parts.append('    </div>')

        # Architecture diagram (for AI section, full-width below columns)
        arch = dept.get("architecture")
        if arch:
            parts.append('    <hr class="bp-sep">')
            parts.append(f'    <div class="bp-label">{t["architecture"]}</div>')
            parts.append(self._render_architecture(arch))

        parts.append('</section>')
        return '\n'.join(parts)

    # --- Special Pages ---

    def _build_growth_wheel(self):
        t = self.t
        gw = self.data.get("growth_wheel")
        if not gw:
            return ""

        spokes = gw.get("spokes", [])
        center = gw.get("center", "GROWTH")

        parts = [f"""
<section class="bp-section" id="growth-wheel">
    <div class="bp-section-header">
        <div class="bp-section-title">{self.company} / {t['strategy']}</div>
        <div class="bp-section-name">{t['content_growth_wheel']}</div>
        <div class="bp-section-subtitle">{t['growth_wheel_subtitle']}</div>
        <div class="bp-section-line"></div>
    </div>
    <div class="bp-container">
        <div class="bp-wheel">
            <div class="bp-wheel-center">
                <span class="bp-wheel-center-text">{_esc(center)}</span>
            </div>"""]

        # Render spokes
        for spoke in spokes:
            parts.append(f"""
            <div class="bp-wheel-spoke">
                <div class="bp-wheel-spoke-title">{_esc(spoke.get('name', ''))}</div>
                <div class="bp-wheel-spoke-desc">{_esc(spoke.get('description', ''))}</div>
            </div>""")

        # Connecting lines
        for _ in range(min(len(spokes), 5)):
            parts.append('            <div class="bp-wheel-line"></div>')

        parts.append('        </div>')

        # Detailed breakdown below
        parts.append('        <hr class="bp-sep">')
        parts.append(f'        <div class="bp-label">{t["spoke_details"]}</div>')
        parts.append('        <div class="bp-grid-3">')
        for spoke in spokes:
            items_html = ""
            for item in spoke.get("items", []):
                items_html += f'<li>{_esc(item)}</li>'
            parts.append(f"""
            <div class="bp-card">
                <div class="bp-card-header">
                    <div class="bp-card-icon">{_esc(spoke.get('icon', ''))}</div>
                    <div>
                        <div class="bp-card-title">{_esc(spoke.get('name', ''))}</div>
                        <div class="bp-card-text">{_esc(spoke.get('description', ''))}</div>
                    </div>
                </div>
                <ul class="bp-list">{items_html}</ul>
            </div>""")
        parts.append('        </div>')
        parts.append('    </div>')
        parts.append('</section>')
        return '\n'.join(parts)

    def _build_offer_framework(self):
        t = self.t
        of = self.data.get("offer_framework")
        if not of:
            return ""

        parts = [f"""
<section class="bp-section" id="offer">
    <div class="bp-section-header">
        <div class="bp-section-title">{self.company} / {t['framework']}</div>
        <div class="bp-section-name">{t['offer_framework']}</div>
        <div class="bp-section-subtitle">{t['offer_subtitle']}</div>
        <div class="bp-section-line"></div>
    </div>
    <div class="bp-container">
        <div class="bp-funnel">"""]

        for i, step in enumerate(of.get("funnel", []), 1):
            parts.append(f"""
            <div class="bp-funnel-step">
                <div class="bp-funnel-num">{i}</div>
                <div class="bp-funnel-content">
                    <div class="bp-funnel-label">{_esc(step.get('label', ''))}</div>
                    <div class="bp-funnel-text">{_esc(step.get('value', ''))}</div>
                </div>
            </div>""")

        parts.append('        </div>')

        # Checklist
        checklist = of.get("checklist", [])
        if checklist:
            parts.append('        <hr class="bp-sep">')
            parts.append(f'        <div class="bp-label">{t["offer_checklist"]}</div>')
            parts.append('        <div class="bp-grid-2">')
            for item in checklist:
                parts.append(f"""
            <div class="bp-kv">
                <span class="bp-kv-key">{_esc(item.get('item', ''))}</span>
                <span class="bp-kv-value">{_esc(item.get('status', ''))}</span>
            </div>""")
            parts.append('        </div>')

        parts.append('    </div>')
        parts.append('</section>')
        return '\n'.join(parts)

    def _build_retention(self):
        t = self.t
        hooks = self.data.get("retention_hooks")
        if not hooks:
            return ""

        parts = [f"""
<section class="bp-section" id="retention">
    <div class="bp-section-header">
        <div class="bp-section-title">{self.company} / {t['retention']}</div>
        <div class="bp-section-name">{t['retention_hooks']}</div>
        <div class="bp-section-subtitle">{t['retention_subtitle']}</div>
        <div class="bp-section-line"></div>
    </div>
    <div class="bp-container">
        <div class="bp-grid-3">"""]

        for i, hook in enumerate(hooks, 1):
            items_html = ""
            for item in hook.get("tactics", []):
                items_html += f'<li>{_esc(item)}</li>'
            parts.append(f"""
            <div class="bp-card">
                <div class="bp-card-header">
                    <div class="bp-card-number">{t['hook']} {i:02d}</div>
                    <div class="bp-card-title">{_esc(hook.get('name', ''))}</div>
                </div>
                <div class="bp-card-text">{_esc(hook.get('description', ''))}</div>
                <ul class="bp-list" style="margin-top: 0.75rem;">{items_html}</ul>
            </div>""")

        parts.append('        </div>')
        parts.append('    </div>')
        parts.append('</section>')
        return '\n'.join(parts)

    # --- Card / Component Renderers ---

    def _card(self, number, title, icon, content):
        return f"""
            <div class="bp-card">
                <div class="bp-card-header">
                    <div class="bp-card-number">{number}</div>
                    <div class="bp-card-icon">{_esc(icon)}</div>
                    <div class="bp-card-label">{_esc(title)}</div>
                </div>
                {content}
            </div>"""

    def _render_north_star(self, ns):
        parts = []
        if ns.get("statement"):
            parts.append(f'<div class="bp-card-text" style="font-size:0.9rem;color:var(--text);font-weight:500;margin-bottom:1rem;">{_esc(ns["statement"])}</div>')
        items = ns.get("principles", [])
        if items:
            parts.append('<ul class="bp-list">')
            for item in items:
                parts.append(f'<li>{_esc(item)}</li>')
            parts.append('</ul>')
        return '\n'.join(parts)

    def _render_framework(self, fw):
        parts = []
        if fw.get("description"):
            parts.append(f'<div class="bp-card-text" style="margin-bottom:1rem;">{_esc(fw["description"])}</div>')

        steps = fw.get("steps", [])
        if steps:
            parts.append('<ul class="bp-list bp-list-numbered">')
            for step in steps:
                if isinstance(step, dict):
                    parts.append(f'<li><strong>{_esc(step.get("name", ""))}</strong> - {_esc(step.get("detail", ""))}</li>')
                else:
                    parts.append(f'<li>{_esc(step)}</li>')
            parts.append('</ul>')

        # Flow diagram if present
        flow = fw.get("flow")
        if flow:
            parts.append('<div class="bp-flow" style="margin-top:1rem;">')
            for i, node in enumerate(flow):
                if i > 0:
                    parts.append('<div class="bp-flow-arrow bp-flow-arrow-accent"></div>')
                parts.append(f"""
                <div class="bp-flow-node">
                    <div class="bp-flow-node-title">{_esc(node)}</div>
                </div>""")
            parts.append('</div>')

        return '\n'.join(parts)

    def _render_workflow(self, wf):
        parts = []
        if wf.get("description"):
            parts.append(f'<div class="bp-card-text" style="margin-bottom:1rem;">{_esc(wf["description"])}</div>')

        steps = wf.get("steps", [])
        if steps:
            parts.append('<div class="bp-flow">')
            for i, step in enumerate(steps):
                if i > 0:
                    parts.append('<div class="bp-flow-arrow bp-flow-arrow-accent"></div>')
                label = ""
                title = step
                if isinstance(step, dict):
                    label = step.get("label", "")
                    title = step.get("name", "")
                parts.append(f"""
                <div class="bp-flow-node">
                    <div class="bp-flow-node-label">{_esc(label)}</div>
                    <div class="bp-flow-node-title">{_esc(title)}</div>
                </div>""")
            parts.append('</div>')

        return '\n'.join(parts)

    def _render_kpis(self, kpis):
        parts = ['<div>']
        for kpi in kpis:
            if isinstance(kpi, dict):
                parts.append(f"""
                <div class="bp-kv">
                    <span class="bp-kv-key">{_esc(kpi.get('metric', ''))}</span>
                    <span class="bp-kv-value">{_esc(kpi.get('target', ''))}</span>
                </div>""")
            else:
                parts.append(f'<div class="bp-kv"><span class="bp-kv-value">{_esc(kpi)}</span></div>')
        parts.append('</div>')
        return '\n'.join(parts)

    def _render_tech_stack(self, ts):
        parts = ['<div class="bp-tags">']
        for tool in ts:
            if isinstance(tool, dict):
                name = tool.get("name", "")
                role = tool.get("role", "")
                parts.append(f'<span class="bp-tag bp-tag-accent" title="{_esc(role)}">{_esc(name)}</span>')
            else:
                parts.append(f'<span class="bp-tag">{_esc(tool)}</span>')
        parts.append('</div>')
        return '\n'.join(parts)

    def _render_assets(self, assets):
        parts = ['<ul class="bp-list">']
        for asset in assets:
            if isinstance(asset, dict):
                parts.append(f'<li><strong>{_esc(asset.get("name", ""))}</strong> - {_esc(asset.get("description", ""))}</li>')
            else:
                parts.append(f'<li>{_esc(asset)}</li>')
        parts.append('</ul>')
        return '\n'.join(parts)

    def _render_list(self, items):
        parts = ['<ul class="bp-list">']
        for item in items:
            parts.append(f'<li>{_esc(item)}</li>')
        parts.append('</ul>')
        return '\n'.join(parts)

    def _render_agents(self, agents):
        parts = []
        for agent in agents:
            parts.append(f"""
                <div style="border-bottom:1px solid var(--border-light);padding:0.75rem 0;">
                    <div style="font-size:0.75rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:var(--text);margin-bottom:0.25rem;">{_esc(agent.get('name', ''))}</div>
                    <div style="font-size:0.7rem;color:var(--text-secondary);">{_esc(agent.get('role', ''))}</div>
                    <div class="bp-tags" style="margin-top:0.5rem;">""")
            for tool in agent.get("tools", []):
                parts.append(f'<span class="bp-tag">{_esc(tool)}</span>')
            parts.append('</div></div>')
        return '\n'.join(parts)

    def _render_prompt_library(self, prompts):
        parts = []
        for category in prompts:
            if isinstance(category, dict):
                parts.append(f'<div style="margin-bottom:1rem;">')
                parts.append(f'<div style="font-size:0.6rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:var(--accent);margin-bottom:0.5rem;">{_esc(category.get("category", ""))}</div>')
                parts.append('<ul class="bp-list">')
                for prompt in category.get("prompts", []):
                    parts.append(f'<li>{_esc(prompt)}</li>')
                parts.append('</ul></div>')
            else:
                parts.append(f'<div class="bp-card-text">{_esc(category)}</div>')
        return '\n'.join(parts)

    def _render_memory_system(self, memory):
        parts = []
        if isinstance(memory, dict):
            if memory.get("description"):
                parts.append(f'<div class="bp-card-text" style="margin-bottom:1rem;">{_esc(memory["description"])}</div>')
            for layer in memory.get("layers", []):
                parts.append(f"""
                <div class="bp-kv">
                    <span class="bp-kv-key">{_esc(layer.get('file', ''))}</span>
                    <span class="bp-kv-value">{_esc(layer.get('purpose', ''))}</span>
                </div>""")
        elif isinstance(memory, list):
            return self._render_list(memory)
        return '\n'.join(parts)

    def _render_architecture(self, arch):
        parts = ['<div class="bp-arch">']
        for layer in arch.get("layers", []):
            parts.append(f"""
            <div class="bp-arch-layer">
                <div class="bp-arch-layer-title">{_esc(layer.get('name', ''))}</div>
                <div class="bp-arch-nodes">""")
            for node in layer.get("nodes", []):
                if isinstance(node, dict):
                    parts.append(f'<div class="bp-arch-node">{_esc(node.get("name", ""))}</div>')
                else:
                    parts.append(f'<div class="bp-arch-node">{_esc(node)}</div>')
            parts.append('</div></div>')
        parts.append('</div>')
        return '\n'.join(parts)

    # --- Footer ---

    def _build_footer(self):
        t = self.t
        bp_label = t["blueprint_v"].format(version=self.version)
        return f"""
<footer class="bp-footer">
    <div class="bp-footer-text">{t['generated']} {datetime.now().strftime('%Y-%m-%d %H:%M')} / {t['theme_label']}: {self.theme_name.upper()}</div>
    <div class="bp-footer-brand">{self.company} {bp_label}</div>
</footer>"""

    # --- Full Build ---

    def build(self, section_only=None):
        """Build the complete HTML document."""
        parts = [f"""<!DOCTYPE html>
<html lang="{self.lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{_esc(self.company)} {self.t['business_blueprint']} V{_esc(self.version)}</title>
    <style>
{generate_css()}
{self._theme_vars()}
    </style>
</head>
<body>
{self._build_nav(sections_only=section_only)}
<main class="bp-main">"""]

        departments = self.data.get("departments", {})

        if section_only:
            # Single section mode
            if section_only in departments:
                parts.append(self._build_department(section_only, departments[section_only]))
            else:
                parts.append(f'<section class="bp-section"><div class="bp-section-header"><div class="bp-section-name">Section "{section_only}" not found</div></div></section>')
        else:
            # Full build
            parts.append(self._build_overview())

            for key, dept in departments.items():
                parts.append(self._build_department(key, dept))

            parts.append(self._build_growth_wheel())
            parts.append(self._build_offer_framework())
            parts.append(self._build_retention())

        parts.append(self._build_footer())
        parts.append("""
</main>
<script>
// Highlight active nav link on scroll
(function() {
    var links = document.querySelectorAll('.bp-nav-link');
    var sections = [];
    links.forEach(function(link) {
        var id = link.getAttribute('href');
        if (id && id.startsWith('#')) {
            var el = document.querySelector(id);
            if (el) sections.push({ el: el, link: link });
        }
    });
    function onScroll() {
        var scrollY = window.scrollY + 100;
        var active = null;
        sections.forEach(function(s) {
            if (s.el.offsetTop <= scrollY) active = s;
        });
        links.forEach(function(l) { l.classList.remove('active'); });
        if (active) active.link.classList.add('active');
    }
    window.addEventListener('scroll', onScroll);
    onScroll();

    // --- Font Size Controls ---
    var fontBtns = document.querySelectorAll('.bp-font-btn');
    fontBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var size = this.getAttribute('data-size');
            document.documentElement.className = size;
            fontBtns.forEach(function(b) { b.classList.remove('active'); });
            this.classList.add('active');
            try { localStorage.setItem('bp-font-size', size); } catch(e) {}
        });
    });
    // Restore saved font size preference
    try {
        var saved = localStorage.getItem('bp-font-size');
        if (saved) {
            document.documentElement.className = saved;
            fontBtns.forEach(function(b) {
                b.classList.remove('active');
                if (b.getAttribute('data-size') === saved) b.classList.add('active');
            });
        }
    } catch(e) {}
})();
</script>
</body>
</html>""")

        return '\n'.join(parts)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _esc(text):
    """Escape HTML entities."""
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="BEHIQUE Blueprint Generator V2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 blueprint_v2.py data.json                     # midnight theme
  python3 blueprint_v2.py data.json --theme carbon      # carbon theme
  python3 blueprint_v2.py data.json --all-themes        # all 4 themes
  python3 blueprint_v2.py data.json --section marketing  # single dept
  python3 blueprint_v2.py data.json -o output.html      # custom output
        """
    )
    parser.add_argument("input", help="Path to JSON data file")
    parser.add_argument("--theme", choices=list(THEMES.keys()), default="midnight", help="Color theme (default: midnight)")
    parser.add_argument("--all-themes", action="store_true", help="Generate all 4 themes")
    parser.add_argument("--section", help="Generate only a single department section")
    parser.add_argument("--lang", choices=SUPPORTED_LANGS, default="en", help="Language for UI labels (default: en)")
    parser.add_argument("-o", "--output", help="Output file path (default: auto-generated)")

    args = parser.parse_args()

    # Load data
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    company = data.get("company", "blueprint").lower().replace(" ", "-")

    lang = args.lang

    if args.all_themes:
        # Generate all themes
        for theme_name in THEMES:
            builder = BlueprintBuilder(data, theme_name, lang=lang)
            html = builder.build(section_only=args.section)
            lang_suffix = f"-{lang}" if lang != "en" else ""
            out_name = args.output or f"{company}-blueprint-{theme_name}{lang_suffix}.html"
            if args.output and len(THEMES) > 1:
                base, ext = os.path.splitext(args.output)
                out_name = f"{base}-{theme_name}{ext}"
            out_path = Path(out_name)
            out_path.write_text(html, encoding="utf-8")
            print(f"  [{theme_name.upper()}] {out_path} ({len(html):,} bytes)")
        print(f"\nGenerated {len(THEMES)} theme variants.")
    else:
        # Single theme
        theme_name = data.get("theme", args.theme)
        if theme_name not in THEMES:
            theme_name = "midnight"
        builder = BlueprintBuilder(data, theme_name, lang=lang)
        html = builder.build(section_only=args.section)

        if args.output:
            out_path = Path(args.output)
        else:
            lang_suffix = f"-{lang}" if lang != "en" else ""
            suffix = f"-{args.section}" if args.section else ""
            out_path = Path(f"{company}-blueprint-{theme_name}{lang_suffix}{suffix}.html")

        out_path.write_text(html, encoding="utf-8")
        print(f"  Generated: {out_path} ({len(html):,} bytes)")
        print(f"  Theme: {theme_name}")
        if args.section:
            print(f"  Section: {args.section}")
        print(f"  Open in browser: file://{out_path.resolve()}")


if __name__ == "__main__":
    main()
