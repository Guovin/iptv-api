import asyncio
import http.cookies
import json
import re
import subprocess
from time import time
from urllib.parse import quote, urlparse

import m3u8
from aiohttp import ClientSession, TCPConnector
from multidict import CIMultiDictProxy

import utils.constants as constants
from utils.config import config
from utils.tools import get_resolution_value
from utils.types import TestResult, ChannelTestResult, TestResultCacheData

http.cookies._is_legal_key = lambda _: True
cache: TestResultCacheData = {}


async def get_speed_with_download(url: str, session: ClientSession = None, timeout: int = config.sort_timeout) -> dict[
    str, float | None]:
    """
    Get the speed of the url with a total timeout
    """
    start_time = time()
    total_size = 0
    total_time = 0
    info = {'speed': None, 'delay': None}
    if session is None:
        session = ClientSession(connector=TCPConnector(ssl=False), trust_env=True)
        created_session = True
    else:
        created_session = False
    try:
        async with session.get(url, timeout=timeout) as response:
            if response.status != 200:
                raise Exception("Invalid response")
            info['delay'] = int(round((time() - start_time) * 1000))
            async for chunk in response.content.iter_any():
                if chunk:
                    total_size += len(chunk)
    except:
        pass
    finally:
        if total_size > 0:
            total_time += time() - start_time
            info['speed'] = ((total_size / total_time) if total_time > 0 else 0) / 1024 / 1024
        if created_session:
            await session.close()
        return info


async def get_m3u8_headers(url: str, session: ClientSession = None, timeout: int = 5) -> CIMultiDictProxy[str] | dict[
    any, any]:
    """
    Get the headers of the m3u8 url
    """
    if session is None:
        session = ClientSession(connector=TCPConnector(ssl=False), trust_env=True)
        created_session = True
    else:
        created_session = False
    headers = {}
    try:
        async with session.head(url, timeout=timeout) as response:
            headers = response.headers
    except:
        pass
    finally:
        if created_session:
            await session.close()
        return headers


def check_m3u8_valid(headers: CIMultiDictProxy[str] | dict[any, any]) -> bool:
    """
    Check if the m3u8 url is valid
    """
    content_type = headers.get('Content-Type', '').lower()
    if not content_type:
        return False
    return any(item in content_type for item in ['application/vnd.apple.mpegurl', 'audio/mpegurl', 'audio/x-mpegurl'])


async def get_speed_m3u8(url: str, resolution: str = None, filter_resolution: bool = config.open_filter_resolution,
                         timeout: int = config.sort_timeout) -> dict[str, float | None]:
    """
    Get the speed of the m3u8 url with a total timeout
    """
    info = {'speed': None, 'delay': None, 'resolution': resolution}
    location = None
    try:
        url = quote(url, safe=':/?$&=@[]%').partition('$')[0]
        async with ClientSession(connector=TCPConnector(ssl=False), trust_env=True) as session:
            headers = await get_m3u8_headers(url, session)
            location = headers.get('Location')
            if location:
                info.update(await get_speed_m3u8(location, resolution, filter_resolution, timeout))
            elif check_m3u8_valid(headers):
                m3u8_obj = m3u8.load(url, timeout=2)
                playlists = m3u8_obj.data.get('playlists')
                segments = m3u8_obj.segments
                if not segments and playlists:
                    parsed_url = urlparse(url)
                    uri = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/', 1)[0]}/{playlists[0].get('uri', '')}"
                    uri_headers = await get_m3u8_headers(uri, session)
                    if not check_m3u8_valid(uri_headers):
                        if uri_headers.get('Content-Length'):
                            info.update(await get_speed_with_download(uri, session, timeout))
                        raise Exception("Invalid m3u8")
                    m3u8_obj = m3u8.load(uri, timeout=2)
                    segments = m3u8_obj.segments
                if not segments:
                    raise Exception("Segments not found")
                ts_urls = [segment.absolute_uri for segment in segments]
                speed_list = []
                start_time = time()
                for ts_url in ts_urls:
                    if time() - start_time > timeout:
                        break
                    download_info = await get_speed_with_download(ts_url, session, timeout)
                    speed_list.append(download_info['speed'])
                    if info['delay'] is None and download_info['delay'] is not None:
                        info['delay'] = download_info['delay']
                info['speed'] = (sum(speed_list) / len(speed_list)) if speed_list else 0
            elif headers.get('Content-Length'):
                info.update(await get_speed_with_download(url, session, timeout))
    except:
        pass
    finally:
        if not resolution and filter_resolution and not location and info['delay'] is not None:
            info['resolution'] = await get_resolution_ffprobe(url, timeout)
        return info


