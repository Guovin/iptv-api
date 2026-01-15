import asyncio
import gzip
import json
import math
import os
import pickle
import re
import tempfile
from collections import defaultdict
from logging import INFO

import utils.constants as constants
from utils.alias import Alias
from utils.config import config
from utils.db import get_db_connection, return_db_connection
from utils.frozen import is_url_frozen, mark_url_bad, mark_url_good
from utils.i18n import t
from utils.ip_checker import IPChecker
from utils.speed import (
    get_speed,
    get_speed_result,
    get_sort_result,
    check_ffmpeg_installed_status
)
from utils.tools import (
    format_name,
    get_name_value,
    check_url_by_keywords,
    get_total_urls,
    add_url_info,
    resource_path,
    get_name_urls_from_file,
    get_logger,
    get_datetime_now,
    get_url_host,
    check_ipv_type_match,
    convert_to_m3u,
    custom_print,
    get_name_uri_from_dir,
    get_resolution_value,
    get_public_url
)
from utils.types import ChannelData, OriginType, CategoryChannelData, WhitelistMaps
from utils.whitelist import is_url_whitelisted, get_whitelist_url, get_whitelist_total_count

channel_alias = Alias()
ip_checker = IPChecker()
location_list = config.location
isp_list = config.isp
min_resolution_value = config.min_resolution_value
open_history = config.open_history
open_local = config.open_local
open_rtmp = config.open_rtmp
retain_origin = ["whitelist", "hls"]


def format_channel_data(url: str, origin: OriginType) -> ChannelData:
    """
    Format the channel data
    """
    url_partition = url.partition("$")
    url = url_partition[0]
    info = url_partition[2]
    if info and info.startswith("!"):
        origin = "whitelist"
        info = info[1:]
    return {
        "id": hash(url),
        "url": url,
        "host": get_url_host(url),
        "origin": origin,
        "ipv_type": None,
        "extra_info": info
    }


def check_channel_need_frozen(info) -> bool:
    """
    Check if the channel need to be frozen
    """
    delay = info.get("delay", 0)
    if delay == -1 or info.get("speed", 0) == 0:
        return True
    if info.get("resolution"):
        if get_resolution_value(info["resolution"]) < min_resolution_value:
            return True
    return False


def get_channel_data_from_file(channels, file, whitelist_maps, blacklist,
                               local_data=None, hls_data=None) -> CategoryChannelData:
    """
    Get the channel data from the file
    """
    current_category = ""

    for line in file:
        line = line.strip()
        if "#genre#" in line:
            current_category = line.partition(",")[0]
        else:
            name_value = get_name_value(
                line, pattern=constants.demo_txt_pattern, check_value=False
            )
            if name_value and name_value[0]:
                name = name_value[0]["name"]
                url = name_value[0]["value"]
                category_dict = channels[current_category]
                first_time = name not in category_dict
                if first_time:
                    category_dict[name] = []
                existing_urls = {d.get("url") for d in category_dict.get(name, []) if d.get("url")}

                if first_time:
                    for whitelist_url in get_whitelist_url(whitelist_maps, name):
                        formatted = format_channel_data(whitelist_url, "whitelist")
                        if formatted["url"] not in existing_urls:
                            category_dict[name].append(formatted)
                            existing_urls.add(formatted["url"])

                    if hls_data and name in hls_data:
                        for hls_url in hls_data[name]:
                            formatted = format_channel_data(hls_url, "hls")
                            if formatted["url"] not in existing_urls:
                                category_dict[name].append(formatted)
                                existing_urls.add(formatted["url"])

                    if open_local and local_data:
                        alias_names = channel_alias.get(name)
                        alias_names.update([name, format_name(name)])
                        for alias_name in alias_names:
                            if alias_name in local_data:
                                for local_url in local_data[alias_name]:
                                    if not check_url_by_keywords(local_url, blacklist):
                                        formatted = format_channel_data(local_url, "local")
                                        if formatted["url"] not in existing_urls:
                                            category_dict[name].append(formatted)
                                            existing_urls.add(formatted["url"])
                            elif alias_name.startswith("re:"):
                                raw_pattern = alias_name[3:]
                                try:
                                    pattern = re.compile(raw_pattern)
                                    for local_name in local_data:
                                        if re.match(pattern, local_name):
                                            for local_url in local_data[local_name]:
                                                if not check_url_by_keywords(local_url, blacklist):
                                                    formatted = format_channel_data(local_url, "local")
                                                    if formatted["url"] not in existing_urls:
                                                        category_dict[name].append(formatted)
                                                        existing_urls.add(formatted["url"])
                                except re.error:
                                    pass
                if url:
                    if is_url_whitelisted(whitelist_maps, url, name):
                        formatted = format_channel_data(url, "whitelist")
                        if formatted["url"] not in existing_urls:
                            category_dict[name].append(formatted)
                            existing_urls.add(formatted["url"])
                    elif open_local and not check_url_by_keywords(url, blacklist):
                        formatted = format_channel_data(url, "local")
                        if formatted["url"] not in existing_urls:
                            category_dict[name].append(formatted)
                            existing_urls.add(formatted["url"])
    return channels


