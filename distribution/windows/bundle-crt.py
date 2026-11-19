#!/usr/bin/env python3

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

BEGIN_RES = "# >>> CRT_RESOURCES >>>"
END_RES = "# <<< CRT_RESOURCES <<<"
BEGIN_SEC = "; >>> VC_REDIST_SECTION >>>"
END_SEC = "; <<< VC_REDIST_SECTION <<<"

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CARGO_TOML = REPO_ROOT / "packages" / "oneclient_app" / "Cargo.toml"
DEFAULT_OUT = REPO_ROOT / "target" / "crt"

VSWHERE = Path(
    r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
)
CRT_GLOB = r"VC\Redist\MSVC\**\x64\Microsoft.VC*.CRT\*.dll"

# NSIS runs this section during installation. The app-local DLLs below are the
# primary runtime fallback; this bootstrap also installs Microsoft's official
# x64 redistributable system-wide so other native apps can use it too.
SECTION_REPLACEMENT = r"""; >>> VC_REDIST_SECTION >>>
Section "-NOVEXVCppRuntime"
  SetRegView 64
  ReadRegDWORD $R0 HKLM "SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\X64" "Installed"
  ReadRegDWORD $R1 HKLM "SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\X64" "Major"
  ReadRegDWORD $R2 HKLM "SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\X64" "Minor"
  SetRegView lastused

  ; Skip installation when a sufficiently recent v14 x64 runtime is present.
  ${If} $R0 == 1
  ${AndIf} $R1 == 14
  ${AndIf} $R2 >= 40
    DetailPrint "Microsoft Visual C++ Runtime is already installed."
    Goto vcredist_done
  ${EndIf}

  DetailPrint "Downloading the official Microsoft Visual C++ Redistributable..."
  ; curl.exe is inbox on supported Windows 10/11 systems. Download only from
  ; Microsoft's stable aka.ms endpoint; never ship or execute an untrusted copy.
  ExecWait '"$SYSDIR\curl.exe" --fail --location --silent --show-error "https://aka.ms/vs/17/release/vc_redist.x64.exe" --output "$TEMP\NOVEX-vc_redist.x64.exe"' $R3
  ${If} $R3 != 0
    MessageBox MB_OK|MB_ICONSTOP "NOVEX could not download the Microsoft Visual C++ Runtime. Check your internet connection and run the installer again."
    Abort
  ${EndIf}

  DetailPrint "Installing Microsoft Visual C++ Redistributable (x64)..."
  ExecWait '"$TEMP\NOVEX-vc_redist.x64.exe" /install /quiet /norestart' $R3
  Delete "$TEMP\NOVEX-vc_redist.x64.exe"
  ; 0 = success, 3010 = success (restart required).
  ${If} $R3 != 0
  ${AndIf} $R3 != 3010
    MessageBox MB_OK|MB_ICONSTOP "The Microsoft Visual C++ Runtime installer failed (code $R3). NOVEX setup cannot continue."
    Abort
  ${EndIf}

  vcredist_done:
SectionEnd
; <<< VC_REDIST_SECTION <<<"""


def region(begin: str, end: str) -> re.Pattern:
    return re.compile(
        r"^[ \t]*" + re.escape(begin) + r".*?^[ \t]*" + re.escape(end) + r"[ \t]*$",
        re.DOTALL | re.MULTILINE,
    )


REGION_RES = region(BEGIN_RES, END_RES)
REGION_SEC = region(BEGIN_SEC, END_SEC)


def find_crt_dir() -> Path:
    """Locate the newest x64 Microsoft.VC*.CRT redist directory via vswhere."""
    if not VSWHERE.is_file():
        sys.exit(f"error: vswhere not found at {VSWHERE}; pass --crt-dir explicitly")

    out = subprocess.run(
        [str(VSWHERE), "-latest", "-products", "*", "-find", CRT_GLOB],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    dirs = {Path(line).parent for line in out.splitlines() if line.strip()}
    if not dirs:
        sys.exit(f"error: vswhere found no DLLs matching {CRT_GLOB}")

    def redist_version(path: Path) -> tuple[int, ...]:
        # The directory is nested below a version such as 14.50.35717.
        # Sorting full paths lexicographically misorders versions (for example,
        # 14.9 can sort after 14.50), potentially bundling an older CRT.
        for part in path.parts:
            if re.fullmatch(r"\d+(?:\.\d+){2,}", part):
                return tuple(int(component) for component in part.split("."))
        return ()

    versions = {path: redist_version(path) for path in dirs}
    if any(not version for version in versions.values()):
        missing = [str(path) for path, version in versions.items() if not version]
        sys.exit("error: could not parse a Visual C++ redist version from: " + ", ".join(missing))

    newest = max(dirs, key=lambda path: (versions[path], str(path).casefold()))
    print(f"CRT redist version: {'.'.join(map(str, versions[newest]))}")
    print(f"CRT redist dir: {newest}")
    return newest


def collect(crt_dir: Path, out_dir: Path) -> list[Path]:
    dlls = sorted(crt_dir.glob("*.dll"))
    if not dlls:
        sys.exit(f"error: no DLLs in {crt_dir}")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    copied = []
    for dll in dlls:
        dest = out_dir / dll.name
        shutil.copy2(dll, dest)
        copied.append(dest)
        print(f"  {dll.name} ({dest.stat().st_size} bytes)")
    return copied


def patch(cargo_toml: Path, dlls: list[Path]) -> None:
    text = cargo_toml.read_text(encoding="utf-8")
    for pat, name in ((REGION_RES, "CRT_RESOURCES"), (REGION_SEC, "VC_REDIST_SECTION")):
        if not pat.search(text):
            sys.exit(f"error: {name} region not found in {cargo_toml}")

    entries = "\n".join(
        f'  {{ src = "{str(d).replace(chr(92), chr(92) * 2)}", target = "{d.name}" }},'
        for d in dlls
    )
    block = (
        f"  {BEGIN_RES}\n"
        f"  # Generated by distribution/windows/bundle-crt.py -- do not edit by hand.\n"
        f"{entries}\n"
        f"  {END_RES}"
    )

    text = REGION_RES.sub(lambda _: block, text, count=1)
    text = REGION_SEC.sub(lambda _: SECTION_REPLACEMENT, text, count=1)
    cargo_toml.write_text(text, encoding="utf-8")
    print(f"patched {cargo_toml} with {len(dlls)} app-local CRT DLLs and enabled VC++ bootstrap")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cargo-toml", type=Path, default=DEFAULT_CARGO_TOML)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument(
        "--crt-dir",
        type=Path,
        help="Microsoft.VC*.CRT directory to copy from (default: ask vswhere)",
    )
    args = ap.parse_args()

    crt_dir = args.crt_dir.resolve() if args.crt_dir else find_crt_dir()
    dlls = collect(crt_dir, args.out_dir.resolve())
    patch(args.cargo_toml.resolve(), dlls)


if __name__ == "__main__":
    main()
