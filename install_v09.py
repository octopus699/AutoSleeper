"""Non-destructive v0.9 patch to load QSS assets from packaged paths.

Only imports core.bundle_resources and replaces the existing QSS reader.
Does not change timers, modes, tray, language or visual design.
"""

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.py"
MODULE = ROOT / "core" / "bundle_resources.py"

IMPORT_LINE = "from core.bundle_resources import load_qss_with_assets"
OLD_LOADER = 'styles.append(qss_path.read_text(encoding="utf-8"))'
NEW_LOADER = "styles.append(load_qss_with_assets(qss_path, root))"


def patch_source(source: str) -> tuple[str, bool]:
    """Return (patched_text, changed); fail atomically on unexpected format."""
    has_import = IMPORT_LINE in source
    has_new_loader = NEW_LOADER in source
    if has_import and has_new_loader:
        return source, False
    if has_import or has_new_loader:
        raise ValueError("Partially installed v0.9 patch; inspect main.py manually.")

    if source.count(OLD_LOADER) != 1:
        raise ValueError("Cannot find the exact existing QSS loader once in main.py.")
    marker = "from core.power_events import WindowsPowerEvents"
    if source.count(marker) != 1:
        raise ValueError("Cannot find expected power-events import in main.py.")
    source = source.replace(marker, IMPORT_LINE + "\n" + marker, 1)
    source = source.replace(OLD_LOADER, NEW_LOADER, 1)
    return source, True


def main() -> int:
    if not MAIN.is_file() or not MODULE.is_file():
        print("ERROR: Extract this ZIP into the AutoSleeper project root first.")
        return 1

    original_bytes = MAIN.read_bytes()
    has_bom = original_bytes.startswith(b"\xef\xbb\xbf")
    try:
        updated, changed = patch_source(original_bytes.decode("utf-8-sig"))
        if not changed:
            print("v0.9 QSS resource loader already installed. No changes.")
            return 0
        compile(updated, str(MAIN), "exec")
    except (UnicodeError, ValueError, SyntaxError) as exc:
        print(f"ERROR: {exc}. main.py was not changed.")
        return 1

    backups = Path(tempfile.gettempdir()) / "AutoSleeper_backups"
    backups.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup = backups / f"main_before_v09_{stamp}.py"
    shutil.copy2(MAIN, backup)

    temp = MAIN.with_name("main.py.v09tmp")
    try:
        contents = updated.encode("utf-8")
        if has_bom:
            contents = b"\xef\xbb\xbf" + contents
        temp.write_bytes(contents)
        os.replace(temp, MAIN)
    except OSError as exc:
        print(f"ERROR: Unable to patch main.py: {exc}")
        print(f"Backup: {backup}")
        return 1
    finally:
        temp.unlink(missing_ok=True)

    print("v0.9 installed: QSS asset links now work from external folders.")
    print(f"Backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
