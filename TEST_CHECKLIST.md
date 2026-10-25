# AutoSleeper v1.0.0-rc1 — Windows validation checklist

Run all tests on a Windows computer. Start with **Real shutdown OFF**.

- [ ] `python -m unittest discover -s tests -v` completes with `OK`.
- [ ] PyInstaller completes and creates `dist\AutoSleeper.exe`.
- [ ] Copy the executable to an unrelated folder (e.g., Desktop), without `assets/` or `.venv/`, and launch it.
- [ ] AutoSleeper's own icon appears in the taskbar and system tray.
- [ ] All fonts, colors, QSS effects, logo images, and footer appear correctly.
- [ ] A 10-second timer in test mode ends **without** shutting down Windows.
- [ ] A running countdown continues while the window is hidden to the system tray.
- [ ] Double-clicking the tray icon restores the window.
- [ ] Reopening the `.exe` restores the existing window rather than creating a second process or timer.
- [ ] Cancel Timer stops an active countdown immediately.
- [ ] Exit AutoSleeper closes the process and cancels the countdown.
- [ ] Switching to Spanish and restarting AutoSleeper retains Spanish.
- [ ] System tray text reflects the selected language and active countdown.
- [ ] Suspending then resuming Windows cancels the timer permanently.
- [ ] On a machine with all work saved, an intentional test with Real shutdown ON shuts down Windows at the expected time.
- [ ] After that test, AutoSleeper still starts and handles a new timer correctly.
- [ ] SHA-256 checksum in `dist\AutoSleeper.exe.sha256` matches the distributed executable.

**Do not publish as a stable release if any safety-critical test fails.**
