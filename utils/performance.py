import os
from dataclasses import dataclass
from functools import lru_cache


PERFORMANCE_MODES = ("auto", "powersave", "balance", "fast")


@dataclass(frozen=True)
class PerformanceSettings:
    requested_mode: str
    resolved_mode: str
    cpu_count: float
    memory_gb: float
    speed_test_concurrency: int
    probe_concurrency: int
    fetch_workers: int


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except (OSError, ValueError):
        return ""


def _positive_float(value):
    try:
        number = float(value)
        return number if number > 0 else None
    except (TypeError, ValueError):
        return None


def _cpu_quota():
    cpu_max = _read_text("/sys/fs/cgroup/cpu.max").split()
    if len(cpu_max) == 2 and cpu_max[0] != "max":
        quota = _positive_float(cpu_max[0])
        period = _positive_float(cpu_max[1])
        if quota and period:
            return quota / period

    quota = _positive_float(_read_text("/sys/fs/cgroup/cpu/cpu.cfs_quota_us"))
    period = _positive_float(_read_text("/sys/fs/cgroup/cpu/cpu.cfs_period_us"))
    if quota and period:
        return quota / period
    return None


def _physical_memory_bytes():
    try:
        return int(os.sysconf("SC_PHYS_PAGES")) * int(os.sysconf("SC_PAGE_SIZE"))
    except (AttributeError, OSError, TypeError, ValueError):
        return 0


def _memory_limit_bytes():
    values = [
        _read_text("/sys/fs/cgroup/memory.max"),
        _read_text("/sys/fs/cgroup/memory/memory.limit_in_bytes"),
    ]
    limits = []
    for value in values:
        if value and value != "max":
            try:
                limit = int(value)
            except ValueError:
                continue
            if 0 < limit < (1 << 60):
                limits.append(limit)
    return min(limits) if limits else 0


@lru_cache(maxsize=1)
def detect_resources():
    cpu_values = [float(os.cpu_count() or 1)]
    try:
        cpu_values.append(float(len(os.sched_getaffinity(0))))
    except (AttributeError, OSError):
        pass
    if quota := _cpu_quota():
        cpu_values.append(quota)
    cpu_count = max(0.25, min(cpu_values))

    memory_values = [value for value in (_physical_memory_bytes(), _memory_limit_bytes()) if value > 0]
    memory_bytes = min(memory_values) if memory_values else 2 * 1024 ** 3
    return cpu_count, memory_bytes / 1024 ** 3


def _bounded(value, lower, upper):
    return max(lower, min(upper, int(value)))


@lru_cache(maxsize=16)
def get_performance_settings(mode="auto", speed_test_limit=0):
    requested_mode = str(mode or "auto").lower()
    if requested_mode not in PERFORMANCE_MODES:
        requested_mode = "auto"

    cpu_count, memory_gb = detect_resources()
    if requested_mode == "auto":
        if cpu_count <= 1.5 or memory_gb <= 1.5:
            resolved_mode = "powersave"
        elif cpu_count >= 6 and memory_gb >= 6:
            resolved_mode = "fast"
        else:
            resolved_mode = "balance"
    else:
        resolved_mode = requested_mode

    memory_http_limit = _bounded(memory_gb * 3, 2, 16)
    memory_probe_limit = _bounded(memory_gb / 1.5, 1, 4)
    memory_fetch_limit = _bounded(memory_gb * 2, 2, 16)
    cpu_probe_limit = _bounded(cpu_count / 2, 1, 4)

    if resolved_mode == "powersave":
        http_concurrency = 3
        probe_concurrency = 1
        fetch_workers = 4
    elif resolved_mode == "fast":
        http_concurrency = _bounded(cpu_count * 2.5, 8, 16)
        probe_concurrency = _bounded(cpu_count / 2, 1, 4)
        fetch_workers = _bounded(cpu_count * 2, 8, 16)
    else:
        http_concurrency = _bounded(cpu_count * 2, 5, 10)
        probe_concurrency = _bounded(cpu_count / 2, 1, 2)
        fetch_workers = _bounded(cpu_count * 2, 6, 10)

    http_concurrency = min(http_concurrency, memory_http_limit)
    probe_concurrency = min(probe_concurrency, memory_probe_limit, cpu_probe_limit)
    fetch_workers = min(fetch_workers, memory_fetch_limit)

    try:
        configured_limit = int(speed_test_limit or 0)
    except (TypeError, ValueError):
        configured_limit = 0
    if configured_limit > 0:
        http_concurrency = _bounded(configured_limit, 1, 64)

    return PerformanceSettings(
        requested_mode=requested_mode,
        resolved_mode=resolved_mode,
        cpu_count=round(cpu_count, 2),
        memory_gb=round(memory_gb, 2),
        speed_test_concurrency=max(1, http_concurrency),
        probe_concurrency=max(1, probe_concurrency),
        fetch_workers=max(1, fetch_workers),
    )
