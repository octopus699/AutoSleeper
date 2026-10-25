
import tempfile
import unittest

from pathlib import Path

from core.bundle_resources import load_qss_with_assets


class BundleResourceTests(unittest.TestCase):

    def test_qss_paths_are_absolute_and_other_urls_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            (root / "assets").mkdir()
            (root / "ui").mkdir()

            icon = root / "assets" / "sleep icon.png"
            icon.touch()

            style = root / "ui" / "styles.qss"
            style.write_text(
                "QWidget {image: url('assets/sleep icon.png'); "
                "border-image: url(:/icons/qt.png);}",
                encoding="utf-8",
            )

            result = load_qss_with_assets(style, root)

            self.assertIn(icon.resolve().as_uri(), result)
            self.assertIn("url(:/icons/qt.png)", result)

    def test_missing_asset_is_left_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            (root / "ui").mkdir()

            style = root / "ui" / "styles.qss"
            style.write_text(
                "url(assets/optional.png)",
                encoding="utf-8",
            )

            self.assertEqual(
                load_qss_with_assets(style, root),
                "url(assets/optional.png)",
            )


if __name__ == "__main__":
    unittest.main()