def get_channel_items(whitelist_maps, blacklist) -> CategoryChannelData:
    """
    Get the channel items from the source file
    """
    user_source_file = resource_path(config.source_file)
    channels = defaultdict(lambda: defaultdict(list))
    hls_data = None
    if config.open_rtmp:
        hls_data = get_name_uri_from_dir(constants.hls_path)
    local_data = get_name_urls_from_file(config.local_file)
    whitelist_count = get_whitelist_total_count(whitelist_maps)
    blacklist_count = len(blacklist)
    if whitelist_count:
        print(t("msg.whitelist_found").format(count=whitelist_count))
    if blacklist_count:
        print(t("msg.blacklist_found").format(count=blacklist_count))

    if os.path.exists(user_source_file):
        with open(user_source_file, "r", encoding="utf-8") as file:
            channels = get_channel_data_from_file(
                channels, file, whitelist_maps, blacklist, local_data, hls_data
            )

    if config.open_history:
        if os.path.exists(constants.cache_path):
            try:
                with gzip.open(constants.cache_path, "rb") as file:
                    old_result = pickle.load(file)
                    for cate, data in channels.items():
                        if cate in old_result:
                            for name, info_list in data.items():
                                urls = [
                                    url
                                    for item in info_list
                                    if (url := item["url"])
                                ]
                                if name in old_result[cate]:
                                    channel_data = channels[cate][name]
                                    for info in old_result[cate][name]:
                                        if info:
                                            info_url = info["url"]
                                            try:
                                                if info["origin"] in retain_origin or check_url_by_keywords(info_url,
                                                                                                            blacklist):
                                                    continue
                                                if check_channel_need_frozen(info):
                                                    mark_url_bad(info_url, initial=True)
                                                    continue
                                            except:
                                                pass
                                            if info_url not in urls:
                                                channel_data.append(info)

                                    if not channel_data:
                                        for info in old_result[cate][name]:
                                            old_result_url = info["url"]
                                            if info and info[
                                                "origin"] not in retain_origin and old_result_url not in urls and not check_url_by_keywords(
                                                old_result_url, blacklist):
                                                channel_data.append(info)

            except Exception as e:
                print(t("msg.error_load_cache").format(info=e))
                pass
    return channels


def format_channel_name(name):
    """
    Format the channel name with sub and replace and lower
    """
    return channel_alias.get_primary(name)


def channel_name_is_equal(name1, name2):
    """
    Check if the channel name is equal
    """
    name1_format = format_channel_name(name1)
    name2_format = format_channel_name(name2)
    return name1_format == name2_format


def get_channel_results_by_name(name, data):
    """
    Get channel results from data by name
    """
    format_name = format_channel_name(name)
    results = data.get(format_name, [])
    return results


def get_channel_url(text):
    """
    Get the url from text
    """
    url = None
    url_search = constants.url_pattern.search(text)
    if url_search:
        url = url_search.group()
    return url


def init_info_data(data: dict, category: str, name: str) -> None:
    """
    Initialize channel info data structure if not exists
    """
    data.setdefault(category, {}).setdefault(name, [])


