import gzip
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Lock
from time import time
import sys

from requests import Session
from tqdm.asyncio import tqdm_asyncio

import utils.constants as constants
from utils.channel import format_channel_name
from utils.config import config
from utils.i18n import t
from utils.retry import retry_func
from utils.tools import (
    get_pbar_remaining,
    opencc_t2s,
    github_blob_to_raw,
    get_request_url_candidates,
    request_first,
    get_subscribe_entries,
    count_disabled_urls,
    disable_urls_in_file,
)


def _normalize_epg_content(content, request_url=None, response=None):
    if not content:
        return None

    if isinstance(content, str):
        return content

    if isinstance(content, bytearray):
        content = bytes(content)

    if isinstance(content, bytes) and content.startswith(b"\x1f\x8b"):
        content = gzip.decompress(content)

    if isinstance(content, bytes):
        return content.decode("utf-8", errors="replace")
    return content


def parse_epg(epg_content):
    try:
        parser = ET.XMLParser(encoding='UTF-8')
        root = ET.fromstring(epg_content, parser=parser)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        if isinstance(epg_content, (bytes, bytearray)):
            preview = bytes(epg_content[:500]).decode("utf-8", errors="replace")
        else:
            preview = epg_content[:500]
        print(f"Problematic content: {preview}")
        return {}, defaultdict(list)

    channels = {}
    programmes = defaultdict(list)
    now_by_timezone = {}

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

        timezone = channel_start.tzinfo
        if timezone not in now_by_timezone:
            now_by_timezone[timezone] = datetime.now(timezone) if timezone else datetime.now()
        now = now_by_timezone[timezone]
        if channel_start < (now - timedelta(days=7)):
            continue

        channel_text = opencc_t2s.convert(programme.find('title').text)
        channel_elem = ET.Element(
            'programme', attrib={"channel": channel_id, "start": channel_start.strftime("%Y%m%d%H%M%S +0800"),
                                 "stop": channel_stop.strftime("%Y%m%d%H%M%S +0800")})
        channel_elem_s = ET.SubElement(
            channel_elem, 'title', attrib={"lang": "zh"})
        channel_elem_s.text = channel_text
        programmes[channel_id].append(channel_elem)

    return channels, programmes


def _epg_dedup_key(url) -> str:
    """
    Normalize an EPG url for de-duplication (scheme / .gz / trailing-slash insensitive).
    """
    if not url:
        return ""
    key = github_blob_to_raw(str(url)).strip()
    key = re.sub(r"^https?://", "", key, flags=re.IGNORECASE).rstrip("/")
    if key.endswith(".gz"):
        key = key[:-3]
    return key.lower()


async def get_epg(names=None, callback=None, extra_entries=None):
    normalized_names = {format_channel_name(name) for name in (names or []) if name}
    whitelist_entries, default_entries = get_subscribe_entries(constants.epg_path)
    configured_entries = whitelist_entries + default_entries
    discovered_entries = []
    if extra_entries:
        seen_keys = {_epg_dedup_key(e.get("url") if isinstance(e, dict) else e) for e in configured_entries}
        for url in extra_entries:
            key = _epg_dedup_key(url)
            if url and key and key not in seen_keys:
                discovered_entries.append(url)
                seen_keys.add(key)
    disabled_count = count_disabled_urls(constants.epg_path)
    print(
        t("msg.epg_urls_whitelist_total").format(
            default_count=len(default_entries),
            whitelist_count=len(whitelist_entries),
            disabled_count=disabled_count,
            total=len(configured_entries),
        )
    )
    if not configured_entries and not discovered_entries:
        return {}
    urls_len = len(configured_entries) + len(discovered_entries)
    pbar = tqdm_asyncio(
        total=urls_len,
        desc=t("pbar.getting_name").format(name=t("name.epg")),
        file=sys.stdout,
        mininterval=1.0,
        miniters=1,
        dynamic_ncols=False,
    )
    start_time = time()
    result = defaultdict(list)
    all_result_verify = set()
    result_lock = Lock()
    session = Session()
    open_unmatch_category = config.open_unmatch_category
    open_auto_disable_source = config.open_auto_disable_source
    disabled_urls = set()
    disabled_lock = Lock()

    def _mark_disabled(source_url: str, reason: str):
        if not open_auto_disable_source or not source_url:
            return
        with disabled_lock:
            disabled_urls.add(source_url)
        print(t("msg.auto_disable_source").format(name=t("name.epg"), url=source_url, reason=reason), flush=True)

    def process_run(entry):
        nonlocal all_result_verify, result
        disable_reason = None
        request_url = entry.get('url') if isinstance(entry, dict) else entry
        source_url = None
        try:
            source_url = entry.get('source_url', request_url) if isinstance(entry, dict) else request_url
            headers = entry.get('headers') if isinstance(entry, dict) else None
            response = None
            try:
                candidates = get_request_url_candidates(request_url)

                def _fetch(u):
                    resp = session.get(u, timeout=config.request_timeout, headers=headers)
                    resp.raise_for_status()
                    return resp

                response = retry_func(
                    lambda: request_first(candidates, _fetch),
                    name=request_url,
                )
            except Exception as e:
                print(e, flush=True)
                disable_reason = t("msg.auto_disable_request_failed")
            if response:
                content = _normalize_epg_content(response.content, request_url=request_url, response=response)
                if content:
                    channels, programmes = parse_epg(content)
                    entry_matched = False
                    for channel_id, display_name in channels.items():
                        display_name = format_channel_name(display_name)
                        if not open_unmatch_category and normalized_names and display_name not in normalized_names:
                            continue
                        entry_matched = True
                        if channel_id not in all_result_verify and display_name not in all_result_verify:
                            with result_lock:
                                if channel_id not in all_result_verify and display_name not in all_result_verify:
                                    if not channel_id.isdigit():
                                        all_result_verify.add(channel_id)
                                    all_result_verify.add(display_name)
                                    result[display_name] = programmes[channel_id]
                    if not entry_matched and not disable_reason:
                        disable_reason = t("msg.auto_disable_no_match")
                elif not disable_reason:
                    disable_reason = t("msg.auto_disable_empty_content")
            elif not disable_reason:
                disable_reason = t("msg.auto_disable_request_failed")
        except Exception as e:
            print(t("msg.error_name_info").format(name=request_url, info=e), flush=True)
            if not disable_reason:
                disable_reason = t("msg.auto_disable_request_failed")
        finally:
            if disable_reason:
                _mark_disabled(source_url, disable_reason)
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

    with ThreadPoolExecutor(max_workers=config.performance_settings.fetch_workers) as executor:
        for entry in configured_entries:
            executor.submit(process_run, entry)
    with ThreadPoolExecutor(max_workers=config.performance_settings.fetch_workers) as executor:
        for entry in discovered_entries:
            executor.submit(process_run, entry)
    session.close()
    pbar.close()
    active_count = len(configured_entries)
    disabled_count = 0
    if disabled_urls:
        counts = disable_urls_in_file(constants.epg_path, disabled_urls)
        active_count = counts["active"]
        disabled_count = counts["disabled"]
    print(t("msg.auto_disable_source_done").format(name=t("name.epg"), active_count=active_count,
                                                   disabled_count=disabled_count), flush=True)
    return result
