# Socratic Debug Installer for Windows (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Installing Socratic Debug on Windows..."
Write-Host "----------------------------------------"

# Verify Python
if (-not (Get-Command py -ErrorAction SilentlyContinue) -and -not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python 3 was not found in your PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.10 or newer from python.org and try again."
    Exit 1
}

$PyCmd = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }

# Prefer pipx if installed
if (Get-Command pipx -ErrorAction SilentlyContinue) {
    Write-Host "Found pipx, installing globally in isolated environment..."
    pipx install socratic-debug --force
    Write-Host ""
    Write-Host "Socratic Debug installed successfully via pipx." -ForegroundColor Green
    Write-Host "Run 'socratic --help' to get started."
    Exit 0
}

# Fallback: create isolated virtualenv in $HOME\.socratic\env
$InstallDir = Join-Path $HOME ".socratic\env"
$ScriptsDir = Join-Path $InstallDir "Scripts"

Write-Host "Creating isolated environment at $InstallDir..."
& $PyCmd -m venv $InstallDir

Write-Host "Installing socratic-debug and dependencies..."
$PipExe = Join-Path $ScriptsDir "pip.exe"
& $PipExe install --upgrade pip --quiet
& $PipExe install socratic-debug --quiet

# Add Scripts directory to User PATH if not already present
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$ScriptsDir*") {
    Write-Host "Adding $ScriptsDir to User PATH..."
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$ScriptsDir", "User")
    $env:Path += ";$ScriptsDir"
}

Write-Host ""
Write-Host "Socratic Debug installed successfully." -ForegroundColor Green
Write-Host "Run 'socratic --help' to get started."
Write-Host ""
