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
- Local files are saved in `~/.quran_tui/`.