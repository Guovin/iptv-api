import asyncio
import base64
import copy
import json
import os
import pickle
import re
from collections import defaultdict
from logging import INFO

from bs4 import NavigableString

import utils.constants as constants
from utils.alias import Alias
from utils.config import config
from utils.db import get_db_connection, return_db_connection
from utils.speed import (
    get_speed,
    sort_urls,
    check_ffmpeg_installed_status
)
from utils.tools import (
    format_name,
    get_name_url,
    check_url_by_keywords,
    get_total_urls,
    process_nested_dict,
    add_url_info,
    resource_path,
    get_urls_from_file,
    get_name_urls_from_file,
    get_logger,
    get_datetime_now,
    get_url_host,
    check_url_ipv6,
    check_ipv_type_match,
    get_ip_address,
    convert_to_m3u,
    custom_print,
    get_name_uri_from_dir
)
from utils.types import ChannelData, OriginType, CategoryChannelData

channel_alias = Alias()


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


def get_channel_data_from_file(channels, file, whitelist, open_local=config.open_local,
                               local_data=None, live_data=None, hls_data=None) -> CategoryChannelData:
    """
    Get the channel data from the file
    """
    current_category = ""

    for line in file:
        line = line.strip()
        if "#genre#" in line:
            current_category = line.partition(",")[0]
        else:
            name_url = get_name_url(
                line, pattern=constants.demo_txt_pattern, check_url=False
            )
            if name_url and name_url[0]:
                name = name_url[0]["name"]
                url = name_url[0]["url"]
                category_dict = channels[current_category]
                if name not in category_dict:
                    category_dict[name] = []
                if name in whitelist:
                    for whitelist_url in whitelist[name]:
                        category_dict[name].append(format_channel_data(whitelist_url, "whitelist"))
                if live_data and name in live_data:
                    for live_url in live_data[name]:
                        category_dict[name].append(format_channel_data(live_url, "live"))
                if hls_data and name in hls_data:
                    for hls_url in hls_data[name]:
                        category_dict[name].append(format_channel_data(hls_url, "hls"))
                if open_local:
                    if url:
                        category_dict[name].append(format_channel_data(url, "local"))
                    if local_data:
                        format_key = format_name(name)
                        if format_key in local_data:
                            for local_url in local_data[format_key]:
                                category_dict[name].append(format_channel_data(local_url, "local"))
    return channels


def get_channel_items() -> CategoryChannelData:
    """
    Get the channel items from the source file
    """
    user_source_file = resource_path(config.source_file)
    channels = defaultdict(lambda: defaultdict(list))
    live_data = None
    hls_data = None
    if config.open_rtmp:
        live_data = get_name_uri_from_dir(constants.live_path)
        hls_data = get_name_uri_from_dir(constants.hls_path)
    local_data = get_name_urls_from_file(config.local_file, format_name_flag=True)
    whitelist = get_name_urls_from_file(constants.whitelist_path)
    whitelist_urls = get_urls_from_file(constants.whitelist_path)
    whitelist_len = len(list(whitelist.keys()))
    if whitelist_len:
        print(f"Found {whitelist_len} channel in whitelist")

    if os.path.exists(user_source_file):
        with open(user_source_file, "r", encoding="utf-8") as file:
            channels = get_channel_data_from_file(
                channels, file, whitelist, config.open_local, local_data, live_data, hls_data
            )

    if config.open_history:
        if os.path.exists(constants.cache_path):
            with open(constants.cache_path, "rb") as file:
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
                                for info in old_result[cate][name]:
                                    if info:
                                        try:
                                            if info["origin"] == "whitelist" and not any(
                                                    url in info["url"] for url in whitelist_urls):
                                                continue
                                        except:
                                            pass
                                        if info["url"] not in urls:
                                            channels[cate][name].append(info)
    return channels


def format_channel_name(name):
    """
    Format the channel name with sub and replace and lower
    """
    return name if config.open_keep_all else channel_alias.get_primary(name)


def channel_name_is_equal(name1, name2):
    """
    Check if the channel name is equal
    """
    if config.open_keep_all:
        return True
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


