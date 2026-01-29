import copy
import datetime
import json
import logging
import os
import re
import shutil
import sys
from collections import defaultdict
from logging.handlers import RotatingFileHandler
from pathlib import Path
from time import time
from typing import Iterable, List, Optional, Union
from urllib.parse import urlparse, urlunparse

import pytz
import requests
from bs4 import BeautifulSoup
from flask import send_file, make_response
from opencc import OpenCC

import utils.constants as constants
from utils.config import config, resource_path
from utils.i18n import t
from utils.types import ChannelData

opencc_t2s = OpenCC("t2s")


def get_logger(path, level=logging.ERROR, init=False):
    """
    get the logger
    """
    dir_name = os.path.dirname(path) or "."
    os.makedirs(dir_name, exist_ok=True)
    os.makedirs(constants.output_dir, exist_ok=True)

    logger = logging.getLogger(path)

    if init:
        for h in logger.handlers[:]:
            try:
                logger.removeHandler(h)
                h.close()
            except Exception:
                pass

        if os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8"):
                    pass
            except PermissionError:
                pass
            except Exception:
                pass

    handler = RotatingFileHandler(path, encoding="utf-8", delay=True)

    abs_path = os.path.abspath(path)
    if not any(
            isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", None) == abs_path
            for h in logger.handlers
    ):
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger


def format_interval(t):
    """
    Formats a number of seconds as a clock time, [H:]MM:SS

    Parameters
    ----------
    t  : int or float
        Number of seconds.
    Returns
    -------
    out  : str
        [H:]MM:SS
    """
    mins, s = divmod(int(t), 60)
    h, m = divmod(mins, 60)
    if h:
        return "{0:d}:{1:02d}:{2:02d}".format(h, m, s)
    else:
        return "{0:02d}:{1:02d}".format(m, s)


def get_pbar_remaining(n=0, total=0, start_time=None):
    """
    Get the remaining time of the progress bar
    """
    try:
        elapsed = time() - start_time
        completed_tasks = n
        if completed_tasks > 0:
            avg_time_per_task = elapsed / completed_tasks
            remaining_tasks = total - completed_tasks
            remaining_time = format_interval(avg_time_per_task * remaining_tasks)
        else:
            remaining_time = "未知"
        return remaining_time
    except Exception as e:
        print(f"Error: {e}")


def update_file(final_file, old_file, copy=False):
    """
    Update the file
    """
    old_file_path = resource_path(old_file, persistent=True)
    final_file_path = resource_path(final_file, persistent=True)
    if os.path.exists(old_file_path):
        if copy:
            shutil.copyfile(old_file_path, final_file_path)
        else:
            os.replace(old_file_path, final_file_path)


def filter_by_date(data):
    """
    Filter by date and limit
    """
    default_recent_days = 30
    use_recent_days = config.recent_days
    if not isinstance(use_recent_days, int) or use_recent_days <= 0:
        use_recent_days = default_recent_days
    start_date = datetime.datetime.now() - datetime.timedelta(days=use_recent_days)
    recent_data = []
    unrecent_data = []
    for info, response_time in data:
        item = (info, response_time)
        date = info["date"]
        if date:
            date = datetime.datetime.strptime(date, "%m-%d-%Y")
            if date >= start_date:
                recent_data.append(item)
            else:
                unrecent_data.append(item)
        else:
            unrecent_data.append(item)
    recent_data_len = len(recent_data)
    if recent_data_len == 0:
        recent_data = unrecent_data
    elif recent_data_len < config.urls_limit:
        recent_data.extend(unrecent_data[: config.urls_limit - len(recent_data)])
    return recent_data


def get_soup(source):
    """
    Get soup from source
    """
    source = re.sub(
        r"<!--.*?-->",
        "",
        source,
        flags=re.DOTALL,
    )
    soup = BeautifulSoup(source, "html.parser")
    return soup


def get_resolution_value(resolution_str):
    """
    Get resolution value from string
    """
    try:
        if resolution_str:
            pattern = r"(\d+)[xX*](\d+)"
            match = re.search(pattern, resolution_str)
            if match:
                width, height = map(int, match.groups())
                return width * height
    except:
        pass
    return 0