def append_data_to_info_data(
        info_data: dict,
        category: str,
        name: str,
        data: list,
        origin: str = None,
        whitelist_maps: WhitelistMaps = None,
        blacklist: list = None,
        ipv_type_data: dict = None
) -> None:
    """
    Append channel data to total info data with deduplication and validation

    Args:
        info_data: The main data structure to update
        category: Category key for the data
        name: Name key within the category
        data: List of channel items to process
        origin: Default origin for items
        whitelist_maps: Maps of whitelist keywords
        blacklist: List of blacklist keywords
        ipv_type_data: Dictionary to cache IP type information
    """
    init_info_data(info_data, category, name)

    channel_list = info_data[category][name]
    existing_urls = {info["url"] for info in channel_list if "url" in info}

    for item in data:
        try:
            channel_id = item.get("id") or hash(item["url"])
            url = item["url"]
            host = item.get("host") or get_url_host(url)
            date = item.get("date")
            delay = item.get("delay")
            speed = item.get("speed")
            resolution = item.get("resolution")
            url_origin = item.get("origin", origin)
            ipv_type = item.get("ipv_type")
            location = item.get("location")
            isp = item.get("isp")
            headers = item.get("headers")
            catchup = item.get("catchup")
            extra_info = item.get("extra_info", "")

            if not url or url in existing_urls:
                continue

            if url_origin != "whitelist" and whitelist_maps and is_url_whitelisted(whitelist_maps, url, name):
                url_origin = "whitelist"

            if not url_origin:
                continue

            if url_origin not in retain_origin:
                url = get_channel_url(url)
                if not url or is_url_frozen(url) or blacklist and check_url_by_keywords(url, blacklist):
                    continue

                if not ipv_type:
                    if ipv_type_data and host in ipv_type_data:
                        ipv_type = ipv_type_data[host]
                    else:
                        ipv_type = ip_checker.get_ipv_type(url)
                        if ipv_type_data is not None:
                            ipv_type_data[host] = ipv_type

                if not check_ipv_type_match(ipv_type):
                    continue

                if not location or not isp:
                    ip = ip_checker.get_ip(url)
                    if ip:
                        location, isp = ip_checker.find_map(ip)

                if location and location_list and not any(item in location for item in location_list):
                    continue

                if isp and isp_list and not any(item in isp for item in isp_list):
                    continue
            channel_list.append({
                "id": channel_id,
                "url": url,
                "host": host,
                "date": date,
                "delay": delay,
                "speed": speed,
                "resolution": resolution,
                "origin": url_origin,
                "ipv_type": ipv_type,
                "location": location,
                "isp": isp,
                "headers": headers,
                "catchup": catchup,
                "extra_info": extra_info
            })
            existing_urls.add(url)

        except Exception as e:
            print(t("msg.error_append_channel_data").format(info=e))
            continue


def append_old_data_to_info_data(info_data, cate, name, data, whitelist_maps=None, blacklist=None, ipv_type_data=None):
    """
    Append old existed channel data to total info data
    """

    def append_and_print(items, origin, label):
        if items:
            append_data_to_info_data(
                info_data, cate, name, items,
                origin=origin if origin else None,
                whitelist_maps=whitelist_maps,
                blacklist=blacklist,
                ipv_type_data=ipv_type_data
            )
        items_len = len(items)
        if items_len > 0:
            print(f"{label}: {items_len}", end=", ")

    whitelist_data = [item for item in data if item["origin"] == "whitelist"]
    append_and_print(whitelist_data, "whitelist", t("name.whitelist"))

    if open_local:
        local_data = [item for item in data if item["origin"] == "local"]
        append_and_print(local_data, "local", t("name.local"))

    if open_rtmp:
        hls_data = [item for item in data if item["origin"] == "hls"]
        append_and_print(hls_data, None, t("name.hls"))

    if open_history:
        history_data = [item for item in data if item["origin"] not in ["hls", "local", "whitelist"]]
        append_and_print(history_data, None, t("name.history"))


def print_channel_number(data: CategoryChannelData, cate: str, name: str):
    """
    Print channel number
    """
    channel_list = data.get(cate, {}).get(name, [])
    print("IPv4:", len([channel for channel in channel_list if channel["ipv_type"] == "ipv4"]), end=", ")
    print("IPv6:", len([channel for channel in channel_list if channel["ipv_type"] == "ipv6"]), end=", ")
    print(
        f"{t("name.total")}:",
        len(channel_list),
    )


