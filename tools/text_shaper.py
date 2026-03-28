#!/usr/bin/env python3
"""
Text Shape Generator -- Robert Greene style shaped paragraphs.

Formats text into visual shapes like diamonds, hourglasses, triangles,
and other geometric forms. Used in books like Mastery, 48 Laws of Power,
The Art of Seduction.

Usage:
    python3 text_shaper.py "Your text here" --shape diamond
    python3 text_shaper.py --file essay.txt --shape hourglass
    python3 text_shaper.py "Text" --shape triangle --width 60
    python3 text_shaper.py --list   # show all shapes
    echo "text" | python3 text_shaper.py --shape diamond

Shapes: diamond, hourglass, triangle, inverted-triangle, vase,
        hexagon, arrow, wave, circle, rectangle
"""
import sys
import argparse
import textwrap
import math


def get_shape_widths(shape, max_width, num_lines):
    """Generate line widths for each shape."""
    widths = []
    n = num_lines

    if shape == "diamond":
        mid = n // 2
        for i in range(n):
            if i <= mid:
                w = int(max_width * (i + 1) / (mid + 1))
            else:
                w = int(max_width * (n - i) / (mid + 1))
            widths.append(max(10, w))

    elif shape == "hourglass":
        mid = n // 2
        for i in range(n):
            if i <= mid:
                w = int(max_width * (mid - i + 1) / (mid + 1))
            else:
                w = int(max_width * (i - mid + 1) / (mid + 1))
            widths.append(max(10, w))

    elif shape == "triangle":
        for i in range(n):
            w = int(max_width * (i + 1) / n)
            widths.append(max(10, w))

    elif shape == "inverted-triangle":
        for i in range(n):
            w = int(max_width * (n - i) / n)
            widths.append(max(10, w))

    elif shape == "vase":
        for i in range(n):
            t = i / max(n - 1, 1)
            # Parabola: wide at top, narrow in middle, wide at bottom
            w = max_width * (0.4 + 0.6 * abs(2 * t - 1) ** 1.5)
            widths.append(max(10, int(w)))

    elif shape == "hexagon":
        third = n // 3
        for i in range(n):
            if i < third:
                w = int(max_width * (i + 1) / (third + 1))
            elif i >= n - third:
                w = int(max_width * (n - i) / (third + 1))
            else:
                w = max_width
            widths.append(max(10, w))

    elif shape == "arrow":
        # Arrow pointing right: starts narrow, widens, then sharp point
        two_thirds = int(n * 0.7)
        for i in range(n):
            if i < two_thirds:
                w = int(max_width * 0.4 + max_width * 0.6 * (i / two_thirds))
            else:
                remaining = n - two_thirds
                w = int(max_width * (n - i) / remaining)
            widths.append(max(10, w))

    elif shape == "wave":
        for i in range(n):
            t = i / max(n - 1, 1)
            w = max_width * (0.5 + 0.5 * math.sin(t * math.pi * 2))
            widths.append(max(10, int(w)))

    elif shape == "circle":
        for i in range(n):
            t = i / max(n - 1, 1)
            w = max_width * math.sin(t * math.pi)
            widths.append(max(10, int(w)))

    elif shape == "rectangle":
        widths = [max_width] * n

    elif shape == "claw":
        # Claw/lobster shape: two pincers at top, narrow stem, wide base
        for i in range(n):
            t = i / max(n - 1, 1)
            if t < 0.15:
                w = max_width * 0.7  # left pincer
            elif t < 0.25:
                w = max_width * 0.3  # pincer gap
            elif t < 0.35:
                w = max_width * 0.7  # right pincer
            elif t < 0.5:
                w = max_width * (0.3 + 0.1 * ((t - 0.35) / 0.15))  # narrow neck
            else:
                w = max_width * (0.4 + 0.6 * ((t - 0.5) / 0.5))  # widening body
            widths.append(max(10, int(w)))

    elif shape == "shield":
        # Shield/badge shape: flat top, widens, then tapers to point
        for i in range(n):
            t = i / max(n - 1, 1)
            if t < 0.1:
                w = max_width * 0.8  # flat top
            elif t < 0.3:
                w = max_width * (0.8 + 0.2 * ((t - 0.1) / 0.2))  # widen
            elif t < 0.6:
                w = max_width  # full width body
            else:
                w = max_width * (1.0 - ((t - 0.6) / 0.4) ** 1.5)  # taper to point
            widths.append(max(10, int(w)))

    elif shape == "bolt":
        # Lightning bolt: zig-zag pattern
        for i in range(n):
            t = i / max(n - 1, 1)
            if t < 0.3:
                w = max_width * (0.8 - 0.4 * (t / 0.3))  # narrow down
            elif t < 0.35:
                w = max_width * 0.9  # wide jog
            elif t < 0.65:
                w = max_width * (0.9 - 0.5 * ((t - 0.35) / 0.3))  # narrow again
            elif t < 0.7:
                w = max_width * 0.7  # another jog
            else:
                w = max_width * (0.7 - 0.5 * ((t - 0.7) / 0.3))  # taper to point
            widths.append(max(10, int(w)))

    elif shape == "brain":
        # Brain/cloud shape: bumpy, organic
        for i in range(n):
            t = i / max(n - 1, 1)
            bump = 0.15 * math.sin(t * math.pi * 4)
            base = math.sin(t * math.pi)
            w = max_width * (base * 0.8 + bump + 0.2)
            widths.append(max(10, int(w)))

    elif shape == "tower":
        # Tower/skyscraper: narrow top, slightly wider middle, narrow base
        for i in range(n):
            t = i / max(n - 1, 1)
            if t < 0.08:
                w = max_width * 0.2  # antenna
            elif t < 0.15:
                w = max_width * 0.4  # top
            elif t < 0.85:
                w = max_width * (0.4 + 0.15 * math.sin((t - 0.15) / 0.7 * math.pi))
            else:
                w = max_width * 0.6  # base
            widths.append(max(10, int(w)))

    else:
        widths = [max_width] * n

    return widths


