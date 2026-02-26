import math
import time
import platform
from dataclasses import asdict
from datetime import datetime
from typing import Dict, Optional

import customtkinter as ctk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .config import CONFIG
from .monitor import SystemMonitor
from .exporter import export_snapshot_csv, export_app_usage_csv
from .window_tracker import ActiveWindowTracker


def _status_from_percent(p: float, warn: float, crit: float) -> str:
    if p >= crit:
        return "CRITICAL"
    if p >= warn:
        return "WARNING"
    return "OK"


def _status_color(status: str) -> str:
    # CustomTkinter takes hex or named colors; keep simple
    if status == "CRITICAL":
        return "#ff4d4d"
    if status == "WARNING":
        return "#ffb84d"
    return "#4dff88"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("SysPulse — System Monitor")
        self.geometry("1200x720")
        self.minsize(1100, 650)

        self.monitor = SystemMonitor(history_points=CONFIG.history_points)
        self.tracker = ActiveWindowTracker()
        self.enable_usage = CONFIG.enable_app_usage_tracker and self.tracker.enabled

        self._build_layout()

        self._last_snapshot = None
        self._usage_seconds: Dict[str, int] = {}

        self.after(200, self.refresh)

    def _build_layout(self):
        # Top bar
        top = ctk.CTkFrame(self, corner_radius=12)
        top.pack(fill="x", padx=12, pady=(12, 6))

        self.title_lbl = ctk.CTkLabel(top, text="SysPulse", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_lbl.pack(side="left", padx=12, pady=10)

        self.subtitle_lbl = ctk.CTkLabel(
            top,
            text=f"{platform.system()} • refresh {CONFIG.refresh_ms}ms",
            font=ctk.CTkFont(size=12),
        )
        self.subtitle_lbl.pack(side="left", padx=6)

        self.btn_export = ctk.CTkButton(top, text="Export Snapshot CSV", command=self._export_snapshot)
        self.btn_export.pack(side="right", padx=10, pady=10)

        if self.enable_usage:
            self.btn_export_usage = ctk.CTkButton(top, text="Export App Usage CSV", command=self._export_usage)
            self.btn_export_usage.pack(side="right", padx=10, pady=10)

        # Main split
        body = ctk.CTkFrame(self, corner_radius=12)
        body.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        left = ctk.CTkFrame(body, corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=(10, 6), pady=10)

        right = ctk.CTkFrame(body, corner_radius=12)
        right.pack(side="right", fill="both", expand=True, padx=(6, 10), pady=10)

        # Left: cards + charts
        cards = ctk.CTkFrame(left, corner_radius=12)
        cards.pack(fill="x", padx=10, pady=10)

        self.cpu_card = self._stat_card(cards, "CPU", row=0, col=0)
        self.ram_card = self._stat_card(cards, "RAM", row=0, col=1)
        self.net_card = self._stat_card(cards, "Network", row=0, col=2)
        self.batt_card = self._stat_card(cards, "Battery", row=1, col=0)
        self.disk_card = self._stat_card(cards, "Disk", row=1, col=1, colspan=2)

        # Charts section
        charts = ctk.CTkFrame(left, corner_radius=12)
        charts.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        charts_title = ctk.CTkLabel(charts, text="Live Charts (last ~60s)", font=ctk.CTkFont(size=14, weight="bold"))
        charts_title.pack(anchor="w", padx=10, pady=(10, 0))

        self.fig = Figure(figsize=(8, 3.6), dpi=100)
        self.ax1 = self.fig.add_subplot(311)
        self.ax2 = self.fig.add_subplot(312)
        self.ax3 = self.fig.add_subplot(313)

        self.canvas = FigureCanvasTkAgg(self.fig, master=charts)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Right: connections + optional usage
        conn_frame = ctk.CTkFrame(right, corner_radius=12)
        conn_frame.pack(fill="both", expand=True, padx=10, pady=10)

        conn_title = ctk.CTkLabel(conn_frame, text="Active Connections", font=ctk.CTkFont(size=14, weight="bold"))
        conn_title.pack(anchor="w", padx=10, pady=(10, 0))

        self.conn_box = ctk.CTkTextbox(conn_frame, height=260)
        self.conn_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.conn_box.configure(state="disabled")

        usage_frame = ctk.CTkFrame(right, corner_radius=12)
        usage_frame.pack(fill="x", padx=10, pady=(0, 10))

        usage_title_text = "App Usage (Windows)" if self.enable_usage else "App Usage (Disabled)"
        usage_title = ctk.CTkLabel(usage_frame, text=usage_title_text, font=ctk.CTkFont(size=14, weight="bold"))
        usage_title.pack(anchor="w", padx=10, pady=(10, 0))

        self.usage_lbl = ctk.CTkLabel(usage_frame, text="Enable in app/config.py (Windows only).", justify="left")
        self.usage_lbl.pack(anchor="w", padx=10, pady=(6, 10))

        # Footer
        self.footer = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11))
        self.footer.pack(anchor="w", padx=18, pady=(0, 10))

    def _stat_card(self, parent, title: str, row: int, col: int, colspan: int = 1):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=row, column=col, columnspan=colspan, padx=8, pady=8, sticky="nsew")

        parent.grid_columnconfigure(col, weight=1)
        if row == 0:
            parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        t = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"))
        t.pack(anchor="w", padx=12, pady=(10, 0))

        v = ctk.CTkLabel(card, text="—", font=ctk.CTkFont(size=12))
        v.pack(anchor="w", padx=12, pady=(4, 6))

        bar = ctk.CTkProgressBar(card)
        bar.set(0.0)
        bar.pack(fill="x", padx=12, pady=(0, 10))

        status = ctk.CTkLabel(card, text="OK", font=ctk.CTkFont(size=12, weight="bold"))
        status.pack(anchor="e", padx=12, pady=(0, 10))

        return {"frame": card, "value": v, "bar": bar, "status": status}

    def refresh(self):
        snap = self.monitor.read_snapshot()
        self._last_snapshot = snap

        # CPU
        cpu_status = _status_from_percent(snap.cpu.percent, CONFIG.cpu_warn, CONFIG.cpu_crit)
        self._update_card(
            self.cpu_card,
            f"{snap.cpu.percent:.1f}%  •  {snap.cpu.freq_mhz:.0f} MHz" if snap.cpu.freq_mhz else f"{snap.cpu.percent:.1f}%",
            snap.cpu.percent / 100.0,
            cpu_status,
        )

        # RAM
        ram_status = _status_from_percent(snap.ram.percent, CONFIG.ram_warn, CONFIG.ram_crit)
        self._update_card(
            self.ram_card,
            f"{snap.ram.used_gb:.2f} / {snap.ram.total_gb:.2f} GB  •  {snap.ram.percent:.1f}%",
            snap.ram.percent / 100.0,
            ram_status,
        )

                # NET
        up = self.monitor.format_speed(snap.net.up_bps)
        down = self.monitor.format_speed(snap.net.down_bps)

        net_text = (
            f"↑ {up}   ↓ {down}\n"
            f"Total ↑ {snap.net.total_sent_gb:.2f} GB   ↓ {snap.net.total_recv_gb:.2f} GB"
        )

        self._update_card(
            self.net_card,
            net_text,
            min(1.0, (snap.net.up_bps + snap.net.down_bps) / (10 * 1024 * 1024)),  # rough scale up to 10MB/s
            "OK",
        )

        # Battery
        if snap.battery.present:
            pct = snap.battery.percent if snap.battery.percent is not None else 0.0
            plugged = snap.battery.plugged
            left = self.monitor.format_time_left(snap.battery.secs_left)
            status = "CHARGING" if plugged else "ON BATTERY"
            self._update_card(
                self.batt_card,
                f"{pct:.0f}%  •  {status}  •  left {left}",
                (pct / 100.0) if pct is not None else 0.0,
                "OK",
            )
        else:
            self._update_card(self.batt_card, "No battery detected", 0.0, "OK")

        # Disk
        disk_lines = []
        worst_free = None
        for d in snap.disks[:6]:  # show a few
            disk_lines.append(f"{d.mount}: {d.used_gb:.1f}/{d.total_gb:.1f} GB ({d.percent:.0f}%) • free {d.free_gb:.1f} GB")
            worst_free = d.free_gb if worst_free is None else min(worst_free, d.free_gb)

        if worst_free is None:
            disk_val = "No disks found"
            disk_bar = 0.0
            disk_status = "OK"
        else:
            disk_val = "\n".join(disk_lines)
            # bar shows max used across disks
            disk_bar = max([d.percent for d in snap.disks]) / 100.0 if snap.disks else 0.0
            if worst_free <= CONFIG.disk_free_crit_gb:
                disk_status = "CRITICAL"
            elif worst_free <= CONFIG.disk_free_warn_gb:
                disk_status = "WARNING"
            else:
                disk_status = "OK"

        self._update_card(self.disk_card, disk_val, disk_bar, disk_status)

        # Connections
        rows = self.monitor.get_connections(max_rows=CONFIG.max_connections_rows)
        self._render_connections(rows)

        # App usage (optional)
        if self.enable_usage:
            current, usage = self.tracker.tick()
            self._usage_seconds = usage
            tops = self.tracker.top_usage(usage, limit=8)
            now_app = f"Now: {current.name} (PID {current.pid})\nTitle: {current.title}" if current else "Now: —"
            lines = [now_app, "", "Top apps today:"]
            for t in tops:
                lines.append(f"• {t['app']}: {t['time']}")
            self.usage_lbl.configure(text="\n".join(lines))
        else:
            self.usage_lbl.configure(text="Enable in app/config.py (Windows only).")

        # Charts
        self._update_charts()

        # Footer
        self.footer.configure(text=f"Updated: {datetime.fromtimestamp(snap.ts).strftime('%Y-%m-%d %H:%M:%S')}")

        self.after(CONFIG.refresh_ms, self.refresh)

    def _update_card(self, card, text: str, progress: float, status: str):
        card["value"].configure(text=text)
        card["bar"].set(max(0.0, min(1.0, progress)))
        card["status"].configure(text=status, text_color=_status_color(status))

    def _render_connections(self, rows):
        header = f"{'PROCESS':18} {'PID':6} {'STATUS':12} {'LOCAL':22} {'REMOTE':22}"
        lines = [header, "-" * len(header)]
        for r in rows:
            proc = str(r["process"])[:18].ljust(18)
            pid = str(r["pid"]).ljust(6)
            status = str(r["status"])[:12].ljust(12)
            local = str(r["local"])[:22].ljust(22)
            remote = str(r["remote"])[:22].ljust(22)
            lines.append(f"{proc} {pid} {status} {local} {remote}")
        txt = "\n".join(lines) if lines else "No connections."

        self.conn_box.configure(state="normal")
        self.conn_box.delete("1.0", "end")
        self.conn_box.insert("1.0", txt)
        self.conn_box.configure(state="disabled")

    def _update_charts(self):
        ts = list(self.monitor.ts_hist)
        if len(ts) < 2:
            return
        t0 = ts[0]
        x = [t - t0 for t in ts]

        cpu = list(self.monitor.cpu_hist)
        ram = list(self.monitor.ram_hist)
        up = list(self.monitor.net_up_hist)
        down = list(self.monitor.net_down_hist)

        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        self.ax1.plot(x, cpu)
        self.ax1.set_ylabel("CPU %")
        self.ax1.set_ylim(0, 100)

        self.ax2.plot(x, ram)
        self.ax2.set_ylabel("RAM %")
        self.ax2.set_ylim(0, 100)

        # scale net to MB/s for readability
        up_mb = [v / (1024**2) for v in up]
        down_mb = [v / (1024**2) for v in down]
        self.ax3.plot(x, up_mb, label="Up (MB/s)")
        self.ax3.plot(x, down_mb, label="Down (MB/s)")
        self.ax3.set_ylabel("Net MB/s")
        self.ax3.set_xlabel("seconds")
        self.ax3.legend(loc="upper right", fontsize=8)

        self.fig.tight_layout()
        self.canvas.draw_idle()

    def _export_snapshot(self):
        if not self._last_snapshot:
            return
        path = export_snapshot_csv(self._last_snapshot)
        self._toast(f"Exported snapshot: {path}")

    def _export_usage(self):
        if not self._usage_seconds:
            self._toast("No usage data yet.")
            return
        path = export_app_usage_csv(self._usage_seconds)
        self._toast(f"Exported app usage: {path}")

    def _toast(self, msg: str):
        # simple transient message in footer
        self.footer.configure(text=msg)
