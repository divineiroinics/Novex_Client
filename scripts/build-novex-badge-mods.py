#!/usr/bin/env python3
"""Build NOVEX badge jars for every Fabric version in the launcher's catalog."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_DIR = ROOT / "novex-badge-mod"
STAGE_DIR = ROOT / "packages" / "oneclient_core"
CATALOG_URL = "https://data-v2.polyfrost.org/oneclient/versions/metadata.json"
FABRIC_META = "https://meta.fabricmc.net/v2/versions"
USER_AGENT = "NOVEX-Client-Badge-Build/1.0"
PREVIEW_VERSION_RE = re.compile(
    r"^(?:1\\.\\d+(?:\\.\\d+)?|26\\.\\d+(?:\\.\\d+)?)-(?:snapshot-\\d+|pre-?\\d+|rc-?\\d+)$"
)


def fetch_json(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def catalog_versions() -> list[str]:
    catalog = fetch_json(CATALOG_URL)
    versions: set[str] = set()
    unsupported_versions: set[str] = set()
    for cluster in catalog.get("clusters", []):
        major = int(cluster["major_version"])
        for entry in cluster.get("entries", []):
            if str(entry.get("loader", "")).lower() != "fabric":
                continue
            minor = int(entry["minor_version"])
            patch = entry.get("patch_version")
            base = f"{major}.{minor}" if major >= 26 else f"1.{major}.{minor}"
            version = f"{base}.{int(patch)}" if patch is not None else base
            if not re.fullmatch(r"(?:1|[2-9][0-9]*)\.\d+(?:\.\d+)?", version):
                continue
            numeric = tuple(int(part) for part in version.split("."))
            if major == 1 and numeric[1] < 18:
                unsupported_versions.add(version)
            else:
                versions.add(version)

    if unsupported_versions:
        print(
            "Skipped because the current badge source requires Minecraft 1.18+: "
            + ", ".join(sorted(unsupported_versions)),
            flush=True,
        )

    # Preserve the four Minecraft versions already shipped by NOVEX even if
    # the remote catalog later removes them from its curated quick-pick list.
    versions.update({"1.21.1", "1.21.4", "1.21.5", "1.21.8"})

    def key(value: str):
        return tuple(int(part) for part in value.split("."))

    return sorted(versions, key=key)


def preview_versions() -> list[str]:
    """Return the newest Fabric preview for each supported namespace family.

    Keep previews out of signed releases. Nightly builds may include them when
    Fabric publishes mappings and the current badge source still compiles.
    """
    entries = fetch_json(f"{FABRIC_META}/game")
    selected: list[str] = []
    for family in ("26.", "1."):
        for item in entries:
            version = str(item.get("version", ""))
            if (
                item.get("stable") is False
                and version.startswith(family)
                and PREVIEW_VERSION_RE.fullmatch(version)
            ):
                selected.append(version)
                break
    return selected


def latest_yarn(version: str) -> str:
    entries = fetch_json(f"{FABRIC_META}/yarn/{version}")
    stable = next((item for item in entries if item.get("stable")), None)
    selected = stable or (entries[0] if entries else None)
    if not selected:
        raise RuntimeError(f"No Yarn mappings published for Minecraft {version}")
    return selected.get("version") or selected.get("maven", "").split(":")[-1]


def latest_loader(version: str) -> str:
    entries = fetch_json(f"{FABRIC_META}/loader/{version}")
    stable = next((item for item in entries if item.get("loader", {}).get("stable")), None)
    selected = stable or (entries[0] if entries else None)
    if not selected:
        raise RuntimeError(f"No Fabric Loader build published for Minecraft {version}")
    return selected["loader"]["version"]


def java_release(version: str) -> int:
    match = re.match(r"^(\\d+)\\.(\\d+)(?:\\.(\\d+))?", version)
    if not match:
        raise ValueError(f"Unsupported Minecraft version format: {version}")
    major, minor, patch = (int(part or 0) for part in match.groups())
    # Minecraft 26.x requires Java 25; 1.20.5+ requires Java 21;
    # earlier supported 1.x releases run on Java 17.
    if major >= 26:
        return 25
    if major == 1 and (minor, patch) >= (20, 5):
        return 21
    return 17

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--include-previews",
        action="store_true",
        help="best-effort build the newest Fabric snapshot/RC/pre-release for 1.x and 26.x",
    )
    args = parser.parse_args()

    versions = catalog_versions()
    if not versions:
        raise RuntimeError(f"No supported Fabric Minecraft versions were found in {CATALOG_URL}")

    previews: list[str] = []
    if args.include_previews:
        try:
            previews = preview_versions()
        except (
            urllib.error.URLError,
            json.JSONDecodeError,
            KeyError,
            ValueError,
            RuntimeError,
        ) as error:
            print(f"::warning::Could not discover Fabric preview versions; stable builds will continue: {error}")

    previews = [version for version in previews if version not in versions]
    all_versions = versions + previews
    preview_set = set(previews)

    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    for stale in STAGE_DIR.glob("novex-badges-*.jar"):
        stale.unlink()

    built: list[str] = []
    skipped_previews: list[str] = []
    for version in all_versions:
        is_preview = version in preview_set
        try:
            modern = version.startswith("26.")
            yarn = None if modern else latest_yarn(version)
            loader = latest_loader(version)
            release = java_release(version)
            mapping_mode = "official" if modern else "yarn"
            mixin_package = (
                "org.xirx.novexbadge.modern.mixin"
                if modern else "org.xirx.novexbadge.mixin"
            )
            mixin_compatibility = "JAVA_25" if modern else f"JAVA_{release}"
            print(
                f"\\n=== Building NOVEX Badges for Minecraft {version} "
                f"({mapping_mode} mappings, Fabric Loader {loader}, Java release {release}) ===",
                flush=True,
            )
            command = [
                "gradle", "--no-daemon", "-p", str(MOD_DIR), "clean", "build",
                f"-Pminecraft_version={version}",
                f"-Pmapping_mode={mapping_mode}",
                f"-Ploader_version={loader}",
                f"-Pjava_release={release}",
                f"-Pmixin_package={mixin_package}",
                f"-Pmixin_compatibility={mixin_compatibility}",
            ]
            if yarn:
                command.append(f"-Pyarn_mappings={yarn}")
            subprocess.run(command, cwd=ROOT, check=True)

            built_jar = MOD_DIR / "build" / "libs" / "novex-badges-0.1.0.jar"
            if not built_jar.is_file() or built_jar.stat().st_size == 0:
                raise RuntimeError(f"Gradle did not produce a non-empty badge jar for Minecraft {version}")
            staged = STAGE_DIR / f"novex-badges-{version}.jar"
            shutil.copy2(built_jar, staged)
            built.append(version)
            print(f"Staged {staged.relative_to(ROOT)} ({staged.stat().st_size} bytes)", flush=True)
        except (
            urllib.error.URLError,
            json.JSONDecodeError,
            KeyError,
            ValueError,
            RuntimeError,
            subprocess.CalledProcessError,
        ) as error:
            if not is_preview:
                raise
            skipped_previews.append(version)
            print(f"::warning::Skipping preview {version}; current badge sources are not compatible yet: {error}")

    (STAGE_DIR / "novex-badge-versions.txt").write_text(
        "\\n".join(built) + "\\n", encoding="utf-8"
    )
    print(f"\\nBuilt {len(built)} Fabric badge mod variants: {', '.join(built)}")
    if skipped_previews:
        print("Preview variants not built: " + ", ".join(skipped_previews))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        urllib.error.URLError,
        json.JSONDecodeError,
        KeyError,
        ValueError,
        RuntimeError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"::error::{error}", file=sys.stderr)
        raise SystemExit(1)
