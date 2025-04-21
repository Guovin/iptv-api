import asyncio
import http.cookies
import json
import re
import subprocess
from time import time
from urllib.parse import quote, urljoin

import m3u8
from aiohttp import ClientSession, TCPConnector
from multidict import CIMultiDictProxy

import utils.constants as constants
from utils.config import config
from utils.tools import get_resolution_value
from utils.types import TestResult, ChannelTestResult, TestResultCacheData, ChannelData

http.cookies._is_legal_key = lambda _: True
cache: TestResultCacheData = {}
sort_timeout = config.sort_timeout
sort_duplicate_limit = config.sort_duplicate_limit
open_filter_resolution = config.open_filter_resolution
min_resolution_value = config.min_resolution_value
max_resolution_value = config.max_resolution_value
open_supply = config.open_supply
open_filter_speed = config.open_filter_speed
min_speed_value = config.min_speed
m3u8_headers = ['application/x-mpegurl', 'application/vnd.apple.mpegurl', 'audio/mpegurl', 'audio/x-mpegurl']
default_ipv6_delay = 0.1
default_ipv6_resolution = "1920x1080"


async def get_speed_with_download(url: str, headers: dict = None, session: ClientSession = None,
                                  timeout: int = sort_timeout) -> dict[
    str, float | None]:
    """
    Get the speed of the url with a total timeout
    """
    start_time = time()
    delay = None
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
                          timeout: int = sort_timeout) -> str:
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
                     timeout: int = sort_timeout) -> dict[str, float | None]:
    """
    Get the test result of the url
    """
    info = {'speed': None, 'delay': None, 'resolution': resolution}
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
                if not url_content:
                    raise Exception("Unable to get url content")
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
                    if res_headers.get('Content-Length'):
                        res_info = await get_speed_with_download(url, headers, session, timeout)
                        info.update({'speed': res_info['speed'], 'delay': res_info['delay']})
                    raise Exception("Segment urls not found")
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
        if not resolution and filter_resolution and not location and info['delay'] is not None:
            info['resolution'] = await get_resolution_ffprobe(url, headers, timeout)
        return info


async def get_delay_requests(url, timeout=sort_timeout, proxy=None):
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


async def ffmpeg_url(url, timeout=sort_timeout):
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


async def get_resolution_ffprobe(url: str, headers: dict = None, timeout: int = sort_timeout) -> str | None:
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


def get_avg_result(result, default_resolution=0) -> TestResult:
    return {
        'speed': sum(item['speed'] or 0 for item in result) / len(result),
        'delay': max(
            int(sum(item['delay'] or -1 for item in result) / len(result)), -1),
        'resolution': max((item['resolution'] for item in result), key=get_resolution_value) or default_resolution
    }


async def get_speed(url, headers=None, cache_key=None, is_ipv6=False, ipv6_proxy=None, resolution=None,
                    filter_resolution=open_filter_resolution, timeout=sort_timeout, callback=None) -> TestResult:
    """
    Get the speed (response time and resolution) of the url
    """
    data: TestResult = {'speed': None, 'delay': None, 'resolution': resolution}
    try:
        if cache_key in cache and len(cache[cache_key]) >= sort_duplicate_limit:
            data = get_avg_result(cache[cache_key], resolution)
        else:
            if is_ipv6 and ipv6_proxy:
                data['speed'] = float("inf")
                data['delay'] = default_ipv6_delay
                data['resolution'] = default_ipv6_resolution
            elif constants.rt_url_pattern.match(url) is not None:
                start_time = time()
                if not data['resolution'] and filter_resolution:
                    data['resolution'] = await get_resolution_ffprobe(url, headers, timeout)
                data['delay'] = int(round((time() - start_time) * 1000))
                data['speed'] = float("inf") if data['resolution'] is not None else 0
            else:
                data.update(await get_result(url, headers, resolution, filter_resolution, timeout))
            if cache_key:
                cache.setdefault(cache_key, []).append(data)
    finally:
        if callback:
            callback()
        return data


def sort_urls_key(item: TestResult | ChannelData) -> float:
    """
    Sort the urls with key
    """
    speed, origin = item["speed"], item["origin"]
    if origin in ["whitelist", "live", "hls"]:
        return float("inf")
    else:
        return speed


def sort_urls(name, data, supply=open_supply, filter_speed=open_filter_speed, min_speed=min_speed_value,
              filter_resolution=open_filter_resolution, min_resolution=min_resolution_value,
              max_resolution=max_resolution_value, logger=None) -> list[ChannelTestResult]:
    """
    Sort the urls with info
    """
    filter_data = []
    for item in data:
        host, date, resolution, origin, ipv_type = (
            item["host"],
            item["date"],
            item["resolution"],
            item["origin"],
            item["ipv_type"]
        )
        result: ChannelTestResult = {
            **item,
            "delay": None,
            "speed": None,
        }
        if origin in ["whitelist", "live", "hls"]:
            filter_data.append(result)
            continue
        if host and host in cache:
            cache_list = cache[host]
            if cache_list:
                avg_result = get_avg_result(cache_list, resolution)
                avg_speed, avg_delay, resolution = avg_result["speed"], avg_result["delay"], avg_result["resolution"]
                try:
                    if logger:
                        logger.info(
                            f"Name: {name}, URL: {result["url"]}, IPv_Type: {ipv_type}, Date: {date}, Delay: {avg_delay} ms, Speed: {avg_speed:.2f} M/s, Resolution: {resolution}"
                        )
                except Exception as e:
                    print(e)
                if avg_delay < 0:
                    continue
                if not supply:
                    if filter_speed and avg_speed < min_speed:
                        continue
                    if filter_resolution and resolution:
                        resolution_value = get_resolution_value(resolution)
                        if resolution_value < min_resolution or resolution_value > max_resolution:
                            continue
                result["delay"] = avg_delay
                result["speed"] = avg_speed
                result["resolution"] = resolution
                filter_data.append(result)
    filter_data.sort(key=sort_urls_key, reverse=True)
    return filter_data
