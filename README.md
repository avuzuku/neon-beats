# 🎵 Neon Beats Pro

> A modern, feature-packed desktop audio player with an animated neon visualizer and local state persistence.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)
![Pygame](https://img.shields.io/badge/Audio-Pygame--CE-red)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)


> **Note:** This is an educational project created for learning purposes.

---

## ✨ Features

- 🎨 **Modern Dark UI** — Minimalist interface with rounded styling built with CustomTkinter.
- ⚡ **Neon Audio Spectrum** — Animated equalizer canvas with smooth height interpolation (lerp) and 4 color themes.
- 💾 **State Persistence** — Automatically remembers playlist, volume, shuffle/repeat toggles, and last active track.
- 🔍 **Real-Time Search** — Instantly filter playlist tracks as you type.
- 📁 **Batch & Folder Import** — Add individual tracks or recursively scan folders (`.mp3`, `.wav`, `.ogg`, `.flac`).
- ⏱️ **Timeline Scrubber** — Interactive seek bar with current and total duration indicators.
- 🔀 **Playback Modes** — Shuffle and repeat mode toggles.
- ⌨️ **Keyboard Controls** — Full hotkey support for smooth hands-on-keyboard control.

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| `Space` | Play / Pause |
| `Left` / `Right` | Seek backward / forward 5 seconds |
| `Up` / `Down` | Volume up / down (±5%) |
| `M` | Mute / Unmute |
| `Delete` | Remove selected track from playlist |

---

## 🚀 Quick Start (From Source)

### 1. Clone repository

```bash
git clone https://github.com/avuzuku/neon-beats.git
cd neon-beats
```

### 2. Run application

#### 🪟 Windows (CMD / PowerShell)
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python player.py
```

#### 🐧 Linux (Arch / Ubuntu)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python player.py
```

---

## 📦 Building Standalone Executables

#### 🪟 Windows (.exe)
```cmd
pip install pyinstaller
pyinstaller --noconsole --onefile --clean --collect-all customtkinter --collect-all pygame player.py
```
Output: `dist\player.exe`

#### 🐧 Linux Binary
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --clean --collect-all customtkinter --collect-all pygame player.py
```
Output: `dist/player`

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
