"""Safe tests. These never invoke shutdown.exe on the real machine."""
import subprocess
import unittest
from unittest.mock import patch

from core.shutdown_manager import ShutdownExecutionError, ShutdownManager


class ShutdownManagerTests(unittest.TestCase):

    def test_starts_in_real_mode(self):
        manager = ShutdownManager()

        self.assertTrue(manager.real_enabled)


    def test_test_mode_does_not_shutdown(self):
        manager = ShutdownManager()
        manager.set_real_mode(False)

        with patch("core.shutdown_manager.subprocess.run") as run:
            self.assertFalse(manager.request_shutdown())
            run.assert_not_called()


    def test_real_mode_uses_immediate_non_force_command(self):
        manager = ShutdownManager()
        manager.set_real_mode(True)
        with patch("core.shutdown_manager.os.name", "nt"):
            with patch("core.shutdown_manager.subprocess.run") as run:
                run.return_value.returncode = 0
                self.assertTrue(manager.request_shutdown())
                args = run.call_args.args[0]
                self.assertEqual(args, ["shutdown.exe", "/s", "/t", "0"])
                self.assertNotIn("/f", args)

    def test_failure_reports_error(self):
        manager = ShutdownManager()
        manager.set_real_mode(True)
        with patch("core.shutdown_manager.os.name", "nt"):
            with patch("core.shutdown_manager.subprocess.run") as run:
                run.return_value.returncode = 5
                run.return_value.stderr = "Access denied"
                with self.assertRaisesRegex(ShutdownExecutionError, "Access denied"):
                    manager.request_shutdown()

    def test_timeouts_report_error(self):
        manager = ShutdownManager()
        manager.set_real_mode(True)
        with patch("core.shutdown_manager.os.name", "nt"):
            with patch("core.shutdown_manager.subprocess.run") as run:
                run.side_effect = subprocess.TimeoutExpired("shutdown.exe", 10)
                with self.assertRaises(ShutdownExecutionError):
                    manager.request_shutdown()


if __name__ == "__main__":
    unittest.main()
