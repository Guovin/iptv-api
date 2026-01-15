import gzip
import os
import pickle
import time
from typing import Dict, Optional, Set

MAX_BACKOFF = 24 * 3600
BASE_BACKOFF = 60

_frozen: Dict[str, Dict] = {}


def _now_ts() -> int:
    return int(time.time())


def mark_url_bad(url: str, initial: bool = False) -> None:
    if not url:
        return
    meta = _frozen.setdefault(url, {"bad_count": 0, "last_bad": 0, "last_good": 0, "frozen_until": None})
    if initial:
        meta["bad_count"] = max(meta["bad_count"], 3)
    meta["bad_count"] += 1
    meta["last_bad"] = _now_ts()
    backoff = min(MAX_BACKOFF, (2 ** meta["bad_count"]) * BASE_BACKOFF)
    meta["frozen_until"] = _now_ts() + backoff


def mark_url_good(url: str) -> None:
    if not url:
        return
    meta = _frozen.get(url)
    if not meta:
        return
    meta["last_good"] = _now_ts()
    meta["bad_count"] = max(0, meta.get("bad_count", 0) - 1)
    meta["frozen_until"] = None
    if meta["bad_count"] == 0:
        _frozen.pop(url, None)


def is_url_frozen(url: str) -> bool:
    meta = _frozen.get(url)
    if not meta:
        return False
    fu = meta.get("frozen_until")
    if not fu:
        return False
    now = _now_ts()
    if fu > now:
        return True
    meta["frozen_until"] = None
    meta["bad_count"] = max(0, meta.get("bad_count", 0) - 1)
    if meta["bad_count"] == 0:
        _frozen.pop(url, None)
    return False


def get_current_frozen_set() -> Set[str]:
    now = _now_ts()
    res = set()
    for url, meta in list(_frozen.items()):
        fu = meta.get("frozen_until")
        if fu and fu > now:
            res.add(url)
        else:
            is_url_frozen(url)
    return res


def load(path: Optional[str]) -> None:
    if not path or not os.path.exists(path):
        return
    try:
        with gzip.open(path, "rb") as f:
            data = pickle.load(f)
            if isinstance(data, dict):
                for k, v in data.items():
                    if k not in _frozen:
                        _frozen[k] = v
    except Exception:
        pass


def save(path: Optional[str]) -> None:
    if not path:
        return
    try:
        dirp = os.path.dirname(path)
        if dirp:
            os.makedirs(dirp, exist_ok=True)
        with gzip.open(path, "wb") as f:
            pickle.dump(_frozen, f)
    except Exception:
        pass


__all__ = ["mark_url_bad", "mark_url_good", "is_url_frozen", "get_current_frozen_set", "load", "save"]
