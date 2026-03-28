#!/usr/bin/env python3
"""Batch SVG-to-PDF converter for GoodNotes-compatible blueprints."""

import argparse, glob, os, shutil, subprocess, sys

SCAN_DIR = os.path.expanduser("~/behique/READY-TO-SELL")


def find_converter():
    """Return (name, convert_fn) for the first available method."""
    # Method 1: cairosvg
    try:
        import cairosvg
        cairosvg.svg2pdf(url=None, bytestring=b"<svg></svg>", write_to="/dev/null")
        def convert(svg, pdf):
            cairosvg.svg2pdf(url=svg, write_to=pdf)
        return "cairosvg", convert
    except Exception:
        pass

    # Method 2: rsvg-convert
    if shutil.which("rsvg-convert"):
        def convert(svg, pdf):
            subprocess.run(["rsvg-convert", "-f", "pdf", "-o", pdf, svg], check=True)
        return "rsvg-convert", convert

    # Method 3: wkhtmltopdf
    if shutil.which("wkhtmltopdf"):
        def convert(svg, pdf):
            subprocess.run(["wkhtmltopdf", "--quiet", svg, pdf], check=True)
        return "wkhtmltopdf", convert

    # Method 4: weasyprint
    try:
        from weasyprint import HTML
        def convert(svg, pdf):
            with open(svg) as f:
                svg_content = f.read()
            html = f'<html><body style="margin:0">{svg_content}</body></html>'
            HTML(string=html).write_pdf(pdf)
        return "weasyprint", convert
    except ImportError:
        pass

    return None, None


def should_convert(svg, pdf, force):
    if force or not os.path.exists(pdf):
        return True
    return os.path.getmtime(svg) > os.path.getmtime(pdf)


def main():
    parser = argparse.ArgumentParser(description="Convert SVGs to GoodNotes-compatible PDFs")
    parser.add_argument("--file", help="Convert a single SVG file")
    parser.add_argument("--force", action="store_true", help="Reconvert even if PDF exists")
    args = parser.parse_args()

    name, convert = find_converter()
    if not convert:
        print("ERROR: No converter found. Run: bash tools/install_pdf_tools.sh")
        sys.exit(1)
    print(f"Using: {name}")

    if args.file:
        svgs = [os.path.abspath(args.file)]
    else:
        svgs = sorted(glob.glob(os.path.join(SCAN_DIR, "**", "*.svg"), recursive=True))

    if not svgs:
        print("No SVG files found.")
        return

    converted = skipped = errors = 0
    for svg in svgs:
        pdf = os.path.splitext(svg)[0] + ".pdf"
        if not should_convert(svg, pdf, args.force):
            skipped += 1
            continue
        try:
            convert(svg, pdf)
            converted += 1
            print(f"  OK  {os.path.relpath(pdf, SCAN_DIR)}")
        except Exception as e:
            errors += 1
            print(f"  ERR {os.path.relpath(svg, SCAN_DIR)}: {e}")

    total = converted + skipped + errors
    print(f"\nConverted {converted} of {total} SVGs. {skipped} skipped (up to date). Errors: {errors}")


if __name__ == "__main__":
    main()
