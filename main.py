import asyncio
import copy
import os
import pickle
from time import time

from tqdm import tqdm

import utils.constants as constants
from service.app import run_service
from updates.fofa import get_channels_by_fofa
from updates.hotel import get_channels_by_hotel
from updates.multicast import get_channels_by_multicast
from updates.online_search import get_channels_by_online_search
from updates.subscribe import get_channels_by_subscribe_urls
from utils.channel import (
    get_channel_items,
    append_total_data,
    process_sort_channel_list,
    write_channel_to_file,
    get_channel_data_cache_with_compare,
)
from utils.config import config
from utils.tools import (
    get_pbar_remaining,
    get_ip_address,
    process_nested_dict,
    format_interval,
    check_ipv6_support,
    get_urls_from_file,
    get_version_info,
    join_url
)
from utils.types import CategoryChannelData


class UpdateSource:

    def __init__(self):
        self.update_progress = None
        self.run_ui = False
        self.tasks = []
        self.channel_items: CategoryChannelData = {}
        self.hotel_fofa_result = {}
        self.hotel_foodie_result = {}
        self.multicast_result = {}
        self.subscribe_result = {}
        self.online_search_result = {}
        self.channel_data: CategoryChannelData = {}
        self.pbar = None
        self.total = 0
        self.start_time = None

    async def visit_page(self, channel_names: list[str] = None):
        tasks_config = [
            ("hotel_fofa", get_channels_by_fofa, "hotel_fofa_result"),
            ("multicast", get_channels_by_multicast, "multicast_result"),
            ("hotel_foodie", get_channels_by_hotel, "hotel_foodie_result"),
            ("subscribe", get_channels_by_subscribe_urls, "subscribe_result"),
            (
                "online_search",
                get_channels_by_online_search,
                "online_search_result",
            ),
        ]

        for setting, task_func, result_attr in tasks_config:
            if (
                    setting == "hotel_foodie" or setting == "hotel_fofa"
            ) and config.open_hotel == False:
                continue
            if config.open_method[setting]:
                if setting == "subscribe":
                    subscribe_urls = get_urls_from_file(constants.subscribe_path)
                    whitelist_urls = get_urls_from_file(constants.whitelist_path)
                    if not os.environ.get("GITHUB_ACTIONS") and config.cdn_url:
                        subscribe_urls = [join_url(config.cdn_url, url) if "raw.githubusercontent.com" in url else url
                                          for url in subscribe_urls]
                    task = asyncio.create_task(
                        task_func(subscribe_urls, whitelist=whitelist_urls, callback=self.update_progress)
                    )
                elif setting == "hotel_foodie" or setting == "hotel_fofa":
                    task = asyncio.create_task(task_func(callback=self.update_progress))
                else:
                    task = asyncio.create_task(
                        task_func(channel_names, callback=self.update_progress)
                    )
                self.tasks.append(task)
                setattr(self, result_attr, await task)

    def pbar_update(self, name: str = "", item_name: str = ""):
        if self.pbar.n < self.total:
            self.pbar.update()
            self.update_progress(
                f"正在进行{name}, 剩余{self.total - self.pbar.n}个{item_name}, 预计剩余时间: {get_pbar_remaining(n=self.pbar.n, total=self.total, start_time=self.start_time)}",
                int((self.pbar.n / self.total) * 100),
            )

    def get_urls_len(self, is_filter: bool = False) -> int:
        data = copy.deepcopy(self.channel_data)
        if is_filter:
            process_nested_dict(data, seen={}, force_str="!")
        processed_urls = set(
            url_info["url"]
            for channel_obj in data.values()
            for url_info_list in channel_obj.values()
            for url_info in url_info_list
        )
        return len(processed_urls)

    async def main(self):
        try:
            user_final_file = config.final_file
            main_start_time = time()
            if config.open_update:
                self.channel_items = get_channel_items()
                channel_names = [
                    name
                    for channel_obj in self.channel_items.values()
                    for name in channel_obj.keys()
                ]
                if not channel_names:
                    print(f"❌ No channel names found! Please check the {config.source_file}!")
                    return
                await self.visit_page(channel_names)
                self.tasks = []
                append_total_data(
                    self.channel_items.items(),
                    channel_names,
                    self.channel_data,
                    self.hotel_fofa_result,
                    self.multicast_result,
                    self.hotel_foodie_result,
                    self.subscribe_result,
                    self.online_search_result,
                )
                channel_data_cache = copy.deepcopy(self.channel_data)
                ipv6_support = config.ipv6_support or check_ipv6_support()
                open_sort = config.open_sort
                if open_sort:
                    urls_total = self.get_urls_len()
                    self.total = self.get_urls_len(is_filter=True)
                    print(f"Total urls: {urls_total}, need to sort: {self.total}")
                    sort_callback = lambda: self.pbar_update(name="测速", item_name="接口")
                    self.update_progress(
                        f"正在测速排序, 共{urls_total}个接口, {self.total}个接口需要进行测速",
                        0,
                    )
                    self.start_time = time()
                    self.pbar = tqdm(total=self.total, desc="Sorting")
                    self.channel_data = await process_sort_channel_list(
                        self.channel_data,
                        ipv6=ipv6_support,
                        callback=sort_callback,
                    )
                self.total = 12
                self.pbar = tqdm(total=self.total, desc="Writing")
                self.start_time = time()
                write_channel_to_file(
                    self.channel_data,
                    ipv6=ipv6_support,
                    first_channel_name=channel_names[0],
                    callback=lambda: self.pbar_update(name="写入结果", item_name="文件"),
                )
                self.pbar.close()
                if config.open_history:
                    if open_sort:
                        get_channel_data_cache_with_compare(
                            channel_data_cache, self.channel_data
                        )
                    with open(
                            constants.cache_path,
                            "wb",
                    ) as file:
                        pickle.dump(channel_data_cache, file)
                print(
                    f"🥳 Update completed! Total time spent: {format_interval(time() - main_start_time)}. Please check the {user_final_file} file!"
                )
            if self.run_ui:
                open_service = config.open_service
                service_tip = ", 可使用以下地址观看直播:" if open_service else ""
                tip = (
                    f"✅ 服务启动成功{service_tip}"
                    if open_service and config.open_update == False
                    else f"🥳 更新完成, 耗时: {format_interval(time() - main_start_time)}, 请检查{user_final_file}文件{service_tip}"
                )
                self.update_progress(
                    tip,
                    100,
                    True,
                    url=f"{get_ip_address()}" if open_service else None,
                )
                if open_service:
                    run_service()
        except asyncio.exceptions.CancelledError:
            print("Update cancelled!")

    async def start(self, callback=None):
        def default_callback(self, *args, **kwargs):
            pass

        self.update_progress = callback or default_callback
        self.run_ui = True if callback else False
        await self.main()

    def stop(self):
        for task in self.tasks:
            task.cancel()
        self.tasks = []
        if self.pbar:
            self.pbar.close()


if __name__ == "__main__":
    info = get_version_info()
    print(f"ℹ️ {info['name']} Version: {info['version']}")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    update_source = UpdateSource()
    loop.run_until_complete(update_source.start())
