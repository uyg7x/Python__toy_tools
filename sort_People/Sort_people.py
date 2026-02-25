import csv
from pathlib import Path

INPUT_FILE = "people.csv"
OUTPUT_FILE = "people_sorted.csv"

def norm(s: str) -> str:
    return (s or "").strip().lower()

def normalize_text(text: str) -> str:
    # If file contains literal "\n" sequences, convert them to real new lines
    if "\\n" in text and "\n" not in text:
        text = text.replace("\\n", "\n")
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text

def main():
    path = Path(INPUT_FILE)
    if not path.exists():
        print("File not found:", INPUT_FILE)
        return

    text = path.read_text(encoding="utf-8", errors="replace")
    text = normalize_text(text)

    lines = [ln for ln in text.split("\n") if ln.strip()]
    if len(lines) < 2:
        print("Your CSV seems to have no data lines. Check people.csv formatting.")
        return

    # Parse CSV line-by-line
    rows = []
    for ln in lines:
        rows.append(next(csv.reader([ln])))

    header = [norm(h).replace(" ", "_") for h in rows[0]]

    # Find columns (supports Full Name / Full_Name etc.)
    def col(*names):
        for n in names:
            n = n.replace(" ", "_")
            if n in header:
                return header.index(n)
        return None

    name_i = col("full_name", "name")
    dob_i = col("dob", "date_of_birth")
    ms_i  = col("marital_status", "status", "marriage_status")
    addr_i = col("address", "addres")

    # If header not detected, fallback to positions
    if name_i is None:
        name_i, dob_i, ms_i, addr_i = 0, 1, 2, 3
        data_rows = rows
    else:
        data_rows = rows[1:]

    cleaned = []
    for r in data_rows:
        if len(r) < 4:
            continue
        name = r[name_i].strip()
        dob = r[dob_i].strip() if dob_i is not None and dob_i < len(r) else ""
        status = r[ms_i].strip() if ms_i is not None and ms_i < len(r) else ""
        address = ",".join(r[addr_i:]).strip() if addr_i is not None else ",".join(r[3:]).strip()
        cleaned.append([name, dob, status, address])

    # DEBUG: show how many rows were read
    print("Rows parsed:", len(cleaned))
    if cleaned:
        print("First row:", cleaned[0])

    cleaned.sort(key=lambda x: (norm(x[0]), norm(x[3])))

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Full Name", "DOB", "Marital Status", "Address"])
        w.writerows(cleaned)

    print("Saved:", OUTPUT_FILE)

if __name__ == "__main__":
    main()