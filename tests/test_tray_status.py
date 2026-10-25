"""Tests for the non-Qt status calculation used by the system tray."""

import unittest

from core.tray_status import build_tray_display, format_remaining
from ui.translations import TRANSLATIONS


class TrayStatusTests(unittest.TestCase):

    @staticmethod
    def t(language):
        return lambda key, **values: TRANSLATIONS[language][key].format(**values)

    def test_initial_state(self):
        result = build_tray_display(
            deadline=None, status_key="ready", real_enabled=True,
            translate=self.t("en"), now=100.0,
        )
        self.assertEqual(result.message, "No active timer")
        self.assertFalse(result.can_cancel)

    def test_active_test_countdown(self):
        result = build_tray_display(
            deadline=166.3, status_key="timer_running", real_enabled=False,
            translate=self.t("en"), now=100.0,
        )
        self.assertEqual(result.message, "Shutdown in 00:01:07 (test mode)")
        self.assertTrue(result.can_cancel)
        self.assertEqual(result.remaining_seconds, 67)

    def test_real_countdown_in_spanish(self):
        result = build_tray_display(
            deadline=101.0, status_key="timer_running_real", real_enabled=True,
            translate=self.t("es"), now=100.0,
        )
        self.assertEqual(result.message, "Apagado en 00:00:01 (apagado real)")

    def test_sleep_cancelled_state(self):
        result = build_tray_display(
            deadline=None, status_key="sleep_cancelled", real_enabled=True,
            translate=self.t("es"), now=100.0,
        )
        self.assertIn("Suspensión", result.message)
        self.assertFalse(result.can_cancel)

    def test_finished_status_and_language(self):
        for language in ("en", "es"):
            with self.subTest(language=language):
                result = build_tray_display(
                    deadline=None, status_key="timer_finished", real_enabled=False,
                    translate=self.t(language), now=100.0,
                )
                self.assertEqual(result.message, self.t(language)("timer_finished"))

    def test_unknown_status_falls_back_to_idle(self):
        result = build_tray_display(
            deadline=None, status_key="some_new_status", real_enabled=True,
            translate=self.t("en"), now=100.0,
        )
        self.assertEqual(result.message, "No active timer")

    def test_duration_above_24_hours(self):
        self.assertEqual(format_remaining(90061), "25:01:01")

    def test_expired_timer_is_zero_not_negative(self):
        result = build_tray_display(
            deadline=99.0, status_key="timer_running", real_enabled=True,
            translate=self.t("en"), now=100.0,
        )
        self.assertEqual(result.remaining_seconds, 0)
        self.assertIn("00:00:00", result.message)


if __name__ == "__main__":
    unittest.main()
