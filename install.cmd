@echo off
setlocal

set REPO_URL=git+https://github.com/mohammadameer/quran-tui.git

where py >nul 2>nul
if %errorlevel% neq 0 (
  where winget >nul 2>nul
  if %errorlevel% neq 0 (
    echo Python launcher (py) and winget are missing. Install Python manually.
    exit /b 1
  )
  echo Installing Python...
  winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
)

where git >nul 2>nul
if %errorlevel% neq 0 (
  where winget >nul 2>nul
  if %errorlevel% neq 0 (
    echo Git is missing and winget is not available. Install Git manually.
    exit /b 1
  )
  echo Installing Git...
  winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
)

py -m pip install --user --upgrade pip pipx
if %errorlevel% neq 0 (
  echo Failed to install pipx.
  exit /b 1
)

py -m pipx ensurepath
py -m pipx install --force "%REPO_URL%"
if %errorlevel% neq 0 (
  echo Failed to install Quran TUI.
  exit /b 1
)

echo Installed Quran TUI.
echo Run: quran-tui
endlocal
