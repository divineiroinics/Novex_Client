#!/usr/bin/env python3
"""Rebuild NOVEX icons and reapply the display-name/update overlay after upstream sync."""
from pathlib import Path
from io import BytesIO
import base64
import json
import re
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "branding" / "novex-mark.png"
APP = ROOT / "packages" / "oneclient_app"
with Image.open(SOURCE) as source_image:
    source_image.verify()
raw = Image.open(SOURCE).convert("RGBA")
if raw.width < 128 or raw.height < 128:
    raise SystemExit("Canonical NOVEX logo source is unexpectedly small")

# Crop transparent padding from the supplied emblem before scaling. This makes
# the mark visibly fill Windows taskbar/tray icon slots instead of appearing tiny.
alpha_bounds = raw.getchannel("A").getbbox()
if alpha_bounds:
    raw = raw.crop(alpha_bounds)

def render(size: int) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mark = raw.copy()
    edge = max(1, round(size * 1.00))
    mark.thumbnail((edge, edge), Image.Resampling.LANCZOS)
    canvas.alpha_composite(mark, ((size - mark.width) // 2, (size - mark.height) // 2))
    if size <= 32:
        # Keep the angular NOVEX mark crisp at Windows shortcut/taskbar sizes.
        canvas = canvas.filter(ImageFilter.UnsharpMask(radius=0.7, percent=180, threshold=2))
    return canvas

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

png_buffer = BytesIO()
raw.save(png_buffer, format="PNG", optimize=True)
png_data = base64.b64encode(png_buffer.getvalue()).decode("ascii")
svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{raw.width}" height="{raw.height}" '
    f'viewBox="0 0 {raw.width} {raw.height}"><image width="{raw.width}" height="{raw.height}" '
    f'href="data:image/png;base64,{png_data}"/></svg>'
)
for path in [
    APP / "assets" / "logo.svg",
    APP / "assets" / "icons" / "icon-logo.svg",
    APP / "assets" / "icons" / "pixel" / "icon-logo.svg",
    APP / "icons" / "OneClient.icon" / "Assets" / "novex-mark.svg",
    APP / "icons" / "OneClient.icon" / "Assets" / "oneclient-mark.svg",
]:
    path.write_text(svg, encoding="utf-8")

# Use the exact same canonical NOVEX emblem for the in-game nameplate and Tab glyph.
# A 16px source with a 12px font height keeps the mark legible beside Minecraft names.
badge_root = ROOT / "novex-badge-mod" / "src" / "main" / "resources" / "assets" / "novex_badges"
badge_image = render(16)
badge_image.save(badge_root / "novex_badge.png", format="PNG", optimize=True)
(badge_root / "textures").mkdir(parents=True, exist_ok=True)
badge_image.save(badge_root / "textures" / "novex_badge.png", format="PNG", optimize=True)
font_path = badge_root / "font" / "badge.json"
font = json.loads(font_path.read_text(encoding="utf-8"))
font["providers"][0]["ascent"] = 10
font["providers"][0]["height"] = 12
font_path.write_text(json.dumps(font, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

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
    lang_path.write_text(
        json.dumps(rebrand_values(messages), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

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

# Keep the launcher label shown in diagnostics branded without renaming internal crates.
common_constants = ROOT / "packages" / "oneclient_common" / "src" / "constants.rs"
if common_constants.exists():
    content = common_constants.read_text(encoding="utf-8")
    content = content.replace('    "OneClient v",', '    "NOVEX Client v",')
    common_constants.write_text(content, encoding="utf-8")

# Keep updater URLs pointed at NOVEX, but never ship an unverified update key.
constants = APP / "src" / "constants.rs"
if constants.exists():
    content = constants.read_text(encoding="utf-8")
    def set_const(source: str, name: str, expression: str) -> str:
        # Remove every old definition, including option_env! expressions.
        # The previous literal-only matcher could append duplicate constants.
        pattern = rf'(?ms)^pub const {name}: &str =.*?;[ \t]*(?:\n|$)'
        source = re.sub(pattern, "", source)
        return source.rstrip() + "\n\n" + f"pub const {name}: &str = {expression};" + "\n"

    content = set_const(
        content, "UPDATER_ENDPOINT",
        '"https://github.com/divineiroinics/Novex_Client/releases/latest/download/latest.json"',
    )
    content = set_const(
        content, "UPDATER_PUBKEY",
        'match option_env!("NOVEX_UPDATER_PUBKEY") { Some(value) => value, None => "" }',
    )
    constants.write_text(content, encoding="utf-8")
    for name in ("UPDATER_ENDPOINT", "UPDATER_PUBKEY"):
        count = len(re.findall(rf"(?m)^pub const {name}:", content))
        if count != 1:
            raise SystemExit(f"Expected exactly one {name} definition, found {count}")

# Rebrand literal UI/runtime strings throughout source without renaming internal
# Rust crate/module/type identifiers that are part of upstream architecture.
string_literal = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')
for source_root in [ROOT / "packages"]:
    for source_path in source_root.rglob("*"):
        if not source_path.is_file() or source_path.suffix not in {".rs", ".toml", ".json", ".plist", ".xml", ".yml", ".yaml"}:
            continue
        try:
            source = source_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        def rebrand_literal(match):
            value = match.group(1)
            value = value.replace("OneClient", "NOVEX Client").replace("One Client", "NOVEX Client")
            # Replace public-facing organization labels, but preserve URLs and
            # legally required upstream copyright / license attribution.
            if "Polyfrost" in value and "://" not in value and not re.search(
                r"(?i)copyright|copyright holder|license|licence|attribution|\u00a9|\(c\)|contributors",
                value,
            ):
                value = value.replace("Polyfrost", "XIRX")
            return '"' + value + '"'

        updated = string_literal.sub(rebrand_literal, source)
        if updated != source:
            source_path.write_text(updated, encoding="utf-8")

print("NOVEX branding overlay applied; app icons, launcher logos, in-game nameplate and Tab badge assets regenerated; legal attribution preserved.")