def get_total_urls(info_list: list[ChannelData], ipv_type_prefer, origin_type_prefer, rtmp_type=None) -> list:
    """
    Get the total urls from info list
    """
    ipv_prefer_bool = bool(ipv_type_prefer)
    origin_prefer_bool = bool(origin_type_prefer)
    if not ipv_prefer_bool:
        ipv_type_prefer = ["all"]
    if not origin_prefer_bool:
        origin_type_prefer = ["all"]
    categorized_urls = {origin: {ipv_type: [] for ipv_type in ipv_type_prefer} for origin in origin_type_prefer}
    total_urls = []
    for info in info_list:
        channel_id, url, origin, resolution, url_ipv_type, extra_info = (
            info["id"],
            info["url"],
            info["origin"],
            info["resolution"],
            info["ipv_type"],
            info.get("extra_info", ""),
        )
        if not origin:
            continue

        if origin == "hls":
            if not rtmp_type or (rtmp_type and origin in rtmp_type):
                total_urls.append(info)
                continue
            else:
                continue

        if origin == "whitelist":
            total_urls.append(info)
            continue

        if origin_prefer_bool and (origin not in origin_type_prefer):
            continue

        if not extra_info:
            info["extra_info"] = constants.origin_map[origin]

        if not origin_prefer_bool:
            origin = "all"

        if ipv_prefer_bool:
            if url_ipv_type in ipv_type_prefer:
                categorized_urls[origin][url_ipv_type].append(info)
        else:
            categorized_urls[origin]["all"].append(info)

    urls_limit = config.urls_limit
    for origin in origin_type_prefer:
        if len(total_urls) >= urls_limit:
            break
        for ipv_type in ipv_type_prefer:
            if len(total_urls) >= urls_limit:
                break
            urls = categorized_urls[origin].get(ipv_type, [])
            if not urls:
                continue
            remaining = urls_limit - len(total_urls)
            limit_urls = urls[:remaining]
            total_urls.extend(limit_urls)

    total_urls = total_urls[:urls_limit]

    return total_urls


def get_total_urls_from_sorted_data(data):
    """
    Get the total urls with filter by date and duplicate from sorted data
    """
    if len(data) > config.urls_limit:
        total_urls = [channel_data["url"] for channel_data, _ in filter_by_date(data)]
    else:
        total_urls = [channel_data["url"] for channel_data, _ in data]
    return list(dict.fromkeys(total_urls))[: config.urls_limit]


def check_ipv6_support():
    """
    Check if the system network supports ipv6
    """
    if os.getenv("GITHUB_ACTIONS"):
        return False
    url = "https://ipv6.tokyo.test-ipv6.com/ip/?callback=?&testdomain=test-ipv6.com&testname=test_aaaa"
    try:
        print(t("msg.check_ipv6_support"))
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(t("msg.ipv6_supported"))
            return True
    except Exception:
        pass
    print(t("msg.ipv6_not_supported"))
    return False


def check_ipv_type_match(ipv_type: str) -> bool:
    """
    Check if the ipv type matches
    """
    config_ipv_type = config.ipv_type
    return config_ipv_type == ipv_type or config_ipv_type == "all"


def check_url_by_keywords(url, keywords=None):
    """
    Check by URL keywords
    """
    if not keywords:
        return False
    else:
        return any(keyword in url for keyword in keywords)


def merge_objects(*objects, match_key=None):
    """
    Merge objects while preserving defaultdict types (including default_factory).
    Args:
        *objects: Dictionaries to merge
        match_key: If dict1[key] is a list of dicts, this key will be used to match and merge dicts
    """

    def clone_empty(value):
        """
        Return an empty container of the same *container* type as value,
        preserving defaultdict default_factory when applicable.
        """
        if isinstance(value, defaultdict):
            return defaultdict(value.default_factory)
        if isinstance(value, dict):
            return {}
        if isinstance(value, list):
            return []
        if isinstance(value, set):
            return set()
        try:
            return copy.copy(value)
        except Exception:
            return value

    def merge_dicts(dict1, dict2):
        for key, value in dict2.items():
            if key in dict1:
                if isinstance(dict1[key], dict) and isinstance(value, dict):
                    merge_dicts(dict1[key], value)
                elif isinstance(dict1[key], set) and isinstance(value, (set, list)):
                    dict1[key].update(value)
                elif isinstance(dict1[key], list) and isinstance(value, list):
                    if match_key and all(isinstance(x, dict) for x in dict1[key] + value):
                        existing_items = {item.get(match_key): item for item in dict1[key] if match_key in item}
                        for new_item in value:
                            if match_key in new_item and new_item[match_key] in existing_items:
                                merge_dicts(existing_items[new_item[match_key]], new_item)
                            else:
                                dict1[key].append(new_item)
                    else:
                        for x in value:
                            if x not in dict1[key]:
                                dict1[key].append(x)
                elif value != dict1[key]:
                    dict1[key] = copy.deepcopy(value)
            else:
                if isinstance(value, dict):
                    dict1[key] = clone_empty(value)
                    merge_dicts(dict1[key], value)
                else:
                    dict1[key] = copy.deepcopy(value)

    if not objects:
        return {}

    for obj in objects:
        if not isinstance(obj, dict):
            raise TypeError("All input objects must be dictionaries")

    first_obj = objects[0]
    if isinstance(first_obj, defaultdict):
        merged_dict = defaultdict(first_obj.default_factory)
    else:
        merged_dict = {}

    for obj in objects:
        merge_dicts(merged_dict, obj)

    return merged_dict


