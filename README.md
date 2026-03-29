<p align="center">
  <img src="app_background.jpg" alt="Brightness Manager" width="100%">
</p>

<p align="center">
  <strong>Multi-monitor brightness & color temperature control for Windows</strong>
</p>

<p align="center">
  <a href="#features">Features</a> &bull;
  <a href="#installation">Installation</a> &bull;
  <a href="#development">Development</a> &bull;
  <a href="#languages">Languages</a> &bull;
  <a href="#license">License</a>
</p>

---

## Features

- **Multi-monitor support** — Control brightness and color temperature per monitor or all at once
- **5 built-in presets** — Day, Office, Night, Reading, Movie — one click to switch
- **Color temperature filter** — Warm overlay from 1000K to 6500K to reduce blue light
- **System tray integration** — Runs in background, double-click to open, right-click for quick menu
- **Auto-start with Windows** — Optional startup toggle
- **15 languages** — English, Turkce, Deutsch, Francais, Espanol, Italiano, Portugues, Russian, Japanese, Korean, Chinese, Arabic, Hindi, Nederlands, Polski

## Installation

### From Release

Download the latest installer from [Releases](https://github.com/Rounted/Brightness-Manager/releases).

### Build from Source (Tauri)

**Requirements:** [Rust](https://rustup.rs/), [Node.js](https://nodejs.org/)

```bash
cd src-tauri
cargo install tauri-cli
cargo tauri build
```

The installer will be in `src-tauri/target/release/bundle/nsis/`.

### Build from Source (PyQt5)

**Requirements:** [Python 3.10+](https://python.org/)

```bash
pip install -r requirements.txt
python main.py
```

## Development

```
brightness-app/
├── src/                    # Tauri web frontend
│   ├── index.html          # Main UI
│   ├── main.js             # App logic
│   ├── lang.js             # Translations (15 languages)
│   ├── overlay.html        # Screen overlay
│   └── styles.css          # Styling
├── src-tauri/
│   └── src/
│       ├── lib.rs          # Tauri commands
│       ├── config.rs       # Config persistence
│       ├── overlay.rs      # Per-monitor overlay windows
│       └── tray.rs         # System tray menu
├── main.py                 # PyQt5 entry point
├── tray_app.py             # PyQt5 tray integration
├── settings_window.py      # PyQt5 settings UI
├── gamma_controller.py     # PyQt5 overlay controller
├── config.py               # PyQt5 config management
└── lang.py                 # PyQt5 translations
```

## Languages

| Language | Code |
|----------|------|
| English | `en` |
| Turkce | `tr` |
| Deutsch | `de` |
| Francais | `fr` |
| Espanol | `es` |
| Italiano | `it` |
| Portugues | `pt` |
| Russian | `ru` |
| Japanese | `ja` |
| Korean | `ko` |
| Chinese | `zh` |
| Arabic | `ar` |
| Hindi | `hi` |
| Nederlands | `nl` |
| Polski | `pl` |

## License

MIT
