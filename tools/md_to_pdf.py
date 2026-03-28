#!/usr/bin/env python3
"""
md_to_pdf.py - Convert Markdown files to PDF using fpdf2.
No system dependencies required (pure Python).

Usage:
    python3 tools/md_to_pdf.py input.md output.pdf
    python3 tools/md_to_pdf.py input.md  # outputs input.pdf
"""

import re
import sys
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError:
    print("Installing fpdf2...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2", "-q"])
    from fpdf import FPDF

# Arial Unicode ships with macOS in two locations; pick whichever exists.
_UNICODE_FONT_CANDIDATES = [
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]

def _find_unicode_font():
    for path in _UNICODE_FONT_CANDIDATES:
        if Path(path).exists():
            return path
    return None

_UNICODE_FONT_PATH = _find_unicode_font()
_UNICODE_FONT_NAME = "UniFont"   # internal fpdf2 alias


class MarkdownPDF(FPDF):
    def __init__(self, title="", author=""):
        super().__init__()
        self.doc_title = title
        self.doc_author = author
        self.set_auto_page_break(auto=True, margin=20)

        if _UNICODE_FONT_PATH:
            # Register regular, bold, italic, and bold-italic variants.
            # Arial Unicode only ships as a single .ttf file, so we map all
            # styles to it; fpdf2 will synthesise bold/italic rendering.
            self.add_font(_UNICODE_FONT_NAME, "", _UNICODE_FONT_PATH)
            self.add_font(_UNICODE_FONT_NAME, "B", _UNICODE_FONT_PATH)
            self.add_font(_UNICODE_FONT_NAME, "I", _UNICODE_FONT_PATH)
            self.add_font(_UNICODE_FONT_NAME, "BI", _UNICODE_FONT_PATH)
            self._uni = True
        else:
            self._uni = False

    def _font(self, style="", size=10):
        """Set the active font, preferring Unicode TTF over Helvetica."""
        if self._uni:
            self.set_font(_UNICODE_FONT_NAME, style, size)
        else:
            # Fall back to Helvetica (Latin-1 only).
            hv_style = style.replace("BI", "BI")  # Helvetica supports BI
            self.set_font("Helvetica", hv_style, size)

    def header(self):
        if self.page_no() > 1:
            self._font("I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, self.doc_title, align="C")
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self._font("I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_cover(self, title, author="", subtitle=""):
        self.add_page()
        self.ln(60)
        self._font("B", 28)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 14, title, align="C")
        if subtitle:
            self.ln(10)
            self._font("I", 14)
            self.set_text_color(100, 100, 100)
            self.multi_cell(0, 8, subtitle, align="C")
        if author:
            self.ln(20)
            self._font("", 14)
            self.set_text_color(80, 80, 80)
            self.multi_cell(0, 8, f"By {author}", align="C")


def clean_text(text):
    """Clean text for PDF rendering.

    When a Unicode font is loaded these replacements are optional, but we keep
    a few that can produce cleaner typography in any font (zero-width space,
    non-breaking space).  The Latin-1 stripping is skipped when a Unicode font
    is available so em dashes, smart quotes, and accented characters render as-is.
    """
    # Always normalise invisible/control characters.
    text = text.replace("\u200b", "")   # zero-width space
    text = text.replace("\u00a0", " ")  # non-breaking space

    if not _UNICODE_FONT_PATH:
        # Helvetica fallback: replace characters outside Latin-1.
        replacements = {
            "\u2014": " - ",  # em dash
            "\u2013": " - ",  # en dash
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u2026": "...",
            "\u2022": "-",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        text = text.encode("latin-1", errors="replace").decode("latin-1")

    return text


def parse_markdown(md_text):
    """Parse markdown into structured blocks."""
    blocks = []
    lines = md_text.split("\n")
    i = 0
    in_code = False
    code_block = []

    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith("```"):
            if in_code:
                blocks.append({"type": "code", "text": "\n".join(code_block)})
                code_block = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_block.append(line)
            i += 1
            continue

        stripped = line.strip()

        # Empty line
        if not stripped:
            i += 1
            continue

        # Frontmatter (skip)
        if stripped == "---":
            if i == 0 or (i > 0 and blocks == []):
                i += 1
                while i < len(lines) and lines[i].strip() != "---":
                    i += 1
                i += 1
                continue
            else:
                blocks.append({"type": "hr"})
                i += 1
                continue

        # Headers
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped.lstrip("#").strip()
            blocks.append({"type": f"h{min(level, 4)}", "text": text})
            i += 1
            continue

        # Tables
        if "|" in stripped and stripped.startswith("|"):
            table_rows = []
            while i < len(lines) and "|" in lines[i].strip():
                row = lines[i].strip()
                # Skip separator rows
                if re.match(r"^\|[-:\s|]+\|$", row):
                    i += 1
                    continue
                cells = [c.strip() for c in row.split("|")[1:-1]]
                table_rows.append(cells)
                i += 1
            blocks.append({"type": "table", "rows": table_rows})
            continue

        # List items
        if re.match(r"^[-*]\s", stripped) or re.match(r"^\d+\.\s", stripped):
            list_items = []
            while i < len(lines):
                l = lines[i].strip()
                if re.match(r"^[-*]\s", l):
                    list_items.append(l[2:].strip())
                elif re.match(r"^\d+\.\s", l):
                    list_items.append(l.split(".", 1)[1].strip())
                elif not l:
                    break
                else:
                    # Continuation line
                    if list_items:
                        list_items[-1] += " " + l
                    else:
                        break
                i += 1
            blocks.append({"type": "list", "items": list_items})
            continue

        # Regular paragraph
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            l = lines[i].strip()
            if not l or l.startswith("#") or l.startswith("```") or l.startswith("|") or l.startswith("---"):
                break
            if re.match(r"^[-*]\s", l) or re.match(r"^\d+\.\s", l):
                break
            para_lines.append(l)
            i += 1
        blocks.append({"type": "paragraph", "text": " ".join(para_lines)})

    return blocks


def strip_markdown_formatting(text):
    """Remove inline markdown formatting."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # bold
    text = re.sub(r"\*(.+?)\*", r"\1", text)  # italic
    text = re.sub(r"`(.+?)`", r"\1", text)  # inline code
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)  # links
    return text


def render_pdf(blocks, title="", author="", subtitle=""):
    """Render parsed blocks into a PDF."""
    pdf = MarkdownPDF(title=title, author=author)
    pdf.set_margins(15, 15, 15)

    # Cover page
    if title:
        pdf.add_cover(title, author, subtitle)

    pdf.add_page()

    for block in blocks:
        btype = block["type"]

        if btype == "h1":
            pdf.add_page()
            pdf.ln(10)
            pdf._font("B", 22)
            pdf.set_text_color(20, 20, 20)
            text = clean_text(strip_markdown_formatting(block["text"]))
            pdf.multi_cell(0, 10, text)
            pdf.ln(6)

        elif btype == "h2":
            pdf.ln(8)
            pdf._font("B", 16)
            pdf.set_text_color(30, 30, 30)
            text = clean_text(strip_markdown_formatting(block["text"]))
            pdf.multi_cell(0, 8, text)
            pdf.ln(4)

        elif btype == "h3":
            pdf.ln(6)
            pdf._font("B", 13)
            pdf.set_text_color(40, 40, 40)
            text = clean_text(strip_markdown_formatting(block["text"]))
            pdf.multi_cell(0, 7, text)
            pdf.ln(3)

        elif btype == "h4":
            pdf.ln(4)
            pdf._font("BI", 11)
            pdf.set_text_color(50, 50, 50)
            text = clean_text(strip_markdown_formatting(block["text"]))
            pdf.multi_cell(0, 6, text)
            pdf.ln(2)

        elif btype == "paragraph":
            pdf._font("", 10)
            pdf.set_text_color(30, 30, 30)
            text = clean_text(strip_markdown_formatting(block["text"]))
            try:
                pdf.multi_cell(0, 5, text)
            except Exception:
                safe = text.encode("ascii", errors="replace").decode("ascii")
                pdf.multi_cell(0, 5, safe)
            pdf.ln(3)

        elif btype == "list":
            pdf._font("", 10)
            pdf.set_text_color(30, 30, 30)
            for item in block["items"]:
                text = clean_text(strip_markdown_formatting(item))
                try:
                    pdf.cell(8)
                    pdf.multi_cell(0, 5, f"  - {text}")
                except Exception:
                    safe = text.encode("ascii", errors="replace").decode("ascii")
                    pdf.cell(8)
                    pdf.multi_cell(0, 5, f"  - {safe}")
                pdf.ln(1)
            pdf.ln(2)

        elif btype == "code":
            # Code blocks: use UniFont at small size (Courier is Latin-1 only).
            pdf._font("", 8)
            pdf.set_text_color(50, 50, 50)
            pdf.set_fill_color(245, 245, 245)
            text = clean_text(block["text"])
            for code_line in text.split("\n"):
                try:
                    pdf.cell(0, 4, f"  {code_line}", new_x="LMARGIN", new_y="NEXT", fill=True)
                except Exception:
                    safe = code_line.encode("ascii", errors="replace").decode("ascii")
                    pdf.cell(0, 4, f"  {safe}", new_x="LMARGIN", new_y="NEXT", fill=True)
            pdf.ln(4)

        elif btype == "table":
            rows = block["rows"]
            if not rows:
                continue
            num_cols = max(len(r) for r in rows)
            col_width = (pdf.w - 30) / num_cols

            for ri, row in enumerate(rows):
                pdf._font("B" if ri == 0 else "", 9)
                pdf.set_text_color(30, 30, 30)
                for ci, cell in enumerate(row):
                    text = clean_text(strip_markdown_formatting(cell))[:50]
                    try:
                        pdf.cell(col_width, 6, text, border=1)
                    except Exception:
                        pdf.cell(col_width, 6, "...", border=1)
                pdf.ln()
            pdf.ln(4)

        elif btype == "hr":
            pdf.ln(4)
            y = pdf.get_y()
            pdf.set_draw_color(200, 200, 200)
            pdf.line(15, y, pdf.w - 15, y)
            pdf.ln(4)

    return pdf


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 md_to_pdf.py input.md [output.pdf]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.with_suffix(".pdf")

    print(f"Reading: {input_path}")
    md_text = input_path.read_text(encoding="utf-8")

    # Extract title from first H1
    title_match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    title = title_match.group(1) if title_match else input_path.stem.replace("-", " ").title()

    # Strip markdown formatting from title
    title = strip_markdown_formatting(title)

    print(f"Title: {title}")
    print("Parsing markdown...")
    blocks = parse_markdown(md_text)
    print(f"Found {len(blocks)} content blocks")

    print("Rendering PDF...")
    pdf = render_pdf(blocks, title=title, author="Kalani Andre Gomez Padin")
    pdf.output(str(output_path))

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Done: {output_path} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
