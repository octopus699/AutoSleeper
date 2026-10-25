# AutoSleeper v1.0.0 — First Stable Release

**AutoSleeper** is a lightweight, portable automatic shutdown timer for Windows, developed by Blackout Studios.

## Features

- Quick 15/30/45/60-minute shutdown presets and a custom HH:MM:SS countdown.
- Live countdown and estimated shutdown time.
- Windows system-tray integration, including timer status and cancellation.
- Single-instance protection: reopening AutoSleeper restores the existing window.
- Cancellation when Windows enters or resumes from sleep.
- English and Spanish user interface with persistent language selection.
- Separate test and real-shutdown modes, with the user's confirmed choice remembered.
- Matrix Green dark interface and a standalone Windows executable.

## Changes since the early release candidates

- Fixed the startup error caused by a missing `Preferences.load_real_shutdown()` method in an earlier build.
- Real shutdown defaults to **OFF when no preference has been saved**. The user's latest confirmed ON/OFF choice persists across launches.
- Automated Windows compilation and checksum generation with GitHub Actions.

## Download and run

1. Download `AutoSleeper.exe` from **Assets** below.
2. Run the executable on **64-bit Windows 10/11**. Python is not required.
3. Select a delay and check the Real shutdown switch before starting.

Optional: download `AutoSleeper.exe.sha256` and verify the executable's SHA-256 checksum.

## Important safety note

The first launch starts in test mode (**Real shutdown OFF**), but AutoSleeper **remembers a user's previously confirmed ON setting**. Always check the switch and save your work before starting a timer in real-shutdown mode. A countdown reaching zero in real mode requests an immediate Windows shutdown (`shutdown.exe /s /t 0`).

The executable is not digitally signed. Windows may display an unknown-publisher warning.

## Validation

**Publish as a stable release only after the v1.0 manual verification checklist has passed.** In particular, check the portable executable, test mode, settings persistence, single-instance behavior, sleep cancellation, and a controlled real-shutdown test on Windows.

Developed by **Blackout Studios**.
