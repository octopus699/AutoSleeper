# AutoSleeper

**A lightweight automatic shutdown timer for Windows.**  
Developed by **Blackout Studios** with Python and PySide6.

AutoSleeper lets you schedule a Windows shutdown using a quick preset or a custom countdown. Its dark Matrix Green interface can be hidden to the system tray without interrupting the timer.

## Features

- **Quick timers:** 15, 30, 45, and 60 minutes.
- **Custom countdown:** hours, minutes, and seconds.
- **Live display:** remaining time and estimated shutdown clock time.
- **System tray:** keep the countdown running while the window is hidden; restore, cancel, or exit from the tray menu.
- **Single instance:** launching AutoSleeper again restores the existing window instead of starting another timer.
- **Sleep handling:** cancels the active countdown when Windows suspends; it does not resume automatically.
- **Languages:** English and Spanish, with the language choice saved between launches.
- **Shutdown preference:** separate test mode and real-shutdown mode, with the user's last choice saved between launches.
- **Portable executable:** run the Windows build without installing Python.

## Download

Download **`AutoSleeper.exe`** from the **Releases** section of this repository. The release may also include **`AutoSleeper.exe.sha256`** for integrity verification.

The provided build targets **64-bit Windows 10/11**. It is not digitally signed; Windows might show an unknown-publisher warning. Obtain the executable from this project's release page and check its checksum if needed.

## Getting started

1. Open `AutoSleeper.exe`.
2. Select a preset, or choose **Set Custom** to specify a duration.
3. Check **Real shutdown** before starting: **OFF** means a test countdown without shutting down Windows; **ON** allows the countdown to shut down Windows.
4. Start the countdown. Closing the window with **X** hides it to the Windows system tray.
5. Choose **Cancel Timer** to stop the countdown, or **Exit AutoSleeper** from the tray menu to exit completely.

### Safety and saved preferences

- On a **first launch with no saved preferences**, Real shutdown is **OFF**.
- The application **remembers the last confirmed ON/OFF setting**, even after a restart. If you previously enabled real shutdown, it may therefore open in **ON** mode on the next launch.
- Switching to ON requires confirmation. If you decline, the previous setting is retained.
- A running timer is **not** saved or resumed after exiting.
- Windows sleep/resume cancels an active timer instead of continuing it.
- Real shutdown uses `shutdown.exe /s /t 0` when the countdown reaches zero. It does not request forced application closure, but you should **save all work** before allowing shutdown.

## Development

Requires **Python 3.13** on Windows and the project's Python dependencies.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Run the tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Build a portable executable:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\prepare_release.ps1
```

The generated executable is placed in `dist\AutoSleeper.exe`. Building for Windows requires Windows.

## Automated builds

The workflow at `.github/workflows/windows-build.yml` runs tests and builds the Windows executable for pushes and version tags. Version tags also create a **draft** GitHub Release for manual review; drafts are not automatically published.


## License

AutoSleeper is open-source software licensed under the
[MIT License](LICENSE).

Copyright © 2026 Blackout Studios.



