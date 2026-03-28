#!/usr/bin/env python3
# Copyright 2026 Behike. All rights reserved.
"""
Auto Thumbnail Generator. Creates 1080x1080 (IG) and 1280x720 (YT)
thumbnails using pure Python (Pillow).

Templates: bold, minimal, number, split

Usage:
    python3 thumbnail_generator.py --title "5 AI Tools You Need" --template bold
    python3 thumbnail_generator.py --title "The Truth About Dropshipping" --template minimal --size yt
    python3 thumbnail_generator.py --title "3 Mistakes" --template number --number 3 --size both
    python3 thumbnail_generator.py --title "Before vs After" --template split --size ig
    python3 thumbnail_generator.py --auto-from-script path/to/script.json
    python3 thumbnail_generator.py --help

Requires: Pillow (pip install Pillow)
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("[ERROR] Pillow is required. Install with: pip install Pillow")
    sys.exit(1)

# --- Paths ---
TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
THUMB_DIR = PROJECT_DIR / "Ceiba" / "news" / "thumbnails"

# --- Sizes ---
SIZES = {
    "ig": (1080, 1080),
    "yt": (1280, 720),
}

# --- Color palettes (Apple design system) ---
PALETTES = {
    "dark": {
        "bg_start": (10, 10, 10),
        "bg_end": (30, 30, 35),
        "text": (245, 245, 247),
        "accent": (255, 59, 48),
        "muted": (142, 142, 147),
    },
    "light": {
        "bg_start": (250, 249, 246),
        "bg_end": (245, 245, 247),
        "text": (29, 29, 31),
        "accent": (255, 59, 48),
        "muted": (134, 134, 139),
    },
    "warm": {
        "bg_start": (242, 239, 232),
        "bg_end": (232, 228, 219),
        "text": (45, 41, 38),
        "accent": (196, 69, 54),
        "muted": (138, 132, 128),
    },
    "blue": {
        "bg_start": (10, 15, 30),
        "bg_end": (20, 30, 60),
        "text": (245, 245, 247),
        "accent": (0, 122, 255),
        "muted": (142, 142, 147),
    },
}

# --- Font loading ---
def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load Inter or system font at the given size."""
    font_paths = [
        # Inter font (preferred)
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue

    return ImageFont.load_default()


def _draw_gradient(img: Image.Image, color_start: tuple, color_end: tuple):
    """Draw a vertical gradient on the image."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    for y in range(h):
        ratio = y / h
        r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        bbox = font.getbbox(test)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def _draw_text_block(draw: ImageDraw.Draw, lines: list, font: ImageFont.FreeTypeFont,
                     x: int, y: int, color: tuple, line_spacing: float = 1.2) -> int:
    """Draw wrapped text lines. Returns total height used."""
    total_h = 0
    for line in lines:
        bbox = font.getbbox(line)
        line_h = bbox[3] - bbox[1]
        draw.text((x, y + total_h), line, font=font, fill=color)
        total_h += int(line_h * line_spacing)
    return total_h


def _add_brand_dot(draw: ImageDraw.Draw, x: int, y: int, color: tuple, radius: int = 6):
    """Draw a small brand dot (Behike signature element)."""
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)


def _add_accent_line(draw: ImageDraw.Draw, x: int, y: int, width: int, color: tuple, thickness: int = 3):
    """Draw a thin accent line."""
    draw.rectangle([x, y, x + width, y + thickness], fill=color)


# --- Template renderers ---

def render_bold(title: str, size: tuple, palette: dict, subtitle: str = "") -> Image.Image:
    """Bold text on gradient. High impact, news style."""
    img = Image.new("RGB", size)
    _draw_gradient(img, palette["bg_start"], palette["bg_end"])
    draw = ImageDraw.Draw(img)

    w, h = size
    margin = int(w * 0.09)
    text_area = w - margin * 2

    # Title
    title_size = int(w * 0.075)
    title_font = _load_font(title_size, bold=True)
    lines = _wrap_text(title.upper(), title_font, text_area)

    # Calculate vertical position (centered with slight upward bias)
    bbox_h = 0
    for line in lines:
        bbox = title_font.getbbox(line)
        bbox_h += int((bbox[3] - bbox[1]) * 1.15)

    y_start = int(h * 0.35) - bbox_h // 2

    # Accent line above title
    _add_accent_line(draw, margin, y_start - 30, int(w * 0.15), palette["accent"], 4)

    # Draw title
    total = _draw_text_block(draw, lines, title_font, margin, y_start, palette["text"], 1.15)

    # Subtitle or brand
    if subtitle:
        sub_font = _load_font(int(w * 0.028))
        draw.text((margin, y_start + total + 20), subtitle.upper(),
                  font=sub_font, fill=palette["muted"])

    # Brand dot
    _add_brand_dot(draw, margin + 4, int(h * 0.08), palette["text"])

    # Brand name bottom
    brand_font = _load_font(int(w * 0.022))
    draw.text((margin, h - margin), "BEHIKE", font=brand_font, fill=palette["muted"])

    return img


def render_minimal(title: str, size: tuple, palette: dict, subtitle: str = "") -> Image.Image:
    """Minimal text with lots of whitespace. Clean, premium feel."""
    img = Image.new("RGB", size)
    _draw_gradient(img, palette["bg_start"], palette["bg_end"])
    draw = ImageDraw.Draw(img)

    w, h = size
    margin = int(w * 0.12)
    text_area = w - margin * 2

    # Title (smaller, elegant)
    title_size = int(w * 0.05)
    title_font = _load_font(title_size, bold=False)
    lines = _wrap_text(title, title_font, text_area)

    # Center vertically
    bbox_h = 0
    for line in lines:
        bbox = title_font.getbbox(line)
        bbox_h += int((bbox[3] - bbox[1]) * 1.4)

    y_start = (h - bbox_h) // 2

    _draw_text_block(draw, lines, title_font, margin, y_start, palette["text"], 1.4)

    # Brand dot top left
    _add_brand_dot(draw, margin, int(h * 0.08), palette["accent"])

    # Subtitle bottom
    if subtitle:
        sub_font = _load_font(int(w * 0.025))
        sub_bbox = sub_font.getbbox(subtitle)
        sub_w = sub_bbox[2] - sub_bbox[0]
        draw.text(((w - sub_w) // 2, h - margin - 10), subtitle,
                  font=sub_font, fill=palette["muted"])

    return img


def render_number(title: str, size: tuple, palette: dict, number: int = 5, subtitle: str = "") -> Image.Image:
    """Large number + topic text. Great for listicles."""
    img = Image.new("RGB", size)
    _draw_gradient(img, palette["bg_start"], palette["bg_end"])
    draw = ImageDraw.Draw(img)

    w, h = size
    margin = int(w * 0.09)

    # Giant number
    num_size = int(h * 0.45)
    num_font = _load_font(num_size, bold=True)
    num_str = str(number)
    num_bbox = num_font.getbbox(num_str)
    num_w = num_bbox[2] - num_bbox[0]

    # Draw number with slight transparency effect (use accent color, lighter)
    num_color = tuple(min(255, c + 30) for c in palette["accent"])
    draw.text((margin, int(h * 0.15)), num_str, font=num_font, fill=num_color)

    # Title text (to the right of number or below)
    title_size = int(w * 0.055)
    title_font = _load_font(title_size, bold=True)
    text_area = w - margin * 2

    lines = _wrap_text(title.upper(), title_font, text_area)
    y_text = int(h * 0.65)
    _draw_text_block(draw, lines, title_font, margin, y_text, palette["text"], 1.2)

    # Brand
    _add_brand_dot(draw, w - margin, int(h * 0.08), palette["text"])

    return img


def render_split(title: str, size: tuple, palette: dict, subtitle: str = "") -> Image.Image:
    """Split layout with accent bar. Good for comparisons or two-part topics."""
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)

    w, h = size
    margin = int(w * 0.09)

    # Left section (accent color gradient)
    split_x = int(w * 0.35)
    for x in range(split_x):
        ratio = x / split_x
        r = int(palette["accent"][0] * (0.3 + 0.7 * ratio))
        g = int(palette["accent"][1] * (0.3 + 0.7 * ratio))
        b = int(palette["accent"][2] * (0.3 + 0.7 * ratio))
        draw.line([(x, 0), (x, h)], fill=(r, g, b))

    # Right section (dark gradient)
    for x in range(split_x, w):
        ratio = (x - split_x) / (w - split_x)
        r = int(palette["bg_start"][0] + (palette["bg_end"][0] - palette["bg_start"][0]) * ratio)
        g = int(palette["bg_start"][1] + (palette["bg_end"][1] - palette["bg_start"][1]) * ratio)
        b = int(palette["bg_start"][2] + (palette["bg_end"][2] - palette["bg_start"][2]) * ratio)
        draw.line([(x, 0), (x, h)], fill=(r, g, b))

    # Title on the right side
    title_size = int(w * 0.06)
    title_font = _load_font(title_size, bold=True)
    text_area = w - split_x - margin * 2

    lines = _wrap_text(title.upper(), title_font, text_area)
    bbox_h = 0
    for line in lines:
        bbox = title_font.getbbox(line)
        bbox_h += int((bbox[3] - bbox[1]) * 1.2)

    y_start = (h - bbox_h) // 2
    _draw_text_block(draw, lines, title_font, split_x + margin, y_start, palette["text"], 1.2)

    # Brand on left side
    brand_font = _load_font(int(w * 0.035), bold=True)
    draw.text((int(split_x * 0.15), h - margin - 10), "BEHIKE",
              font=brand_font, fill=(255, 255, 255, 200))

    return img


# --- Template dispatcher ---

TEMPLATES = {
    "bold": render_bold,
    "minimal": render_minimal,
    "number": render_number,
    "split": render_split,
}

TEMPLATE_DESCRIPTIONS = {
    "bold": "Bold text on gradient. High impact, news style.",
    "minimal": "Minimal text, lots of whitespace. Clean, premium feel.",
    "number": "Large number + topic. Great for listicles.",
    "split": "Split layout with accent bar. Good for comparisons.",
}


def auto_select_template(title: str, content_type: str = "") -> str:
    """Auto-select the best template based on content characteristics."""
    title_lower = title.lower()

    # Number template for listicles
    if any(title_lower.startswith(f"{n} ") for n in range(1, 100)):
        return "number"
    if any(w in title_lower for w in ["top ", "best ", " ways", " tips", " tools", " steps"]):
        return "number"

    # Split for comparisons
    if any(w in title_lower for w in [" vs ", "before", "after", "versus", "compared"]):
        return "split"

    # Minimal for thought pieces
    if any(w in title_lower for w in ["truth", "why", "what if", "the real", "nobody"]):
        return "minimal"

    # Default: bold
    return "bold"


def auto_select_palette(content_type: str = "") -> str:
    """Pick a palette based on content type."""
    if content_type in ["news", "carousel"]:
        return "dark"
    if content_type in ["education", "tutorial"]:
        return "blue"
    if content_type in ["story", "personal"]:
        return "warm"
    return "dark"


def extract_number_from_title(title: str) -> int:
    """Extract a leading number from the title, or return 5 as default."""
    import re
    match = re.match(r"^(\d+)\s", title)
    if match:
        return int(match.group(1))
    return 5


def generate_thumbnail(title: str, template: str = "bold", size_key: str = "ig",
                       palette_name: str = "dark", number: int = None,
                       subtitle: str = "") -> list:
    """Generate thumbnail(s). Returns list of saved file paths."""
    THUMB_DIR.mkdir(parents=True, exist_ok=True)

    palette = PALETTES.get(palette_name, PALETTES["dark"])
    renderer = TEMPLATES.get(template, render_bold)

    sizes_to_generate = []
    if size_key == "both":
        sizes_to_generate = [("ig", SIZES["ig"]), ("yt", SIZES["yt"])]
    else:
        sizes_to_generate = [(size_key, SIZES.get(size_key, SIZES["ig"]))]

    saved = []
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_title = "".join(c for c in title.lower().replace(" ", "-") if c.isalnum() or c == "-")[:40]

    for sz_key, sz in sizes_to_generate:
        kwargs = {"title": title, "size": sz, "palette": palette, "subtitle": subtitle}
        if template == "number":
            kwargs["number"] = number or extract_number_from_title(title)

        img = renderer(**kwargs)

        filename = f"thumb-{safe_title}-{template}-{sz_key}-{timestamp}.png"
        filepath = THUMB_DIR / filename
        img.save(filepath, "PNG", quality=95)
        saved.append(filepath)

    return saved


def generate_from_script(script_path: str) -> list:
    """Generate thumbnails from a script JSON file."""
    with open(script_path) as f:
        script = json.load(f)

    title = script.get("title", "").replace("-", " ").title()
    if not title:
        title = script.get("hook", "Untitled")

    content_type = script.get("category", "")
    template = auto_select_template(title, content_type)
    palette = auto_select_palette(content_type)

    return generate_thumbnail(title, template, "both", palette)


def main():
    parser = argparse.ArgumentParser(
        description="Auto Thumbnail Generator. Apple design system. Copyright 2026 Behike."
    )
    parser.add_argument("--title", type=str, help="Thumbnail title text")
    parser.add_argument("--template", choices=list(TEMPLATES.keys()),
                        default=None, help="Template style (default: auto-select)")
    parser.add_argument("--size", choices=["ig", "yt", "both"], default="ig",
                        help="Output size: ig (1080x1080), yt (1280x720), both")
    parser.add_argument("--palette", choices=list(PALETTES.keys()), default="dark",
                        help="Color palette (default: dark)")
    parser.add_argument("--number", type=int, help="Number to display (for number template)")
    parser.add_argument("--subtitle", type=str, default="", help="Subtitle text")
    parser.add_argument("--auto-from-script", type=str,
                        help="Generate thumbnail from a script JSON file")
    parser.add_argument("--list-templates", action="store_true",
                        help="Show available templates")

    args = parser.parse_args()

    if args.list_templates:
        print("\nAvailable thumbnail templates:\n")
        for key, desc in TEMPLATE_DESCRIPTIONS.items():
            print(f"  {key:10s}  {desc}")
        print(f"\nAvailable palettes: {', '.join(PALETTES.keys())}")
        print(f"Available sizes: ig (1080x1080), yt (1280x720), both")
        print()
        return

    if args.auto_from_script:
        print(f"Generating thumbnails from: {args.auto_from_script}")
        paths = generate_from_script(args.auto_from_script)
        for p in paths:
            print(f"  [SAVED] {p}")
        return

    if not args.title:
        parser.print_help()
        return

    template = args.template or auto_select_template(args.title)

    print(f"\nGenerating thumbnail:")
    print(f"  Title:    {args.title}")
    print(f"  Template: {template}")
    print(f"  Size:     {args.size}")
    print(f"  Palette:  {args.palette}")

    paths = generate_thumbnail(
        title=args.title,
        template=template,
        size_key=args.size,
        palette_name=args.palette,
        number=args.number,
        subtitle=args.subtitle,
    )

    print()
    for p in paths:
        print(f"  [SAVED] {p}")
    print()


if __name__ == "__main__":
    main()