def get_element_child_text_list(element, child_name):
    """
    Get the child text of the element
    """
    text_list = []
    children = element.find_all(child_name)
    if children:
        for child in children:
            text = child.get_text(strip=True)
            if text:
                text_list.append(text)
    return text_list


def get_multicast_ip_list(urls):
    """
    Get the multicast ip list from urls
    """
    ip_list = []
    for url in urls:
        pattern = r"rtp://((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::(\d+))?)"
        matcher = re.search(pattern, url)
        if matcher:
            ip_list.append(matcher.group(1))
    return ip_list


def get_channel_multicast_region_ip_list(result, channel_region, channel_type):
    """
    Get the channel multicast region ip list by region and type from result
    """
    return [
        ip
        for result_region, result_obj in result.items()
        if result_region in channel_region
        for url_type, urls in result_obj.items()
        if url_type in channel_type
        for ip in get_multicast_ip_list(urls)
    ]


def get_channel_multicast_name_region_type_result(result, names):
    """
    Get the multicast name and region and type result by names from result
    """
    name_region_type_result = {}
    for name in names:
        data = result.get(name)
        if data:
            name_region_type_result[name] = data
    return name_region_type_result


def get_channel_multicast_region_type_list(result):
    """
    Get the channel multicast region type list from result
    """
    region_list = config.multicast_region_list
    region_type_list = {
        (region, r_type)
        for region_type in result.values()
        for region, types in region_type.items()
        if "all" in region_list
           or "ALL" in region_list
           or "全部" in region_list
           or region in region_list
        for r_type in types
    }
    return list(region_type_list)


def get_channel_multicast_result(result, search_result):
    """
    Get the channel multicast info result by result and search result
    """
    info_result = {}
    multicast_name = constants.origin_map["multicast"]
    for name, result_obj in result.items():
        info_list = [
            {
                "url":
                    add_url_info(
                        total_url,
                        f"{result_region}{result_type}{multicast_name}",
                    ),
                "date": date,
                "resolution": resolution,
            }
            for result_region, result_types in result_obj.items()
            if result_region in search_result
            for result_type, result_type_urls in result_types.items()
            if result_type in search_result[result_region]
            for ip in get_multicast_ip_list(result_type_urls) or []
            for url, date, resolution in search_result[result_region][result_type]
            if (total_url := f"http://{url}/rtp/{ip}")
        ]
        info_result[name] = info_list
    return info_result


def get_results_from_soup(soup, name):
    """
    Get the results from the soup
    """
    results = []
    if not soup.descendants:
        return results
    for element in soup.descendants:
        if isinstance(element, NavigableString):
            text = element.get_text(strip=True)
            url = get_channel_url(text)
            if url and not any(item[0] == url for item in results):
                url_element = soup.find(lambda tag: tag.get_text(strip=True) == url)
                if url_element:
                    name_element = url_element.find_previous_sibling()
                    if name_element:
                        channel_name = name_element.get_text(strip=True)
                        if channel_name_is_equal(name, channel_name):
                            info_element = url_element.find_next_sibling()
                            date, resolution = get_channel_info(
                                info_element.get_text(strip=True)
                            )
                            results.append({
                                "url": url,
                                "date": date,
                                "resolution": resolution,
                            })
    return results


def get_results_from_multicast_soup(soup, hotel=False):
    """
    Get the results from the multicast soup
    """
    results = []
    if not soup.descendants:
        return results
    for element in soup.descendants:
        if isinstance(element, NavigableString):
            text = element.strip()
            if "失效" in text:
                continue
            url = get_channel_url(text)
            if url and not any(item["url"] == url for item in results):
                url_element = soup.find(lambda tag: tag.get_text(strip=True) == url)
                if not url_element:
                    continue
                parent_element = url_element.find_parent()
                info_element = parent_element.find_all(recursive=False)[-1]
                if not info_element:
                    continue
                info_text = info_element.get_text(strip=True)
                if "上线" in info_text and " " in info_text:
                    date, region, channel_type = get_multicast_channel_info(info_text)
                    if hotel and "酒店" not in region:
                        continue
                    results.append(
                        {
                            "url": url,
                            "date": date,
                            "region": region,
                            "type": channel_type,
                        }
                    )
    return results


