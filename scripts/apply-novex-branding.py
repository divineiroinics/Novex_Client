#!/usr/bin/env python3
"""Rebuild NOVEX app icons from the canonical, user-approved emblem."""
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "branding" / "novex-mark.png"
APP = ROOT / "packages" / "oneclient_app"
raw = Image.open(SOURCE).convert("RGBA")
# Keep the source's black canvas and proportions; fit, never crop or redraw.
def render(size):
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    mark = raw.copy()
    mark.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas.alpha_composite(mark, ((size-mark.width)//2, (size-mark.height)//2))
    return canvas.convert("RGB")

icons = APP / "icons"
for size, name in [(32,"32x32.png"),(64,"64x64.png"),(128,"128x128.png"),(256,"128x128@2x.png"),(512,"512x512.png"),(512,"icon.png"),(50,"StoreLogo.png"),(32,"tray.png")]:
    render(size).save(icons / name, format="PNG", optimize=True)
render(512).save(icons / "icon.ico", format="ICO", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{raw.width}" height="{raw.height}" viewBox="0 0 {raw.width} {raw.height}"><image width="{raw.width}" height="{raw.height}" href="data:image/png;base64,{base64.b64encode(SOURCE.read_bytes()).decode("ascii")}"/></svg>'''
for path in [APP/"assets"/"logo.svg", APP/"assets"/"icons"/"icon-logo.svg", APP/"assets"/"icons"/"pixel"/"icon-logo.svg"]:
    path.write_text(svg, encoding="utf-8")
print("NOVEX emblem applied to PNG, ICO and SVG app assets.")
