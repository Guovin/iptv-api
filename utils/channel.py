import asyncio
import base64
import copy
import os
import pickle
import re
from collections import defaultdict
from logging import INFO

from bs4 import NavigableString
from opencc import OpenCC

import utils.constants as constants
from utils.config import config
from utils.speed import (
    get_speed,
    sort_urls,
    check_ffmpeg_installed_status
)
from utils.tools import (
    get_name_url,
    check_url_by_keywords,
    check_url_ipv_type,
    get_total_urls,
    process_nested_dict,
    add_url_info,
    remove_cache_info,
    resource_path,
    get_urls_from_file,
    get_name_urls_from_file,
    get_logger,
    get_datetime_now,
    format_url_with_cache
)


def format_channel_data(url: str, origin: str = None) -> tuple:
    """
    Format the channel data
    """
    info = url.partition("$")[2]
    url_origin = "whitelist" if info and info.startswith("!") else origin
    url = format_url_with_cache(url) if url_origin == origin else url
    return url, None, None, url_origin


def get_channel_data_from_file(channels, file, whitelist, open_local=config.open_local, local_data=None):
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
                        category_dict[name].append((whitelist_url, None, None, "whitelist"))
                if open_local and url:
                    data = format_channel_data(url, "local")
                    if data not in category_dict[name]:
                        category_dict[name].append(data)
                    if local_data and name in local_data:
                        for local_url in local_data[name]:
                            local_channel_data = format_channel_data(local_url, "local")
                            if local_channel_data not in category_dict[name]:
                                category_dict[name].append(local_channel_data)
    return channels


def get_channel_items():
    """
    Get the channel items from the source file
    """
    user_source_file = resource_path(config.source_file)
    channels = defaultdict(lambda: defaultdict(list))
    local_data = get_name_urls_from_file(resource_path(config.local_file))
    whitelist = get_name_urls_from_file(constants.whitelist_path)
    whitelist_urls = get_urls_from_file(constants.whitelist_path)
    whitelist_len = len(list(whitelist.keys()))
    if whitelist_len:
        print(f"Found {whitelist_len} channel in whitelist")

    if os.path.exists(user_source_file):
        with open(user_source_file, "r", encoding="utf-8") as file:
            channels = get_channel_data_from_file(
                channels, file, whitelist, config.open_local, local_data
            )

    if config.open_history:
        result_cache_path = resource_path(constants.cache_path)
        if os.path.exists(result_cache_path):
            with open(result_cache_path, "rb") as file:
                old_result = pickle.load(file)
                for cate, data in channels.items():
                    if cate in old_result:
                        for name, info_list in data.items():
                            urls = [
                                item[0].partition("$")[0]
                                for item in info_list
                                if item[0]
                            ]
                            if name in old_result[cate]:
                                for info in old_result[cate][name]:
                                    if info:
                                        try:
                                            if info[3] == "whitelist" and not any(
                                                    url in info[0] for url in whitelist_urls):
                                                continue
                                        except:
                                            pass
                                        pure_url = info[0].partition("$")[0]
                                        if pure_url not in urls:
                                            channels[cate][name].append(info)
    return channels


def format_channel_name(name):
    """
    Format the channel name with sub and replace and lower
    """
    if config.open_keep_all:
        return name
    cc = OpenCC("t2s")
    name = cc.convert(name)
    for region in constants.region_list:
        name = name.replace(f"{region}｜", "")
    name = re.sub(constants.sub_pattern, "", name)
    for old, new in constants.replace_dict.items():
        name = name.replace(old, new)
    return name.lower()


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
        for type, urls in result_obj.items()
        if type in channel_type
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
        (region, type)
        for region_type in result.values()
        for region, types in region_type.items()
        if "all" in region_list
           or "ALL" in region_list
           or "全部" in region_list
           or region in region_list
        for type in types
    }
    return list(region_type_list)


