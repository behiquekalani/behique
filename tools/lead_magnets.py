#!/usr/bin/env python3
"""
Lead Magnet Delivery for Behike.
When someone subscribes, auto-sends them a free PDF.

Usage:
    python tools/lead_magnets.py --send subscriber@email.com
    python tools/lead_magnets.py --build-pdf
    python tools/lead_magnets.py --preview

Copyright 2026 Behike.
"""

import argparse
import json
import os
import smtplib
import subprocess
import sys
import webbrowser
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

# -- Config --

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

LEAD_MAGNET_MD = BASE_DIR / "Ceiba" / "projects" / "content-empire" / "products" / "free" / "zero-dollar-ai-stack.md"
LEAD_MAGNET_PDF = BASE_DIR / "Ceiba" / "projects" / "content-empire" / "products" / "free" / "zero-dollar-ai-stack.pdf"

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "")
FROM_NAME = os.getenv("FROM_NAME", "Behike")

UNSUBSCRIBE_BASE = os.getenv("UNSUBSCRIBE_BASE", "http://localhost:8082")


# -- Lead Magnet Email Template --

WELCOME_EMAIL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Welcome to Behike</title>
<style>
  body {{
    margin: 0; padding: 0; background: #000; color: #f5f5f7;
    font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  }}
  .container {{ max-width: 560px; margin: 0 auto; padding: 48px 24px; }}
  h1 {{ font-size: 28px; font-weight: 700; letter-spacing: -0.03em; margin: 0 0 20px; }}
  p {{ font-size: 15px; line-height: 1.6; color: #d1d1d6; margin: 0 0 16px; }}
  .highlight {{
    background: rgba(10,132,255,0.08); border: 1px solid rgba(10,132,255,0.2);
    border-radius: 12px; padding: 24px; margin: 24px 0; text-align: center;
  }}
  .highlight h2 {{ font-size: 18px; font-weight: 700; margin: 0 0 8px; color: #f5f5f7; }}
  .highlight p {{ font-size: 14px; color: #86868b; margin: 0; }}
  .footer {{
    border-top: 1px solid rgba(245,245,247,0.08); padding-top: 20px; margin-top: 32px;
    font-size: 12px; color: #86868b; text-align: center;
  }}
  .footer a {{ color: #0a84ff; text-decoration: none; }}
</style>
</head>
<body>
<div class="container">
  <h1>Welcome to Behike.</h1>
  <p>You just joined a small group of builders who care about doing more with less.</p>
  <p>Attached is your free copy of <strong>The $0 AI Stack</strong>, a checklist of 10 free tools that replace paid software. Every tool on this list is something I actually use.</p>

  <div class="highlight">
    <h2>The $0 AI Stack (PDF attached)</h2>
    <p>10 free tools. Zero subscriptions. Real results.</p>
  </div>

  <p>Every week you'll get one email with AI news, a product spotlight, and a quick tip. No fluff, no spam.</p>
  <p>If you ever want to go deeper, check out the <a href="https://behike.com" style="color: #0a84ff;">full product lineup</a>.</p>
  <p>Talk soon,<br>Kalani</p>

  <div class="footer">
    <p>Copyright 2026 Behike. Built in Puerto Rico.</p>
    <p><a href="{unsubscribe_url}">Unsubscribe</a></p>
  </div>
</div>
</body>
</html>"""


# -- Functions --

def build_pdf():
    """Convert the markdown lead magnet to PDF using pandoc or weasyprint."""
    if not LEAD_MAGNET_MD.exists():
        print(f"Lead magnet markdown not found: {LEAD_MAGNET_MD}")
        return False

    # Try pandoc first
    try:
        subprocess.run(
            [
                "pandoc", str(LEAD_MAGNET_MD),
                "-o", str(LEAD_MAGNET_PDF),
                "--pdf-engine=wkhtmltopdf",
                "-V", "geometry:margin=1in",
                "-V", "fontsize=12pt",
            ],
            check=True,
            capture_output=True,
        )
        print(f"PDF created: {LEAD_MAGNET_PDF}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try with just pandoc (default engine)
    try:
        subprocess.run(
            ["pandoc", str(LEAD_MAGNET_MD), "-o", str(LEAD_MAGNET_PDF)],
            check=True,
            capture_output=True,
        )
        print(f"PDF created: {LEAD_MAGNET_PDF}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fallback: try python markdown + weasyprint
    try:
        import markdown
        from weasyprint import HTML

        md_content = LEAD_MAGNET_MD.read_text()
        html_content = markdown.markdown(md_content)
        styled = f"""<html><head><style>
            body {{ font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; line-height: 1.6; }}
            h1 {{ font-size: 24px; }} h2 {{ font-size: 18px; color: #333; }} li {{ margin-bottom: 8px; }}
            .cta {{ background: #0a84ff; color: white; padding: 12px 24px; border-radius: 8px; display: inline-block; text-decoration: none; margin-top: 16px; }}
        </style></head><body>{html_content}</body></html>"""

        HTML(string=styled).write_pdf(str(LEAD_MAGNET_PDF))
        print(f"PDF created: {LEAD_MAGNET_PDF}")
        return True
    except ImportError:
        print("Could not create PDF. Install pandoc or weasyprint:")
        print("  brew install pandoc")
        print("  pip install weasyprint markdown")
        return False


def send_lead_magnet(to_email: str) -> bool:
    """Send the welcome email with PDF attachment."""
    if not SMTP_USER or not SMTP_PASS or not FROM_EMAIL:
        print("ERROR: SMTP credentials not configured. Set SMTP_USER, SMTP_PASS, FROM_EMAIL in .env")
        return False

    if not LEAD_MAGNET_PDF.exists():
        print("PDF not found. Building it first...")
        if not build_pdf():
            print("Cannot send without PDF. Build it manually or install pandoc.")
            return False

    unsubscribe_url = f"{UNSUBSCRIBE_BASE}/unsubscribe?email={to_email}"
    html_body = WELCOME_EMAIL.format(unsubscribe_url=unsubscribe_url)

    msg = MIMEMultipart("mixed")
    msg["Subject"] = "Welcome to Behike. Here's your free AI stack."
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    msg["List-Unsubscribe"] = f"<{unsubscribe_url}>"

    # HTML body
    html_part = MIMEMultipart("alternative")
    plain = "Welcome to Behike. Your free AI stack checklist is attached."
    html_part.attach(MIMEText(plain, "plain"))
    html_part.attach(MIMEText(html_body, "html"))
    msg.attach(html_part)

    # PDF attachment
    with open(LEAD_MAGNET_PDF, "rb") as f:
        pdf_part = MIMEApplication(f.read(), _subtype="pdf")
        pdf_part.add_header("Content-Disposition", "attachment", filename="The-Zero-Dollar-AI-Stack.pdf")
        msg.attach(pdf_part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send to {to_email}: {e}")
        return False


def preview():
    """Open the lead magnet markdown in the browser as HTML."""
    if not LEAD_MAGNET_MD.exists():
        print(f"Not found: {LEAD_MAGNET_MD}")
        return

    try:
        import markdown
        md_content = LEAD_MAGNET_MD.read_text()
        html = markdown.markdown(md_content)
        preview_file = LEAD_MAGNET_MD.parent / "preview.html"
        preview_file.write_text(f"""<!DOCTYPE html><html><head>
            <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>body {{ font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; line-height: 1.6; background: #fff; color: #1d1d1f; }}
            h1 {{ font-size: 28px; }} h2 {{ font-size: 20px; color: #333; }} li {{ margin-bottom: 10px; }}</style>
            </head><body>{html}</body></html>""")
        webbrowser.open(f"file://{preview_file}")
    except ImportError:
        # Just open the markdown file
        webbrowser.open(f"file://{LEAD_MAGNET_MD}")


# -- Main --

def main():
    parser = argparse.ArgumentParser(description="Behike Lead Magnet Delivery")
    parser.add_argument("--send", metavar="EMAIL", help="Send lead magnet to email")
    parser.add_argument("--build-pdf", action="store_true", help="Build PDF from markdown")
    parser.add_argument("--preview", action="store_true", help="Preview lead magnet in browser")

    args = parser.parse_args()

    if args.send:
        print(f"Sending lead magnet to {args.send}...")
        if send_lead_magnet(args.send):
            print("Sent successfully.")
        else:
            print("Send failed.")
    elif args.build_pdf:
        build_pdf()
    elif args.preview:
        preview()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
