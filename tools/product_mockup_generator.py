#!/usr/bin/env python3
"""
Product Mockup Generator -- composites screenshots onto device frames.

Creates professional-looking product mockups with dark gradient backgrounds,
device frames, product titles, and behike.co watermark.

Usage:
    python3 tools/product_mockup_generator.py --input screenshot.png --title "Product Name" --output mockup.png
    python3 tools/product_mockup_generator.py --batch            # processes all *-preview.png in READY-TO-SELL/
    python3 tools/product_mockup_generator.py --input shot.png --device ipad --title "Guide" --output out.png

Dependencies: Pillow
"""

import argparse
import math
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)


# -- Constants ----------------------------------------------------------------

CANVAS_W, CANVAS_H = 1280, 720
BG_TOP = (18, 18, 24)
BG_BOTTOM = (30, 30, 45)
WATERMARK_TEXT = "behike.co"
FONT_SIZES = {"title": 28, "watermark": 16}

# Device frame configs (outer rect, screen inset, corner radius)
DEVICES = {
    "laptop": {
        "frame": (140, 80, 1140, 520),       # x1, y1, x2, y2 of outer bezel
        "screen": (160, 100, 1120, 500),      # where the screenshot goes
        "bezel_color": (40, 40, 48),
        "border_color": (60, 60, 70),
        "corner_radius": 12,
        "base": True,                          # draw laptop base/keyboard area
    },
    "ipad": {
        "frame": (300, 50, 980, 540),
        "screen": (320, 70, 960, 520),
        "bezel_color": (35, 35, 42),
        "border_color": (55, 55, 65),
        "corner_radius": 18,
        "base": False,
    },
}

TITLE_Y = 570
WATERMARK_POS = (CANVAS_W - 20, CANVAS_H - 15)  # bottom-right anchor

BASE_DIR = Path(__file__).resolve().parent.parent
READY_TO_SELL = BASE_DIR / "READY-TO-SELL"


# -- Drawing helpers ----------------------------------------------------------

def draw_gradient(draw, width, height, top_color, bottom_color):
    """Draw a vertical linear gradient."""
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_rounded_rect(draw, coords, fill, outline, radius):
    """Draw a rectangle with rounded corners."""
    x1, y1, x2, y2 = coords
    # Main body
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    # Corners
    draw.pieslice([x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=fill)
    # Outline
    if outline:
        draw.rounded_rectangle(coords, radius=radius, outline=outline, width=2)


def draw_laptop_base(draw, frame_coords, bezel_color, border_color):
    """Draw the keyboard/base section below the laptop screen."""
    x1, _, x2, y2 = frame_coords
    base_h = 20
    hinge_h = 6
    # Hinge strip
    draw.rectangle([x1 + 40, y2, x2 - 40, y2 + hinge_h], fill=border_color)
    # Base trapezoid (wider than screen)
    base_x1 = x1 - 40
    base_x2 = x2 + 40
    draw.polygon(
        [(x1 + 20, y2 + hinge_h), (base_x1, y2 + hinge_h + base_h),
         (base_x2, y2 + hinge_h + base_h), (x2 - 20, y2 + hinge_h)],
        fill=bezel_color, outline=border_color
    )


def get_font(size):
    """Try to load a nice font, fall back to default."""
    font_paths = [
        "/System/Library/Fonts/SFPro-Regular.otf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


# -- Core mockup function -----------------------------------------------------

def generate_mockup(input_path, title, output_path, device="laptop"):
    """Generate a single product mockup image."""
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        print(f"  SKIP: {input_path} not found")
        return False

    dev = DEVICES.get(device, DEVICES["laptop"])

    # Create canvas with gradient
    img = Image.new("RGB", (CANVAS_W, CANVAS_H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, CANVAS_W, CANVAS_H, BG_TOP, BG_BOTTOM)

    # Draw device frame
    frame = dev["frame"]
    draw_rounded_rect(draw, frame, dev["bezel_color"], dev["border_color"], dev["corner_radius"])

    if dev.get("base"):
        draw_laptop_base(draw, frame, dev["bezel_color"], dev["border_color"])

    # Load and paste screenshot into screen area
    screen = dev["screen"]
    screen_w = screen[2] - screen[0]
    screen_h = screen[3] - screen[1]

    try:
        screenshot = Image.open(input_path)
        screenshot = screenshot.convert("RGB")
        screenshot = screenshot.resize((screen_w, screen_h), Image.LANCZOS)
        img.paste(screenshot, (screen[0], screen[1]))
    except Exception as e:
        print(f"  WARN: Could not load {input_path}: {e}")
        # Fill screen with dark placeholder
        draw.rectangle(screen, fill=(20, 20, 30))

    # Add subtle screen border
    draw.rectangle(screen, outline=(50, 50, 60), width=1)

    # Add title text
    if title:
        title_font = get_font(FONT_SIZES["title"])
        bbox = draw.textbbox((0, 0), title, font=title_font)
        text_w = bbox[2] - bbox[0]
        title_x = (CANVAS_W - text_w) // 2
        # Shadow
        draw.text((title_x + 1, TITLE_Y + 1), title, fill=(0, 0, 0), font=title_font)
        # Main text
        draw.text((title_x, TITLE_Y), title, fill=(230, 230, 240), font=title_font)

    # Add watermark
    wm_font = get_font(FONT_SIZES["watermark"])
    bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=wm_font)
    wm_w = bbox[2] - bbox[0]
    draw.text(
        (WATERMARK_POS[0] - wm_w, WATERMARK_POS[1]),
        WATERMARK_TEXT,
        fill=(100, 100, 120),
        font=wm_font,
    )

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), quality=95)
    print(f"  OK: {output_path}")
    return True


# -- Batch mode ---------------------------------------------------------------

def batch_process(source_dir=None, device="laptop"):
    """Process all *-preview.png files in READY-TO-SELL/."""
    source = Path(source_dir) if source_dir else READY_TO_SELL

    if not source.exists():
        print(f"ERROR: Directory not found: {source}")
        return

    previews = sorted(source.glob("*-preview.png"))
    if not previews:
        print(f"No *-preview.png files found in {source}")
        return

    print(f"Found {len(previews)} preview files in {source}")
    output_dir = source / "mockups"
    output_dir.mkdir(exist_ok=True)

    success = 0
    for preview in previews:
        # Derive title from filename: "behike-os-v3-preview.png" -> "Behike OS V3"
        stem = preview.stem.replace("-preview", "")
        title = stem.replace("-", " ").replace("_", " ").title()
        out_name = stem + "-mockup.png"
        out_path = output_dir / out_name

        if generate_mockup(preview, title, out_path, device):
            success += 1

    print(f"\nDone: {success}/{len(previews)} mockups generated in {output_dir}")


# -- CLI ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate product mockup images with device frames"
    )
    parser.add_argument("--input", "-i", help="Input screenshot/preview image")
    parser.add_argument("--title", "-t", default="", help="Product title text")
    parser.add_argument("--output", "-o", help="Output mockup path")
    parser.add_argument("--device", "-d", choices=["laptop", "ipad"], default="laptop",
                        help="Device frame type (default: laptop)")
    parser.add_argument("--batch", action="store_true",
                        help="Batch process all *-preview.png in READY-TO-SELL/")
    parser.add_argument("--batch-dir", help="Custom source directory for batch mode")

    args = parser.parse_args()

    if args.batch:
        batch_process(args.batch_dir, args.device)
    elif args.input:
        if not args.output:
            inp = Path(args.input)
            args.output = str(inp.parent / (inp.stem + "-mockup.png"))
        generate_mockup(args.input, args.title, args.output, args.device)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
