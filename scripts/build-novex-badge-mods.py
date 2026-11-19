#!/usr/bin/env python3
"""Build NOVEX badge jars for every Fabric version in the launcher's catalog."""
from __future__ import annotations

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


def fetch_json(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def catalog_versions() -> list[str]:
    catalog = fetch_json(CATALOG_URL)
    versions: set[str] = set()
    unsupported_major_versions: set[str] = set()
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
            if major >= 26:
                unsupported_major_versions.add(version)
            else:
                versions.add(version)

    if unsupported_major_versions:
        raise RuntimeError(
            "The launcher catalog includes Minecraft 26.x Fabric targets "
            f"({', '.join(sorted(unsupported_major_versions))}). Those versions use "
            "the new unobfuscated Minecraft namespace and need a separate source port; "
            "the legacy Yarn-based badge mod cannot safely be reused."
        )

    def key(value: str):
        return tuple(int(part) for part in value.split("."))

    return sorted(versions, key=key)


def latest_yarn(version: str) -> str:
    entries = fetch_json(f"{FABRIC_META}/yarn/{version}")
    stable = next((item for item in entries if item.get("stable")), None)
    selected = stable or (entries[0] if entries else None)
    if not selected:
        raise RuntimeError(f"No Yarn mappings published for Minecraft {version}")
    return selected.get("maven") or selected.get("version")


def latest_loader(version: str) -> str:
    entries = fetch_json(f"{FABRIC_META}/loader/{version}")
    stable = next((item for item in entries if item.get("loader", {}).get("stable")), None)
    selected = stable or (entries[0] if entries else None)
    if not selected:
        raise RuntimeError(f"No Fabric Loader build published for Minecraft {version}")
    return selected["loader"]["version"]


def java_release(version: str) -> int:
    parts = tuple(int(part) for part in version.split("."))
    # Minecraft 1.20.5+ requires Java 21; earlier releases run on Java 17.
    if parts[0] == 1 and (parts[1], parts[2] if len(parts) > 2 else 0) >= (20, 5):
        return 21
    return 17


def main() -> int:
    versions = catalog_versions()
    if not versions:
        raise RuntimeError(f"No legacy Fabric Minecraft versions were found in {CATALOG_URL}")

    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    for stale in STAGE_DIR.glob("novex-badges-*.jar"):
        stale.unlink()

    built: list[str] = []
    for version in versions:
        yarn = latest_yarn(version)
        loader = latest_loader(version)
        release = java_release(version)
        print(
            f"\n=== Building NOVEX Badges for Minecraft {version} "
            f"(Yarn {yarn}, Fabric Loader {loader}, Java release {release}) ===",
            flush=True,
        )
        command = [
            "gradle", "--no-daemon", "-p", str(MOD_DIR), "clean", "build",
            f"-Pminecraft_version={version}",
            f"-Pyarn_mappings={yarn}",
            f"-Ploader_version={loader}",
            f"-Pjava_release={release}",
        ]
        subprocess.run(command, cwd=ROOT, check=True)
        built_jar = MOD_DIR / "build" / "libs" / "novex-badges-0.1.0.jar"
        if not built_jar.is_file() or built_jar.stat().st_size == 0:
            raise RuntimeError(f"Gradle did not produce a non-empty badge jar for Minecraft {version}")
        staged = STAGE_DIR / f"novex-badges-{version}.jar"
        shutil.copy2(built_jar, staged)
        built.append(version)
        print(f"Staged {staged.relative_to(ROOT)} ({staged.stat().st_size} bytes)", flush=True)

    (STAGE_DIR / "novex-badge-versions.txt").write_text(
        "\n".join(built) + "\n", encoding="utf-8"
    )
    print(f"\nBuilt {len(built)} Fabric badge mod variants: {', '.join(built)}")
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
