
# 🎵 Neon Beats

> A lightweight, modern desktop music player with a cyberpunk-style animated neon visualizer.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)
![Pygame](https://img.shields.io/badge/Audio-Pygame--CE-red)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- 🎨 **Modern Dark UI** — Rounded corners and clean dark styling powered by CustomTkinter.
- ⚡ **Neon Audio Spectrum** — Animated equalizer canvas with smooth height interpolation (lerp) and idle decay.
- 📂 **Playlist Support** — Multi-select audio files (`.mp3`, `.wav`, `.ogg`) and start playback via double-click.
- 🎛️ **Full Controls** — Play/pause, track skipping, and real-time volume slider.
- 💻 **Cross-Platform** — Built on Arch Linux, natively runs on Windows and Linux.

---

## 🚀 Quick Start (From Source)

### 1. Clone the repository
```bash
git clone https://github.com/avuzuku/neon-beats.git
cd neon-beats
```

### 2. Run the application

<details>
<summary><b>🪟 Windows (CMD / PowerShell)</b></summary>

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python player.py
```
</details>

<details>
<summary><b>🐧 Linux (Arch / Ubuntu)</b></summary>

```bash
# Arch dependencies: sudo pacman -S tk sdl2_mixer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python player.py
```
</details>

---

## 📦 Build Standalone Executables

<details>
<summary><b>🪟 Build for Windows (.exe)</b></summary>

Run natively inside PowerShell or Command Prompt:
```cmd
pip install pyinstaller
pyinstaller --noconsole --onefile --clean --collect-all customtkinter --collect-all pygame player.py
```
*Output file:* `dist\player.exe`
</details>

<details>
<summary><b>🐧 Build for Linux (Binary)</b></summary>

Run inside your terminal:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --clean --collect-all customtkinter --collect-all pygame player.py
```
*Output file:* `dist/player`
</details>

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
