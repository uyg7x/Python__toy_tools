from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    # UI refresh rate (ms)
    refresh_ms: int = 1000

    # History length for charts (seconds)
    history_points: int = 60

    # Alerts (percent)
    cpu_warn: float = 85.0
    cpu_crit: float = 95.0
    ram_warn: float = 85.0
    ram_crit: float = 95.0

    # Disk alert: free space below GB
    disk_free_warn_gb: float = 10.0
    disk_free_crit_gb: float = 5.0

    # Optional (Windows) active app usage tracker
    enable_app_usage_tracker: bool = True

    # Connections table rows
    max_connections_rows: int = 50

CONFIG = Config()