def get_public_url(port: int = config.public_port) -> str:
    host = config.public_domain
    scheme = config.public_scheme
    default_port = 80 if scheme == 'http' else 443
    port_part = f":{port}" if port != default_port else ""
    return f"{scheme}://{host}{port_part}"


def get_epg_url():
    """
    Get the epg result url
    """
    if os.getenv("GITHUB_ACTIONS"):
        repository = os.getenv("GITHUB_REPOSITORY", "Guovin/iptv-api")
        ref = os.getenv("GITHUB_REF", "gd")
        return join_url(config.cdn_url, f"https://raw.githubusercontent.com/{repository}/{ref}/output/epg/epg.gz")
    else:
        return f"{get_public_url()}/epg/epg.gz"


def get_logo_url():
    """
    Get the logo url
    """
    logo_url = join_url(config.cdn_url,
                        config.logo_url) if "raw.githubusercontent.com" in config.logo_url else config.logo_url
    if not logo_url:
        logo_url = f"{get_public_url()}/logo/"
    return logo_url


def convert_to_m3u(path=None, first_channel_name=None, data=None):
    """
    Convert result txt to m3u format
    """
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            m3u_output = f'#EXTM3U x-tvg-url="{get_epg_url()}"\n' if config.open_epg else "#EXTM3U\n"
            current_group = None
            logo_url = get_logo_url()
            from_fanmingming = "https://raw.githubusercontent.com/fanmingming/live/main/tv" in logo_url
            for line in file:
                trimmed_line = line.strip()
                if trimmed_line != "":
                    if "#genre#" in trimmed_line:
                        current_group = trimmed_line.replace(",#genre#", "").strip()
                    else:
                        try:
                            original_channel_name, _, channel_link = map(
                                str.strip, trimmed_line.partition(",")
                            )
                        except:
                            continue
                        use_name = first_channel_name if current_group in (t("content.update_time"),
                                                                           t("content.update_running")) else original_channel_name
                        processed_channel_name = use_name
                        if from_fanmingming:
                            processed_channel_name = re.sub(
                                r"(CCTV|CETV)-(\d+)(\+.*)?",
                                lambda m: f"{m.group(1)}{m.group(2)}"
                                          + ("+" if m.group(3) else ""),
                                use_name,
                            )
                        m3u_output += f'#EXTINF:-1 tvg-name="{processed_channel_name}" tvg-logo="{join_url(logo_url, f'{processed_channel_name}.{config.logo_type}')}"'
                        if current_group:
                            m3u_output += f' group-title="{current_group}"'
                        item_data = {}
                        if data:
                            item_list = data.get(original_channel_name, [])
                            for item in item_list:
                                if item["url"] == channel_link:
                                    item_data = item
                                    break
                        if item_data:
                            catchup = item_data.get("catchup")
                            if catchup:
                                for key, value in catchup.items():
                                    m3u_output += f' {key}="{value}"'
                        m3u_output += f",{original_channel_name}\n"
                        if item_data and config.open_headers:
                            headers = item_data.get("headers")
                            if headers:
                                for key, value in headers.items():
                                    m3u_output += f"#EXTVLCOPT:http-{key.lower()}={value}\n"
                        m3u_output += f"{channel_link}\n"
            m3u_file_path = os.path.splitext(path)[0] + ".m3u"
            with open(m3u_file_path, "w", encoding="utf-8") as m3u_file:
                m3u_file.write(m3u_output)


