# Quran TUI

A terminal-based Quran reader with Arabic text, English translation, and fuzzy search.

## Features

- Browse all 114 surahs
- Read with Arabic text and English translation (M.A.S. Abdel Haleem)
- Fuzzy verse search
- Resume from last reading position
- Bismillah displayed separately
- Auto-update support
- Works on Linux, macOS, and Windows

## Install

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/mohammadameer/quran-tui/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/mohammadameer/quran-tui/main/install.ps1 | iex
```

**With pip/pipx:**
```bash
pipx install git+https://github.com/mohammadameer/quran-tui.git
```

## Usage

```bash
quran                    # Start the app
quran --version          # Show version
quran --refresh-cache    # Re-download Quran data
quran --rtl-mode raw     # Use native terminal BiDi (for iTerm2, kitty)
quran --plain            # Disable colors
```

## Controls

| Key | Action |
|-----|--------|
| `↑/k` | Previous ayah |
| `↓/j` | Next ayah |
| `n` | Next surah |
| `p` | Previous surah |
| `Tab` | Switch pane |
| `/` | Search |
| `g` | Jump to surah |
| `r` | Resume reading |
| `b` | Back to browse |
| `q` | Quit |

## RTL Display

Arabic text display depends on your terminal. Try different modes if text looks wrong:

```bash
quran --rtl-mode auto     # Default: reshape + bidi
quran --rtl-mode raw      # For terminals with native BiDi (iTerm2, kitty, mlterm)
quran --rtl-mode reshape  # Connected glyphs only
```

## Data

- Quran text and translation from [quran.com API](https://quran.com)
- Data cached locally in `~/.quran-tui/`
- First run downloads ~3MB of data

## Requirements

- Python 3.10+
- Terminal with Unicode support

## Attribution

- Quran text: [quran.com](https://quran.com) - Uthmani script
- English translation: M.A.S. Abdel Haleem
- Arabic reshaping: [arabic-reshaper](https://github.com/mpcabd/python-arabic-reshaper)

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Please open an issue or PR.

## Disclaimer

This software is provided for educational purposes. Please verify Quranic text accuracy with authoritative sources. The developers are not responsible for any errors in the text.
