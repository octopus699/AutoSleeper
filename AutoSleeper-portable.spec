# -*- mode: python ; coding: utf-8 -*-
"""Build AutoSleeper as a single Windows executable (run via PyInstaller).

Run: python -m PyInstaller --noconfirm --clean AutoSleeper-portable.spec
Set AUTOSLEEPER_CONSOLE=1 for a diagnostic console build.
"""

import os
from pathlib import Path

ROOT = Path(SPECPATH).resolve()
ASSETS = ROOT / "assets"
UI = ROOT / "ui"
ICON = ASSETS / "AutoSleeper.ico"

# Fail early rather than silently shipping a broken window or tray icon.
required = [
    ROOT / "main.py",
    UI / "styles.qss",
    ASSETS / "logo.png",
    ASSETS / "blackout_logo.png",
    ICON,
]
missing = [str(item.relative_to(ROOT)) for item in required if not item.is_file()]
if missing:
    raise SystemExit("Missing AutoSleeper project resources: " + ", ".join(missing))

# Keep the original assets/ui folder structure in the bundle. In a one-file
# build these are extracted to PyInstaller's temporary bundle directory.
asset_extensions = {".png", ".jpg", ".jpeg", ".webp", ".ico", ".svg", ".gif", ".bmp"}
data_files = [
    (str(path), str(path.parent.relative_to(ROOT)))
    for path in sorted(ASSETS.rglob("*"))
    if path.is_file() and path.suffix.lower() in asset_extensions
]
data_files += [
    (str(path), str(path.parent.relative_to(ROOT)))
    for path in sorted(UI.rglob("*.qss"))
    if path.is_file()
]

console_mode = os.environ.get("AUTOSLEEPER_CONSOLE") == "1"

analysis = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=data_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="AutoSleeper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=console_mode,
    icon=str(ICON),
    uac_admin=False,
)
