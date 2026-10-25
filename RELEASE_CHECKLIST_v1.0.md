# AutoSleeper v1.0.0 — Final Release Checklist

Do not publish a stable version while any safety-critical item remains unchecked.

## Code and build

- [ ] The `Preferences.load_real_shutdown()` startup failure is fixed and committed to `main`.
- [ ] `python -m unittest discover -s tests -v` finishes with `OK`.
- [ ] GitHub Actions **Test and build on Windows** succeeds on the exact commit to be tagged.
- [ ] The downloaded GitHub Actions artifact includes `AutoSleeper.exe` and `AutoSleeper.exe.sha256`.
- [ ] The executable opens from a separate folder without `assets`, `.venv`, or Python installed.
- [ ] Matrix theme, application icon, Spanish/English labels, and tray menu display correctly.

## Timer and safety

- [ ] On a Windows user account with **no saved settings**, Real shutdown starts **OFF**.
- [ ] A short countdown in OFF mode finishes **without** requesting Windows shutdown.
- [ ] Setting ON and accepting the confirmation persists after exit and relaunch.
- [ ] Setting OFF again persists after exit and relaunch.
- [ ] Rejecting the ON confirmation does **not** persist ON.
- [ ] Cancel Timer stops the countdown.
- [ ] Closing the window hides it to the system tray and keeps the active timer running.
- [ ] A second launch restores the existing process without creating another timer.
- [ ] Exit AutoSleeper stops the countdown and ends the process.
- [ ] Windows sleep/resume cancels the timer, without restarting it.
- [ ] Controlled real shutdown was tested after saving all work.
- [ ] Changing language persists across relaunches and the tray reflects the selected language.

## Release housekeeping

- [ ] The public README reflects **first-run OFF, remembered ON/OFF** (not the old default-ON behavior).
- [ ] `v1.0.0-rc1` is marked as superseded in its release notes because of the startup bug.
- [ ] `v1.0.0-rc2` has been validated, or any unresolved issue has been fixed before the stable tag.
- [ ] Decide whether the source should be open source. If yes, choose a license and add its actual `LICENSE` file before calling the repository open source.
- [ ] No `.venv`, temporary installers, secrets, or `dist` binaries are accidentally committed.
- [ ] Create and push `v1.0.0` only after checking all the above.
- [ ] Verify that GitHub Actions creates a release **draft** containing the EXE and checksum.
- [ ] Compare the checksum to the download, review the release notes, and only then click **Publish release**.

## SHA-256 verification (Windows PowerShell)

```powershell
Get-FileHash .\AutoSleeper.exe -Algorithm SHA256
Get-Content .\AutoSleeper.exe.sha256
```

Compare the displayed hexadecimal hashes; they must match.
