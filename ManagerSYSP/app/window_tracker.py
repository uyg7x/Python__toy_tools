import time
import platform
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

IS_WINDOWS = platform.system().lower() == "windows"

if IS_WINDOWS:
    try:
        import win32gui
        import win32process
        import psutil
    except Exception:  # pragma: no cover
        win32gui = None
        win32process = None
        psutil = None
else:
    win32gui = None
    win32process = None
    psutil = None


@dataclass
class ActiveApp:
    name: str
    title: str
    pid: int


class ActiveWindowTracker:
    """Tracks foreground app usage time (Windows only)."""
    def __init__(self):
        self.enabled = IS_WINDOWS and win32gui is not None and win32process is not None and psutil is not None
        self._last_app: Optional[ActiveApp] = None
        self._last_ts: float = time.time()
        self.usage_seconds: Dict[str, int] = {}

    def _get_active_app(self) -> Optional[ActiveApp]:
        if not self.enabled:
            return None
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None
            title = win32gui.GetWindowText(hwnd) or ""
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if not pid:
                return None
            try:
                name = psutil.Process(pid).name()
            except Exception:
                name = f"PID {pid}"
            return ActiveApp(name=name, title=title[:80], pid=int(pid))
        except Exception:
            return None

    def tick(self) -> Tuple[Optional[ActiveApp], Dict[str, int]]:
        """Call once per refresh cycle."""
        now = time.time()
        dt = int(max(0, now - self._last_ts))
        self._last_ts = now

        current = self._get_active_app()
        if self._last_app and dt > 0:
            key = self._last_app.name
            self.usage_seconds[key] = self.usage_seconds.get(key, 0) + dt

        self._last_app = current
        return current, dict(self.usage_seconds)

    @staticmethod
    def top_usage(usage_seconds: Dict[str, int], limit: int = 8):
        items = sorted(usage_seconds.items(), key=lambda kv: kv[1], reverse=True)[:limit]
        return [{"app": k, "time": ActiveWindowTracker._fmt(v)} for k, v in items]

    @staticmethod
    def _fmt(secs: int) -> str:
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        if h > 0:
            return f"{h}h {m}m"
        if m > 0:
            return f"{m}m {s}s"
        return f"{s}s"
