#!/usr/bin/env python3
"""
Blueprint Builder - Professional one-page business blueprint generator.
Generates self-contained HTML files styled as dark-mode architectural blueprints.

Usage:
    python3 blueprint.py data.json                    # midnight theme (default)
    python3 blueprint.py data.json --theme clean      # specific theme
    python3 blueprint.py data.json --all-themes       # all 5 variants
    python3 blueprint.py data.json --pdf              # also convert to PDF (requires weasyprint)
    python3 blueprint.py data.json -o output.html     # custom output path
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


THEMES = {
    "midnight": {
        "bg": "#0a0a0a",
        "text": "#ffffff",
        "text_muted": "#999999",
        "border": "#333333",
        "accent": "#f0c040",
        "accent_dim": "rgba(240, 192, 64, 0.08)",
        "section_bg": "rgba(255, 255, 255, 0.02)",
        "header_bg": "rgba(255, 255, 255, 0.04)",
    },
    "clean": {
        "bg": "#ffffff",
        "text": "#1a1a1a",
        "text_muted": "#6b7280",
        "border": "#dddddd",
        "accent": "#2563eb",
        "accent_dim": "rgba(37, 99, 235, 0.05)",
        "section_bg": "rgba(0, 0, 0, 0.01)",
        "header_bg": "rgba(0, 0, 0, 0.03)",
    },
    "navy": {
        "bg": "#0f172a",
        "text": "#e2e8f0",
        "text_muted": "#94a3b8",
        "border": "#334155",
        "accent": "#f59e0b",
        "accent_dim": "rgba(245, 158, 11, 0.08)",
        "section_bg": "rgba(255, 255, 255, 0.02)",
        "header_bg": "rgba(255, 255, 255, 0.04)",
    },
    "forest": {
        "bg": "#1a2e1a",
        "text": "#e8f0e8",
        "text_muted": "#9ab89a",
        "border": "#2d4a2d",
        "accent": "#d4a574",
        "accent_dim": "rgba(212, 165, 116, 0.08)",
        "section_bg": "rgba(255, 255, 255, 0.02)",
        "header_bg": "rgba(255, 255, 255, 0.04)",
    },
    "slate": {
        "bg": "#1e293b",
        "text": "#f1f5f9",
        "text_muted": "#94a3b8",
        "border": "#475569",
        "accent": "#f43f5e",
        "accent_dim": "rgba(244, 63, 94, 0.08)",
        "section_bg": "rgba(255, 255, 255, 0.02)",
        "header_bg": "rgba(255, 255, 255, 0.04)",
    },
}


def get_css(theme_name: str) -> str:
    t = THEMES[theme_name]
    return f"""
    :root {{
        --bg: {t["bg"]};
        --text: {t["text"]};
        --text-muted: {t["text_muted"]};
        --border: {t["border"]};
        --accent: {t["accent"]};
        --accent-dim: {t["accent_dim"]};
        --section-bg: {t["section_bg"]};
        --header-bg: {t["header_bg"]};
    }}

    @page {{
        size: letter landscape;
        margin: 0;
    }}

    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    html, body {{
        width: 100%;
        height: 100%;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        background: var(--bg);
        color: var(--text);
        font-size: 10px;
        line-height: 1.4;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    .blueprint {{
        width: 11in;
        min-height: 8.5in;
        max-height: 8.5in;
        margin: 0 auto;
        padding: 0.35in 0.4in 0.3in 0.4in;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        position: relative;
    }}

    /* Corner marks */
    .blueprint::before,
    .blueprint::after {{
        content: "";
        position: absolute;
        width: 12px;
        height: 12px;
        border-color: var(--border);
        border-style: solid;
    }}
    .blueprint::before {{
        top: 8px;
        left: 8px;
        border-width: 1px 0 0 1px;
    }}
    .blueprint::after {{
        top: 8px;
        right: 8px;
        border-width: 1px 1px 0 0;
    }}
    .corner-bl, .corner-br {{
        position: absolute;
        width: 12px;
        height: 12px;
        border-color: var(--border);
        border-style: solid;
    }}
    .corner-bl {{
        bottom: 8px;
        left: 8px;
        border-width: 0 0 1px 1px;
    }}
    .corner-br {{
        bottom: 8px;
        right: 8px;
        border-width: 0 1px 1px 0;
    }}

    /* Header */
    .header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid var(--border);
        padding: 8px 14px;
        margin-bottom: 10px;
        background: var(--header-bg);
    }}
    .header-left {{
        display: flex;
        align-items: baseline;
        gap: 12px;
    }}
    .header h1 {{
        font-size: 16px;
        font-weight: 800;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--accent);
    }}
    .header .subtitle {{
        font-size: 9px;
        color: var(--text-muted);
        letter-spacing: 1px;
        text-transform: uppercase;
    }}
    .header-right {{
        display: flex;
        align-items: center;
        gap: 16px;
        font-size: 8px;
        color: var(--text-muted);
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}
    .header-right .version {{
        color: var(--accent);
        font-weight: 700;
    }}

    /* Columns */
    .columns {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        flex: 1;
        min-height: 0;
    }}
    .column {{
        display: flex;
        flex-direction: column;
        gap: 8px;
        min-height: 0;
    }}

    /* Section */
    .section {{
        border: 1px solid var(--border);
        background: var(--section-bg);
        flex-shrink: 0;
    }}
    .section-header {{
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 5px 10px;
        border-bottom: 1px solid var(--border);
        background: var(--header-bg);
    }}
    .section-icon {{
        font-size: 10px;
        color: var(--accent);
        width: 14px;
        text-align: center;
    }}
    .section-title {{
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--accent);
    }}
    .section-body {{
        padding: 7px 10px;
    }}

    /* Content type: paragraph + items */
    .content-text {{
        font-size: 8.5px;
        color: var(--text-muted);
        line-height: 1.5;
        margin-bottom: 5px;
    }}
    .kv-list {{
        display: flex;
        flex-direction: column;
        gap: 3px;
    }}
    .kv-item {{
        display: flex;
        gap: 6px;
        font-size: 8.5px;
        line-height: 1.4;
    }}
    .kv-label {{
        color: var(--accent);
        font-weight: 600;
        white-space: nowrap;
        min-width: 60px;
    }}
    .kv-value {{
        color: var(--text);
    }}

    /* Subsections */
    .subsection {{
        margin-bottom: 5px;
    }}
    .subsection:last-child {{
        margin-bottom: 0;
    }}
    .subsection-title {{
        font-size: 8.5px;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 3px;
        letter-spacing: 0.5px;
    }}
    .subsection-items {{
        list-style: none;
        padding-left: 0;
    }}
    .subsection-items li {{
        font-size: 8px;
        color: var(--text-muted);
        padding: 1px 0 1px 10px;
        position: relative;
        line-height: 1.4;
    }}
    .subsection-items li::before {{
        content: "\\2022";
        position: absolute;
        left: 0;
        color: var(--accent);
        font-size: 7px;
    }}

    /* Grid */
    .grid {{
        display: grid;
        grid-template-columns: repeat(var(--grid-cols, 3), 1fr);
        gap: 5px;
    }}
    .grid-item {{
        border: 1px solid var(--border);
        padding: 5px 7px;
        text-align: center;
        background: var(--accent-dim);
    }}
    .grid-icon {{
        font-size: 12px;
        margin-bottom: 2px;
        display: block;
    }}
    .grid-label {{
        font-size: 7.5px;
        font-weight: 600;
        color: var(--text);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: block;
    }}
    .grid-desc {{
        font-size: 7px;
        color: var(--text-muted);
        margin-top: 1px;
        display: block;
    }}

    /* Checklist */
    .checklist {{
        display: flex;
        flex-direction: column;
        gap: 2px;
    }}
    .checklist-item {{
        display: flex;
        align-items: flex-start;
        gap: 5px;
        font-size: 8px;
        color: var(--text-muted);
        line-height: 1.4;
    }}
    .checkbox {{
        width: 9px;
        height: 9px;
        border: 1px solid var(--accent);
        flex-shrink: 0;
        margin-top: 1px;
    }}

    /* Metrics */
    .metrics {{
        display: grid;
        grid-template-columns: repeat(var(--metrics-cols, 3), 1fr);
        gap: 5px;
    }}
    .metric {{
        text-align: center;
        padding: 6px 4px;
        border: 1px solid var(--border);
        background: var(--accent-dim);
    }}
    .metric-value {{
        font-size: 16px;
        font-weight: 800;
        color: var(--accent);
        line-height: 1;
        margin-bottom: 2px;
    }}
    .metric-label {{
        font-size: 7px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .metric-sub {{
        font-size: 6.5px;
        color: var(--text-muted);
        opacity: 0.7;
        margin-top: 1px;
    }}

    /* Footer */
    .footer {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid var(--border);
        padding: 4px 14px;
        margin-top: 10px;
        font-size: 7.5px;
        color: var(--text-muted);
        letter-spacing: 1px;
        text-transform: uppercase;
        background: var(--header-bg);
    }}
    .footer-center {{
        color: var(--accent);
        font-weight: 600;
    }}

    /* Print */
    @media print {{
        html, body {{
            width: 11in;
            height: 8.5in;
        }}
        .blueprint {{
            width: 11in;
            min-height: 8.5in;
            max-height: 8.5in;
        }}
    }}
    """


def escape(text: str) -> str:
    """Escape HTML entities."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_section(section: dict) -> str:
    """Render a single section block."""
    icon = escape(section.get("icon", ""))
    title = escape(section.get("title", ""))

    parts = []
    parts.append('<div class="section">')
    parts.append(f'  <div class="section-header">')
    if icon:
        parts.append(f'    <span class="section-icon">{icon}</span>')
    parts.append(f'    <span class="section-title">{title}</span>')
    parts.append(f'  </div>')
    parts.append(f'  <div class="section-body">')

    # Content text
    if "content" in section:
        parts.append(f'    <p class="content-text">{escape(section["content"])}</p>')

    # Key-value items
    if "items" in section and isinstance(section["items"], list):
        first = section["items"][0] if section["items"] else None
        if first and isinstance(first, dict) and "label" in first:
            parts.append('    <div class="kv-list">')
            for item in section["items"]:
                label = escape(item.get("label", ""))
                value = escape(item.get("value", ""))
                parts.append(
                    f'      <div class="kv-item">'
                    f'<span class="kv-label">{label}</span>'
                    f'<span class="kv-value">{value}</span></div>'
                )
            parts.append("    </div>")

    # Subsections
    if "subsections" in section:
        for sub in section["subsections"]:
            parts.append('    <div class="subsection">')
            sub_title = escape(sub.get("title", ""))
            parts.append(f'      <div class="subsection-title">{sub_title}</div>')
            if "items" in sub:
                parts.append('      <ul class="subsection-items">')
                for item in sub["items"]:
                    parts.append(f"        <li>{escape(item)}</li>")
                parts.append("      </ul>")
            parts.append("    </div>")

    # Grid
    if "grid" in section:
        cols = section.get("grid_cols", 3)
        parts.append(f'    <div class="grid" style="--grid-cols: {cols}">')
        for g in section["grid"]:
            g_icon = escape(g.get("icon", ""))
            g_label = escape(g.get("label", ""))
            g_desc = escape(g.get("desc", ""))
            parts.append('      <div class="grid-item">')
            if g_icon:
                parts.append(f'        <span class="grid-icon">{g_icon}</span>')
            parts.append(f'        <span class="grid-label">{g_label}</span>')
            if g_desc:
                parts.append(f'        <span class="grid-desc">{g_desc}</span>')
            parts.append("      </div>")
        parts.append("    </div>")

    # Checklist
    if "checklist" in section:
        parts.append('    <div class="checklist">')
        for item in section["checklist"]:
            text = escape(item) if isinstance(item, str) else escape(item.get("text", ""))
            parts.append(
                f'      <div class="checklist-item">'
                f'<div class="checkbox"></div>'
                f'<span>{text}</span></div>'
            )
        parts.append("    </div>")

    # Metrics
    if "metrics" in section:
        cols = section.get("metrics_cols", 3)
        parts.append(f'    <div class="metrics" style="--metrics-cols: {cols}">')
        for m in section["metrics"]:
            val = escape(m.get("value", ""))
            label = escape(m.get("label", ""))
            sub = escape(m.get("sub", ""))
            parts.append('      <div class="metric">')
            parts.append(f'        <div class="metric-value">{val}</div>')
            parts.append(f'        <div class="metric-label">{label}</div>')
            if sub:
                parts.append(f'        <div class="metric-sub">{sub}</div>')
            parts.append("      </div>")
        parts.append("    </div>")

    parts.append("  </div>")
    parts.append("</div>")
    return "\n".join(parts)


def render_blueprint(data: dict, theme_name: str) -> str:
    """Render the full HTML blueprint."""
    title = escape(data.get("title", "BLUEPRINT"))
    subtitle = escape(data.get("subtitle", ""))
    author = escape(data.get("author", ""))
    version = escape(data.get("version", "1.0"))
    footer_left = escape(data.get("footer_left", ""))
    footer_center = escape(data.get("footer_center", ""))
    footer_right = escape(data.get("footer_right", ""))
    date_str = datetime.now().strftime("%Y-%m-%d")

    css = get_css(theme_name)

    # Build columns
    columns_html = []
    for col in data.get("columns", []):
        sections_html = []
        for section in col.get("sections", []):
            sections_html.append(render_section(section))
        columns_html.append(
            '<div class="column">\n' + "\n".join(sections_html) + "\n</div>"
        )

    columns_block = "\n".join(columns_html)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<div class="blueprint">
  <div class="corner-bl"></div>
  <div class="corner-br"></div>

  <div class="header">
    <div class="header-left">
      <h1>{title}</h1>
      <span class="subtitle">{subtitle}</span>
    </div>
    <div class="header-right">
      <span>{author}</span>
      <span class="version">{version}</span>
      <span>{date_str}</span>
    </div>
  </div>

  <div class="columns">
    {columns_block}
  </div>

  <div class="footer">
    <span>{footer_left}</span>
    <span class="footer-center">{footer_center}</span>
    <span>{footer_right}</span>
  </div>
</div>
</body>
</html>"""
    return html


def generate(input_path: str, theme: str, output_path: str = None) -> str:
    """Generate a single blueprint HTML file. Returns the output path."""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    html = render_blueprint(data, theme)

    if output_path is None:
        stem = Path(input_path).stem
        suffix = f"-{theme}" if theme != "midnight" else ""
        output_path = str(Path(input_path).parent / f"{stem}{suffix}.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def convert_to_pdf(html_path: str) -> str:
    """Convert HTML to PDF using weasyprint if available."""
    try:
        from weasyprint import HTML
    except (ImportError, OSError):
        print("  [skip] weasyprint not available. Install with: pip install weasyprint")
        print("         On macOS also run: brew install pango gdk-pixbuf libffi")
        return None

    pdf_path = html_path.replace(".html", ".pdf")
    HTML(filename=html_path).write_pdf(pdf_path)
    return pdf_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate professional business blueprint PDFs from JSON data."
    )
    parser.add_argument("input", help="Path to blueprint JSON file")
    parser.add_argument(
        "--theme",
        choices=list(THEMES.keys()),
        default="midnight",
        help="Color theme (default: midnight)",
    )
    parser.add_argument(
        "--all-themes",
        action="store_true",
        help="Generate all 5 theme variants",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Also convert to PDF (requires weasyprint)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (only with single theme)",
    )

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: file not found: {args.input}")
        sys.exit(1)

    themes_to_build = list(THEMES.keys()) if args.all_themes else [args.theme]

    for theme in themes_to_build:
        out = args.output if (not args.all_themes and args.output) else None
        html_path = generate(args.input, theme, out)
        print(f"  [+] {theme:10s} -> {html_path}")

        if args.pdf:
            pdf_path = convert_to_pdf(html_path)
            if pdf_path:
                print(f"  [+] {'pdf':10s} -> {pdf_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
