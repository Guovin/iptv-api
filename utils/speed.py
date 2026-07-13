import asyncio
import http.cookies
import re
from collections import deque
from contextlib import asynccontextmanager
from importlib import import_module
from time import time
from typing import Any
from urllib.parse import quote, urljoin

import m3u8

import utils.constants as constants
from utils.config import config
from utils.ffmpeg import probe_url, ffmpeg_url
from utils.i18n import t
from utils.requests.tools import headers as request_headers
from utils.tools import get_resolution_value
from utils.types import TestResult, ChannelTestResult, TestResultCacheData

http.cookies._is_legal_key = lambda _: True
_aiohttp = import_module("aiohttp")
ClientSession = getattr(_aiohttp, "ClientSession")
TCPConnector = getattr(_aiohttp, "TCPConnector")
ClientTimeout = getattr(_aiohttp, "ClientTimeout")
cache: TestResultCacheData = {}
speed_test_timeout = config.speed_test_timeout
speed_test_filter_host = config.speed_test_filter_host
open_filter_resolution = config.open_filter_resolution
min_resolution_value = config.min_resolution_value
max_resolution_value = config.max_resolution_value
open_supply = config.open_supply
sort_by = config.sort_by
open_filter_speed = config.open_filter_speed
min_speed_value = config.min_speed
resolution_speed_map = config.resolution_speed_map
open_filter_ad = config.open_filter_ad
m3u8_headers = ['application/x-mpegurl', 'application/vnd.apple.mpegurl', 'audio/mpegurl', 'audio/x-mpegurl']
default_ipv6_delay = 0.1
default_ipv6_resolution = "1920x1080"
default_ipv6_result = {
    'speed': float("inf"),
    'delay': default_ipv6_delay,
    'resolution': default_ipv6_resolution
}

min_measure_time = 1.0
stability_window = 4
stability_threshold = 0.12
segment_sample_limit = 2
playlist_max_bytes = 2 * 1024 * 1024

ad_filter_keywords = [
    "no_signal",
    "nosignal",
    "no-signal",
    "signal_offline",
    "no_video",
    "novideo",
    "advertisement",
    "advert",
    "placeholder",
    "default_video",
    "cctv_off",
    "/ad/",
    "/ads/",
]
ad_max_loop_duration = 90


def create_speed_test_session(concurrency: int):
    limit = max(1, int(concurrency or 1))
    return ClientSession(
        connector=TCPConnector(ssl=False, limit=limit, limit_per_host=min(2, limit), ttl_dns_cache=300),
        timeout=ClientTimeout(total=None),
        trust_env=True,
    )


@asynccontextmanager
async def _limit(semaphore):
    if semaphore is None:
        yield
        return
    async with semaphore:
        yield


@asynccontextmanager
async def _session(session, concurrency: int = 1):
    if session is not None:
        yield session
        return
    async with create_speed_test_session(concurrency) as created_session:
        yield created_session


