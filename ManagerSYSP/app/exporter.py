import csv
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .monitor import Snapshot


def ensure_reports_dir() -> str:
    out = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    os.makedirs(out, exist_ok=True)
    return out


def export_snapshot_csv(snap: Snapshot, path: Optional[str] = None) -> str:
    reports = ensure_reports_dir()
    if path is None:
        name = datetime.now().strftime("snapshot_%Y-%m-%d_%H-%M-%S.csv")
        path = os.path.join(reports, name)

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", datetime.fromtimestamp(snap.ts).isoformat()])
        w.writerow([])
        w.writerow(["CPU %", f"{snap.cpu.percent:.2f}"])
        w.writerow(["CPU freq MHz", f"{snap.cpu.freq_mhz:.0f}" if snap.cpu.freq_mhz else "N/A"])
        w.writerow(["RAM used GB", snap.ram.used_gb])
        w.writerow(["RAM total GB", snap.ram.total_gb])
        w.writerow(["RAM %", f"{snap.ram.percent:.2f}"])
        w.writerow(["Net up (bytes/s)", f"{snap.net.up_bps:.2f}"])
        w.writerow(["Net down (bytes/s)", f"{snap.net.down_bps:.2f}"])
        w.writerow(["Total sent GB", snap.net.total_sent_gb])
        w.writerow(["Total recv GB", snap.net.total_recv_gb])
        w.writerow([])
        w.writerow(["Disks"])
        w.writerow(["mount", "used_gb", "total_gb", "free_gb", "percent"])
        for d in snap.disks:
            w.writerow([d.mount, d.used_gb, d.total_gb, d.free_gb, f"{d.percent:.2f}"])
        w.writerow([])
        w.writerow(["Battery present", snap.battery.present])
        w.writerow(["Battery %", snap.battery.percent if snap.battery.percent is not None else "N/A"])
        w.writerow(["Charging", snap.battery.plugged if snap.battery.plugged is not None else "N/A"])
        w.writerow(["Seconds left", snap.battery.secs_left if snap.battery.secs_left is not None else "N/A"])

    return path


def export_app_usage_csv(usage_seconds: Dict[str, int], path: Optional[str] = None) -> str:
    reports = ensure_reports_dir()
    if path is None:
        name = datetime.now().strftime("app_usage_%Y-%m-%d_%H-%M-%S.csv")
        path = os.path.join(reports, name)

    items = sorted(usage_seconds.items(), key=lambda kv: kv[1], reverse=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["app", "seconds"])
        for app, secs in items:
            w.writerow([app, secs])
    return path