async def get_delay_requests(url, timeout=config.sort_timeout, proxy=None):
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


async def ffmpeg_url(url, timeout=config.sort_timeout):
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


async def get_resolution_ffprobe(url: str, timeout: int = config.sort_timeout) -> str | None:
    """
    Get the resolution of the url by ffprobe
    """
    resolution = None
    proc = None
    try:
        probe_args = [
            'ffprobe',
            '-v', 'error',
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


async def get_speed(url, cache_key=None, is_ipv6=False, ipv6_proxy=None, resolution=None,
                    filter_resolution=config.open_filter_resolution,
                    min_resolution=config.min_resolution_value, timeout=config.sort_timeout,
                    callback=None) -> TestResult:
    """
    Get the speed (response time and resolution) of the url
    """
    data: TestResult = {'speed': None, 'delay': None, 'resolution': resolution}
    try:
        if cache_key in cache:
            cache_list = cache[cache_key]
            for cache_item in cache_list:
                if cache_item['speed'] > 0 and cache_item['delay'] != -1 and get_resolution_value(
                        cache_item['resolution']) > min_resolution:
                    data = cache_item
                    break
        else:
            if is_ipv6 and ipv6_proxy:
                data['speed'] = float("inf")
                data['delay'] = 0.1
                data['resolution'] = "1920x1080"
            elif constants.rt_url_pattern.match(url) is not None:
                start_time = time()
                if not data['resolution'] and filter_resolution:
                    data['resolution'] = await get_resolution_ffprobe(url, timeout)
                data['delay'] = int(round((time() - start_time) * 1000))
                data['speed'] = float("inf") if data['resolution'] is not None else 0
            else:
                data.update(await get_speed_m3u8(url, resolution, filter_resolution, timeout))
            if cache_key:
                cache.setdefault(cache_key, []).append(data)
    finally:
        if callback:
            callback()
        return data


def sort_urls_key(item: ChannelTestResult) -> float:
    """
    Sort the urls with key
    """
    speed, resolution, origin = item["speed"], item["resolution"], item["origin"]
    if origin == "whitelist":
        return float("inf")
    else:
        return speed + get_resolution_value(resolution)


def sort_urls(name, data, supply=config.open_supply, filter_speed=config.open_filter_speed, min_speed=config.min_speed,
              filter_resolution=config.open_filter_resolution, min_resolution=config.min_resolution_value,
              logger=None) -> list[ChannelTestResult]:
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
        if origin == "whitelist":
            filter_data.append(result)
            continue
        if host and host in cache:
            cache_list = cache[host]
            if cache_list:
                avg_speed: int | float | None = sum(item['speed'] or 0 for item in cache_list) / len(cache_list)
                avg_delay: int | float | None = max(
                    int(sum(item['delay'] or -1 for item in cache_list) / len(cache_list)), -1)
                resolution = max((item['resolution'] for item in cache_list), key=get_resolution_value) or resolution
                try:
                    if logger:
                        logger.info(
                            f"Name: {name}, URL: {result["url"]}, IPv_Type: {ipv_type}, Date: {date}, Delay: {avg_delay} ms, Speed: {avg_speed:.2f} M/s, Resolution: {resolution}"
                        )
                except Exception as e:
                    print(e)
                if avg_delay < 0 or (not supply and ((filter_speed and avg_speed < min_speed) or (
                        filter_resolution and get_resolution_value(resolution) < min_resolution))):
                    continue
                result["delay"] = avg_delay
                result["speed"] = avg_speed
                result["resolution"] = resolution
                filter_data.append(result)
    filter_data.sort(key=sort_urls_key, reverse=True)
    return filter_data