def shape_text(text, shape="diamond", max_width=60, center=True):
    """Shape text into the given form."""
    words = text.split()
    if not words:
        return ""

    # Estimate how many lines we need
    avg_word_len = sum(len(w) for w in words) / len(words)
    avg_line_width = max_width * 0.65  # average across shape
    estimated_lines = max(5, int(len(words) * (avg_word_len + 1) / avg_line_width * 1.3))

    # Generate shape widths
    widths = get_shape_widths(shape, max_width, estimated_lines)

    # Fill lines with words according to widths
    lines = []
    word_idx = 0

    for target_width in widths:
        if word_idx >= len(words):
            break

        line = []
        line_len = 0

        while word_idx < len(words):
            word = words[word_idx]
            new_len = line_len + len(word) + (1 if line else 0)

            if new_len <= target_width or not line:
                line.append(word)
                line_len = new_len
                word_idx += 1
            else:
                break

        if line:
            lines.append(' '.join(line))

    # Handle remaining words
    while word_idx < len(words):
        remaining = ' '.join(words[word_idx:])
        wrapped = textwrap.wrap(remaining, width=max_width)
        lines.extend(wrapped)
        break

    # Center the output
    if center:
        output_lines = []
        for line in lines:
            padding = (max_width - len(line)) // 2
            output_lines.append(' ' * padding + line)
        return '\n'.join(output_lines)
    else:
        return '\n'.join(lines)


def list_shapes():
    """Show all available shapes with a preview."""
    sample = "The key to power is the ability to judge who is best able to further your interests in all situations. Keep friends for friendship but work with the skilled and competent."

    shapes = [
        "diamond", "hourglass", "triangle", "inverted-triangle",
        "vase", "hexagon", "arrow", "wave", "circle",
        "claw", "shield", "bolt", "brain", "tower"
    ]

    for s in shapes:
        print(f"\n{'=' * 60}")
        print(f"  {s.upper()}")
        print(f"{'=' * 60}")
        print(shape_text(sample, shape=s, max_width=50))
        print()


def main():
    parser = argparse.ArgumentParser(description="Text Shape Generator (Robert Greene style)")
    parser.add_argument("text", nargs="?", help="Text to shape")
    parser.add_argument("--shape", "-s", default="diamond",
                        choices=["diamond", "hourglass", "triangle", "inverted-triangle",
                                 "vase", "hexagon", "arrow", "wave", "circle", "rectangle",
                                 "claw", "shield", "bolt", "brain", "tower"],
                        help="Shape to use (default: diamond)")
    parser.add_argument("--width", "-w", type=int, default=60, help="Max width in characters")
    parser.add_argument("--file", "-f", help="Read text from file")
    parser.add_argument("--list", "-l", action="store_true", help="Show all shapes with preview")
    parser.add_argument("--no-center", action="store_true", help="Left-align instead of center")

    args = parser.parse_args()

    if args.list:
        list_shapes()
        return

    text = args.text
    if args.file:
        with open(args.file) as f:
            text = f.read()
    elif not text and not sys.stdin.isatty():
        text = sys.stdin.read()

    if not text:
        parser.print_help()
        return

    text = ' '.join(text.split())  # normalize whitespace
    result = shape_text(text, shape=args.shape, max_width=args.width, center=not args.no_center)
    print(result)


if __name__ == "__main__":
    main()