def get_results_from_soup_requests(soup, name):
    """
    Get the results from the soup by requests
    """
    results = []
    elements = soup.find_all("div", class_="resultplus") if soup else []
    for element in elements:
        name_element = element.find("div", class_="channel")
        if name_element:
            channel_name = name_element.get_text(strip=True)
            if channel_name_is_equal(name, channel_name):
                text_list = get_element_child_text_list(element, "div")
                url = date = resolution = None
                for text in text_list:
                    text_url = get_channel_url(text)
                    if text_url:
                        url = text_url
                    if " " in text:
                        text_info = get_channel_info(text)
                        date, resolution = text_info
                if url:
                    results.append({
                        "url": url,
                        "date": date,
                        "resolution": resolution,
                    })
    return results


def get_results_from_multicast_soup_requests(soup, hotel=False):
    """
    Get the results from the multicast soup by requests
    """
    results = []
    if not soup:
        return results

    elements = soup.find_all("div", class_="result")
    for element in elements:
        name_element = element.find("div", class_="channel")
        if not name_element:
            continue

        text_list = get_element_child_text_list(element, "div")
        url, date, region, channel_type = None, None, None, None
        valid = True

        for text in text_list:
            if "失效" in text:
                valid = False
                break

            text_url = get_channel_url(text)
            if text_url:
                url = text_url

            if url and "上线" in text and " " in text:
                date, region, channel_type = get_multicast_channel_info(text)

        if url and valid:
            if hotel and "酒店" not in region:
                continue
            results.append({"url": url, "date": date, "region": region, "type": channel_type})

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


def get_channel_info(text):
    """
    Get the channel info from text
    """
    date, resolution = None, None
    if text:
        date, resolution = (
            (text.partition(" ")[0] if text.partition(" ")[0] else None),
            (
                text.partition(" ")[2].partition("•")[2]
                if text.partition(" ")[2].partition("•")[2]
                else None
            ),
        )
    return date, resolution


def get_multicast_channel_info(text):
    """
    Get the multicast channel info from text
    """
    date, region, channel_type = None, None, None
    if text:
        text_split = text.split(" ")
        filtered_data = list(filter(lambda x: x.strip() != "", text_split))
        if filtered_data and len(filtered_data) == 4:
            date = filtered_data[0]
            region = filtered_data[2]
            channel_type = filtered_data[3]
    return date, region, channel_type


def init_info_data(data, cate, name):
    """
    Init channel info data
    """
    if data.get(cate) is None:
        data[cate] = {}
    if data[cate].get(name) is None:
        data[cate][name] = []


