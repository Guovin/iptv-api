import asyncio
import http.cookies
import json
import re
import subprocess
from logging import INFO
from time import time
from urllib.parse import quote, urljoin

import m3u8
from aiohttp import ClientSession, TCPConnector
from multidict import CIMultiDictProxy

import utils.constants as constants
from utils.config import config
from utils.tools import get_resolution_value, get_logger
from utils.types import TestResult, ChannelTestResult, TestResultCacheData

http.cookies._is_legal_key = lambda _: True
cache: TestResultCacheData = {}
speed_test_timeout = config.speed_test_timeout
speed_test_filter_host = config.speed_test_filter_host
open_filter_resolution = config.open_filter_resolution
min_resolution_value = config.min_resolution_value
max_resolution_value = config.max_resolution_value
open_supply = config.open_supply
open_filter_speed = config.open_filter_speed
min_speed_value = config.min_speed
m3u8_headers = ['application/x-mpegurl', 'application/vnd.apple.mpegurl', 'audio/mpegurl', 'audio/x-mpegurl']
default_ipv6_delay = 0.1
default_ipv6_resolution = "1920x1080"
default_ipv6_result = {
    'speed': float("inf"),
    'delay': default_ipv6_delay,
    'resolution': default_ipv6_resolution
}
logger = get_logger(constants.speed_test_log_path, level=INFO, init=True)


async def get_speed_with_download(url: str, headers: dict = None, session: ClientSession = None,
                                  timeout: int = speed_test_timeout) -> dict[
    str, float | None]:
    """
    Get the speed of the url with a total timeout
    """
    start_time = time()
    delay = -1
    total_size = 0
    if session is None:
        session = ClientSession(connector=TCPConnector(ssl=False), trust_env=True)
        created_session = True
    else:
        created_session = False
    try:
        async with session.get(url, headers=headers, timeout=timeout) as response:
            if response.status != 200:
                raise Exception("Invalid response")
            delay = int(round((time() - start_time) * 1000))
            async for chunk in response.content.iter_any():
                if chunk:
                    total_size += len(chunk)
    except:
        pass
    finally:
        total_time = time() - start_time
        if created_session:
            await session.close()
        return {
            'speed': total_size / total_time / 1024 / 1024,
            'delay': delay,
            'size': total_size,
            'time': total_time,
        }


async def get_headers(url: str, headers: dict = None, session: ClientSession = None, timeout: int = 5) -> \
        CIMultiDictProxy[str] | dict[
            any, any]:
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
        async with session.head(url, headers=headers, timeout=timeout) as response:
            res_headers = response.headers
    except:
        pass
    finally:
        if created_session:
            await session.close()
        return res_headers


async def get_url_content(url: str, headers: dict = None, session: ClientSession = None,
                          timeout: int = speed_test_timeout) -> str:
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
        async with session.get(url, headers=headers, timeout=timeout) as response:
            if response.status == 200:
                content = await response.text()
            else:
                raise Exception("Invalid response")
    except:
        pass
    finally:
        if created_session:
            await session.close()
        return content


def check_m3u8_valid(headers: CIMultiDictProxy[str] | dict[any, any]) -> bool:
    """
    Check if the m3u8 url is valid
    """
    content_type = headers.get('Content-Type', '').lower()
    if not content_type:
        return False
    return any(item in content_type for item in m3u8_headers)


async def get_result(url: str, headers: dict = None, resolution: str = None,
                     filter_resolution: bool = config.open_filter_resolution,
                     timeout: int = speed_test_timeout) -> dict[str, float | None]:
    """
    Get the test result of the url
    """
    info = {'speed': 0, 'delay': -1, 'resolution': resolution}
    location = None
    try:
        url = quote(url, safe=':/?$&=@[]%').partition('$')[0]
        async with ClientSession(connector=TCPConnector(ssl=False), trust_env=True) as session:
            res_headers = await get_headers(url, headers, session)
            location = res_headers.get('Location')
            if location:
                info.update(await get_result(location, headers, resolution, filter_resolution, timeout))
            else:
                url_content = await get_url_content(url, headers, session, timeout)
                if url_content:
                    m3u8_obj = m3u8.loads(url_content)
                    playlists = m3u8_obj.playlists
                    segments = m3u8_obj.segments
                    if playlists:
                        best_playlist = max(m3u8_obj.playlists, key=lambda p: p.stream_info.bandwidth)
                        playlist_url = urljoin(url, best_playlist.uri)
                        playlist_content = await get_url_content(playlist_url, headers, session, timeout)
                        if playlist_content:
                            media_playlist = m3u8.loads(playlist_content)
                            segment_urls = [urljoin(playlist_url, segment.uri) for segment in media_playlist.segments]
                    else:
                        segment_urls = [urljoin(url, segment.uri) for segment in segments]
                    if not segment_urls:
                        raise Exception("Segment urls not found")
                else:
                    res_info = await get_speed_with_download(url, headers, session, timeout)
                    info.update({'speed': res_info['speed'], 'delay': res_info['delay']})
                    raise Exception("No url content, use download with timeout to test")
                start_time = time()
                tasks = [get_speed_with_download(ts_url, headers, session, timeout) for ts_url in segment_urls[:5]]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                total_size = sum(result['size'] for result in results if isinstance(result, dict))
                total_time = sum(result['time'] for result in results if isinstance(result, dict))
                info['speed'] = total_size / total_time / 1024 / 1024 if total_time > 0 else 0
                info['delay'] = int(round((time() - start_time) * 1000))
    except:
        pass
    finally:
        if not resolution and filter_resolution and not location and info['delay'] != -1:
            info['resolution'] = await get_resolution_ffprobe(url, headers, timeout)
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


