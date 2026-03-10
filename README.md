# colorpick

Color format converter, palette generator, and contrast checker.

One file. Zero deps. Speaks color.

## Usage

```bash
# Convert between formats
python3 colorpick.py "#ff6600"
python3 colorpick.py "rgb(255,102,0)"
python3 colorpick.py "hsl(24,100%,50%)"
python3 colorpick.py tomato

# Mix colors
python3 colorpick.py mix "#ff0000" "#0000ff"

# Generate palette
python3 colorpick.py palette "#ff6600" 5

# WCAG contrast ratio
python3 colorpick.py contrast white "#333"
```

## Features

- Hex, RGB, HSL, named colors (30+)
- Color mixing with ratio
- Palette generation (hue rotation)
- WCAG AA/AAA contrast checking
- Terminal color swatches

## Requirements

Python 3.8+. No dependencies.

## License

MIT