def append_data_to_info_data(info_data, cate, name, data, origin=None, check=True, whitelist=None, blacklist=None,
                             ipv_type_data=None):
    """
    Append channel data to total info data
    """
    init_info_data(info_data, cate, name)
    urls = set([url for info in info_data[cate][name] if (url := info["url"])])
    url_hosts = set([get_url_host(url) for url in urls])
    for item in data:
        try:
            channel_id, url, host, date, resolution, url_origin, ipv_type, headers, extra_info = (
                item.get("id", None),
                item["url"],
                item.get("host", None),
                item.get("date", None),
                item.get("resolution", None),
                item.get("origin", origin),
                item.get("ipv_type", None),
                item.get("headers", None),
                item.get("extra_info", ""),
            )
            if not url_origin:
                continue
            if url:
                if not channel_id:
                    channel_id = hash(url)
                if not host:
                    host = get_url_host(url)
                from_whitelist = url_origin == "whitelist"
                if not from_whitelist and url in urls and not headers:
                    continue
                if not ipv_type:
                    if ipv_type_data:
                        ipv_type = ipv_type_data.get(host, None)
                    if not ipv_type:
                        ipv_type = "ipv6" if check_url_ipv6(url) else "ipv4"
                        if ipv_type_data:
                            ipv_type_data[host] = ipv_type
                if not from_whitelist:
                    if host in url_hosts:
                        for p_url in urls:
                            if get_url_host(p_url) == host and (len(p_url) < len(url) or headers):
                                urls.remove(p_url)
                                urls.add(url)
                                for index, info in enumerate(info_data[cate][name]):
                                    if info["url"] and get_url_host(info["url"]) == host:
                                        info_data[cate][name][index] = {
                                            "id": channel_id,
                                            "url": url,
                                            "host": host,
                                            "date": date,
                                            "resolution": resolution,
                                            "origin": url_origin,
                                            "ipv_type": ipv_type,
                                            "headers": headers,
                                            "extra_info": extra_info
                                        }
                                        break
                                break
                        continue
                if whitelist and check_url_by_keywords(url, whitelist):
                    url_origin = "whitelist"
                if (
                        url_origin in ["whitelist", "live", "hls"]
                        or (not check)
                        or (
                        check and check_ipv_type_match(ipv_type) and not check_url_by_keywords(url, blacklist))
                ):
                    info_data[cate][name].append({
                        "id": channel_id,
                        "url": url,
                        "host": host,
                        "date": date,
                        "resolution": resolution,
                        "origin": url_origin,
                        "ipv_type": ipv_type,
                        "headers": headers,
                        "extra_info": extra_info
                    })
                    urls.add(url)
                    url_hosts.add(host)
        except Exception as e:
            print(f"Error on append data to info data: {e}")
            continue


def get_origin_method_name(method):
    """
    Get the origin method name
    """
    return "hotel" if method.startswith("hotel_") else method


def append_old_data_to_info_data(info_data, cate, name, data, whitelist=None, blacklist=None, ipv_type_data=None):
    """
    Append history and local channel data to total info data
    """
    append_data_to_info_data(
        info_data,
        cate,
        name,
        data,
        whitelist=whitelist,
        blacklist=blacklist,
        ipv_type_data=ipv_type_data
    )
    live_len = sum(1 for item in data if item["origin"] == "live")
    hls_len = sum(1 for item in data if item["origin"] == "hls")
    local_len = sum(1 for item in data if item["origin"] == "local")
    whitelist_len = sum(1 for item in data if item["origin"] == "whitelist")
    history_len = len(data) - (live_len + hls_len + local_len + whitelist_len)
    print(f"History: {history_len}, Live: {live_len}, HLS: {hls_len}, Local: {local_len}, Whitelist: {whitelist_len}",
          end=", ")


def print_channel_number(data: CategoryChannelData, cate: str, name: str):
    """
    Print channel number
    """
    channel_list = data.get(cate, {}).get(name, [])
    print("IPv4:", len([channel for channel in channel_list if channel["ipv_type"] == "ipv4"]), end=", ")
    print("IPv6:", len([channel for channel in channel_list if channel["ipv_type"] == "ipv6"]), end=", ")
    print(
        "Total:",
        len(channel_list),
    )


