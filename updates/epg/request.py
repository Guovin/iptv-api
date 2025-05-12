import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from time import time

from requests import Session, exceptions
from tqdm.asyncio import tqdm_asyncio

import utils.constants as constants
from utils.channel import format_channel_name
from utils.config import config
from utils.retry import retry_func
from utils.tools import get_pbar_remaining, get_urls_from_file, opencc_t2s, join_url


def parse_epg(epg_content):
    try:
        parser = ET.XMLParser(encoding='UTF-8')
        root = ET.fromstring(epg_content, parser=parser)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        print(f"Problematic content: {epg_content[:500]}")
        return {}, defaultdict(list)

    channels = {}
    programmes = defaultdict(list)

    for channel in root.findall('channel'):
        channel_id = channel.get('id')
        display_name = channel.find('display-name').text
        channels[channel_id] = display_name

    for programme in root.findall('programme'):
        channel_id = programme.get('channel')
        channel_start = datetime.strptime(
            re.sub(r'\s+', '', programme.get('start')), "%Y%m%d%H%M%S%z")
        channel_stop = datetime.strptime(
            re.sub(r'\s+', '', programme.get('stop')), "%Y%m%d%H%M%S%z")
        channel_text = opencc_t2s.convert(programme.find('title').text)
        channel_elem = ET.SubElement(
            root, 'programme', attrib={"channel": channel_id, "start": channel_start.strftime("%Y%m%d%H%M%S +0800"),
                                       "stop": channel_stop.strftime("%Y%m%d%H%M%S +0800")})
        channel_elem_s = ET.SubElement(
            channel_elem, 'title', attrib={"lang": "zh"})
        channel_elem_s.text = channel_text
        programmes[channel_id].append(channel_elem)

    return channels, programmes


async def get_epg(names=None, callback=None):
    urls = get_urls_from_file(constants.epg_path)
    if not os.getenv("GITHUB_ACTIONS") and config.cdn_url:
        urls = [join_url(config.cdn_url, url) if "raw.githubusercontent.com" in url else url
                for url in urls]
    urls_len = len(urls)
    pbar = tqdm_asyncio(
        total=urls_len,
        desc=f"Processing epg",
    )
    start_time = time()
    result = defaultdict(list)
    all_result_verify = set()
    session = Session()

    def process_run(url):
        nonlocal all_result_verify, result
        try:
            response = None
            try:
                response = (
                    retry_func(
                        lambda: session.get(
                            url, timeout=config.request_timeout
                        ),
                        name=url,
                    )
                )
            except exceptions.Timeout:
                print(f"Timeout on epg: {url}")
            if response:
                response.encoding = "utf-8"
                content = response.text
                if content:
                    channels, programmes = parse_epg(content)
                    for channel_id, display_name in channels.items():
                        display_name = format_channel_name(display_name)
                        if names and display_name not in names:
                            continue
                        if channel_id not in all_result_verify and display_name not in all_result_verify:
                            if not channel_id.isdigit():
                                all_result_verify.add(channel_id)
                            all_result_verify.add(display_name)
                            result[display_name] = programmes[channel_id]
        except Exception as e:
            print(f"Error on {url}: {e}")
        finally:
            pbar.update()
            remain = urls_len - pbar.n
            if callback:
                callback(
                    f"正在获取EPG源, 剩余{remain}个源待获取, 预计剩余时间: {get_pbar_remaining(n=pbar.n, total=pbar.total, start_time=start_time)}",
                    int((pbar.n / urls_len) * 100),
                )

    with ThreadPoolExecutor(max_workers=10) as executor:
        for epg_url in urls:
            executor.submit(process_run, epg_url)
    session.close()
    pbar.close()
    return result
