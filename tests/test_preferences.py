"""Run from the project root: python -m unittest discover -s tests -v"""

import tempfile
import unittest
from pathlib import Path

from PySide6.QtCore import QSettings

from core.preferences import Preferences


class PreferencesTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.settings_path = str(Path(self.temp_directory.name) / "test.ini")
        self.settings = QSettings(self.settings_path, QSettings.Format.IniFormat)
        self.preferences = Preferences(self.settings)
        self.languages = {"en": {}, "es": {}}

    def test_default_language_is_english(self):
        self.assertEqual(self.preferences.load_language(self.languages), "en")

    def test_selected_language_persists(self):
        self.preferences.save_language("es")
        new_settings = QSettings(self.settings_path, QSettings.Format.IniFormat)
        reloaded = Preferences(new_settings)
        self.assertEqual(reloaded.load_language(self.languages), "es")

    def test_unknown_language_falls_back_to_english(self):
        self.settings.setValue(Preferences.LANGUAGE_KEY, "not-supported")
        self.assertEqual(self.preferences.load_language(self.languages), "en")

    def test_first_launch_real_shutdown_is_off(self):
        self.assertFalse(self.preferences.load_real_shutdown())

    def test_real_shutdown_on_is_persisted(self):
        self.preferences.save_real_shutdown(True)
        restarted = Preferences(
            QSettings(self.settings_path, QSettings.Format.IniFormat)
        )
        self.assertTrue(restarted.load_real_shutdown())

    def test_real_shutdown_off_is_persisted(self):
        self.preferences.save_real_shutdown(True)
        self.preferences.save_real_shutdown(False)
        restarted = Preferences(
            QSettings(self.settings_path, QSettings.Format.IniFormat)
        )
        self.assertFalse(restarted.load_real_shutdown())

    def test_string_false_is_not_interpreted_as_true(self):
        self.settings.setValue(Preferences.SHUTDOWN_MODE_KEY, "false")
        self.assertFalse(self.preferences.load_real_shutdown())

    def test_non_boolean_shutdown_mode_is_rejected(self):
        with self.assertRaises(TypeError):
            self.preferences.save_real_shutdown("true")

    def test_empty_language_is_rejected(self):
        with self.assertRaises(ValueError):
            self.preferences.save_language("")


if __name__ == "__main__":
    unittest.main()
