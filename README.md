# Quran TUI

Quran terminal app with clean, fast navigation.

## Features

- Browse all surahs.
- Mushaf-style reading view.
- Active ayah highlighting.
- Fuzzy verse search.
- Direct surah jump.
- Resume from last reading.
- Works on common terminals and systems.

## One-line install

Linux:
```bash
(command -v apt-get >/dev/null && sudo apt-get update && sudo apt-get install -y python3 python3-pip pipx) || (command -v dnf >/dev/null && sudo dnf install -y python3 python3-pip pipx) || (command -v pacman >/dev/null && sudo pacman -Sy --noconfirm python python-pip python-pipx); python3 -m pipx ensurepath; pipx install "git+https://github.com/mohammadameer/quran-tui.git"
```

macOS:
```bash
brew install python pipx && pipx ensurepath && pipx install "git+https://github.com/mohammadameer/quran-tui.git"
```

Windows (PowerShell):
```powershell
winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements; py -m pip install --user pipx; py -m pipx ensurepath; pipx install "git+https://github.com/mohammadameer/quran-tui.git"
```

## Run

```bash
quran-tui
```

## Controls

- `↑ / ↓` or `j / k`: move.
- `tab`: switch pane.
- `n / p`: next or previous surah.
- `/`: fuzzy search verse text.
- `g`: jump to surah number.
- `enter`: open selected search result.
- `b`: back to browse mode.
- `r`: resume from saved reading position.
- `q`: quit.

## Notes

- First run downloads Quran text from API and caches it locally.
- Local files are saved in `~/.quran-tui/`.
- Old `~/.quran_tui/` data auto-migrates on next run.
- On start, app checks for updates and asks: Enter/y to update, n to skip.