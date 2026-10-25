param(
    [switch]$SkipTests,
    [switch]$Console
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root ".venv\Scripts\python.exe"
$spec = Join-Path $root "AutoSleeper-portable.spec"

if ($env:OS -ne "Windows_NT") {
    throw "Windows is required to build AutoSleeper.exe."
}
if (-not (Test-Path -LiteralPath $python)) {
    throw "Python virtual environment not found. Create .venv first."
}
if (-not (Test-Path -LiteralPath $spec)) {
    throw "AutoSleeper-portable.spec not found."
}

Push-Location $root
$oldConsole = $env:AUTOSLEEPER_CONSOLE
try {
    & $python -c "import PyInstaller, PySide6"
    if ($LASTEXITCODE -ne 0) {
        throw "Install build dependencies: .\.venv\Scripts\python.exe -m pip install -r requirements-build.txt"
    }

    if (-not $SkipTests -and (Test-Path -LiteralPath (Join-Path $root "tests"))) {
        & $python -m unittest discover -s tests -v
        if ($LASTEXITCODE -ne 0) {
            throw "Unit tests failed. Fix them before creating a release or use -SkipTests only for diagnosis."
        }
    }

    if ($Console) {
        $env:AUTOSLEEPER_CONSOLE = "1"
        Write-Host "Building with diagnostic console..."
    } else {
        $env:AUTOSLEEPER_CONSOLE = "0"
        Write-Host "Building windowed portable executable..."
    }

    & $python -m PyInstaller --noconfirm --clean --distpath (Join-Path $root "dist") --workpath (Join-Path $root "build") $spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed."
    }

    $exe = Join-Path $root "dist\AutoSleeper.exe"
    if (-not (Test-Path -LiteralPath $exe)) {
        throw "PyInstaller did not create dist\AutoSleeper.exe"
    }
    $file = Get-Item -LiteralPath $exe
    Write-Host "Build successful: $($file.FullName)"
    Write-Host "Size: $([math]::Round($file.Length / 1MB, 1)) MB"
    Write-Host "Test the EXE from another folder before publishing."
} finally {
    if ($null -eq $oldConsole) {
        Remove-Item Env:AUTOSLEEPER_CONSOLE -ErrorAction SilentlyContinue
    } else {
        $env:AUTOSLEEPER_CONSOLE = $oldConsole
    }
    Pop-Location
}
