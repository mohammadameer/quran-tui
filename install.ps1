$ErrorActionPreference = "Stop"

$RepoUrl = "git+https://github.com/mohammadameer/quran-tui.git"

function Has-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Ensure-Python {
    if (Has-Command "py") { return }
    if (-not (Has-Command "winget")) {
        throw "Python launcher (py) and winget are missing. Install Python manually and rerun."
    }
    Write-Host "Installing Python..."
    winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements | Out-Null
}

function Ensure-Git {
    if (Has-Command "git") { return }
    if (Has-Command "winget") {
        Write-Host "Installing Git..."
        winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements | Out-Null
        return
    }
    throw "Git is missing and winget is not available. Install Git manually and rerun."
}

function Install-QuranTui {
    py -m pip install --user --upgrade pip pipx | Out-Null
    py -m pipx ensurepath | Out-Null
    py -m pipx install --force $RepoUrl
}

Ensure-Python
Ensure-Git
Install-QuranTui

Write-Host "Downloading Quran data..."
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + $env:Path
quran --download-data 2>$null

Write-Host "Installed. Run: quran"
