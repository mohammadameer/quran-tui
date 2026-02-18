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

## One-line install (different systems)

Linux/macOS:
```bash
python3 -m pip install --user pipx && python3 -m pipx ensurepath && pipx install "git+https://github.com/mohammadameer/quran-cli.git"
```

Windows PowerShell:
```powershell
py -m pip install --user pipx; py -m pipx ensurepath; pipx install "git+https://github.com/mohammadameer/quran-cli.git"
```

Windows CMD:
```bat
py -m pip install --user pipx && py -m pipx ensurepath && pipx install "git+https://github.com/mohammadameer/quran-cli.git"
```

Local repo (dev/test):
```bash
pipx install .
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