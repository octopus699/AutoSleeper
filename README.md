# AutoSleeper

A lightweight Windows shutdown timer developed by **Blackout Studios** using Python and PySide6.

AutoSleeper can shut down Windows after a selected countdown, while keeping its interface accessible from the system tray.

## Features

- Quick presets: 15, 30, 45, or 60 minutes.
- Custom countdown: hours, minutes, and seconds.
- Remaining-time display and expected shutdown time.
- Windows system tray with countdown status, restore, cancel, and exit actions.
- Single-instance protection: launching AutoSleeper again restores the existing window.
- Automatic cancellation when Windows suspends or resumes.
- English and Spanish interface, with the selected language remembered using `QSettings`.
- Real-shutdown mode and a separate test mode.
- Portable build for Windows using PyInstaller.

## Download and run

After the first release has been published, download `AutoSleeper.exe` from the GitHub **Releases** section. Save it in any folder and run it. No separate Python installation is required.

The executable must be built on Windows; test the built executable on Windows 10/11 before release. The current build targets the architecture of the Python environment used to package it.

## Usage

1. Open AutoSleeper.
2. Choose a preset, or select **Set Custom** to enter a duration.
3. Check the **Real shutdown** switch before starting. When this switch is ON, reaching zero can shut down Windows immediately.
4. Start the timer. You may hide the application with **X**; it continues running in the system tray.
5. To stop the timer, select **Cancel Timer** in the window or tray menu. Use **Exit AutoSleeper** to quit completely.

> **Important:** In the current configuration, *Real shutdown* starts **ON** by default. Save your work before starting a timer. Switch it **OFF** when testing the application. The shutdown command does not forcibly close applications; Windows may delay or prevent shutdown when unsaved work is present.

## Development

Requires Python 3.13 and project dependencies installed in a virtual environment.

```powershell
.\.venv\Scripts\python.exe main.py
```

Run tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Build on Windows:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build_portable.ps1
```

Output: `dist\AutoSleeper.exe`.

## Project status

Preparing the first Windows release candidate. The source, automated tests, and portable build configuration are maintained in this repository. Real shutdown, Windows power events, and the packaged executable must be validated on Windows before the initial stable release.

## License

No open-source license has been selected yet. Add an appropriate `LICENSE` file before distributing the source code under an open-source license.
