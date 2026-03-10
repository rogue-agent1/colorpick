#!/usr/bin/env python3
"""colorpick - Color format converter and palette tool.

One file. Zero deps. Speaks color.

Usage:
  colorpick.py "#ff6600"                → all formats
  colorpick.py "rgb(255,102,0)"         → all formats
  colorpick.py "hsl(24,100%,50%)"       → all formats
  colorpick.py red                      → named color
  colorpick.py mix "#ff0000" "#0000ff"  → blend colors
  colorpick.py palette "#ff6600" 5      → generate palette
  colorpick.py contrast "#fff" "#000"   → contrast ratio
"""

import argparse
import colorsys
import json
import re
import sys

NAMED = {
    "black": (0,0,0), "white": (255,255,255), "red": (255,0,0),
    "green": (0,128,0), "blue": (0,0,255), "yellow": (255,255,0),
    "cyan": (0,255,255), "magenta": (255,0,255), "orange": (255,165,0),
    "purple": (128,0,128), "pink": (255,192,203), "brown": (165,42,42),
    "gray": (128,128,128), "grey": (128,128,128), "lime": (0,255,0),
    "navy": (0,0,128), "teal": (0,128,128), "olive": (128,128,0),
    "maroon": (128,0,0), "silver": (192,192,192), "coral": (255,127,80),
    "salmon": (250,128,114), "gold": (255,215,0), "indigo": (75,0,130),
    "violet": (238,130,238), "turquoise": (64,224,208), "tan": (210,180,140),
    "tomato": (255,99,71), "skyblue": (135,206,235), "plum": (221,160,221),
}


def parse_color(s: str) -> tuple[int, int, int]:
    s = s.strip().lower()

    if s in NAMED:
        return NAMED[s]

    # Hex
    m = re.match(r'^#?([0-9a-f]{6})$', s)
    if m:
        h = m.group(1)
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    m = re.match(r'^#?([0-9a-f]{3})$', s)
    if m:
        h = m.group(1)
        return int(h[0]*2, 16), int(h[1]*2, 16), int(h[2]*2, 16)

    # rgb(r, g, b)
    m = re.match(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', s)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))

    # hsl(h, s%, l%)
    m = re.match(r'hsl\(\s*(\d+)\s*,\s*(\d+)%?\s*,\s*(\d+)%?\s*\)', s)
    if m:
        h, sat, l = int(m.group(1)), int(m.group(2)), int(m.group(3))
        r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, sat / 100)
        return int(r * 255), int(g * 255), int(b * 255)

    raise ValueError(f"Cannot parse color: {s}")


def rgb_to_hex(r, g, b) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsl(r, g, b) -> tuple[int, int, int]:
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    return int(h * 360), int(s * 100), int(l * 100)


def luminance(r, g, b) -> float:
    def lin(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast_ratio(c1, c2) -> float:
    l1 = luminance(*c1)
    l2 = luminance(*c2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def swatch(r, g, b) -> str:
    return f"\033[48;2;{r};{g};{b}m    \033[0m"


def show_color(r, g, b, label=""):
    h, s, l = rgb_to_hsl(r, g, b)
    hex_c = rgb_to_hex(r, g, b)
    if label:
        print(f"  {label}")
    print(f"  {swatch(r,g,b)} {hex_c}  rgb({r},{g},{b})  hsl({h},{s}%,{l}%)")


def cmd_convert(args):
    try:
        r, g, b = parse_color(args.color)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    if args.json:
        h, s, l = rgb_to_hsl(r, g, b)
        print(json.dumps({"hex": rgb_to_hex(r,g,b), "rgb": [r,g,b], "hsl": [h,s,l]}))
    else:
        show_color(r, g, b)
    return 0


def cmd_mix(args):
    try:
        c1 = parse_color(args.color1)
        c2 = parse_color(args.color2)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    ratio = args.ratio
    r = int(c1[0] * (1-ratio) + c2[0] * ratio)
    g = int(c1[1] * (1-ratio) + c2[1] * ratio)
    b = int(c1[2] * (1-ratio) + c2[2] * ratio)
    show_color(r, g, b, f"Mix ({int((1-ratio)*100)}:{int(ratio*100)})")
    return 0


def cmd_palette(args):
    try:
        r, g, b = parse_color(args.color)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    n = args.count
    for i in range(n):
        new_h = (h + i / n) % 1.0
        nr, ng, nb = colorsys.hls_to_rgb(new_h, l, s)
        show_color(int(nr*255), int(ng*255), int(nb*255))
    return 0


def cmd_contrast(args):
    try:
        c1 = parse_color(args.fg)
        c2 = parse_color(args.bg)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    ratio = contrast_ratio(c1, c2)
    aa_normal = "✓" if ratio >= 4.5 else "✗"
    aa_large = "✓" if ratio >= 3.0 else "✗"
    aaa_normal = "✓" if ratio >= 7.0 else "✗"
    print(f"  Contrast ratio: {ratio:.2f}:1")
    print(f"  AA  normal: {aa_normal}  large: {aa_large}")
    print(f"  AAA normal: {aaa_normal}")
    return 0


def main():
    argv = sys.argv[1:]
    subcmds = {"mix", "palette", "contrast"}

    if argv and argv[0] not in subcmds and argv[0] not in ('-h', '--help'):
        parser = argparse.ArgumentParser()
        parser.add_argument("color")
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args(argv)
        return cmd_convert(args)

    parser = argparse.ArgumentParser(description="Color format converter")
    sub = parser.add_subparsers(dest="command")

    m = sub.add_parser("mix", help="Blend two colors")
    m.add_argument("color1")
    m.add_argument("color2")
    m.add_argument("--ratio", type=float, default=0.5)

    p = sub.add_parser("palette", help="Generate color palette")
    p.add_argument("color")
    p.add_argument("count", type=int, nargs="?", default=5)

    c = sub.add_parser("contrast", help="WCAG contrast ratio")
    c.add_argument("fg")
    c.add_argument("bg")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1
    return {"mix": cmd_mix, "palette": cmd_palette, "contrast": cmd_contrast}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