def get_result_file_content(path=None, show_content=False, file_type=None):
    """
    Get the content of the result file
    """
    result_file = (
        os.path.splitext(path)[0] + f".{file_type}"
        if file_type
        else path
    )
    if os.path.exists(result_file):
        if config.open_m3u_result:
            if file_type == "m3u" or not file_type:
                result_file = os.path.splitext(path)[0] + ".m3u"
            if file_type != "txt" and show_content == False:
                return send_file(resource_path(result_file), as_attachment=True)
        with open(result_file, "r", encoding="utf-8") as file:
            content = file.read()
    else:
        content = constants.waiting_tip
    response = make_response(content)
    response.mimetype = 'text/plain'
    return response


def remove_duplicates_from_list(data_list, seen, filter_host=False, ipv6_support=True):
    """
    Remove duplicates from data list
    """
    unique_list = []
    for item in data_list:
        if item["origin"] in ["whitelist", "hls"]:
            continue
        if not ipv6_support and item["ipv_type"] == "ipv6":
            continue
        part = item["host"] if filter_host else item["url"]
        if part not in seen:
            seen.add(part)
            unique_list.append(item)
    return unique_list


def process_nested_dict(data, seen, filter_host=False, ipv6_support=True):
    """
    Process nested dict
    """
    for key, value in data.items():
        if isinstance(value, dict):
            process_nested_dict(value, seen, filter_host, ipv6_support)
        elif isinstance(value, list):
            data[key] = remove_duplicates_from_list(value, seen, filter_host, ipv6_support)


def get_url_host(url):
    """
    Get the url host
    """
    matcher = constants.url_host_pattern.search(url)
    if matcher:
        return matcher.group()
    return None


def add_url_info(url, info):
    """
    Add url info to the URL
    """
    if info:
        separator = "-" if "$" in url else "$"
        url += f"{separator}{info}"
    return url


def format_url_with_cache(url, cache=None):
    """
    Format the URL with cache
    """
    cache = cache or get_url_host(url) or ""
    return add_url_info(url, f"cache:{cache}") if cache else url


def remove_cache_info(string):
    """
    Remove the cache info from the string
    """
    return re.sub(r"[.*]?\$?-?cache:.*", "", string)


def resource_path(relative_path, persistent=False):
    """
    Get the resource path
    """
    base_path = os.path.abspath(".")
    total_path = os.path.join(base_path, relative_path)
    if persistent or os.path.exists(total_path):
        return total_path
    else:
        try:
            base_path = sys._MEIPASS
            return os.path.join(base_path, relative_path)
        except Exception:
            return total_path


def write_content_into_txt(content, path=None, position=None, callback=None):
    """
    Write content into txt file
    """
    if not path:
        return

    mode = "r+" if position == "top" else "a"
    with open(path, mode, encoding="utf-8") as f:
        if position == "top":
            existing_content = f.read()
            f.seek(0, 0)
            f.write(f"{content}\n{existing_content}")
        else:
            f.write(content)

    if callback:
        callback()


def format_name(name: str) -> str:
    """
    Format the  name with sub and replace and lower
    """
    name = opencc_t2s.convert(name)
    name = constants.sub_pattern.sub("", name)
    for old, new in constants.replace_dict.items():
        name = name.replace(old, new)
    return name.lower()


def get_headers_key_value(content: str) -> dict:
    """
    Get the headers key value from content
    """
    key_value = {}
    for match in constants.key_value_pattern.finditer(content):
        key = match.group("key").strip().replace("http-", "").replace("-", "").lower()
        if "refer" in key:
            key = "referer"
        value = match.group("value").replace('"', "").strip()
        if key and value:
            key_value[key] = value
    return key_value