def append_total_data(
        items,
        names,
        data,
        hotel_fofa_result=None,
        multicast_result=None,
        hotel_foodie_result=None,
        subscribe_result=None,
        online_search_result=None,
):
    """
    Append all method data to total info data
    """
    total_result = [
        ("hotel_fofa", hotel_fofa_result),
        ("multicast", multicast_result),
        ("hotel_foodie", hotel_foodie_result),
        ("subscribe", subscribe_result),
        ("online_search", online_search_result),
    ]
    whitelist = get_urls_from_file(constants.whitelist_path)
    blacklist = get_urls_from_file(constants.blacklist_path, pattern_search=False)
    url_hosts_ipv_type = {}
    for obj in data.values():
        for value_list in obj.values():
            for value in value_list:
                if value_ipv_type := value.get("ipv_type", None):
                    url_hosts_ipv_type[get_url_host(value["url"])] = value_ipv_type
    for cate, channel_obj in items:
        for name, old_info_list in channel_obj.items():
            print(f"{name}:", end=" ")
            if old_info_list and (config.open_history or config.open_local or config.open_rtmp):
                append_old_data_to_info_data(data, cate, name, old_info_list, whitelist=whitelist, blacklist=blacklist,
                                             ipv_type_data=url_hosts_ipv_type)
            for method, result in total_result:
                if config.open_method[method]:
                    origin_method = get_origin_method_name(method)
                    if not origin_method:
                        continue
                    name_results = get_channel_results_by_name(name, result)
                    append_data_to_info_data(
                        data, cate, name, name_results, origin=origin_method, whitelist=whitelist, blacklist=blacklist,
                        ipv_type_data=url_hosts_ipv_type
                    )
                    print(f"{method.capitalize()}:", len(name_results), end=", ")
            print_channel_number(data, cate, name)
        if config.open_keep_all:
            extra_cate = "📥其它频道"
            for method, result in total_result:
                if config.open_method[method]:
                    origin_method = get_origin_method_name(method)
                    if not origin_method:
                        continue
                    for name, urls in result.items():
                        if name in names:
                            continue
                        print(f"{name}:", end=" ")
                        if config.open_history or config.open_local or config.open_rtmp:
                            old_info_list = channel_obj.get(name, [])
                            if old_info_list:
                                append_old_data_to_info_data(
                                    data, extra_cate, name, old_info_list, whitelist=whitelist, blacklist=blacklist,
                                    ipv_type_data=url_hosts_ipv_type
                                )
                        append_data_to_info_data(
                            data, extra_cate, name, urls, origin=origin_method, whitelist=whitelist,
                            blacklist=blacklist, ipv_type_data=url_hosts_ipv_type
                        )
                        print(name, f"{method.capitalize()}:", len(urls), end=", ")
                        print_channel_number(data, cate, name)


async def process_sort_channel_list(data, filter_data=None, ipv6=False, callback=None):
    """
    Process the sort channel list
    """
    ipv6_proxy_url = None if (not config.open_ipv6 or ipv6) else constants.ipv6_proxy
    open_filter_resolution = config.open_filter_resolution
    open_headers = config.open_headers
    get_resolution = open_filter_resolution and check_ffmpeg_installed_status()
    if not filter_data:
        filter_data = copy.deepcopy(data)
        process_nested_dict(filter_data, seen={})
    result = {}
    semaphore = asyncio.Semaphore(10)

    async def limited_get_speed(url, headers, cache_key, is_ipv6, ipv6_proxy, resolution, filter_resolution, callback):
        async with semaphore:
            return await get_speed(url, headers, cache_key, is_ipv6=is_ipv6, ipv6_proxy=ipv6_proxy,
                                   resolution=resolution, filter_resolution=filter_resolution, callback=callback)

    tasks = [
        asyncio.create_task(
            limited_get_speed(
                url=info["url"],
                headers=(open_headers and info.get("headers", None)) or None,
                cache_key=info["host"],
                is_ipv6=info["ipv_type"] == "ipv6",
                ipv6_proxy=ipv6_proxy_url,
                resolution=info["resolution"],
                filter_resolution=get_resolution,
                callback=callback,
            )
        )
        for channel_obj in filter_data.values()
        for info_list in channel_obj.values()
        for info in info_list
    ]
    await asyncio.gather(*tasks)
    logger = get_logger(constants.sort_log_path, level=INFO, init=True)
    for cate, obj in data.items():
        for name, info_list in obj.items():
            info_list = sort_urls(name, info_list, logger=logger)
            append_data_to_info_data(
                result,
                cate,
                name,
                info_list,
                check=False,
            )
    logger.handlers.clear()
    return result


