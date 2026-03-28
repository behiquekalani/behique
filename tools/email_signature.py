#!/usr/bin/env python3
"""
Behike Email Signature Generator
Generates HTML email signatures compatible with Gmail, Outlook, Apple Mail.
All styles are inline CSS for maximum compatibility.

Usage:
    python email_signature.py --variant full --theme light --name "Kalani" --title "Founder"
    python email_signature.py --variant minimal --theme dark
    python email_signature.py --variant sales --theme light --cta-url "https://behike.co/blueprint"
"""

import argparse
import os
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "signatures"

# -- Brand defaults --
DEFAULTS = {
    "name": "Kalani",
    "title": "Founder, Behike",
    "website": "https://behike.co",
    "website_display": "behike.co",
    "tagline": "Build with intention.",
    "cta_text": "Get our free blueprint",
    "cta_url": "https://behike.co/blueprint",
    "instagram": "https://instagram.com/behikeai",
    "twitter": "https://x.com/behikeai",
    "youtube": "https://youtube.com/@behikeai",
    "tiktok": "https://tiktok.com/@behikeai",
}

# -- Theme palettes --
THEMES = {
    "light": {
        "bg": "#ffffff",
        "text": "#1a1a1a",
        "text_secondary": "#555555",
        "accent": "#000000",
        "link": "#1a1a1a",
        "divider": "#e0e0e0",
        "cta_bg": "#1a1a1a",
        "cta_text": "#ffffff",
        "icon_fill": "#1a1a1a",
    },
    "dark": {
        "bg": "#1a1a1a",
        "text": "#f0f0f0",
        "text_secondary": "#aaaaaa",
        "accent": "#ffffff",
        "link": "#f0f0f0",
        "divider": "#333333",
        "cta_bg": "#ffffff",
        "cta_text": "#1a1a1a",
        "icon_fill": "#f0f0f0",
    },
}

# SVG social icons (16x16, inline)
def _icon_svg(platform: str, fill: str) -> str:
    icons = {
        "instagram": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
            f'fill="none" stroke="{fill}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'<rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>'
            f'<path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>'
            f'<line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>'
        ),
        "twitter": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
            f'fill="{fill}">'
            f'<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'
        ),
        "youtube": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
            f'fill="{fill}">'
            f'<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>'
        ),
        "tiktok": (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
            f'fill="{fill}">'
            f'<path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .54.04.79.1v-3.5a6.37 6.37 0 0 0-.79-.05A6.34 6.34 0 0 0 3.15 15a6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.34-6.34V8.72a8.19 8.19 0 0 0 4.76 1.52V6.79a4.83 4.83 0 0 1-1-.1z"/></svg>'
        ),
    }
    return icons.get(platform, "")


def _social_link(url: str, platform: str, fill: str) -> str:
    icon = _icon_svg(platform, fill)
    return (
        f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
        f'style="text-decoration:none;margin-right:12px;display:inline-block;">'
        f'{icon}</a>'
    )


def _social_row(config: dict, fill: str) -> str:
    links = ""
    for platform in ("instagram", "twitter", "youtube", "tiktok"):
        url = config.get(platform)
        if url:
            links += _social_link(url, platform, fill)
    return links