def get_name_value(content, pattern, open_headers=False, check_value=True):
    """
    Extract name and value from content using a regex pattern.
    :param content: str, the input content to search.
    :param pattern: re.Pattern, the compiled regex pattern to match.
    :param open_headers: bool, whether to extract headers.
    :param check_value: bool, whether to validate the presence of a URL.
    """
    result = []
    for match in pattern.finditer(content):
        group_dict = match.groupdict()
        name = (group_dict.get("name", "") or "").strip()
        value = (group_dict.get("value", "") or "").strip()
        if not name or (check_value and not value):
            continue
        data = {"name": name, "value": value}
        attributes = {**get_headers_key_value(group_dict.get("attributes", "")),
                      **get_headers_key_value(group_dict.get("options", ""))}
        headers = {
            "User-Agent": attributes.get("useragent", ""),
            "Referer": attributes.get("referer", ""),
            "Origin": attributes.get("origin", "")
        }
        catchup = {
            "catchup": attributes.get("catchup", ""),
            "catchup-source": attributes.get("catchupsource", ""),
        }
        headers = {k: v for k, v in headers.items() if v}
        catchup = {k: v for k, v in catchup.items() if v}
        if not open_headers and headers:
            continue
        if open_headers:
            data["headers"] = headers
        data["catchup"] = catchup
        result.append(data)
    return result


def get_real_path(path) -> str:
    """
    Get the real path
    """
    dir_path, file = os.path.split(path)
    user_real_path = os.path.join(dir_path, 'user_' + file)
    real_path = user_real_path if os.path.exists(user_real_path) else path
    return real_path


