import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from updates.subscribe import get_channels_by_subscribe_urls
from utils.driver.tools import get_soup_driver
from utils.config import config
import utils.constants as constants
from utils.channel import format_channel_name
from utils.tools import get_pbar_remaining, resource_path, get_name_url
import json

# import asyncio
from requests import Session
from collections import defaultdict
from time import time
from tqdm import tqdm


def get_region_urls_from_IPTV_Multicast_source():
    """
    Get the region urls from IPTV_Multicast_source
    """
    region_url = {}
    origin_url = "https://github.com/xisohi/IPTV-Multicast-source/blob/main/README.md"
    soup = get_soup_driver(origin_url)
    tbody = soup.find("tbody")
    trs = tbody.find_all("tr") if tbody else []
    for tr in trs:
        tds = tr.find_all("td")
        name = tds[0].get_text().strip()
        unicom = tds[1].find("a", href=True).get("href")
        mobile = tds[2].find("a", href=True).get("href")
        telecom = tds[3].find("a", href=True).get("href")
        if name not in region_url:
            region_url[name] = {}
        region_url[name]["联通"] = unicom
        region_url[name]["移动"] = mobile
        region_url[name]["电信"] = telecom
    with open(
            resource_path("updates/multicast/multicast_map.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(region_url, f, ensure_ascii=False, indent=4)


def get_multicast_urls_info_from_region_list():
    """
    Get the multicast urls info from region
    """
    urls_info = []
    with open(
            resource_path("updates/multicast/multicast_map.json"), "r", encoding="utf-8"
    ) as f:
        region_url = json.load(f)
        urls_info = [
            {"region": region, "type": type, "url": url}
            for region, value in region_url.items()
            for type, url in value.items()
        ]
        return urls_info


async def get_multicast_region_result():
    """
    Get multicast region result
    """
    multicast_region_urls_info = get_multicast_urls_info_from_region_list()
    multicast_result = await get_channels_by_subscribe_urls(
        multicast_region_urls_info, multicast=True
    )
    with open(
            resource_path("updates/multicast/multicast_region_result.json"),
            "w",
            encoding="utf-8",
    ) as f:
        json.dump(multicast_result, f, ensure_ascii=False, indent=4)


def get_multicast_region_type_result_txt():
    """
    Get multicast region type result txt
    """
    with open(
            resource_path("updates/multicast/multicast_map.json"), "r", encoding="utf-8"
    ) as f:
        region_url = json.load(f)
        session = Session()
        for region, value in region_url.items():
            for type, url in value.items():
                response = session.get(url)
                content = response.text
                with open(
                        resource_path(f"config/rtp/{region}_{type}.txt"),
                        "w",
                        encoding="utf-8",
                ) as f:
                    f.write(content)


def get_multicast_region_result_by_rtp_txt(callback=None):
    """
    Get multicast region result by rtp txt
    """
    rtp_path = resource_path("config/rtp")
    config_region_list = set(config.multicast_region_list)
    rtp_file_list = [
        filename.rsplit(".", 1)[0]
        for filename in os.listdir(rtp_path)
        if filename.endswith(".txt")
           and "_" in filename
           and (
                   filename.rsplit(".", 1)[0].partition("_")[0] in config_region_list
                   or config_region_list & {"all", "ALL", "全部"}
           )
    ]

    total_files = len(rtp_file_list)
    if callback:
        callback(f"正在读取本地组播数据, 共{total_files}个文件", 0)

    pbar = tqdm(total=total_files, desc="Loading local multicast rtp files")
    multicast_result = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    start_time = time()

    for filename in rtp_file_list:
        region, _, type = filename.partition("_")
        with open(
                os.path.join(rtp_path, f"{filename}.txt"), "r", encoding="utf-8"
        ) as f:
            for line in f:
                name_url = get_name_url(line, pattern=constants.rtp_pattern)
                if name_url and name_url[0]:
                    channel_name = format_channel_name(name_url[0]["name"])
                    url = name_url[0]["url"]
                    if url not in multicast_result[channel_name][region][type]:
                        multicast_result[channel_name][region][type].append(url)
        pbar.update()
        if callback:
            remaining_files = total_files - pbar.n
            estimated_time = get_pbar_remaining(pbar.n, total_files, start_time)
            callback(
                f"正在读取{region}_{type}的组播数据, 剩余{remaining_files}个文件, 预计剩余时间: {estimated_time}",
                int((pbar.n / total_files) * 100),
            )

    with open(
            resource_path("updates/multicast/multicast_region_result.json"),
            "w",
            encoding="utf-8",
    ) as f:
        json.dump(multicast_result, f, ensure_ascii=False, indent=4)

    pbar.close()
    return multicast_result


if __name__ == "__main__":
    get_region_urls_from_IPTV_Multicast_source()
    # asyncio.run(get_multicast_region_result())
    get_multicast_region_type_result_txt()
    # get_multicast_region_result_by_rtp_txt()
