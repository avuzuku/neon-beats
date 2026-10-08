# 🎵 Neon Beats

A lightweight and modern desktop music player with a cyberpunk-inspired animated neon audio visualizer.  
Built with **Python**, **CustomTkinter**, and **Pygame**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)
![Audio](https://img.shields.io/badge/Audio-Pygame--CE-red)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- 🎨 **Modern Dark UI:** Sleek, rounded interface styled with CustomTkinter.
- ⚡ **Animated Neon Spectrum:** Custom canvas-based visualizer reacting to playback with smooth height interpolation (lerp) and idle decay.
- 📂 **Playlist Management:** Batch load audio files (`.mp3`, `.wav`, `.ogg`) and launch tracks via double-click.
- 🎛️ **Playback Controls:** Play, pause, skip, and volume slider.
- 💻 **Cross-Platform:** Runs natively on both Windows and Linux.

---

## 🚀 Quick Start (Running from Source)

### 1. Clone Repository
```bash
git clone https://github.com/avuzuku/neon-beats.git
cd neon-beats

2. Setup Environment

On Windows (CMD / PowerShell):

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python player.py

On Linux (Arch / Ubuntu):

# On Arch: sudo pacman -S tk sdl2_mixer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python player.py

📦 Building Standalone Executable
🪟 Windows (.exe)

Run natively in PowerShell or Command Prompt:

pip install pyinstaller
pyinstaller --noconsole --onefile --clean --collect-all customtkinter --collect-all pygame player.py

Output: dist\player.exe
🐧 Linux Binary

pip install pyinstaller
pyinstaller --noconsole --onefile --clean --collect-all customtkinter --collect-all pygame player.py

Output: dist/player
📄 License

This project is licensed under the MIT License — see the LICENSE file for details.