def append_total_data(
        items,
        data,
        subscribe_result=None,
        whitelist_maps=None,
        blacklist=None,
):
    """
    Append all method data to total info data
    """
    total_result = [
        ("subscribe", subscribe_result),
    ]
    url_hosts_ipv_type = {}
    for obj in data.values():
        for value_list in obj.values():
            for value in value_list:
                if value_ipv_type := value.get("ipv_type", None):
                    url_hosts_ipv_type[get_url_host(value["url"])] = value_ipv_type
    for cate, channel_obj in items:
        for name, old_info_list in channel_obj.items():
            print(f"{name}:", end=" ")
            if old_info_list:
                append_old_data_to_info_data(data, cate, name, old_info_list, whitelist_maps=whitelist_maps,
                                             blacklist=blacklist,
                                             ipv_type_data=url_hosts_ipv_type)
            for method, result in total_result:
                if config.open_method[method]:
                    name_results = get_channel_results_by_name(name, result)
                    append_data_to_info_data(
                        data, cate, name, name_results, origin=method, whitelist_maps=whitelist_maps,
                        blacklist=blacklist,
                        ipv_type_data=url_hosts_ipv_type
                    )
                    print(f"{t(f"name.{method}")}:", len(name_results), end=", ")
            print_channel_number(data, cate, name)


async def test_speed(data, ipv6=False, callback=None, on_task_complete=None):
    """
    Test speed of channel data
    """
    ipv6_proxy_url = None if (not config.open_ipv6 or ipv6) else constants.ipv6_proxy
    open_headers = config.open_headers
    get_resolution = config.open_filter_resolution and check_ffmpeg_installed_status()
    semaphore = asyncio.Semaphore(config.speed_test_limit)
    logger = get_logger(constants.speed_test_log_path, level=INFO, init=True)

    async def limited_get_speed(channel_info):
        async with semaphore:
            headers = (open_headers and channel_info.get("headers")) or None
            return await get_speed(
                channel_info,
                headers=headers,
                ipv6_proxy=ipv6_proxy_url,
                filter_resolution=get_resolution,
                logger=logger,
                callback=callback,
            )

    total_tasks = sum(len(info_list) for channel_obj in data.values() for info_list in channel_obj.values())
    total_tasks_by_channel = defaultdict(int)
    for cate, channel_obj in data.items():
        for name, info_list in channel_obj.items():
            total_tasks_by_channel[(cate, name)] += len(info_list)
    completed = 0
    tasks = []
    channel_map = {}
    grouped_results = {}
    completed_by_channel = defaultdict(int)

    def _on_task_done(task):
        nonlocal completed
        try:
            result = task.result()
        except Exception:
            result = {}
        meta = channel_map.get(task)
        if not meta:
            return
        cate, name, info = meta
        if cate not in grouped_results:
            grouped_results[cate] = {}
        if name not in grouped_results[cate]:
            grouped_results[cate][name] = []
        merged = {**info, **result}
        grouped_results[cate][name].append(merged)

        if check_channel_need_frozen(merged):
            mark_url_bad(merged.get("url"))
        else:
            mark_url_good(merged.get("url"))

        completed += 1
        completed_by_channel[(cate, name)] += 1

        is_channel_last = completed_by_channel[(cate, name)] >= total_tasks_by_channel.get((cate, name), 0)
        is_last = completed >= total_tasks

        if on_task_complete:
            try:
                on_task_complete(cate, name, merged, is_channel_last, is_last)
            except Exception:
                pass

    for cate, channel_obj in data.items():
        for name, info_list in channel_obj.items():
            for info in info_list:
                info['name'] = name
                task = asyncio.create_task(limited_get_speed(info))
                channel_map[task] = (cate, name, info)
                task.add_done_callback(_on_task_done)
                tasks.append(task)

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

    logger.handlers.clear()
    return grouped_results


def sort_channel_result(channel_data, result=None, filter_host=False, ipv6_support=True):
    """
    Sort channel result
    """
    channel_result = defaultdict(lambda: defaultdict(list))
    for cate, obj in channel_data.items():
        for name, values in obj.items():
            whitelist_result = []
            test_result = result.get(cate, {}).get(name, []) if result else []
            if values:
                for value in values:
                    if value["origin"] in retain_origin or (
                            not ipv6_support and result and value["ipv_type"] == "ipv6"
                    ):
                        whitelist_result.append(value)
                    elif filter_host or not result:
                        test_result.append({**value, **get_speed_result(value["host"])} if filter_host else value)
            total_result = whitelist_result + get_sort_result(test_result, ipv6_support=ipv6_support)
            channel_result[cate][name].extend(total_result)
    return channel_result


