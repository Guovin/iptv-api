import asyncio
import copy
from collections import defaultdict
from logging import INFO
from typing import Any, Dict, Optional, Set, Tuple

import utils.constants as constants
from utils.channel import sort_channel_result, generate_channel_statistic, write_channel_to_file, retain_origin
from utils.config import config
from utils.tools import get_logger, close_logger_handlers


class ResultAggregator:
    """
    Aggregates test results and periodically writes sorted views to files.
    """

    def __init__(
            self,
            base_data: Dict[str, Dict[str, Any]],
            first_channel_name: Optional[str] = None,
            ipv6_support: bool = True,
            write_interval: float = 5.0,
            min_items_before_flush: int = config.urls_limit,
            flush_debounce: Optional[float] = None,
            stat_logger=None,
            result: Optional[Dict[str, Dict[str, list]]] = None,
    ):
        self.base_data = base_data
        self.result = sort_channel_result(
            base_data,
            result=result,
            ipv6_support=ipv6_support
        )
        self.test_results: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        self._dirty = False
        self._dirty_count = 0
        self._stopped = True
        self._task: Optional[asyncio.Task] = None
        self.realtime_write = config.open_realtime_write
        self.write_interval = write_interval
        self.first_channel_name = first_channel_name
        self.ipv6_support = ipv6_support
        self.stat_logger = stat_logger or get_logger(constants.statistic_log_path, level=INFO, init=True)
        self.is_last = False
        self._lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()
        self._min_items_before_flush = min_items_before_flush
        self.flush_debounce = flush_debounce if flush_debounce is not None else max(0.2, write_interval / 2)
        self._flush_event = asyncio.Event()
        self._pending_channels: Set[Tuple[str, str]] = set()
        self._finished_channels: Set[Tuple[str, str]] = set()

    def add_item(self, cate: str, name: str, item: dict, is_channel_last: bool = False, is_last: bool = False,
                 is_valid: bool = True):
        """
        Add a test result item for a specific category and name.
        """
        self.test_results[cate][name].append(item)
        self.is_last = is_last
        self._pending_channels.add((cate, name))

        if is_channel_last:
            try:
                self._finished_channels.add((cate, name))
                generate_channel_statistic(self.stat_logger, cate, name, self.test_results[cate][name])
            except Exception:
                pass

        if is_valid and self.realtime_write:
            self._dirty = True
            self._dirty_count += 1
            if self._dirty_count < self._min_items_before_flush:
                return
            self._dirty_count = 0
            try:
                asyncio.get_running_loop()
                self._flush_event.set()
            except RuntimeError:
                try:
                    loop = asyncio.get_event_loop()
                    loop.call_soon_threadsafe(self._flush_event.set)
                except Exception:
                    pass

    async def _atomic_write_sorted_view(
            self,
            test_copy: Dict[str, Dict[str, list]],
            affected: Optional[Set[Tuple[str, str]]] = None,
            finished: Optional[Set[Tuple[str, str]]] = None,
            is_last: bool = False,
    ) -> None:
        """
        Atomic write of sorted view to file, either partially or fully.
        """
        async with self._write_lock:
            await self._write_sorted_view(test_copy, affected, finished, is_last)

    async def _write_sorted_view(
            self,
            test_copy: Dict[str, Dict[str, list]],
            affected: Optional[Set[Tuple[str, str]]] = None,
            finished: Optional[Set[Tuple[str, str]]] = None,
            is_last: bool = False,
    ) -> None:
        if finished is None:
            finished = set()

        speed_test_filter_host = config.speed_test_filter_host
        if affected:
            partial_base = defaultdict(lambda: defaultdict(list))
            partial_result = defaultdict(lambda: defaultdict(list))

            for cate, name in affected:
                base_entries = self.base_data.get(cate, {})
                if name in base_entries:
                    partial_base[cate][name] = list(base_entries[name])

                partial_result[cate][name] = list(test_copy.get(cate, {}).get(name, []))

                if (cate, name) not in finished:
                    prev_sorted = self.result.get(cate, {}).get(name, [])
                    seen = {it.get("url") for it in partial_result[cate][name] if
                            isinstance(it, dict) and it.get("url")}
                    for item in prev_sorted:
                        if not isinstance(item, dict):
                            continue
                        url = item.get("url")
                        if url and url not in seen and item.get("origin") not in retain_origin:
                            partial_result[cate][name].append(item)
                            seen.add(url)
            try:
                if len(affected) == 1:
                    cate_single, name_single = next(iter(affected))
                    new_sorted = sort_channel_result(
                        partial_base,
                        result=partial_result,
                        filter_host=speed_test_filter_host,
                        ipv6_support=self.ipv6_support,
                        cate=cate_single,
                        name=name_single,
                    )
                else:
                    new_sorted = sort_channel_result(
                        partial_base, result=partial_result, filter_host=speed_test_filter_host,
                        ipv6_support=self.ipv6_support
                    )
            except Exception:
                new_sorted = defaultdict(lambda: defaultdict(list))
        else:
            try:
                new_sorted = sort_channel_result(
                    self.base_data, result=test_copy, filter_host=speed_test_filter_host,
                    ipv6_support=self.ipv6_support
                )
            except Exception:
                new_sorted = defaultdict(lambda: defaultdict(list))

        merged = defaultdict(lambda: defaultdict(list))

        for cate, names in self.base_data.items():
            for name in names.keys():
                merged[cate][name] = list(self.result.get(cate, {}).get(name, []))

        for cate, names in new_sorted.items():
            if cate not in self.base_data:
                continue
            for name, vals in names.items():
                if name in self.base_data.get(cate, {}) and vals:
                    merged[cate][name] = list(vals)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            write_channel_to_file,
            merged,
            self.ipv6_support,
            self.first_channel_name,
            True,
            is_last,
        )

        self.result = merged

    async def flush_once(self, force: bool = False) -> None:
        """
        Flush the current test results to file once.
        """
        async with self._lock:
            if not self._dirty and not force:
                return

            pending = set(self._pending_channels)
            self._pending_channels.clear()

            if force:
                test_copy = copy.deepcopy(self.test_results)
                finished_for_flush = set(self._finished_channels)
                self._finished_channels.clear()
            else:
                test_copy = defaultdict(lambda: defaultdict(list))
                for cate, name in pending:
                    items = self.test_results.get(cate, {}).get(name, [])
                    copied_items = [it.copy() if isinstance(it, dict) else it for it in items]
                    if copied_items:
                        test_copy[cate][name] = copied_items

                finished_for_flush = set(self._finished_channels & pending)
                self._finished_channels.difference_update(finished_for_flush)

            self._dirty = False
            self._dirty_count = 0
            is_last_for_flush = self.is_last

        affected = None if force else (pending if pending else None)
        try:
            await self._atomic_write_sorted_view(
                test_copy,
                affected=affected,
                finished=finished_for_flush,
                is_last=is_last_for_flush,
            )
        except Exception:
            pass

    async def _run_loop(self):
        """
        Run the periodic flush loop.
        """
        try:
            while not self._stopped:
                triggered = False
                try:
                    await asyncio.wait_for(self._flush_event.wait(), timeout=self.write_interval)
                    triggered = True
                except asyncio.TimeoutError:
                    pass
                if self._stopped:
                    break
                if triggered:
                    await asyncio.sleep(self.flush_debounce)
                    if self._stopped:
                        break
                self._flush_event.clear()
                if self._dirty:
                    await self.flush_once()
        finally:
            self._stopped = True
            self._flush_event.clear()

    async def start(self) -> None:
        """
        Start the aggregator's periodic flush loop.
        """
        if not self.realtime_write:
            self._stopped = False
            return
        if self._task and not self._task.done():
            return
        self._stopped = False
        self._flush_event.clear()
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        """
        Stop the aggregator and clean up resources.
        """
        self._stopped = True
        self._flush_event.set()
        if self._task:
            await self._task
            self._task = None
        try:
            await self.flush_once(force=True)
        except Exception:
            pass
        if self.stat_logger:
            close_logger_handlers(self.stat_logger)
