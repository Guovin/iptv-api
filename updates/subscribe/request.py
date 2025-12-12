from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from logging import INFO
from time import time

from tqdm.asyncio import tqdm_asyncio

import utils.constants as constants
from utils.channel import format_channel_name
from utils.config import config
from utils.i18n import t
from utils.requests.tools import get_soup_requests
from utils.retry import retry_func
from utils.tools import (
    merge_objects,
    get_pbar_remaining,
    get_name_url,
    get_logger
)


async def get_channels_by_subscribe_urls(
        urls,
        names=None,
        multicast=False,
        hotel=False,
        retry=True,
        error_print=True,
        whitelist=None,
        pbar_desc="Processing subscribe",
        callback=None,
):
    """
    Get the channels by subscribe urls
    """
    if whitelist:
        urls.sort(key=lambda url: whitelist.index(url) if url in whitelist else len(whitelist))
    subscribe_results = {}
    subscribe_urls_len = len(urls)
    pbar = tqdm_asyncio(
        total=subscribe_urls_len,
        desc=pbar_desc,
    )
    start_time = time()
    mode_name = t("name.multicast") if multicast else t("name.hotel") if hotel else t("name.subscribe")
    if callback:
        callback(
            f"{t("pbar.getting_name").format(name=mode_name)}",
            0,
        )
    hotel_name = constants.origin_map["hotel"]
    logger = get_logger(constants.nomatch_log_path, level=INFO, init=True)

    def process_subscribe_channels(subscribe_info: str | dict) -> defaultdict:
        region = ""
        url_type = ""
        if (multicast or hotel) and isinstance(subscribe_info, dict):
            region = subscribe_info.get("region")
            url_type = subscribe_info.get("type", "")
            subscribe_url = subscribe_info.get("url")
        else:
            subscribe_url = subscribe_info
        channels = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        in_whitelist = whitelist and (subscribe_url in whitelist)
        try:
            response = None
            try:
                response = (
                    retry_func(
                        lambda: get_soup_requests(
                            subscribe_url, timeout=config.request_timeout
                        ),
                        name=subscribe_url,
                    )
                    if retry
                    else get_soup_requests(subscribe_url, timeout=config.request_timeout)
                )
            except Exception as e:
                print(f"{subscribe_url}: {e}")
            if response:
                response.encoding = "utf-8"
                content = response.text
                m3u_type = True if "#EXTM3U" in content else False
                data = get_name_url(
                    content,
                    pattern=(
                        constants.multiline_m3u_pattern
                        if m3u_type
                        else constants.multiline_txt_pattern
                    ),
                    open_headers=config.open_headers if m3u_type else False
                )
                for item in data:
                    name = item["name"]
                    url = item["url"]
                    if name and url:
                        name = format_channel_name(name)
                        if names and name not in names:
                            logger.info(f"{item["name"]},{item["url"]}")
                            continue
                        url_partition = url.partition("$")
                        url = url_partition[0]
                        info = url_partition[2]
                        value = url if multicast else {
                            "url": url,
                            "headers": item.get("headers", None),
                            "extra_info": info
                        }
                        if in_whitelist:
                            value["origin"] = "whitelist"
                        if hotel:
                            value["extra_info"] = f"{region}{hotel_name}"
                        if name in channels:
                            if multicast:
                                if value not in channels[name][region][url_type]:
                                    channels[name][region][url_type].append(value)
                            elif value not in channels[name]:
                                channels[name].append(value)
                        else:
                            if multicast:
                                channels[name][region][url_type] = [value]
                            else:
                                channels[name] = [value]
        except Exception as e:
            if error_print:
                print(f"Error on {subscribe_url}: {e}")
        finally:
            logger.handlers.clear()
            pbar.update()
            if callback:
                callback(
                    t("msg.progress_desc").format(name=f"{t("pbar.get")}{mode_name}",
                                                  remaining_total=subscribe_urls_len - pbar.n,
                                                  item_name=mode_name,
                                                  remaining_time=get_pbar_remaining(n=pbar.n, total=pbar.total,
                                                                                    start_time=start_time)),
                    int((pbar.n / subscribe_urls_len) * 100),
                )
            return channels

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(process_subscribe_channels, subscribe_url)
            for subscribe_url in urls
        ]
        for future in futures:
            subscribe_results = merge_objects(subscribe_results, future.result())
    pbar.close()
    return subscribe_results