def generate_channel_statistic(logger, cate, name, values):
    """
    Generate channel statistic
    """
    total = len(values)
    valid = len([v for v in values if (v.get("speed") or 0) > 0 and (v.get("delay") or -1) != -1])
    valid_rate = (valid / total * 100) if total > 0 else 0
    whitelist_count = len([v for v in values if v.get("origin") == "whitelist"])
    ipv4_count = len([v for v in values if v.get("ipv_type") == "ipv4"])
    ipv6_count = len([v for v in values if v.get("ipv_type") == "ipv6"])
    min_delay = min((v.get("delay") for v in values if (v.get("delay") or -1) != -1), default=-1)
    max_speed = max((v.get("speed") for v in values if (v.get("speed") or 0) > 0 and not math.isinf(v.get("speed"))),
                    default=0)
    avg_speed = (
        sum((v.get("speed") or 0) for v in values if
            (v.get("speed") or 0) > 0 and not math.isinf(v.get("speed"))) / valid
        if valid > 0 else 0
    )
    max_resolution = max(
        (v.get("resolution") for v in values if v.get("resolution")),
        key=lambda r: get_resolution_value(r),
        default="None"
    )
    logger.info(
        f"Category: {cate}, Name: {name}, Total: {total}, Valid: {valid}, Valid Percent: {valid_rate:.2f}%, Whitelist: {whitelist_count}, IPv4: {ipv4_count}, IPv6: {ipv6_count}, Min Delay: {min_delay} ms, Max Speed: {max_speed:.2f} M/s, Avg Speed: {avg_speed:.2f} M/s, Max Resolution: {max_resolution}")
    print(
        f"\n{f"{t("name.category")}: {cate}, {t("name.name")}: {name}, {t("name.total")}: {total}, {t("name.valid")}: {valid}, {t("name.valid_percent")}: {valid_rate:.2f}%, {t("name.whitelist")}: {whitelist_count}, IPv4: {ipv4_count}, IPv6: {ipv6_count}, {t("name.min_delay")}: {min_delay} ms, {t("name.max_speed")}: {max_speed:.2f} M/s, {t("name.average_speed")}: {avg_speed:.2f} M/s, {t("name.max_resolution")}: {max_resolution}"}")


