# colorpick

Color conversion, palette generation, and WCAG contrast checker.

## Usage

```bash
python3 colorpick.py convert "#FF6B35"
python3 colorpick.py convert "rgb(52, 152, 219)"
python3 colorpick.py palette "#3498DB" -t triadic
python3 colorpick.py palette blue -t shades -n 7
python3 colorpick.py contrast white "#333"
python3 colorpick.py mix red blue -r 50
```

## Features

- Convert between HEX, RGB, HSL, HSV
- Named color support (red, blue, etc.)
- Palette generation (monochromatic, complement, analogous, triadic, shades, tints)
- WCAG contrast checking (AA/AAA)
- Color mixing with ratio
- True-color terminal swatches
- Luminance calculation
- Zero dependencies
