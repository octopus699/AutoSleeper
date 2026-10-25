"""Resolve QSS asset URLs for both source runs and PyInstaller bundles.

Qt style-sheet URLs can otherwise depend on the process working directory.
Only local references under assets/ are rewritten. No settings are saved here.
"""

import re
from pathlib import Path

_ASSET_URL = re.compile(
    r"url\(\s*(?P<quote>['\"]?)(?P<path>(?:\./)?assets/[^)\"']+?)(?P=quote)\s*\)",
    flags=re.IGNORECASE,
)


def load_qss_with_assets(qss_path: Path, project_root: Path) -> str:
    """Read a QSS file and anchor `url(assets/...)` at the bundled root.

    Keep nonexistent references unchanged: styling may use runtime resources
    or optional files. The spec includes all common assets extensions.
    """
    stylesheet = Path(qss_path).read_text(encoding="utf-8-sig")
    root = Path(project_root).resolve()
    assets_root = (root / "assets").resolve()

    def substitute(match: re.Match[str]) -> str:
        relative = match.group("path").removeprefix("./")
        file_path = (root / relative.strip()).resolve()
        if not file_path.is_relative_to(assets_root) or not file_path.is_file():
            return match.group(0)
        # QSS understands a file:/// URI; encode spaces/non-ASCII safely.
        return f'url("{file_path.as_uri()}")'

    return _ASSET_URL.sub(substitute, stylesheet)
