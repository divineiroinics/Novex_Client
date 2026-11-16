#!/usr/bin/env python3
"""Rebuild all NOVEX desktop icons from the canonical approved emblem."""
from pathlib import Path
import base64
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "branding" / "novex-mark.webp"
APP = ROOT / "packages" / "oneclient_app"
raw = Image.open(SOURCE).convert("RGBA")

def render(size: int) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    mark = raw.copy()
    mark.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas.alpha_composite(mark, ((size - mark.width) // 2, (size - mark.height) // 2))
    return canvas.convert("RGB")

icons = APP / "icons"
for size, name in [
    (32, "32x32.png"), (64, "64x64.png"), (128, "128x128.png"),
    (256, "128x128@2x.png"), (512, "512x512.png"), (512, "icon.png"),
    (50, "StoreLogo.png"), (32, "tray.png"),
]:
    render(size).save(icons / name, format="PNG", optimize=True)

master = render(512)
master.save(icons / "icon.ico", format="ICO",
            sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
master.save(icons / "icon.icns", format="ICNS")

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{raw.width}" height="{raw.height}" '
    f'viewBox="0 0 {raw.width} {raw.height}"><image width="{raw.width}" height="{raw.height}" '
    f'href="data:image/webp;base64,{base64.b64encode(SOURCE.read_bytes()).decode("ascii")}"/></svg>'
)
for path in [
    APP / "assets" / "logo.svg",
    APP / "assets" / "icons" / "icon-logo.svg",
    APP / "assets" / "icons" / "pixel" / "icon-logo.svg",
]:
    path.write_text(svg, encoding="utf-8")

print("NOVEX emblem applied to PNG, ICO, ICNS and SVG app assets.")
