import time
import psutil
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class CpuInfo:
    percent: float
    freq_mhz: Optional[float]
    per_core: List[float]


@dataclass
class RamInfo:
    used_gb: float
    total_gb: float
    percent: float


@dataclass
class DiskInfo:
    mount: str
    used_gb: float
    total_gb: float
    free_gb: float
    percent: float


@dataclass
class NetInfo:
    up_bps: float
    down_bps: float
    total_sent_gb: float
    total_recv_gb: float


@dataclass
class BatteryInfo:
    present: bool
    percent: Optional[float]
    plugged: Optional[bool]
    secs_left: Optional[int]


@dataclass
class Snapshot:
    ts: float
    cpu: CpuInfo
    ram: RamInfo
    disks: List[DiskInfo]
    net: NetInfo
    battery: BatteryInfo


def _bytes_to_gb(n: float) -> float:
    return n / (1024 ** 3)


def _bytes_per_sec_to_human(bps: float) -> Tuple[float, str]:
    # bps is bytes/sec
    units = [("B/s", 1), ("KB/s", 1024), ("MB/s", 1024**2), ("GB/s", 1024**3)]
    for name, scale in units[::-1]:
        if bps >= scale:
            return (bps / scale, name)
    return (bps, "B/s")


class SystemMonitor:
    def __init__(self, history_points: int = 60):
        self.history_points = history_points
        self.cpu_hist = deque(maxlen=history_points)
        self.ram_hist = deque(maxlen=history_points)
        self.net_up_hist = deque(maxlen=history_points)
        self.net_down_hist = deque(maxlen=history_points)
        self.ts_hist = deque(maxlen=history_points)

        self._last_net = psutil.net_io_counters()
        self._last_ts = time.time()

        # prime cpu measurement
        psutil.cpu_percent(interval=None)

    def read_snapshot(self) -> Snapshot:
        ts = time.time()

        cpu_percent = psutil.cpu_percent(interval=None)
        per_core = psutil.cpu_percent(interval=None, percpu=True)
        freq = psutil.cpu_freq()
        freq_mhz = float(freq.current) if freq else None

        vm = psutil.virtual_memory()
        ram = RamInfo(
            used_gb=round(_bytes_to_gb(vm.used), 2),
            total_gb=round(_bytes_to_gb(vm.total), 2),
            percent=float(vm.percent),
        )

        disks = []
        for part in psutil.disk_partitions(all=False):
            # skip cd-roms / weird
            if "cdrom" in part.opts.lower():
                continue
            try:
                du = psutil.disk_usage(part.mountpoint)
            except Exception:
                continue
            disks.append(DiskInfo(
                mount=part.device or part.mountpoint,
                used_gb=round(_bytes_to_gb(du.used), 2),
                total_gb=round(_bytes_to_gb(du.total), 2),
                free_gb=round(_bytes_to_gb(du.free), 2),
                percent=float(du.percent),
            ))
        # de-dup mounts
        seen = set()
        dedup = []
        for d in disks:
            key = d.mount
            if key in seen:
                continue
            seen.add(key)
            dedup.append(d)
        disks = sorted(dedup, key=lambda x: x.mount.lower())

        net_now = psutil.net_io_counters()
        dt = max(ts - self._last_ts, 1e-6)
        up_bps = (net_now.bytes_sent - self._last_net.bytes_sent) / dt
        down_bps = (net_now.bytes_recv - self._last_net.bytes_recv) / dt
        self._last_net = net_now
        self._last_ts = ts

        net = NetInfo(
            up_bps=up_bps,
            down_bps=down_bps,
            total_sent_gb=round(_bytes_to_gb(net_now.bytes_sent), 2),
            total_recv_gb=round(_bytes_to_gb(net_now.bytes_recv), 2),
        )

        batt = psutil.sensors_battery()
        if batt is None:
            battery = BatteryInfo(present=False, percent=None, plugged=None, secs_left=None)
        else:
            battery = BatteryInfo(
                present=True,
                percent=float(batt.percent) if batt.percent is not None else None,
                plugged=bool(batt.power_plugged) if batt.power_plugged is not None else None,
                secs_left=int(batt.secsleft) if batt.secsleft is not None and batt.secsleft >= 0 else None,
            )

        snap = Snapshot(
            ts=ts,
            cpu=CpuInfo(percent=float(cpu_percent), freq_mhz=freq_mhz, per_core=[float(x) for x in per_core]),
            ram=ram,
            disks=disks,
            net=net,
            battery=battery,
        )

        # history
        self.ts_hist.append(ts)
        self.cpu_hist.append(snap.cpu.percent)
        self.ram_hist.append(snap.ram.percent)
        self.net_up_hist.append(snap.net.up_bps)
        self.net_down_hist.append(snap.net.down_bps)

        return snap

    @staticmethod
    def format_speed(bps: float) -> str:
        value, unit = _bytes_per_sec_to_human(bps)
        return f"{value:.2f} {unit}"

    @staticmethod
    def format_time_left(secs: Optional[int]) -> str:
        if secs is None:
            return "N/A"
        h = secs // 3600
        m = (secs % 3600) // 60
        return f"{h}h {m}m"

    @staticmethod
    def get_connections(max_rows: int = 50):
        rows = []
        try:
            conns = psutil.net_connections(kind="inet")
        except Exception:
            return rows

        # build pid->name map (cache-ish)
        pid_name = {}
        for c in conns:
            if c.pid and c.pid not in pid_name:
                try:
                    pid_name[c.pid] = psutil.Process(c.pid).name()
                except Exception:
                    pid_name[c.pid] = "?"
        for c in conns:
            laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "-"
            raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "-"
            rows.append({
                "local": laddr,
                "remote": raddr,
                "status": c.status,
                "pid": c.pid or "-",
                "process": pid_name.get(c.pid, "-") if c.pid else "-"
            })

        # most informative first: established
        rows.sort(key=lambda r: (r["status"] != "ESTABLISHED", str(r["process"]), str(r["pid"])))
        return rows[:max_rows]
