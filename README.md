# 🔐 PyGenPass

A modern, desktop-based password generator built with Python and CustomTkinter. Features a sleek dark UI with purple accents, slot-machine animation, entropy display, coloured character preview, and password history.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.x-blueviolet)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **Slot-machine animation** – password "rolls" through random characters before revealing the final result
- **Strength meter** – 5-segment bar with labels: Very Weak → Very Strong
- **Entropy display** – shows bits of entropy (e.g. `89.6 bits`) for each generated password
- **Coloured character preview** – each character is colour-coded by type:
  - 🟡 Yellow – Uppercase (A–Z)
  - 🔴 Red – Lowercase (a–z)
  - 🟢 Teal – Digits (0–9)
  - 🌸 Pink – Special characters
- **Toggle switches** – pill-shaped toggles for selecting character types
- **Adjustable length** – slider from 3 to 30 characters with live display
- **Auto-regenerate** – password updates automatically when you change settings
- **History** – keeps last 10 passwords with strength, entropy, and time; copy any with one click
- **Keyboard shortcuts** – `Ctrl+G` generate, `Ctrl+C` copy, `Ctrl+H` clear history, `Enter` generate
- **Custom icon** – purple lock icon matching the app's colour palette

---

## 📸 Screenshot

![preview](preview.png)

---

## 🚀 Getting Started

### Requirements

- Python 3.10 or newer
- pip

### Installation

```bash
git clone https://github.com/theprzemoo/PyGenPass.git
cd PyGenPass
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

Or on Windows, double-click `run.bat`.

---

## 📁 Project Structure

```
PyGenPass/
├── main.py                # Main application
├── icon.ico               # App icon
├── run.bat                # Windows launcher
├── requirements.txt       # Dependencies
├── LICENSE                # MIT License
└── README.md              # This file
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+G` / `Enter` | Generate password |
| `Ctrl+C` | Copy to clipboard |
| `Ctrl+H` | Clear history |

---

## 🛠️ Built With

- [Python](https://www.python.org/) – core language
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) – modern UI framework
- [pyperclip](https://github.com/asweigart/pyperclip) – clipboard support

---

## 📄 License

This project is licensed under the MIT License – see [LICENSE](LICENSE) for details.

