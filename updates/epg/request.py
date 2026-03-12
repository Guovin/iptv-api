import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from time import time

from requests import Session, exceptions
from tqdm.asyncio import tqdm_asyncio

import utils.constants as constants
from utils.channel import format_channel_name
from utils.config import config
from utils.i18n import t
from utils.retry import retry_func
from utils.tools import get_pbar_remaining, opencc_t2s, join_url, github_blob_to_raw, get_subscribe_entries


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

        now = datetime.now(channel_start.tzinfo) if channel_start.tzinfo else datetime.now()
        if channel_start < (now - timedelta(days=7)):
            continue

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
    whitelist_entries, default_entries = get_subscribe_entries(constants.epg_path)
    entries = whitelist_entries + default_entries
    if not entries:
        return {}
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

        entries = [_map_entry(e) for e in entries]

    urls_len = len(entries)
    pbar = tqdm_asyncio(
        total=urls_len,
        desc=t("pbar.getting_name").format(name=t("name.epg")),
    )
    start_time = time()
    result = defaultdict(list)
    all_result_verify = set()
    session = Session()

    def process_run(entry):
        nonlocal all_result_verify, result
        try:
            entry_url = entry.get('url') if isinstance(entry, dict) else entry
            headers = entry.get('headers') if isinstance(entry, dict) else None
            response = None
            try:
                response = retry_func(
                    lambda: session.get(entry_url, timeout=config.request_timeout, headers=headers),
                    name=entry_url,
                )
            except exceptions.Timeout:
                print(t("msg.request_timeout").format(name=entry_url))
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
            print(t("msg.error_name_info").format(name=entry_url, info=e))
        finally:
            pbar.update()
            if callback:
                callback(
                    t("msg.progress_desc").format(name=f"{t("pbar.get")}{t("name.epg")}",
                                                  remaining_total=urls_len - pbar.n,
                                                  item_name=t("pbar.source"),
                                                  remaining_time=get_pbar_remaining(n=pbar.n, total=pbar.total,
                                                                                    start_time=start_time)),
                    int((pbar.n / urls_len) * 100),
                )

    with ThreadPoolExecutor(max_workers=10) as executor:
        for entry in entries:
            executor.submit(process_run, entry)
    session.close()
    pbar.close()
    return result
