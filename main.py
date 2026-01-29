import asyncio
import copy
import datetime
import gzip
import os
import pickle
from time import time
from typing import Callable, Optional, Any

import pytz
from tqdm import tqdm

import utils.constants as constants
import utils.frozen as frozen
from updates.epg import get_epg
from updates.epg.tools import write_to_xml, compress_to_gz
from updates.subscribe import get_channels_by_subscribe_urls
from utils.aggregator import ResultAggregator
from utils.channel import get_channel_items, append_total_data, test_speed
from utils.config import config
from utils.i18n import t
from utils.speed import clear_cache
from utils.tools import (
    get_pbar_remaining,
    process_nested_dict,
    format_interval,
    check_ipv6_support,
    get_urls_from_file,
    get_version_info,
    get_urls_len,
    get_public_url,
    parse_times,
    to_serializable,
)
from utils.types import CategoryChannelData
from utils.whitelist import load_whitelist_maps, get_section_entries

ProgressCallback = Callable[..., Any]


class UpdateSource:
    def __init__(self):
        self.whitelist_maps = None
        self.blacklist = None

        self.update_progress: Optional[ProgressCallback] = None
        self.run_ui = False

        self.tasks: list[asyncio.Task] = []

        self.channel_items: CategoryChannelData = {}
        self.channel_names: list[str] = []

        self.subscribe_result = {}
        self.epg_result = {}

        self.channel_data: CategoryChannelData = {}

        self.pbar: Optional[tqdm] = None
        self.total = 0
        self.start_time = None

        self.stop_event: Optional[asyncio.Event] = None
        self.ipv6_support = False
        self.now = None

        self.aggregator: Optional[ResultAggregator] = None

    # ----------------------------
    # progress / pbar
    # ----------------------------
    def pbar_update(self, name: str = "", item_name: str = ""):
        if not self.pbar:
            return
        if self.pbar.n < self.total:
            self.pbar.update()
            remaining_total = self.total - self.pbar.n
            remaining_time = get_pbar_remaining(n=self.pbar.n, total=self.total, start_time=self.start_time)
            if self.update_progress:
                self.update_progress(
                    t("msg.progress_desc").format(
                        name=name,
                        remaining_total=remaining_total,
                        item_name=item_name,
                        remaining_time=remaining_time,
                    ),
                    int((self.pbar.n / self.total) * 100),
                )

    # ----------------------------
    # IO: cache
    # ----------------------------
    def _load_cache(self) -> dict:
        if not (config.open_history and os.path.exists(constants.cache_path)):
            return {}
        try:
            with gzip.open(constants.cache_path, "rb") as f:
                return pickle.load(f) or {}
        except Exception:
            return {}

    def _save_cache(self, cache_result: dict):
        serializable = to_serializable(cache_result or {})
        cache_dir = os.path.dirname(constants.cache_path)
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
        with gzip.open(constants.cache_path, "wb") as f:
            pickle.dump(serializable, f)

    # ----------------------------
    # stage 1: prepare
    # ----------------------------
    def _prepare_channel_data(self):
        self.whitelist_maps = load_whitelist_maps(constants.whitelist_path)
        self.blacklist = get_urls_from_file(constants.blacklist_path, pattern_search=False)
        self.channel_items = get_channel_items(self.whitelist_maps, self.blacklist)
        self.channel_data = {}

        self.channel_names = [
            name for channel_obj in self.channel_items.values() for name in channel_obj.keys()
        ]

        if config.open_history and os.path.exists(constants.frozen_path):
            frozen.load(constants.frozen_path)

    # ----------------------------
    # stage 2: fetch subscribe/epg (concurrent)
    # ----------------------------
    async def _fetch_subscribe(self, channel_names: list[str]):
        whitelist_subscribe_urls, default_subscribe_urls = get_section_entries(
            constants.subscribe_path,
            pattern=constants.url_pattern,
        )
        subscribe_urls = list(dict.fromkeys(whitelist_subscribe_urls + default_subscribe_urls))
        print(
            t("msg.subscribe_urls_whitelist_total").format(
                default_count=len(default_subscribe_urls),
                whitelist_count=len(whitelist_subscribe_urls),
                total=len(subscribe_urls),
            )
        )
        if not subscribe_urls:
            print(t("msg.no_subscribe_urls").format(file=constants.subscribe_path))
            return {}

        return await get_channels_by_subscribe_urls(
            subscribe_urls,
            names=channel_names,
            whitelist=whitelist_subscribe_urls,
            callback=self.update_progress,
        )

    async def _fetch_epg(self, channel_names: list[str]):
        return await get_epg(channel_names, callback=self.update_progress)

    async def visit_page(self, channel_names: list[str] = None):
        """
        Visits subscribe and epg pages concurrently to fetch data.
        """
        channel_names = channel_names or []

        cors: list[tuple[str, asyncio.Future]] = []
        if config.open_method.get("subscribe"):
            cors.append(("subscribe_result", asyncio.create_task(self._fetch_subscribe(channel_names))))
        if config.open_method.get("epg"):
            cors.append(("epg_result", asyncio.create_task(self._fetch_epg(channel_names))))

        if not cors:
            return

        results = await asyncio.gather(*(c for _, c in cors), return_exceptions=True)
        for (attr, _), res in zip(cors, results):
            if isinstance(res, Exception):
                print(f"{attr} failed: {res}")
                setattr(self, attr, {})
            else:
                setattr(self, attr, res)

    def _write_epg_files_if_needed(self):
        if not self.epg_result:
            return
        write_to_xml(self.epg_result, constants.epg_result_path)
        compress_to_gz(constants.epg_result_path, constants.epg_gz_result_path)

    # ----------------------------
    # stage 3: aggregator lifecycle
    # ----------------------------
    async def _start_aggregator(self, cache: dict):
        self.aggregator = ResultAggregator(
            base_data=self.channel_data,
            first_channel_name=self.channel_names[0] if self.channel_names else None,
            ipv6_support=self.ipv6_support,
            write_interval=2.0,
            result=cache,
        )
        await self.aggregator.start()

    async def _stop_aggregator(self):
        if self.aggregator:
            await self.aggregator.stop()
            self.aggregator = None

    # ----------------------------
    # stage 4: speed test
    # ----------------------------
    async def _run_speed_test(self) -> CategoryChannelData:
        """
        Run speed test on the channel data and return the test results.
        """
        urls_total = get_urls_len(self.channel_data)
        test_data = copy.deepcopy(self.channel_data)

        process_nested_dict(
            test_data,
            seen=set(),
            filter_host=config.speed_test_filter_host,
            ipv6_support=self.ipv6_support,
        )
        self.total = get_urls_len(test_data)

        print(t("msg.total_urls_need_test_speed").format(total=urls_total, speed_total=self.total))

        if self.total <= 0:
            self.aggregator.is_last = True
            await self.aggregator.flush_once(force=True)
            return {}
        if self.update_progress:
            self.update_progress(
                t("msg.progress_speed_test").format(total=urls_total, speed_total=self.total),
                0,
            )

        self.start_time = time()
        self.pbar = tqdm(total=self.total, desc=t("pbar.speed_test"))
        try:
            return await test_speed(
                test_data,
                ipv6=self.ipv6_support,
                callback=lambda: self.pbar_update(name=t("pbar.speed_test"), item_name=t("pbar.url")),
                on_task_complete=self.aggregator.add_item,
            )
        finally:
            if self.pbar:
                self.pbar.close()
                self.pbar = None

    # ----------------------------
    # stage 5: ui final notify
    # ----------------------------
    def _notify_ui_finished(self, main_start_time: float):
        if not self.run_ui:
            return

        open_service = config.open_service
        service_tip = t("msg.service_tip") if open_service else ""

        tip = (
            t("msg.service_run_success").format(service_tip=service_tip)
            if open_service and config.open_update is False
            else t("msg.update_completed").format(
                time=format_interval(time() - main_start_time),
                service_tip=service_tip,
            )
        )

        if self.update_progress:
            self.update_progress(
                tip,
                100,
                finished=True,
                url=f"{get_public_url()}" if open_service else None,
                now=self.now,
            )

    # ----------------------------
    # main flow
    # ----------------------------
    async def main(self):
        try:
            main_start_time = time()

            if not config.open_update:
                self._notify_ui_finished(main_start_time)
                return

            self._prepare_channel_data()

            if not self.channel_names:
                print(t("msg.no_channel_names").format(file=config.source_file))
                self._notify_ui_finished(main_start_time)
                return

            await self.visit_page(self.channel_names)
            self.tasks = []
            self._write_epg_files_if_needed()

            append_total_data(
                self.channel_items.items(),
                self.channel_data,
                self.subscribe_result,
                self.whitelist_maps,
                self.blacklist,
            )

            cache = self._load_cache()

            await self._start_aggregator(cache)
            try:
                if config.open_speed_test:
                    clear_cache()
                    await self._run_speed_test()
                else:
                    self.aggregator.is_last = True
                    await self.aggregator.flush_once(force=True)

            finally:
                if config.open_history:
                    self._save_cache(self.aggregator.result)
                    frozen.save(constants.frozen_path)
                await self._stop_aggregator()

            print(
                t("msg.update_completed").format(
                    time=format_interval(time() - main_start_time),
                    service_tip="",
                )
            )
            self._notify_ui_finished(main_start_time)

        except asyncio.exceptions.CancelledError:
            print(t("msg.update_cancelled"))

    # ----------------------------
    # lifecycle control
    # ----------------------------
    async def start(self, callback=None):
        def default_callback(*args, **kwargs):
            pass

        self.update_progress = callback or default_callback
        self.run_ui = True if callback else False

        if self.run_ui:
            self.update_progress(t("msg.check_ipv6_support"), 0)

        self.ipv6_support = config.ipv6_support or check_ipv6_support()

        if not os.getenv("GITHUB_ACTIONS") and (config.update_interval or config.update_times):
            await self.scheduler(asyncio.Event())
        elif config.update_startup:
            await self.main()

    def stop(self):
        for task in self.tasks:
            task.cancel()
        self.tasks = []

        if self.pbar:
            self.pbar.close()
            self.pbar = None

        if self.stop_event:
            self.stop_event.set()

    async def scheduler(self, stop_event: asyncio.Event):
        self.stop_event = stop_event
        tz = pytz.timezone(config.time_zone)
        mode = config.update_mode
        update_times = parse_times(config.update_times)

        try:
            self.now = datetime.datetime.now(tz)
            if config.update_startup:
                await self.main()

            while not stop_event.is_set():
                self.now = datetime.datetime.now(tz)

                if mode == "time" and update_times:
                    candidates = []
                    for h, m in update_times:
                        candidate = self.now.replace(hour=h, minute=m, second=0, microsecond=0)
                        if candidate <= self.now:
                            candidate = candidate + datetime.timedelta(days=1)
                        candidates.append(candidate)

                    next_time = min(candidates)
                    wait_seconds = (next_time - self.now).total_seconds()
                    print(t("msg.schedule_update_time").format(time=next_time.strftime("%Y-%m-%d %H:%M:%S")))

                    try:
                        await asyncio.wait_for(stop_event.wait(), timeout=wait_seconds)
                        if stop_event.is_set():
                            break
                    except asyncio.TimeoutError:
                        self.now = datetime.datetime.now(tz)
                        await self.main()
                else:
                    next_time = self.now + datetime.timedelta(hours=config.update_interval)
                    print(t("msg.schedule_update_time").format(time=next_time.strftime("%Y-%m-%d %H:%M:%S")))

                    try:
                        await asyncio.wait_for(stop_event.wait(), timeout=config.update_interval * 3600)
                    except asyncio.TimeoutError:
                        self.now = datetime.datetime.now(tz)
                        await self.main()

        except asyncio.CancelledError:
            print(t("msg.schedule_cancelled"))


if __name__ == "__main__":
    info = get_version_info()
    print(t("msg.version_info").format(name=info["name"], version=info["version"]))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    update_source = UpdateSource()
    loop.run_until_complete(update_source.start())