async def get_speed_with_download(url: str, headers: dict = None, session: Any = None,
                                  timeout: int = speed_test_timeout, semaphore=None) -> dict[str, float | None]:
    """
    Get the speed of the url with a total timeout
    """
    start_time = time()
    delay = -1
    total_size = 0
    min_bytes = 64 * 1024
    last_sample_time = start_time
    last_sample_size = 0

    if session is None:
        session = ClientSession(connector=TCPConnector(ssl=False), trust_env=True)
        created_session = True
    else:
        created_session = False

    speed_samples = deque(maxlen=stability_window)
    try:
        async with _limit(semaphore):
            async with session.get(url, headers=headers, timeout=timeout) as response:
                if response.status != 200:
                    raise Exception("Invalid response")
                delay = int(round((time() - start_time) * 1000))
                async for chunk in response.content.iter_any():
                    if chunk:
                        total_size += len(chunk)
                        now = time()
                        elapsed = now - start_time
                        delta_t = now - last_sample_time
                        delta_b = total_size - last_sample_size
                        if delta_t > 0 and delta_b > 0:
                            inst_speed = delta_b / delta_t / 1024.0 / 1024.0
                            speed_samples.append(inst_speed)
                            last_sample_time = now
                            last_sample_size = total_size
                        if (elapsed >= min_measure_time and total_size >= min_bytes
                                and len(speed_samples) >= stability_window):
                            mean = sum(speed_samples) / len(speed_samples)
                            if mean > 0 and (max(speed_samples) - min(speed_samples)) / mean < stability_threshold:
                                total_time = elapsed
                                return {
                                    'speed': total_size / total_time / 1024 / 1024,
                                    'delay': delay,
                                    'size': total_size,
                                    'time': total_time,
                                }
    except:
        pass
    finally:
        if created_session:
            await session.close()
    total_time = time() - start_time
    speed_value = total_size / total_time / 1024 / 1024 if total_time > 0 else 0.0
    return {
        'speed': speed_value,
        'delay': delay,
        'size': total_size,
        'time': total_time,
    }


async def get_headers(url: str, headers: dict = None, session: Any = None, timeout: int = 3,
                      semaphore=None) -> dict:
    """
    Get the headers of the url
    """
    if session is None:
        session = ClientSession(connector=TCPConnector(ssl=False), trust_env=True)
        created_session = True
    else:
        created_session = False
    res_headers = {}
    try:
        async with _limit(semaphore):
            async with session.head(url, headers=headers, timeout=timeout, allow_redirects=False) as response:
                res_headers = dict(response.headers)
    except:
        pass
    finally:
        if created_session:
            await session.close()
    return res_headers