def get_urls_from_file(path: str, pattern_search: bool = True) -> list:
    """
    Get the urls from file
    """
    real_path = get_real_path(resource_path(path))
    urls = []
    if os.path.exists(real_path):
        with open(real_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if pattern_search:
                    match = constants.url_pattern.search(line)
                    if match:
                        urls.append(match.group().strip())
                else:
                    urls.append(line)
    return urls


def get_name_urls_from_file(path: str | list, format_name_flag: bool = False) -> dict[str, list]:
    """
    Get the name and urls from file or list of files.
    - path: single file path or list of file paths.
    - format_name_flag: whether to format the channel name.
    """
    paths = path if isinstance(path, (list, tuple)) else [path]
    name_urls = defaultdict(list)

    for p in paths:
        real_path = resource_path(p)
        if not os.path.exists(real_path):
            continue

        try:
            with open(real_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue

        filename = os.path.basename(real_path)
        m3u_type = filename.lower().endswith(".m3u") or ("#EXTM3U" in content.upper())

        if m3u_type:
            pattern = constants.multiline_m3u_pattern
            open_headers_flag = config.open_headers
            data = get_name_value(content, pattern=pattern, open_headers=open_headers_flag)

            for item in data:
                name = format_name(item["name"]) if format_name_flag else item["name"]
                url = item["value"]
                if url and url not in name_urls[name]:
                    name_urls[name].append(url)
        else:
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                name_value = get_name_value(line, pattern=constants.txt_pattern)
                if name_value and name_value[0]:
                    name = format_name(name_value[0]["name"]) if format_name_flag else name_value[0]["name"]
                    url = name_value[0]["value"]
                    if url and url not in name_urls[name]:
                        name_urls[name].append(url)

    return name_urls


def get_name_uri_from_dir(path: str) -> dict:
    """
    Get the name and uri from dir, only from file name
    """
    real_path = get_real_path(resource_path(path))
    name_urls = defaultdict(list)
    if os.path.exists(real_path):
        for file in os.listdir(real_path):
            filename = file.rsplit(".", 1)[0]
            name_urls[filename].append(f"{real_path}/{file}")
    return name_urls


def get_datetime_now():
    """
    Get the datetime now
    """
    now = datetime.datetime.now()
    time_zone = pytz.timezone(config.time_zone)
    return now.astimezone(time_zone).strftime("%Y-%m-%d %H:%M:%S")


def get_version_info():
    """
    Get the version info
    """
    with open(resource_path("version.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def join_url(url1: str, url2: str) -> str:
    """
    Get the join url
    :param url1: The first url
    :param url2: The second url
    :return: The join url
    """
    if not url1:
        return url2
    if not url2:
        return url1
    if not url1.endswith("/"):
        url1 += "/"
    return url1 + url2


def add_port_to_url(url: str, port: int) -> str:
    """
    Add port to the url
    """
    parsed = urlparse(url)
    netloc = parsed.netloc
    if parsed.username and parsed.password:
        netloc = f"{parsed.username}:{parsed.password}@{netloc}"
    if port:
        netloc = f"{netloc}:{port}"
    new_url = urlunparse((
        parsed.scheme,
        netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    return new_url


def get_url_without_scheme(url: str) -> str:
    """
    Get the url without scheme
    """
    parsed = urlparse(url)
    return parsed.netloc + parsed.path


def find_by_id(data: dict, id: int) -> dict:
    """
    Find the nested dict by id
    :param data: target data
    :param id: target id
    :return: target dict
    """
    if isinstance(data, dict) and 'id' in data and data['id'] == id:
        return data
    for key, value in data.items():
        if isinstance(value, dict):
            result = find_by_id(value, id)
            if result is not None:
                return result
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    result = find_by_id(item, id)
                    if result is not None:
                        return result
    return {}


def custom_print(*args, **kwargs):
    """
    Custom print
    """
    if not custom_print.disable:
        print(*args, **kwargs)


def get_urls_len(data) -> int:
    """
    Get the dict urls length
    """
    urls = set(
        url_info["url"]
        for value in data.values()
        for url_info_list in value.values()
        for url_info in url_info_list
    )
    return len(urls)


def render_nginx_conf(nginx_conf_template, nginx_conf):
    """
    Render the nginx conf file
    """

    with open(nginx_conf_template, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace('${APP_PORT}', str(config.app_port))
    content = content.replace('${NGINX_HTTP_PORT}', str(config.nginx_http_port))
    content = content.replace('${NGINX_RTMP_PORT}', str(config.nginx_rtmp_port))

    with open(nginx_conf, 'w', encoding='utf-8') as f:
        f.write(content)


def parse_times(times_str: str):
    """
    Parse times from a string in the format "HH:MM, HH:MM, ..."
    """
    times = []
    for part in (times_str or "").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            hh_mm = part.split(":")
            h = int(hh_mm[0])
            m = int(hh_mm[1]) if len(hh_mm) > 1 else 0
            times.append((h, m))
        except Exception:
            continue
    return times


def build_path_list(
        dir_path: Union[str, Path],
        exts: Optional[Union[str, Iterable[str]]] = None,
        recursive: bool = True,
        include_hidden: bool = False
) -> List[str]:
    """
    Build a list of file paths from a directory with filtering options.
    :param dir_path: The directory path to search.
    :param exts: Optional; A string or iterable of file extensions to filter by (e.g., '.txt', 'jpg'). Case-insensitive.
    :param recursive: Whether to search subdirectories recursively.
    :param include_hidden: Whether to include hidden files (those starting with a dot).
    :return: A sorted list of file paths matching the criteria.
    """
    p = Path(dir_path)
    if not p.exists() or not p.is_dir():
        return []

    exts_set = None
    if exts:
        if isinstance(exts, str):
            exts = [exts]
        exts_set = {e.lower() if e.startswith('.') else f".{e.lower()}" for e in exts}

    iterator = p.rglob("*") if recursive else p.glob("*")
    paths = []
    for f in iterator:
        if not f.is_file():
            continue
        if not include_hidden and f.name.startswith("."):
            continue
        if exts_set and f.suffix.lower() not in exts_set:
            continue
        paths.append(str(f.resolve()))
    return sorted(paths)


def to_serializable(obj):
    """
    Convert an object to a serializable form.
    Handles dicts, lists, tuples, sets, and other iterables recursively.
    Non-serializable objects are returned as-is.
    """
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_serializable(i) for i in obj]
    try:
        if not isinstance(obj, (str, bytes)) and hasattr(obj, "__iter__"):
            return [to_serializable(i) for i in obj]
    except Exception:
        pass
    return obj


def count_files_by_ext(
        dir_path: Union[str, Path],
        exts: Optional[Union[str, Iterable[str]]] = None,
        recursive: bool = False,
        include_hidden: bool = False
) -> int:
    """
    Count files in a directory with filtering options.
    :param dir_path: The directory path to search.
    :param exts: Optional; A string or iterable of file extensions to filter by (e.g., '.txt', 'jpg'). Case-insensitive.
    :param recursive: Whether to search subdirectories recursively.
    :param include_hidden: Whether to include hidden files (those starting with a dot).
    :return: The count of files matching the criteria.
    """
    p = Path(dir_path)
    if not p.exists() or not p.is_dir():
        return 0

    exts_set = None
    if exts:
        if isinstance(exts, str):
            exts = [exts]
        exts_set = {e.lower() if e.startswith('.') else f".{e.lower()}" for e in exts}

    iterator = p.rglob("*") if recursive else p.glob("*")
    count = 0
    for f in iterator:
        if not f.is_file():
            continue
        if not include_hidden and f.name.startswith("."):
            continue
        if exts_set and f.suffix.lower() not in exts_set:
            continue
        count += 1

    return count
