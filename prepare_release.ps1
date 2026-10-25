# AutoSleeper release candidate preparation for Windows.
# Runs project tests, builds the portable executable, and writes its SHA-256.
# Does NOT upload, tag, or publish anything on GitHub.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root ".venv\Scripts\python.exe"
$builder = Join-Path $root "build_portable.ps1"
$exe = Join-Path $root "dist\AutoSleeper.exe"
$checksum = Join-Path $root "dist\AutoSleeper.exe.sha256"

if ($env:OS -ne "Windows_NT") {
    throw "Build this release on Windows."
}
if (-not (Test-Path -LiteralPath $python)) {
    throw "Missing .venv\Scripts\python.exe"
}
if (-not (Test-Path -LiteralPath $builder)) {
    throw "Missing build_portable.ps1"
}

Push-Location $root
try {
    Write-Host "[1/3] Running unit tests..."
    & $python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) {
        throw "Unit tests failed. No release generated."
    }

    Write-Host "[2/3] Building portable executable..."
    # The existing builder also runs tests, so skip that duplicate pass.
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $builder -SkipTests
    if ($LASTEXITCODE -ne 0) {
        throw "Portable build failed."
    }
    if (-not (Test-Path -LiteralPath $exe)) {
        throw "Expected executable was not created: $exe"
    }

    Write-Host "[3/3] Calculating SHA-256..."
    $hash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  AutoSleeper.exe" | Set-Content -LiteralPath $checksum -Encoding ASCII

    Write-Host "Executable: $exe"
    Write-Host "Checksum:   $checksum"
    Write-Host "SHA-256:    $hash"
    Write-Host "Next: run TEST_CHECKLIST.md on Windows before creating a GitHub release."
} finally {
    Pop-Location
}