async def get_url_content(url: str, headers: dict = None, session: Any = None,
                          timeout: int = speed_test_timeout, semaphore=None) -> str:
    """
    Get the content of the url
    """
    if session is None:
        session = ClientSession(connector=TCPConnector(ssl=False), trust_env=True)
        created_session = True
    else:
        created_session = False
    content = ""
    try:
        async with _limit(semaphore):
            async with session.get(url, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    payload = await response.content.read(playlist_max_bytes + 1)
                    if len(payload) > playlist_max_bytes:
                        raise Exception("Response too large")
                    content = payload.decode(response.charset or "utf-8", errors="replace")
                else:
                    raise Exception("Invalid response")
    except:
        pass
    finally:
        if created_session:
            await session.close()
    return content


def check_m3u8_valid(headers: dict) -> bool:
    """
    Check if the m3u8 url is valid
    """
    content_type = headers.get('Content-Type', '').lower()
    if not content_type:
        return False
    return any(item in content_type for item in m3u8_headers)


def is_ad_playlist(media_playlist, base_url: str = "") -> bool:
    segments = getattr(media_playlist, "segments", None)
    if not segments:
        return False
    haystack = (base_url + " " + " ".join(segment.uri or "" for segment in segments)).lower()
    if any(keyword in haystack for keyword in ad_filter_keywords):
        return True
    if getattr(media_playlist, "is_endlist", False):
        total_duration = sum(segment.duration or 0 for segment in segments)
        if 0 < total_duration <= ad_max_loop_duration:
            return True
    return False


def _parse_time_to_seconds(t: str) -> float:
    """
    Parse time string to seconds
    """
    if not t:
        return 0.0
    parts = [p.strip() for p in t.split(':') if p.strip() != ""]
    if not parts:
        return 0.0
    try:
        total = 0.0
        for i, part in enumerate(reversed(parts)):
            total += float(part) * (60 ** i)
        return total
    except Exception:
        return 0.0


async def get_result(url: str, headers: dict = None, resolution: str = None,
                     filter_resolution: bool = config.open_filter_resolution,
                     timeout: int = speed_test_timeout, session: Any = None,
                     http_semaphore=None, probe_semaphore=None,
                     redirects_remaining: int = 5) -> dict[str, float | None]:
    """
    Get the test result of the url
    """
    info = {'speed': 0.0, 'delay': -1, 'resolution': resolution}
    location = None
    segment_urls = []
    try:
        url = quote(url, safe=':/?$&=@[]%').partition('$')[0]
        async with _session(session) as active_session:
            res_headers = await get_headers(url, headers, active_session, semaphore=http_semaphore)
            location = res_headers.get('Location') if res_headers else None
            if location:
                if redirects_remaining <= 0:
                    raise Exception("Too many redirects")
                info.update(await get_result(
                    urljoin(url, location),
                    headers,
                    resolution,
                    filter_resolution,
                    timeout,
                    session=active_session,
                    http_semaphore=http_semaphore,
                    probe_semaphore=probe_semaphore,
                    redirects_remaining=redirects_remaining - 1,
                ))
            else:
                should_parse_m3u8 = ".m3u8" in url.lower() or check_m3u8_valid(res_headers)
                if should_parse_m3u8:
                    url_content = await get_url_content(
                        url, headers, active_session, timeout, semaphore=http_semaphore
                    )
                else:
                    url_content = ""
                if should_parse_m3u8 and url_content:
                    m3u8_obj = m3u8.loads(url_content)
                    playlists = m3u8_obj.playlists
                    segments = m3u8_obj.segments
                    if playlists:
                        best_playlist = max(m3u8_obj.playlists, key=lambda p: p.stream_info.bandwidth or 0)
                        stream_resolution = getattr(best_playlist.stream_info, "resolution", None)
                        if stream_resolution and len(stream_resolution) == 2:
                            info['resolution'] = f"{stream_resolution[0]}x{stream_resolution[1]}"
                        stream_frame_rate = getattr(best_playlist.stream_info, "frame_rate", None)
                        if stream_frame_rate:
                            info['fps'] = stream_frame_rate
                        playlist_url = urljoin(url, best_playlist.uri)
                        playlist_content = await get_url_content(
                            playlist_url, headers, active_session, timeout, semaphore=http_semaphore
                        )
                        if playlist_content:
                            media_playlist = m3u8.loads(playlist_content)
                            if open_filter_ad and is_ad_playlist(media_playlist, playlist_url):
                                raise Exception("Ad source filtered")
                            segment_urls = [urljoin(playlist_url, segment.uri) for segment in media_playlist.segments]
                    else:
                        if open_filter_ad and is_ad_playlist(m3u8_obj, url):
                            raise Exception("Ad source filtered")
                        segment_urls = [urljoin(url, segment.uri) for segment in segments]
                    if not segment_urls:
                        raise Exception("Segment urls not found")
                else:
                    res_info = await get_speed_with_download(
                        url, headers, active_session, timeout, semaphore=http_semaphore
                    )
                    info.update({'speed': res_info['speed'], 'delay': res_info['delay']})
                if segment_urls:
                    sampled_segment_urls = segment_urls[-(segment_sample_limit + 1):-1]
                    if not sampled_segment_urls:
                        sampled_segment_urls = segment_urls[-segment_sample_limit:]
                    tasks = [
                        get_speed_with_download(
                            ts_url,
                            headers,
                            active_session,
                            timeout,
                            semaphore=http_semaphore,
                        )
                        for ts_url in sampled_segment_urls
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    valid_results = [
                        result for result in results
                        if isinstance(result, dict) and result.get('size') and result.get('time')
                    ]
                    total_size = sum(result['size'] for result in valid_results)
                    total_time = sum(result['time'] for result in valid_results)
                    info['speed'] = total_size / total_time / 1024 / 1024 if total_time > 0 else 0
                    delays = [result['delay'] for result in valid_results if result.get('delay', -1) >= 0]
                    info['delay'] = int(sum(delays) / len(delays)) if delays else -1
    except:
        pass
    finally:
        probe_speed_threshold = min(
            [min_speed_value, *resolution_speed_map.values()],
            default=min_speed_value,
        )
        should_probe = open_supply or not open_filter_speed or (info.get('speed') or 0) >= probe_speed_threshold
        if (filter_resolution and should_probe and not location
                and not info.get('resolution') and info.get('delay') != -1):
            try:
                async with _limit(probe_semaphore):
                    probed = await probe_url(url, headers, timeout=timeout)
                if probed:
                    info['resolution'] = probed.get('resolution')
                    info['fps'] = probed.get('fps')
                    info['video_codec'] = probed.get('video_codec')
                    info['audio_codec'] = probed.get('audio_codec')
            except Exception:
                pass
    return info


async def get_delay_requests(url, timeout=speed_test_timeout, proxy=None):
    """
    Get the delay of the url by requests
    """
    async with ClientSession(
            connector=TCPConnector(ssl=False), trust_env=True
    ) as session:
        start = time()
        end = None
        try:
            async with session.get(url, timeout=timeout, proxy=proxy) as response:
                if response.status == 404:
                    return -1
                content = await response.read()
                if content:
                    end = time()
                else:
                    return -1
        except Exception as e:
            return -1
        return int(round((end - start) * 1000)) if end else -1


def get_video_info(video_info):
    """
    Get the video info from ffmpeg stderr and return a dict with keys:
      - resolution: str or None (e.g. '1280x720')
      - fps: float or None
      - video_codec: str or None
      - audio_codec: str or None
      - speed: float or None
    """
    resolution = None
    fps = None
    video_codec = None
    audio_codec = None
    if video_info is not None:
        match = re.search(r"(\d{3,4}x\d{3,4})", video_info)
        if match:
            resolution = match.group(0)
        m_fps = re.search(r"(\d+(?:\.\d+)?)\s*fps", video_info, re.IGNORECASE)
        if not m_fps:
            m_fps = re.search(r"(\d+(?:\.\d+)?)\s*tbr", video_info, re.IGNORECASE)
        if not m_fps:
            m_fps = re.search(r"(\d+(?:\.\d+)?)\s*tbn", video_info, re.IGNORECASE)
        if m_fps:
            try:
                fps = float(m_fps.group(1))
            except Exception:
                fps = None
        m_vc = re.search(r"Video:\s*([^,\n\r(]+)", video_info, re.IGNORECASE)
        if m_vc:
            vc = m_vc.group(1).strip()
            vc = vc.split(',')[0].split()[0]
            if vc:
                video_codec = vc
        m_ac = re.search(r"Audio:\s*([^,\n\r(]+)", video_info, re.IGNORECASE)
        if m_ac:
            ac = m_ac.group(1).strip()
            ac = ac.split(',')[0].split()[0]
            if ac:
                audio_codec = ac

    def parse_size_value(value_str: str, unit: str | None) -> float:
        try:
            val = float(value_str)
        except Exception:
            return 0.0
        if not unit:
            return val
        unit_lower = unit.lower()
        if unit_lower in ("b", "bytes"):
            return val
        if unit_lower in ("kib", "k"):
            return val * 1024.0
        if unit_lower in ("kb",):
            return val * 1000.0
        if unit_lower in ("mib", "mb"):
            return val * 1024.0 * 1024.0
        return val

    speed_val = None
    try:
        total_bytes = 0.0
        m_video_size = re.search(r"video:\s*([0-9]+(?:\.[0-9]+)?)\s*(KiB|MiB|kB|B|kb|KB)?", video_info, re.IGNORECASE)
        m_audio_size = re.search(r"audio:\s*([0-9]+(?:\.[0-9]+)?)\s*(KiB|MiB|kB|B|kb|KB)?", video_info, re.IGNORECASE)
        if m_video_size:
            total_bytes += parse_size_value(m_video_size.group(1), m_video_size.group(2))
        if m_audio_size:
            total_bytes += parse_size_value(m_audio_size.group(1), m_audio_size.group(2))

        m_time = re.search(r"time=\s*([0-9:.]+)", video_info)
        if total_bytes > 0 and m_time:
            secs = _parse_time_to_seconds(m_time.group(1))
            if secs > 0:
                speed_val = total_bytes / secs / 1024.0 / 1024.0
    except Exception:
        pass

    if speed_val is None:
        try:
            m_lsize = re.search(r"Lsize=\s*([0-9]+(?:\.[0-9]+)?)\s*(KiB|kB|MiB|B|kb|KB)?", video_info, re.IGNORECASE)
            m_size = re.search(r"size=\s*([0-9]+(?:\.[0-9]+)?)\s*(KiB|kB|MiB|B|kb|KB)?", video_info, re.IGNORECASE)
            m_time = re.search(r"time=\s*([0-9:.]+)", video_info)
            size_bytes = 0.0
            if m_lsize and m_lsize.group(1).upper() != "N/A":
                size_bytes = parse_size_value(m_lsize.group(1), m_lsize.group(2))
            elif m_size:
                size_bytes = parse_size_value(m_size.group(1), m_size.group(2))
            if size_bytes > 0 and m_time:
                secs = _parse_time_to_seconds(m_time.group(1))
                if secs > 0:
                    speed_val = size_bytes / secs / 1024.0 / 1024.0
        except Exception:
            pass

    if speed_val is None:
        try:
            m_bitrate = re.search(r"bitrate=\s*([0-9.]+)\s*k?bits/s", video_info)
            if m_bitrate:
                kbps = float(m_bitrate.group(1))
                speed_val = kbps / 8.0 / 1024.0
        except Exception:
            pass

    return {
        'resolution': resolution,
        'fps': fps,
        'video_codec': video_codec,
        'audio_codec': audio_codec,
        'speed': speed_val,
    }


def sample_segment_urls(segment_urls: list, limit: int) -> list:
    """
    Sample up to `limit` segment URLs from `segment_urls` evenly across the playlist.
    If `limit` >= len(segment_urls) the original list is returned.
    """
    if not segment_urls:
        return []
    try:
        limit = int(limit) if limit is not None else 0
    except Exception:
        limit = 0
    total = len(segment_urls)
    if limit <= 0 or limit >= total:
        return list(segment_urls)
    if limit == 1:
        return [segment_urls[total // 2]]
    indices = []
    for i in range(limit):
        idx = round(i * (total - 1) / (limit - 1))
        indices.append(idx)
    seen = set()
    sampled = []
    for idx in indices:
        if idx < 0:
            idx = 0
        if idx >= total:
            idx = total - 1
        if idx not in seen:
            seen.add(idx)
            sampled.append(segment_urls[idx])
    return sampled


def get_avg_result(result) -> TestResult:
    delays = [item.get('delay') for item in result if isinstance(item.get('delay'), (int, float)) and item['delay'] >= 0]
    resolutions = [item.get('resolution') for item in result if item.get('resolution')]
    best = max(result, key=lambda item: item.get('speed') or 0)
    averaged = {
        'speed': sum(item.get('speed') or 0 for item in result) / len(result),
        'delay': int(sum(delays) / len(delays)) if delays else -1,
        'resolution': max(resolutions, key=get_resolution_value) if resolutions else None,
    }
    for key in ('fps', 'video_codec', 'audio_codec'):
        if best.get(key) is not None:
            averaged[key] = best[key]
    return averaged


def get_speed_result(key: str) -> TestResult:
    """
    Get the speed result of the url
    """
    if key in cache:
        return get_avg_result(cache[key])
    else:
        return {'speed': 0, 'delay': -1, 'resolution': None}


async def get_speed(data, headers=None, ipv6_proxy=None, filter_resolution=open_filter_resolution,
                    timeout=speed_test_timeout, logger=None, callback=None, session: Any = None,
                    http_semaphore=None, probe_semaphore=None) -> TestResult:
    """
    Get the speed (response time and resolution) of the url
    """
    url = data['url']
    resolution = data['resolution']
    result: TestResult = {'speed': 0, 'delay': -1, 'resolution': resolution}
    headers = {**request_headers, **(headers or {})}
    try:
        cache_key = data['host'] if speed_test_filter_host else url
        if cache_key and cache_key in cache:
            result = get_avg_result(cache[cache_key])
        else:
            if data['ipv_type'] == "ipv6" and ipv6_proxy:
                result.update(default_ipv6_result)
            elif constants.rt_url_pattern.match(url) is not None:
                async with _limit(probe_semaphore):
                    start_time = time()
                    ff_out = await ffmpeg_url(url, headers, timeout)
                    if ff_out:
                        try:
                            parsed = get_video_info(ff_out)
                            if parsed:
                                result['delay'] = int(round((time() - start_time) * 1000))
                                result['speed'] = parsed['speed']
                                result['resolution'] = parsed['resolution']
                                result['fps'] = parsed['fps']
                                result['video_codec'] = parsed['video_codec']
                                result['audio_codec'] = parsed['audio_codec']
                        except Exception:
                            pass
            else:
                result.update(await get_result(
                    url,
                    headers,
                    resolution,
                    filter_resolution,
                    timeout,
                    session=session,
                    http_semaphore=http_semaphore,
                    probe_semaphore=probe_semaphore,
                ))
            if cache_key:
                cache.setdefault(cache_key, []).append(result)
    except Exception:
        pass
    finally:
        if callback:
            callback()
        if logger:
            origin = data.get('origin')
            origin_name = t(f"name.{origin}") if origin else origin
            logger.info(
                f"ID: {data.get('id')}, {t('name.name')}: {data.get('name')}, {t('pbar.url')}: {data.get('url')}, {t('name.from')}: {origin_name}, {t('name.ipv_type')}: {data.get('ipv_type')}, {t('name.location')}: {data.get('location')}, {t('name.isp')}: {data.get('isp')}, {t('name.delay')}: {result.get('delay') or -1} ms, {t('name.speed')}: {result.get('speed') or 0:.2f} M/s, {t('name.resolution')}: {result.get('resolution')}, {t('name.fps')}: {result.get('fps') or t('name.unknown')}, {t('name.video_codec')}: {result.get('video_codec') or t('name.unknown')}, {t('name.audio_codec')}: {result.get('audio_codec') or t('name.unknown')}"
            )
    return result


def get_sort_result(
        results,
        supply=open_supply,
        filter_speed=open_filter_speed,
        min_speed=min_speed_value,
        filter_resolution=open_filter_resolution,
        min_resolution=min_resolution_value,
        max_resolution=max_resolution_value,
        ipv6_support=True
) -> list[ChannelTestResult]:
    """
    get the sort result
    """
    total_result = []
    for result in results:
        if not ipv6_support and result["ipv_type"] == "ipv6":
            result.update(default_ipv6_result)
        result_speed, result_delay, resolution = (
            result.get("speed") or 0,
            result.get("delay"),
            result.get("resolution")
        )
        if result_delay == -1:
            continue
        if not supply:
            if filter_speed and result_speed < resolution_speed_map.get(resolution, min_speed):
                continue
            if filter_resolution and resolution:
                resolution_value = get_resolution_value(resolution)
                if resolution_value < min_resolution or resolution_value > max_resolution:
                    continue
        total_result.append(result)

    def sort_key(item):
        keys = []
        for dim in sort_by:
            if dim == "speed":
                keys.append(-(item.get("speed") or 0))
            elif dim == "delay":
                delay = item.get("delay")
                keys.append(delay if isinstance(delay, (int, float)) and delay >= 0 else float("inf"))
            elif dim == "resolution":
                keys.append(-(get_resolution_value(item.get("resolution") or "") or 0))
        return tuple(keys)

    total_result.sort(key=sort_key)
    return total_result


def clear_cache():
    """
    Clear the speed test cache
    """
    global cache
    cache = {}
