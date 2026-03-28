#!/usr/bin/env python3
"""
md_to_dark_html.py - Convert Markdown to dark-themed HTML matching Behike v3 style.
Then convert to PDF via Brave headless.

Usage:
    python3 tools/md_to_dark_html.py input.md output.pdf
    python3 tools/md_to_dark_html.py input.md  # outputs input.pdf in same dir
"""

import re
import sys
import os
import subprocess
import tempfile
from pathlib import Path

try:
    import markdown
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown", "-q"])
    import markdown

DARK_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
  :root {{
    --bg: #0a0a0f;
    --card: #111111;
    --border: #222222;
    --white: #F5F5F7;
    --gray: #86868B;
    --cyan: #00D4FF;
    --cyan-dim: rgba(0, 212, 255, 0.15);
    --font: -apple-system, 'Helvetica Neue', 'SF Pro Display', sans-serif;
  }}
  html {{ font-size: 16px; }}
  body {{
    background: var(--bg);
    color: var(--white);
    font-family: var(--font);
    font-weight: 400;
    line-height: 1.8;
    -webkit-font-smoothing: antialiased;
    padding: 80px 40px;
  }}
  .container {{ max-width: 800px; margin: 0 auto; }}

  /* Header */
  .header {{ text-align: center; padding: 60px 0 80px; }}
  .header h1 {{ font-size: 48px; font-weight: 700; letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 16px; }}
  .header .line {{ width: 80px; height: 1px; background: var(--cyan); margin: 24px auto; }}
  .header .subtitle {{ font-size: 15px; color: var(--gray); letter-spacing: 0.05em; }}

  /* Content */
  h1 {{ font-size: 36px; font-weight: 700; margin: 48px 0 20px; letter-spacing: -0.02em; }}
  h2 {{ font-size: 28px; font-weight: 600; margin: 40px 0 16px; color: var(--white); }}
  h3 {{ font-size: 20px; font-weight: 600; margin: 32px 0 12px; color: var(--cyan); }}
  h4 {{ font-size: 16px; font-weight: 600; margin: 24px 0 8px; color: var(--gray); text-transform: uppercase; letter-spacing: 0.1em; }}

  p {{ margin-bottom: 16px; color: var(--white); font-size: 16px; line-height: 1.8; }}

  ul, ol {{ margin: 16px 0; padding-left: 24px; }}
  li {{ margin-bottom: 8px; color: var(--white); line-height: 1.6; }}
  li::marker {{ color: var(--cyan); }}

  strong {{ color: var(--white); font-weight: 600; }}
  em {{ color: var(--gray); }}

  a {{ color: var(--cyan); text-decoration: none; }}

  code {{ background: rgba(0, 212, 255, 0.1); color: var(--cyan); padding: 2px 8px; border-radius: 4px; font-size: 14px; }}
  pre {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin: 24px 0; overflow-x: auto; }}
  pre code {{ background: transparent; padding: 0; }}

  blockquote {{ border-left: 3px solid var(--cyan); padding: 16px 24px; margin: 24px 0; background: var(--card); border-radius: 0 12px 12px 0; }}
  blockquote p {{ color: var(--gray); margin: 0; font-style: italic; }}

  hr {{ border: none; border-top: 1px solid var(--border); margin: 40px 0; }}

  table {{ width: 100%; border-collapse: collapse; margin: 24px 0; }}
  th {{ text-align: left; padding: 12px 16px; font-size: 12px; font-weight: 600; color: var(--gray); text-transform: uppercase; letter-spacing: 0.1em; border-bottom: 1px solid var(--border); }}
  td {{ padding: 12px 16px; border-bottom: 1px solid var(--border); font-size: 14px; }}

  /* Section cards */
  .section {{ background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 40px; margin: 32px 0; page-break-inside: avoid; }}

  /* Footer */
  .footer {{ text-align: center; padding: 60px 0 20px; font-size: 12px; color: var(--gray); letter-spacing: 0.1em; }}
  .footer .brand {{ font-size: 14px; font-weight: 600; letter-spacing: 0.15em; margin-bottom: 8px; color: var(--white); }}

  @media print {{
    body {{ padding: 40px 30px; }}
    .section {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>{title}</h1>
    <div class="line"></div>
    <div class="subtitle">BEHIKE</div>
  </div>
  {content}
  <div class="footer">
    <div class="brand">BEHIKE</div>
    behike.co | Built in Puerto Rico
  </div>
</div>
</body>
</html>"""

BRAVE = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

def extract_title(md_text):
    """Extract title from first H1 or filename."""
    match = re.search(r'^#\s+(.+)', md_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Behike Guide"

def md_to_html_content(md_text):
    """Convert markdown to HTML content."""
    html = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'nl2br'])
    return html

def convert(md_path, pdf_path=None):
    md_path = Path(md_path)
    if pdf_path is None:
        pdf_path = md_path.with_suffix('.pdf')
    else:
        pdf_path = Path(pdf_path)

    md_text = md_path.read_text(encoding='utf-8')
    title = extract_title(md_text)
    content = md_to_html_content(md_text)

    html = DARK_TEMPLATE.format(title=title, content=content)

    # Write temp HTML
    tmp = tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8')
    tmp.write(html)
    tmp.close()

    # Also save HTML alongside PDF for future reconversions
    html_path = pdf_path.with_suffix('.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # Convert to PDF via Brave
    try:
        subprocess.run([
            BRAVE, '--headless', '--disable-gpu',
            f'--print-to-pdf={pdf_path}',
            '--no-margins',
            f'file://{tmp.name}'
        ], capture_output=True, timeout=30)
        print(f"OK: {pdf_path.name}")
    except Exception as e:
        print(f"FAIL: {pdf_path.name} - {e}")
    finally:
        os.unlink(tmp.name)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 md_to_dark_html.py input.md [output.pdf]")
        sys.exit(1)

    md_file = sys.argv[1]
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else None
    convert(md_file, pdf_file)