def check_ffmpeg_installed_status():
    """
    Check ffmpeg is installed
    """
    status = False
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        status = result.returncode == 0
    except FileNotFoundError:
        status = False
    except Exception as e:
        print(e)
    finally:
        return status


async def ffmpeg_url(url, timeout=speed_test_timeout):
    """
    Get url info by ffmpeg
    """
    args = ["ffmpeg", "-t", str(timeout), "-stats", "-i", url, "-f", "null", "-"]
    proc = None
    res = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout + 2)
        if out:
            res = out.decode("utf-8")
        if err:
            res = err.decode("utf-8")
        return None
    except asyncio.TimeoutError:
        if proc:
            proc.kill()
        return None
    except Exception:
        if proc:
            proc.kill()
        return None
    finally:
        if proc:
            await proc.wait()
        return res


async def get_resolution_ffprobe(url: str, headers: dict = None, timeout: int = speed_test_timeout) -> str | None:
    """
    Get the resolution of the url by ffprobe
    """
    resolution = None
    proc = None
    try:
        probe_args = [
            'ffprobe',
            '-v', 'error',
            '-headers', ''.join(f'{k}: {v}\r\n' for k, v in headers.items()) if headers else '',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            "-of", 'json',
            url
        ]
        proc = await asyncio.create_subprocess_exec(*probe_args, stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        out, _ = await asyncio.wait_for(proc.communicate(), timeout)
        video_stream = json.loads(out.decode('utf-8'))["streams"][0]
        resolution = f"{video_stream['width']}x{video_stream['height']}"
    except:
        if proc:
            proc.kill()
    finally:
        if proc:
            await proc.wait()
        return resolution


def get_video_info(video_info):
    """
    Get the video info
    """
    frame_size = -1
    resolution = None
    if video_info is not None:
        info_data = video_info.replace(" ", "")
        matches = re.findall(r"frame=(\d+)", info_data)
        if matches:
            frame_size = int(matches[-1])
        match = re.search(r"(\d{3,4}x\d{3,4})", video_info)
        if match:
            resolution = match.group(0)
    return frame_size, resolution


async def check_stream_delay(url_info):
    """
    Check the stream delay
    """
    try:
        url = url_info["url"]
        video_info = await ffmpeg_url(url)
        if video_info is None:
            return -1
        frame, resolution = get_video_info(video_info)
        if frame is None or frame == -1:
            return -1
        url_info["resolution"] = resolution
        return url_info, frame
    except Exception as e:
        print(e)
        return -1


def get_avg_result(result) -> TestResult:
    return {
        'speed': sum(item['speed'] or 0 for item in result) / len(result),
        'delay': max(
            int(sum(item['delay'] or -1 for item in result) / len(result)), -1),
        'resolution': max((item['resolution'] for item in result), key=get_resolution_value)
    }


def get_speed_result(key: str) -> TestResult:
    """
    Get the speed result of the url
    """
    if key in cache:
        return get_avg_result(cache[key])
    else:
        return {'speed': 0, 'delay': -1, 'resolution': 0}


async def get_speed(data, headers=None, ipv6_proxy=None, filter_resolution=open_filter_resolution,
                    timeout=speed_test_timeout, callback=None) -> TestResult:
    """
    Get the speed (response time and resolution) of the url
    """
    url = data['url']
    resolution = data['resolution']
    result: TestResult = {'speed': 0, 'delay': -1, 'resolution': resolution}
    try:
        cache_key = data['host'] if speed_test_filter_host else url
        if cache_key and cache_key in cache:
            result = get_avg_result(cache[cache_key])
        else:
            if data['ipv_type'] == "ipv6" and ipv6_proxy:
                result.update(default_ipv6_result)
            elif constants.rt_url_pattern.match(url) is not None:
                start_time = time()
                if not result['resolution'] and filter_resolution:
                    result['resolution'] = await get_resolution_ffprobe(url, headers, timeout)
                result['delay'] = int(round((time() - start_time) * 1000))
                if result['resolution'] is not None:
                    result['speed'] = float("inf")
            else:
                result.update(await get_result(url, headers, resolution, filter_resolution, timeout))
            if cache_key:
                cache.setdefault(cache_key, []).append(result)
    finally:
        if callback:
            callback()
        logger.info(
            f"Name: {data.get('name')}, URL: {data.get('url')}, IPv_Type: {data.get("ipv_type")}, Location: {data.get('location')}, ISP: {data.get('isp')}, Date: {data["date"]}, Delay: {result.get('delay') or -1} ms, Speed: {result.get('speed') or 0:.2f} M/s, Resolution: {result.get('resolution')}"
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
            if filter_speed and result_speed < min_speed:
                continue
            if filter_resolution and resolution:
                resolution_value = get_resolution_value(resolution)
                if resolution_value < min_resolution or resolution_value > max_resolution:
                    continue
        total_result.append(result)
    total_result.sort(key=lambda item: item.get("speed") or 0, reverse=True)
    return total_result