def process_write_content(
        path: str,
        data: CategoryChannelData,
        hls_url: str = None,
        open_empty_category: bool = False,
        ipv_type_prefer: list[str] = None,
        origin_type_prefer: list[str] = None,
        first_channel_name: str = None,
        enable_log: bool = False,
        is_last: bool = False,
):
    """
    Get channel write content
    :param path: write into path
    :param data: channel data
    :param hls_url: hls url
    :param open_empty_category: show empty category
    :param ipv_type_prefer: ipv type prefer
    :param origin_type_prefer: origin type prefer
    :param first_channel_name: the first channel name
    :param enable_log: enable log
    :param is_last: is last write
    """
    content = ""
    no_result_name = []
    first_cate = True
    result_data = defaultdict(list)
    custom_print.disable = not enable_log
    rtmp_type = ["hls"] if hls_url else []
    open_url_info = config.open_url_info
    for cate, channel_obj in data.items():
        content += f"{'\n\n' if not first_cate else ''}{cate},#genre#"
        first_cate = False
        channel_obj_keys = channel_obj.keys()
        for i, name in enumerate(channel_obj_keys):
            info_list = data.get(cate, {}).get(name, [])
            channel_urls = get_total_urls(info_list, ipv_type_prefer, origin_type_prefer, rtmp_type)
            result_data[name].extend(channel_urls)
            if not channel_urls:
                if open_empty_category:
                    no_result_name.append(name)
                continue
            for item in channel_urls:
                item_url = item["url"]
                if open_url_info and item["extra_info"]:
                    item_url = add_url_info(item_url, item["extra_info"])
                total_item_url = f"{hls_url}/{item['id']}.m3u8" if hls_url else item_url
                content += f"\n{name},{total_item_url}"
    if open_empty_category and no_result_name:
        custom_print(f"\n{t("msg.no_result_channel")}")
        content += f"\n\n{t("content.no_result_channel_genre")},#genre#"
        for i, name in enumerate(no_result_name):
            end_char = ", " if i < len(no_result_name) - 1 else ""
            custom_print(name, end=end_char)
            content += f"\n{name},url"
    if config.open_update_time:
        update_time_item = next(
            (urls[0] for channel_obj in data.values()
             for info_list in channel_obj.values()
             if (urls := get_total_urls(info_list, ipv_type_prefer, origin_type_prefer, rtmp_type))),
            {"id": "id", "url": "url"}
        )
        now = get_datetime_now()
        update_time_item_url = update_time_item["url"]
        update_title = t("content.update_time") if is_last else t("content.update_running")
        if open_url_info and update_time_item["extra_info"]:
            update_time_item_url = add_url_info(update_time_item_url, update_time_item["extra_info"])
        value = f"{hls_url}/{update_time_item["id"]}.m3u8" if hls_url else update_time_item_url
        if config.update_time_position == "top":
            content = f"{update_title},#genre#\n{now},{value}\n\n{content}"
        else:
            content += f"\n\n{update_title},#genre#\n{now},{value}"
    if hls_url:
        db_dir = os.path.dirname(constants.rtmp_data_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        try:
            conn = get_db_connection(constants.rtmp_data_path)
        except Exception as e:
            print(t("msg.write_error").format(info=f"open rtmp db error: {e}"))
        else:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS result_data (id TEXT PRIMARY KEY, url TEXT, headers TEXT)"
                )
                for data_list in result_data.values():
                    for item in data_list:
                        cursor.execute(
                            "INSERT OR REPLACE INTO result_data (id, url, headers) VALUES (?, ?, ?)",
                            (item["id"], item["url"], json.dumps(item.get("headers", None)))
                        )
                conn.commit()
            finally:
                return_db_connection(constants.rtmp_data_path, conn)
    try:
        target_dir = os.path.dirname(path) or "."
        os.makedirs(target_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, dir=target_dir,
                                         prefix=os.path.basename(path) + ".tmp.") as tmpf:
            tmpf.write(content)
            tmp_path = tmpf.name
        os.replace(tmp_path, path)
        try:
            os.chmod(path, 0o644)
        except Exception:
            pass
    except Exception as e:
        print(e)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e2:
            print(t("msg.write_error").format(info=e2))
            return
    try:
        convert_to_m3u(path, first_channel_name, data=result_data)
    except Exception:
        pass


def write_channel_to_file(data, ipv6=False, first_channel_name=None, skip_print=False, is_last=False):
    """
    Write channel to file
    """
    try:
        if not skip_print:
            print(t("msg.writing_result"))
        open_empty_category = config.open_empty_category
        ipv_type_prefer = list(config.ipv_type_prefer)
        if any(pref == "auto" for pref in ipv_type_prefer):
            ipv_type_prefer = ["ipv6", "ipv4"] if ipv6 else ["ipv4", "ipv6"]
        origin_type_prefer = config.origin_type_prefer
        hls_url = f"{get_public_url()}/hls"
        file_list = [
            {"path": config.final_file, "enable_log": True},
            {"path": constants.ipv4_result_path, "ipv_type_prefer": ["ipv4"]},
            {"path": constants.ipv6_result_path, "ipv_type_prefer": ["ipv6"]}
        ]
        if config.open_rtmp and not os.getenv("GITHUB_ACTIONS"):
            file_list += [
                {"path": constants.hls_result_path, "hls_url": hls_url},
                {
                    "path": constants.hls_ipv4_result_path,
                    "hls_url": hls_url,
                    "ipv_type_prefer": ["ipv4"]
                },
                {
                    "path": constants.hls_ipv6_result_path,
                    "hls_url": hls_url,
                    "ipv_type_prefer": ["ipv6"]
                },
            ]
        for file in file_list:
            target_dir = os.path.dirname(file["path"])
            if target_dir:
                os.makedirs(target_dir, exist_ok=True)
            process_write_content(
                path=file["path"],
                data=data,
                hls_url=file.get("hls_url"),
                open_empty_category=open_empty_category,
                ipv_type_prefer=file.get("ipv_type_prefer", ipv_type_prefer),
                origin_type_prefer=origin_type_prefer,
                first_channel_name=first_channel_name,
                enable_log=file.get("enable_log", False),
                is_last=is_last
            )
        if not skip_print:
            print(t("msg.write_success"))
    except Exception as e:
        print(t("msg.write_error").format(info=e))