def process_write_content(path: str,
                          data: CategoryChannelData,
                          live: bool = False,
                          hls: bool = False,
                          live_url: str = None,
                          hls_url: str = None,
                          open_empty_category: bool = False,
                          ipv_type_prefer: list[str] = None,
                          origin_type_prefer: list[str] = None,
                          first_channel_name: str = None,
                          enable_print: bool = False,
                          callback=None
                          ):
    """
    Get channel write content
    :param path: write into path
    :param live: all live channel url
    :param hls: all hls channel url
    :param live_url: live url
    :param hls_url: hls url
    :param open_empty_category: show empty category
    :param ipv_type_prefer: ipv type prefer
    :param origin_type_prefer: origin type prefer
    :param first_channel_name: the first channel name
    :param callback: callback function
    """
    content = ""
    no_result_name = []
    first_cate = True
    result_data = defaultdict(list)
    custom_print.disable = not enable_print
    rtmp_url = live_url if live else hls_url if hls else None
    rtmp_type = ["live", "hls"] if live and hls else ["live"] if live else ["hls"] if hls else []
    open_url_info = config.open_url_info
    for cate, channel_obj in data.items():
        custom_print(f"\n{cate}:", end=" ")
        content += f"{'\n\n' if not first_cate else ''}{cate},#genre#"
        first_cate = False
        channel_obj_keys = channel_obj.keys()
        names_len = len(list(channel_obj_keys))
        for i, name in enumerate(channel_obj_keys):
            info_list = data.get(cate, {}).get(name, [])
            channel_urls = get_total_urls(info_list, ipv_type_prefer, origin_type_prefer, rtmp_type)
            result_data[name].extend(channel_urls)
            end_char = ", " if i < names_len - 1 else ""
            custom_print(f"{name}:", len(channel_urls), end=end_char)
            if not channel_urls:
                if open_empty_category:
                    no_result_name.append(name)
                continue
            for item in channel_urls:
                item_origin = item.get("origin", None)
                item_rtmp_url = None
                if item_origin == "live":
                    item_rtmp_url = live_url
                elif item_origin == "hls":
                    item_rtmp_url = hls_url
                item_url = item["url"]
                if open_url_info and item["extra_info"]:
                    item_url = add_url_info(item_url, item["extra_info"])
                total_item_url = f"{rtmp_url or item_rtmp_url}{item['id']}" if rtmp_url or item_rtmp_url else item_url
                content += f"\n{name},{total_item_url}"
        custom_print()
    if open_empty_category and no_result_name:
        custom_print("\n🈳 No result channel name:")
        content += "\n\n🈳无结果频道,#genre#"
        for i, name in enumerate(no_result_name):
            end_char = ", " if i < len(no_result_name) - 1 else ""
            custom_print(name, end=end_char)
            content += f"\n{name},url"
        custom_print()
    if config.open_update_time:
        update_time_item = next(
            (urls[0] for channel_obj in data.values()
             for info_list in channel_obj.values()
             if (urls := get_total_urls(info_list, ipv_type_prefer, origin_type_prefer, rtmp_type))),
            {"id": "id", "url": "url"}
        )
        now = get_datetime_now()
        update_time_item_url = update_time_item["url"]
        if open_url_info and update_time_item["extra_info"]:
            update_time_item_url = add_url_info(update_time_item_url, update_time_item["extra_info"])
        value = f"{rtmp_url}{update_time_item["id"]}" if rtmp_url else update_time_item_url
        if config.update_time_position == "top":
            content = f"🕘️更新时间,#genre#\n{now},{value}\n\n{content}"
        else:
            content += f"\n\n🕘️更新时间,#genre#\n{now},{value}"
    if rtmp_url:
        conn = get_db_connection(constants.rtmp_data_path)
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
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        if callback:
            callback()
    convert_to_m3u(path, first_channel_name, data=result_data)
    if callback:
        callback()