def get_channel_multicast_result(result, search_result):
    """
    Get the channel multicast info result by result and search result
    """
    info_result = {}
    multicast_name = constants.origin_map["multicast"]
    whitelist = get_urls_from_file(constants.whitelist_path)
    blacklist = get_urls_from_file(constants.blacklist_path)
    for name, result_obj in result.items():
        info_list = [
            (
                (
                    add_url_info(
                        f"http://{url}/rtp/{ip}",
                        f"{result_region}{result_type}{multicast_name}-cache:{url}",
                    )
                    if config.open_sort
                    else add_url_info(
                        f"http://{url}/rtp/{ip}",
                        f"{result_region}{result_type}{multicast_name}",
                    )
                ),
                date,
                resolution,
            )
            for result_region, result_types in result_obj.items()
            if result_region in search_result
            for result_type, result_type_urls in result_types.items()
            if result_type in search_result[result_region]
            for ip in get_multicast_ip_list(result_type_urls) or []
            for url, date, resolution in search_result[result_region][result_type]
            if (whitelist and check_url_by_keywords(f"http://{url}/rtp/{ip}", whitelist)) or
               (
                       check_url_ipv_type(f"http://{url}/rtp/{ip}") and not check_url_by_keywords(
                   f"http://{url}/rtp/{ip}", blacklist))
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
                            results.append((url, date, resolution))
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
                    date, region, type = get_multicast_channel_info(info_text)
                    if hotel and "酒店" not in region:
                        continue
                    results.append(
                        {
                            "url": url,
                            "date": date,
                            "region": region,
                            "type": type,
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
                    results.append((url, date, resolution))
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
        url, date, region, type = None, None, None, None
        valid = True

        for text in text_list:
            if "失效" in text:
                valid = False
                break

            text_url = get_channel_url(text)
            if text_url:
                url = text_url

            if url and "上线" in text and " " in text:
                date, region, type = get_multicast_channel_info(text)

        if url and valid:
            if hotel and "酒店" not in region:
                continue
            results.append({"url": url, "date": date, "region": region, "type": type})

    return results


def get_channel_url(text):
    """
    Get the url from text
    """
    url = None
    url_search = re.search(
        constants.url_pattern,
        text,
    )
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
    date, region, type = None, None, None
    if text:
        text_split = text.split(" ")
        filtered_data = list(filter(lambda x: x.strip() != "", text_split))
        if filtered_data and len(filtered_data) == 4:
            date = filtered_data[0]
            region = filtered_data[2]
            type = filtered_data[3]
    return date, region, type


def init_info_data(data, cate, name):
    """
    Init channel info data
    """
    if data.get(cate) is None:
        data[cate] = {}
    if data[cate].get(name) is None:
        data[cate][name] = []


def append_data_to_info_data(info_data, cate, name, data, origin=None, check=True, whitelist=None, blacklist=None):
    """
    Append channel data to total info data
    """
    init_info_data(info_data, cate, name)
    urls = [x[0].partition("$")[0] for x in info_data[cate][name] if x[0]]
    for item in data:
        try:
            url, date, resolution, *rest = item
            url_origin = origin or (rest[0] if rest else None)
            if not url_origin:
                continue
            if url:
                url_partition = url.partition("$")
                pure_url = url_partition[0]
                url_info = url_partition[2]
                white_info = url_info and url_info.startswith("!")
                if (pure_url in urls) and not white_info:
                    continue
                if white_info or (whitelist and check_url_by_keywords(url, whitelist)):
                    url_origin = "whitelist"
                if (
                        url_origin == "whitelist"
                        or (not check)
                        or (
                        check and check_url_ipv_type(pure_url) and not check_url_by_keywords(url, blacklist))
                ):
                    info_data[cate][name].append((url, date, resolution, url_origin))
                    urls.append(pure_url)
        except:
            continue


def get_origin_method_name(method):
    """
    Get the origin method name
    """
    return "hotel" if method.startswith("hotel_") else method


def append_old_data_to_info_data(info_data, cate, name, data, whitelist=None, blacklist=None):
    """
    Append history and local channel data to total info data
    """
    append_data_to_info_data(
        info_data,
        cate,
        name,
        data,
        whitelist=whitelist,
        blacklist=blacklist
    )
    local_len = len([x for x in data if x[3] in ["local", 'whitelist']])
    print("History:", len(data) - local_len, end=", ")
    print("Local:", local_len, end=", ")


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
    blacklist = get_urls_from_file(constants.blacklist_path)
    for cate, channel_obj in items:
        for name, old_info_list in channel_obj.items():
            print(f"{name}:", end=" ")
            if old_info_list and (config.open_history or config.open_local):
                append_old_data_to_info_data(data, cate, name, old_info_list, whitelist=whitelist, blacklist=blacklist)
            for method, result in total_result:
                if config.open_method[method]:
                    origin_method = get_origin_method_name(method)
                    if not origin_method:
                        continue
                    name_results = get_channel_results_by_name(name, result)
                    append_data_to_info_data(
                        data, cate, name, name_results, origin=origin_method, whitelist=whitelist, blacklist=blacklist
                    )
                    print(f"{method.capitalize()}:", len(name_results), end=", ")
            print(
                "Total:",
                len(data.get(cate, {}).get(name, [])),
            )
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
                    if config.open_history or config.open_local:
                        old_info_list = channel_obj.get(name, [])
                        if old_info_list:
                            append_old_data_to_info_data(
                                data, extra_cate, name, old_info_list
                            )
                    append_data_to_info_data(
                        data, extra_cate, name, urls, origin=origin_method, whitelist=whitelist, blacklist=blacklist
                    )
                    print(name, f"{method.capitalize()}:", len(urls), end=", ")
                    print(
                        "Total:",
                        len(data.get(cate, {}).get(name, [])),
                    )


async def process_sort_channel_list(data, ipv6=False, callback=None):
    """
    Process the sort channel list
    """
    ipv6_proxy = None if (not config.open_ipv6 or ipv6) else constants.ipv6_proxy
    open_filter_resolution = config.open_filter_resolution
    get_resolution = open_filter_resolution and check_ffmpeg_installed_status()
    sort_timeout = config.sort_timeout
    need_sort_data = copy.deepcopy(data)
    process_nested_dict(need_sort_data, seen=set(), flag=r"cache:(.*)", force_str="!")
    result = {}
    semaphore = asyncio.Semaphore(10)

    async def limited_get_speed(info, ipv6_proxy, filter_resolution, timeout, callback):
        async with semaphore:
            return await get_speed(info[0], ipv6_proxy=ipv6_proxy, filter_resolution=filter_resolution, timeout=timeout,
                                   callback=callback)

    tasks = [
        asyncio.create_task(
            limited_get_speed(
                info,
                ipv6_proxy=ipv6_proxy,
                filter_resolution=get_resolution,
                timeout=sort_timeout,
                callback=callback,
            )
        )
        for channel_obj in need_sort_data.values()
        for info_list in channel_obj.values()
        for info in info_list
    ]
    await asyncio.gather(*tasks)
    logger = get_logger(constants.sort_log_path, level=INFO, init=True)
    open_supply = config.open_supply
    open_filter_speed = config.open_filter_speed
    min_speed = config.min_speed
    min_resolution = config.min_resolution_value
    for cate, obj in data.items():
        for name, info_list in obj.items():
            info_list = sort_urls(name, info_list, supply=open_supply, filter_speed=open_filter_speed,
                                  min_speed=min_speed, filter_resolution=open_filter_resolution,
                                  min_resolution=min_resolution, logger=logger)
            append_data_to_info_data(
                result,
                cate,
                name,
                info_list,
                check=False,
            )
    logger.handlers.clear()
    return result


def write_channel_to_file(data, ipv6=False, callback=None):
    """
    Write channel to file
    """
    try:
        path = constants.result_path
        if not os.path.exists("output"):
            os.makedirs("output")
        no_result_name = []
        open_empty_category = config.open_empty_category
        ipv_type_prefer = list(config.ipv_type_prefer)
        if any(pref in ipv_type_prefer for pref in ["自动", "auto"]) or not ipv_type_prefer:
            ipv_type_prefer = ["ipv6", "ipv4"] if ipv6 else ["ipv4", "ipv6"]
        origin_type_prefer = config.origin_type_prefer
        first_cate = True
        content = ""
        for cate, channel_obj in data.items():
            print(f"\n{cate}:", end=" ")
            content += f"{'\n\n' if not first_cate else ''}{cate},#genre#"
            first_cate = False
            channel_obj_keys = channel_obj.keys()
            names_len = len(list(channel_obj_keys))
            for i, name in enumerate(channel_obj_keys):
                info_list = data.get(cate, {}).get(name, [])
                channel_urls = get_total_urls(info_list, ipv_type_prefer, origin_type_prefer)
                end_char = ", " if i < names_len - 1 else ""
                print(f"{name}:", len(channel_urls), end=end_char)
                if not channel_urls:
                    if open_empty_category:
                        no_result_name.append(name)
                    continue
                for url in channel_urls:
                    content += f"\n{name},{url}"
                    if callback:
                        callback()
            print()
        if open_empty_category and no_result_name:
            print("\n🈳 No result channel name:")
            content += "\n\n🈳无结果频道,#genre#"
            for i, name in enumerate(no_result_name):
                end_char = ", " if i < len(no_result_name) - 1 else ""
                print(name, end=end_char)
                content += f"\n{name},url"
            print()
        if config.open_update_time:
            update_time_url = next(
                (get_total_urls(info_list, ipv_type_prefer, origin_type_prefer)[0]
                 for channel_obj in data.values()
                 for info_list in channel_obj.values() if info_list),
                "url"
            )
            if config.update_time_position == "top":
                content = f"🕘️更新时间,#genre#\n{get_datetime_now()},{update_time_url}\n\n{content}"
            else:
                content += f"\n\n🕘️更新时间,#genre#\n{get_datetime_now()},{update_time_url}"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Write channel to file failed: {e}")


def get_multicast_fofa_search_org(region, type):
    """
    Get the fofa search organization for multicast
    """
    org = None
    if region == "北京" and type == "联通":
        org = "China Unicom Beijing Province Network"
    elif type == "联通":
        org = "CHINA UNICOM China169 Backbone"
    elif type == "电信":
        org = "Chinanet"
    elif type == "移动":
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
    for region, type in region_type_list:
        search_url = "https://fofa.info/result?qbase64="
        search_txt = f'"udpxy" && country="CN" && region="{region}" && org="{get_multicast_fofa_search_org(region, type)}"'
        bytes_string = search_txt.encode("utf-8")
        search_txt = base64.b64encode(bytes_string).decode("utf-8")
        search_url += search_txt
        search_urls.append((search_url, region, type))
    return search_urls


def get_channel_data_cache_with_compare(data, new_data):
    """
    Get channel data with cache compare new data
    """
    for cate, obj in new_data.items():
        for name, url_info in obj.items():
            if url_info and cate in data and name in data[cate]:
                new_urls = {
                    new_url.partition("$")[0]: new_resolution
                    for new_url, _, new_resolution, _ in url_info
                }
                updated_data = []
                for info in data[cate][name]:
                    url, date, resolution, origin = info
                    base_url = url.partition("$")[0]
                    if base_url in new_urls:
                        resolution = new_urls[base_url]
                        updated_data.append((url, date, resolution, origin))
                data[cate][name] = updated_data


def format_channel_url_info(data):
    """
    Format channel url info, remove cache, add resolution to url
    """
    for obj in data.values():
        for url_info in obj.values():
            for i, (url, date, resolution, origin) in enumerate(url_info):
                url = remove_cache_info(url)
                url_info[i] = (url, date, resolution, origin)
