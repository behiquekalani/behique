#!/bin/bash
# Install SVG-to-PDF conversion dependencies
set -e

echo "Installing cairosvg (Python)..."
pip3 install cairosvg

echo ""
echo "Installing librsvg (brew, for rsvg-convert backup)..."
brew install librsvg 2>/dev/null || echo "librsvg already installed or brew unavailable"

echo ""
echo "Done. Run: python3 tools/svg_to_pdf.py"