def write_channel_to_file(data, ipv6=False, first_channel_name=None, callback=None):
    """
    Write channel to file
    """
    try:
        output_dir = constants.output_dir
        dir_list = [output_dir, f"{output_dir}/ipv4", f"{output_dir}/ipv6", f"{output_dir}/data", f"{output_dir}/log"]
        for dir_name in dir_list:
            os.makedirs(dir_name, exist_ok=True)
        open_empty_category = config.open_empty_category
        ipv_type_prefer = list(config.ipv_type_prefer)
        if any(pref in ipv_type_prefer for pref in ["自动", "auto"]):
            ipv_type_prefer = ["ipv6", "ipv4"] if ipv6 else ["ipv4", "ipv6"]
        origin_type_prefer = config.origin_type_prefer
        address = get_ip_address()
        live_url = f"{address}/live/"
        hls_url = f"{address}/hls/"
        file_list = [
            {"path": config.final_file, "enable_log": True},
            {"path": constants.ipv4_result_path, "ipv_type_prefer": ["ipv4"]},
            {"path": constants.ipv6_result_path, "ipv_type_prefer": ["ipv6"]}
        ]
        if config.open_rtmp and not os.environ.get("GITHUB_ACTIONS"):
            file_list += [
                {"path": constants.live_result_path, "live": True},
                {
                    "path": constants.live_ipv4_result_path,
                    "live": True,
                    "ipv_type_prefer": ["ipv4"]
                },
                {
                    "path": constants.live_ipv6_result_path,
                    "live": True,
                    "ipv_type_prefer": ["ipv6"]
                },
                {"path": constants.hls_result_path, "hls": True},
                {
                    "path": constants.hls_ipv4_result_path,
                    "hls": True,
                    "ipv_type_prefer": ["ipv4"]
                },
                {
                    "path": constants.hls_ipv6_result_path,
                    "hls": True,
                    "ipv_type_prefer": ["ipv6"]
                },
            ]
        for file in file_list:
            process_write_content(
                path=file["path"],
                data=data,
                live=file.get("live", False),
                hls=file.get("hls", False),
                live_url=live_url,
                hls_url=hls_url,
                open_empty_category=open_empty_category,
                ipv_type_prefer=file.get("ipv_type_prefer", ipv_type_prefer),
                origin_type_prefer=origin_type_prefer,
                first_channel_name=first_channel_name,
                enable_print=file.get("enable_log", False),
                callback=callback,
            )
    except Exception as e:
        print(f"❌ Write channel to file failed: {e}")


def get_multicast_fofa_search_org(region, org_type):
    """
    Get the fofa search organization for multicast
    """
    org = None
    if region == "北京" and org_type == "联通":
        org = "China Unicom Beijing Province Network"
    elif org_type == "联通":
        org = "CHINA UNICOM China169 Backbone"
    elif org_type == "电信":
        org = "Chinanet"
    elif org_type == "移动":
        org = "China Mobile communications corporation"
    return org


def get_multicast_fofa_search_urls():
    """
    Get the fofa search urls for multicast
    """
    rtp_file_names = []
    for filename in os.listdir(resource_path("config/rtp")):
        if filename.endswith(".txt") and "_" in filename:
            filename = filename.replace(".txt", "")
            rtp_file_names.append(filename)
    region_list = config.multicast_region_list
    region_type_list = [
        (parts[0], parts[1])
        for name in rtp_file_names
        if (parts := name.partition("_"))[0] in region_list
           or "all" in region_list
           or "ALL" in region_list
           or "全部" in region_list
    ]
    search_urls = []
    for region, r_type in region_type_list:
        search_url = "https://fofa.info/result?qbase64="
        search_txt = f'"udpxy" && country="CN" && region="{region}" && org="{get_multicast_fofa_search_org(region, r_type)}"'
        bytes_string = search_txt.encode("utf-8")
        search_txt = base64.b64encode(bytes_string).decode("utf-8")
        search_url += search_txt
        search_urls.append((search_url, region, r_type))
    return search_urls


def get_channel_data_cache_with_compare(data, new_data):
    """
    Get channel data with cache compare new data
    """
    for cate, obj in new_data.items():
        for name, url_info in obj.items():
            if url_info and cate in data and name in data[cate]:
                new_urls = {
                    info["url"]: info["resolution"]
                    for info in url_info
                }
                updated_data = []
                for info in data[cate][name]:
                    url = info["url"]
                    if url in new_urls:
                        resolution = new_urls[url]
                        updated_data.append({
                            "id": info["id"],
                            "url": url,
                            "date": info["date"],
                            "resolution": resolution,
                            "origin": info["origin"],
                            "ipv_type": info["ipv_type"]
                        })
                data[cate][name] = updated_data
