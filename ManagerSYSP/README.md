# SysPulse — System Monitor GUI (Python)

A modern **desktop system monitor** (Task Manager–style) built with **Python + CustomTkinter**.

It shows live stats (updates every 1s), mini-charts, active network connections, and (optional) Windows app-usage tracking.
Designed to look great in screenshots/GIFs for your GitHub profile.

## Features

### Live stats (refresh every 1 second)
- **CPU**: usage %, frequency, per-core usage
- **RAM**: used/total, %
- **Disk**: auto-detects drives (C:, D:, etc.) and shows used/free/%
- **Network**: upload/download speed (KB/s or MB/s) + totals
- **Battery** (laptops): % + charging + time left (when available)

### Visuals
- Mini charts (last ~60 seconds): **CPU, RAM, Net up/down**
- Status colors (OK / Warning / Critical)

### Network insights
- Active connections table: local → remote, state, PID + process name

### Productivity (optional)
- **Active app usage time** (Windows): tracks the **foreground window app** and time spent today
  - You can disable it in `app/config.py`.

### Reports
- Export current snapshot or daily summary to CSV in `reports/`.

## Privacy note
- SysPulse reads **system performance data** (CPU/RAM/Disk/Network) and **active connections** from your OS.
- Optional Windows “app usage” reads only the **active window title/process name** (no keystrokes).
- No data is uploaded anywhere. All exports are local CSV files.

## Tech stack
- UI: `customtkinter`
- System stats: `psutil`
- Charts: `matplotlib`
- Windows app usage (optional): `pywin32`

---

## Run locally

### 1) Create environment
```bash
python -m venv .venv
```

### 2) Activate
**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Start app
```bash
python -m app.main
```

---

## Build EXE (Windows) — optional

Install PyInstaller:
```bash
pip install pyinstaller
```

Build:
```bash
pyinstaller --noconsole --onefile --name SysPulse app/main.py
```

Your EXE will appear in `dist/`.

---

## Project structure
```text
SysPulse/
├─ app/
│  ├─ main.py
│  ├─ ui.py
│  ├─ monitor.py
│  ├─ window_tracker.py
│  ├─ exporter.py
│  ├─ config.py
│  └─ __init__.py
├─ reports/
├─ screenshots/
├─ requirements.txt
└─ README.md
```

## Screenshots / GIF
Add your screenshots in `screenshots/` and link them here in README.
