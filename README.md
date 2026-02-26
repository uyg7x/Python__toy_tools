# Python__toy_tools
                                                              tools help to sort your problem...

A lightweight overlay window that displays the current cursor position:
X: <value>px
Y: <value>px

Features

Live cursor coordinates (pixels)
Smooth refresh (~30–33 FPS)
Press Esc to close  

Requirements
Python 3.9+ recommended

Install dependency:
pip install pyautogui

Run
cd cursor_px
python cursor_px.py

Notes

On some systems, pyautogui may require additional OS permissions (Accessibility / Screen Recording) to read cursor position.
If you package this later, add a small icon + “always on top” option.


                                                                    # People Sorter (Python)

Sort a CSV of **Full Name, DOB, Marital Status, Address** into **A–Z order by Full Name** (Address as tie-breaker) and export a clean output CSV.

## Run

```bash
python sort_people.py
```

## Input / Output

* **Input:** `people.csv` (or rename `sample_people.csv` → `people.csv`)
* **Output:** `people_sorted.csv`

## Notes

* Addresses can contain spaces (OK).
* If output shows only header, fix CSV line breaks (one record per line).
* Use **fake/sample data only** (don’t upload real personal info).


   # SysPulse ⚡ — System Monitor GUI (Python)

A modern **Task Manager–style** desktop app built with **Python + CustomTkinter**.
Live **CPU / RAM / Disk / Network / Battery**, **real-time charts**, **active connections viewer**, and **CSV export** — clean, fast, and portfolio-ready.

<img width="631" height="502" alt="Screenshot 2026-02-27 003240" src="https://github.com/user-attachments/assets/689dbfdd-62da-4abb-8294-dde066c41e30" />

## Features

* ⏱️ Updates every **1s**
* 📊 Mini charts (last ~60s): CPU, RAM, Net Up/Down
* 🌐 Active connections: PID + process + local/remote + status
* 🪫 Battery status + time left (if available)
* 📁 Export: snapshot CSV (+ optional Windows app-usage CSV)

## Run

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

## Build EXE (Windows)

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name SysPulse app/main.py
```

## Privacy

Runs **locally**. No data is uploaded. Exports are saved to `reports/`.

