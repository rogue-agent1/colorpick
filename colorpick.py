#!/usr/bin/env python3
"""colorpick - Color conversion and palette toolkit.

Convert between color formats, generate palettes, analyze contrast. Zero deps.
"""

import argparse
import colorsys
import math
import re
import sys


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    return f"#{r:02X}{g:02X}{b:02X}"


def rgb_to_hsl(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    return round(h * 360), round(s * 100), round(l * 100)


def hsl_to_rgb(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
    return round(r * 255), round(g * 255), round(b * 255)


def parse_color(s):
    s = s.strip()
    if s.startswith("#") or re.match(r'^[0-9a-fA-F]{3,6}$', s):
        return hex_to_rgb(s)
    m = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', s)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    m = re.match(r'hsl\((\d+),\s*(\d+)%?,\s*(\d+)%?\)', s)
    if m:
        return hsl_to_rgb(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    # Named colors
    names = {"red": (255,0,0), "green": (0,128,0), "blue": (0,0,255),
             "white": (255,255,255), "black": (0,0,0), "yellow": (255,255,0),
             "cyan": (0,255,255), "magenta": (255,0,255), "orange": (255,165,0),
             "purple": (128,0,128), "pink": (255,192,203), "gray": (128,128,128)}
    if s.lower() in names:
        return names[s.lower()]
    raise ValueError(f"Cannot parse color: {s}")


def swatch(r, g, b):
    return f"\033[48;2;{r};{g};{b}m    \033[0m"


def luminance(r, g, b):
    def lin(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast_ratio(c1, c2):
    l1 = luminance(*c1)
    l2 = luminance(*c2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def cmd_convert(args):
    r, g, b = parse_color(args.color)
    h, s, l = rgb_to_hsl(r, g, b)
    hsv_h, hsv_s, hsv_v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

    print(f"  {swatch(r, g, b)} {rgb_to_hex(r, g, b)}")
    print(f"  HEX:  {rgb_to_hex(r, g, b)}")
    print(f"  RGB:  rgb({r}, {g}, {b})")
    print(f"  HSL:  hsl({h}, {s}%, {l}%)")
    print(f"  HSV:  hsv({round(hsv_h*360)}, {round(hsv_s*100)}%, {round(hsv_v*100)}%)")
    print(f"  Lum:  {luminance(r, g, b):.4f}")


def cmd_palette(args):
    r, g, b = parse_color(args.color)
    h, s, l = rgb_to_hsl(r, g, b)
    n = args.count or 5

    if args.type == "complement":
        colors = [(h, s, l), ((h + 180) % 360, s, l)]
    elif args.type == "analogous":
        colors = [((h + i * 30) % 360, s, l) for i in range(-1, 2)]
    elif args.type == "triadic":
        colors = [((h + i * 120) % 360, s, l) for i in range(3)]
    elif args.type == "shades":
        colors = [(h, s, max(5, l - i * (l // n))) for i in range(n)]
    elif args.type == "tints":
        colors = [(h, s, min(95, l + i * ((100 - l) // n))) for i in range(n)]
    else:  # monochromatic
        step = 80 // n
        start = max(10, l - (n // 2) * step)
        colors = [(h, s, min(95, start + i * step)) for i in range(n)]

    print(f"  {args.type} palette from {rgb_to_hex(r, g, b)}:\n")
    for ch, cs, cl in colors:
        cr, cg, cb = hsl_to_rgb(ch, cs, cl)
        print(f"  {swatch(cr, cg, cb)} {rgb_to_hex(cr, cg, cb)}  hsl({ch}, {cs}%, {cl}%)")


def cmd_contrast(args):
    c1 = parse_color(args.fg)
    c2 = parse_color(args.bg)
    ratio = contrast_ratio(c1, c2)

    print(f"  FG: {rgb_to_hex(*c1)} {swatch(*c1)}")
    print(f"  BG: {rgb_to_hex(*c2)} {swatch(*c2)}")
    print(f"  Ratio: {ratio:.2f}:1")
    print(f"  AA Normal:  {'✓' if ratio >= 4.5 else '✗'} (need 4.5:1)")
    print(f"  AA Large:   {'✓' if ratio >= 3.0 else '✗'} (need 3.0:1)")
    print(f"  AAA Normal: {'✓' if ratio >= 7.0 else '✗'} (need 7.0:1)")
    print(f"  AAA Large:  {'✓' if ratio >= 4.5 else '✗'} (need 4.5:1)")


def cmd_mix(args):
    c1 = parse_color(args.color1)
    c2 = parse_color(args.color2)
    ratio = args.ratio or 50
    t = ratio / 100
    r = round(c1[0] * (1-t) + c2[0] * t)
    g = round(c1[1] * (1-t) + c2[1] * t)
    b = round(c1[2] * (1-t) + c2[2] * t)
    print(f"  {swatch(*c1)} {rgb_to_hex(*c1)} + {swatch(*c2)} {rgb_to_hex(*c2)}")
    print(f"  = {swatch(r, g, b)} {rgb_to_hex(r, g, b)} ({ratio}% mix)")


def main():
    p = argparse.ArgumentParser(description="Color toolkit")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("convert", help="Convert color formats").add_argument("color")

    pp = sub.add_parser("palette", help="Generate palette")
    pp.add_argument("color")
    pp.add_argument("-t", "--type", default="monochromatic",
                    choices=["monochromatic", "complement", "analogous", "triadic", "shades", "tints"])
    pp.add_argument("-n", "--count", type=int, default=5)

    cp = sub.add_parser("contrast", help="Check WCAG contrast")
    cp.add_argument("fg")
    cp.add_argument("bg")

    mp = sub.add_parser("mix", help="Mix two colors")
    mp.add_argument("color1")
    mp.add_argument("color2")
    mp.add_argument("-r", "--ratio", type=int, default=50)

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)
    {"convert": cmd_convert, "palette": cmd_palette, "contrast": cmd_contrast, "mix": cmd_mix}[args.cmd](args)


if __name__ == "__main__":
    main()
