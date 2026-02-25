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
