# AutoSleeper v1.0.0-rc1

**First release candidate — Windows portable executable**

AutoSleeper is a lightweight shutdown timer for Windows with a dark Matrix Green interface.

## Included features

- 15-, 30-, 45- and 60-minute presets, plus a custom HH:MM:SS timer.
- Remaining countdown and planned shutdown time.
- Background operation using the Windows system tray.
- Restore on second launch; one active process and timer at a time.
- Timer cancellation when Windows enters or resumes from sleep.
- Persistent English/Spanish language selection.
- Real-shutdown and test modes.
- Standalone Windows executable, with application assets and styles bundled.

## Installation

Download `AutoSleeper.exe` from the release assets and run it on Windows. Python is not required.

## Safety warning

**Real shutdown is ON by default in this build.** When a timer finishes, Windows may shut down immediately. Save your work before starting a timer. For testing, switch **Real shutdown** OFF.

## Known release-candidate limitations

- This build has not yet been confirmed on a separate Windows computer.
- The executable is not digitally signed; Windows SmartScreen may warn about an unknown publisher.
- A dedicated installer and automatic updates are not included.

This release should remain a **pre-release** until the manual validation checklist has passed.

Developed by **Blackout Studios**.
