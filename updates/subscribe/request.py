import os
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
    get_name_value,
    get_logger, join_url,
    github_blob_to_raw,
    save_url_content
)


async def get_channels_by_subscribe_urls(
        urls,
        names=None,
        retry=True,
        error_print=True,
        whitelist=None,
        pbar_desc=t("pbar.getting_name").format(name=t("name.subscribe")),
        callback=None,
):
    """
    Get the channels by subscribe urls
    """
    if not os.getenv("GITHUB_ACTIONS") and config.cdn_url:
        def _map_raw(u):
            raw_u = github_blob_to_raw(u)
            return join_url(config.cdn_url, raw_u) if "raw.githubusercontent.com" in raw_u else raw_u

        def _map_entry(e):
            if isinstance(e, dict):
                e = e.copy()
                e['url'] = _map_raw(e.get('url'))
                return e
            return _map_raw(e)

        urls = [_map_entry(u) for u in urls]
        whitelist = [_map_raw(u) for u in whitelist] if whitelist else None
    if whitelist:
        index_map = {u: i for i, u in enumerate(whitelist)}

        def sort_key(u):
            key = u['url'] if isinstance(u, dict) else u
            return index_map.get(key, len(whitelist))

        urls.sort(key=sort_key)
    subscribe_results = {}
    subscribe_urls_len = len(urls)
    pbar = tqdm_asyncio(
        total=subscribe_urls_len,
        desc=pbar_desc,
    )
    start_time = time()
    mode_name = t("name.subscribe")
    if callback:
        callback(
            t("pbar.getting_name").format(name=mode_name),
            0,
        )
    logger = get_logger(constants.nomatch_log_path, level=INFO, init=True)

    def process_subscribe_channels(subscribe_info: str | dict) -> defaultdict:
        subscribe_url = subscribe_info.get('url') if isinstance(subscribe_info, dict) else subscribe_info
        headers = subscribe_info.get('headers') if isinstance(subscribe_info, dict) else None
        channels = defaultdict(list)
        in_whitelist = whitelist and (subscribe_url in whitelist)
        try:
            response = None
            try:
                if retry:
                    response = retry_func(lambda: get_soup_requests(subscribe_url, timeout=config.request_timeout,
                                                                    headers_override=headers), name=subscribe_url)
                else:
                    response = get_soup_requests(subscribe_url, timeout=config.request_timeout,
                                                 headers_override=headers)
            except Exception as e:
                print(f"{subscribe_url}: {e}")
            if response:
                if hasattr(response, 'text'):
                    response.encoding = "utf-8"
                    content = response.text
                else:
                    content = str(response)
                try:
                    save_url_content('subscribe', subscribe_url, content)
                except Exception:
                    pass
                m3u_type = True if "#EXTM3U" in content else False
                data = get_name_value(
                    content,
                    pattern=(
                        constants.multiline_m3u_pattern
                        if m3u_type
                        else constants.multiline_txt_pattern
                    ),
                    open_headers=config.open_headers if m3u_type else False
                )
                for item in data:
                    data_name = item.get("name", "").strip()
                    url = item.get("value", "").strip()
                    if data_name and url:
                        name = format_channel_name(data_name)
                        if names and name not in names:
                            logger.info(f"{data_name},{url}")
                            continue
                        url_partition = url.partition("$")
                        url = url_partition[0]
                        info = url_partition[2]
                        value = {
                            "url": url,
                            "headers": item.get("headers", None),
                            "extra_info": info
                        }
                        if in_whitelist:
                            value["origin"] = "whitelist"
                        if name in channels:
                            if value not in channels[name]:
                                channels[name].append(value)
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
                    t("msg.progress_desc").format(name=f"{t('pbar.get')}{mode_name}",
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