def build_signature(
    variant: str = "full",
    theme: str = "light",
    name: str | None = None,
    title: str | None = None,
    tagline: str | None = None,
    cta_text: str | None = None,
    cta_url: str | None = None,
    **overrides,
) -> str:
    """Build an HTML email signature string."""
    c = {**DEFAULTS, **{k: v for k, v in overrides.items() if v is not None}}
    if name:
        c["name"] = name
    if title:
        c["title"] = title
    if tagline:
        c["tagline"] = tagline
    if cta_text:
        c["cta_text"] = cta_text
    if cta_url:
        c["cta_url"] = cta_url

    t = THEMES[theme]

    # Name
    name_html = (
        f'<span style="font-size:18px;font-weight:700;color:{t["text"]};'
        f'font-family:Helvetica,Arial,sans-serif;letter-spacing:-0.3px;">'
        f'{c["name"]}</span>'
    )

    # Title
    title_html = (
        f'<span style="font-size:13px;color:{t["text_secondary"]};'
        f'font-family:Helvetica,Arial,sans-serif;">'
        f'{c["title"]}</span>'
    )

    # Website link
    site_html = (
        f'<a href="{c["website"]}" target="_blank" rel="noopener noreferrer" '
        f'style="font-size:13px;color:{t["link"]};font-family:Helvetica,Arial,sans-serif;'
        f'text-decoration:none;font-weight:600;">'
        f'{c["website_display"]}</a>'
    )

    # Divider
    divider = (
        f'<tr><td style="padding:10px 0 10px 0;">'
        f'<div style="border-top:1px solid {t["divider"]};"></div>'
        f'</td></tr>'
    )

    # Social icons row
    social_html = _social_row(c, t["icon_fill"])

    # Tagline
    tagline_html = (
        f'<span style="font-size:12px;color:{t["text_secondary"]};'
        f'font-family:Helvetica,Arial,sans-serif;font-style:italic;">'
        f'{c["tagline"]}</span>'
    )

    # CTA button
    cta_html = (
        f'<a href="{c["cta_url"]}" target="_blank" rel="noopener noreferrer" '
        f'style="display:inline-block;padding:8px 20px;background-color:{t["cta_bg"]};'
        f'color:{t["cta_text"]};font-size:13px;font-family:Helvetica,Arial,sans-serif;'
        f'font-weight:600;text-decoration:none;border-radius:4px;letter-spacing:0.2px;">'
        f'{c["cta_text"]}</a>'
    )

    # -- Assemble by variant --
    rows = []

    # Name (all variants)
    rows.append(f'<tr><td style="padding:0 0 2px 0;">{name_html}</td></tr>')

    if variant in ("full", "sales"):
        rows.append(f'<tr><td style="padding:0 0 4px 0;">{title_html}</td></tr>')

    # Website (all variants)
    rows.append(f'<tr><td style="padding:2px 0 0 0;">{site_html}</td></tr>')

    if variant in ("full", "sales"):
        rows.append(divider)
        rows.append(f'<tr><td style="padding:0 0 8px 0;">{social_html}</td></tr>')
        rows.append(f'<tr><td style="padding:0 0 0 0;">{tagline_html}</td></tr>')

    if variant == "sales":
        rows.append(f'<tr><td style="padding:12px 0 0 0;">{cta_html}</td></tr>')

    inner = "\n".join(rows)

    # Wrap in table for email compatibility
    html = f"""<!--
  Behike Email Signature
  Variant: {variant} | Theme: {theme}
  Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
-->
<table cellpadding="0" cellspacing="0" border="0" style="background-color:{t["bg"]};padding:16px;font-family:Helvetica,Arial,sans-serif;max-width:400px;">
  <tbody>
    {inner}
  </tbody>
</table>"""
    return html


def main():
    parser = argparse.ArgumentParser(
        description="Behike Email Signature Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python email_signature.py --variant full --theme light\n"
               "  python email_signature.py --variant sales --theme dark --name 'Kalani' --title 'CEO'\n"
               "  python email_signature.py --variant minimal --theme light\n"
               "  python email_signature.py --all   # generate all 6 combinations",
    )
    parser.add_argument("--variant", choices=["full", "minimal", "sales"], default="full",
                        help="Signature variant (default: full)")
    parser.add_argument("--theme", choices=["dark", "light"], default="light",
                        help="Color theme (default: light)")
    parser.add_argument("--name", default=None, help=f"Name (default: {DEFAULTS['name']})")
    parser.add_argument("--title", default=None, help=f"Title (default: {DEFAULTS['title']})")
    parser.add_argument("--tagline", default=None, help=f"Tagline (default: {DEFAULTS['tagline']})")
    parser.add_argument("--cta-text", default=None, help="CTA button text (sales variant)")
    parser.add_argument("--cta-url", default=None, help="CTA button URL (sales variant)")
    parser.add_argument("--all", action="store_true", help="Generate all 6 variant/theme combos")
    parser.add_argument("--output-dir", default=None, help=f"Output directory (default: {OUTPUT_DIR})")

    args = parser.parse_args()
    out_dir = Path(args.output_dir) if args.output_dir else OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    kwargs = {
        "name": args.name,
        "title": args.title,
        "tagline": args.tagline,
        "cta_text": args.cta_text,
        "cta_url": args.cta_url,
    }

    if args.all:
        combos = [
            ("full", "light"), ("full", "dark"),
            ("minimal", "light"), ("minimal", "dark"),
            ("sales", "light"), ("sales", "dark"),
        ]
    else:
        combos = [(args.variant, args.theme)]

    generated = []
    for variant, theme in combos:
        html = build_signature(variant=variant, theme=theme, **kwargs)
        filename = f"signature_{variant}_{theme}.html"
        filepath = out_dir / filename
        filepath.write_text(html, encoding="utf-8")
        generated.append(filepath)
        print(f"  saved: {filepath}")

    print(f"\n{len(generated)} signature(s) generated in {out_dir}/")


if __name__ == "__main__":
    main()
