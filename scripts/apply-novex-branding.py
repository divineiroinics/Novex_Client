#!/usr/bin/env python3
"""Rebuild NOVEX icons and reapply the display-name overlay after upstream sync."""
from pathlib import Path
import base64
import json
import re
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
for size, name in [(32,"32x32.png"),(64,"64x64.png"),(128,"128x128.png"),(256,"128x128@2x.png"),(512,"512x512.png"),(512,"icon.png"),(50,"StoreLogo.png"),(32,"tray.png")]:
    render(size).save(icons / name, format="PNG", optimize=True)
master = render(512)
master.save(icons / "icon.ico", format="ICO", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
master.save(icons / "icon.icns", format="ICNS")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{raw.width}" height="{raw.height}" '
       f'viewBox="0 0 {raw.width} {raw.height}"><image width="{raw.width}" height="{raw.height}" '
       f'href="data:image/webp;base64,{base64.b64encode(SOURCE.read_bytes()).decode("ascii")}"/></svg>')
for path in [APP/"assets"/"logo.svg", APP/"assets"/"icons"/"icon-logo.svg", APP/"assets"/"icons"/"pixel"/"icon-logo.svg"]:
    path.write_text(svg, encoding="utf-8")

# Change user-facing message values without changing internal translation keys.
lang_path = APP / "lang" / "en_us.json"
if lang_path.exists():
    messages = json.loads(lang_path.read_text(encoding="utf-8"))
    def rebrand_values(value):
        if isinstance(value, dict):
            return {key: rebrand_values(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rebrand_values(item) for item in value]
        if isinstance(value, str):
            return value.replace("OneClient", "NOVEX Client")
        return value
    lang_path.write_text(json.dumps(rebrand_values(messages), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Keep the public package identity stable if upstream changes it.
manifest = APP / "Cargo.toml"
if manifest.exists():
    content = manifest.read_text(encoding="utf-8")
    for pattern, replacement in [
        (r'(?m)^product-name\s*=\s*"[^"]*"', 'product-name = "NOVEX Client"'),
        (r'(?m)^identifier\s*=\s*"[^"]*"', 'identifier = "org.xirx.NOVEXClient"'),
        (r'(?m)^publisher\s*=\s*"[^"]*"', 'publisher = "XIRX"'),
    ]:
        content = re.sub(pattern, replacement, content, count=1)
    manifest.write_text(content, encoding="utf-8")

print("NOVEX branding overlay applied.")
