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
from utils.tools import is_ipv6, remove_cache_info, get_resolution_value

http.cookies._is_legal_key = lambda _: True


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


async def get_speed_m3u8(url: str, filter_resolution: bool = config.open_filter_resolution,
                         timeout: int = config.sort_timeout) -> dict[str, float | None]:
    """
    Get the speed of the m3u8 url with a total timeout
    """
    info = {'speed': None, 'delay': None, 'resolution': None}
    location = None
    try:
        url = quote(url, safe=':/?$&=@[]%').partition('$')[0]
        async with ClientSession(connector=TCPConnector(ssl=False), trust_env=True) as session:
            headers = await get_m3u8_headers(url, session)
            location = headers.get('Location')
            if location:
                info.update(await get_speed_m3u8(location, filter_resolution, timeout))
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
        if filter_resolution and not location and info['delay'] is not None:
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
        url = url_info[0]
        video_info = await ffmpeg_url(url)
        if video_info is None:
            return -1
        frame, resolution = get_video_info(video_info)
        if frame is None or frame == -1:
            return -1
        url_info[2] = resolution
        return url_info, frame
    except Exception as e:
        print(e)
        return -1


cache = {}


async def get_speed(url, ipv6_proxy=None, filter_resolution=config.open_filter_resolution,
                    min_resolution=config.min_resolution_value, timeout=config.sort_timeout,
                    callback=None):
    """
    Get the speed (response time and resolution) of the url
    """
    data = {'speed': None, 'delay': None, 'resolution': None}
    try:
        cache_key = None
        url_is_ipv6 = is_ipv6(url)
        if "$" in url:
            url, _, cache_info = url.partition("$")
            matcher = re.search(r"cache:(.*)", cache_info)
            if matcher:
                cache_key = matcher.group(1)
        if cache_key in cache:
            cache_list = cache[cache_key]
            for cache_item in cache_list:
                if cache_item['speed'] > 0 and cache_item['delay'] != -1 and get_resolution_value(
                        cache_item['resolution']) > min_resolution:
                    return cache_item
        if ipv6_proxy and url_is_ipv6:
            data['speed'] = float("inf")
            data['delay'] = 0
            data['resolution'] = "1920x1080"
        elif re.match(constants.rtmp_url_pattern, url) is not None:
            start_time = time()
            data['resolution'] = await get_resolution_ffprobe(url, timeout)
            data['delay'] = int(round((time() - start_time) * 1000))
            data['speed'] = float("inf") if data['resolution'] is not None else 0
        else:
            data.update(await get_speed_m3u8(url, filter_resolution, timeout))
        if cache_key:
            cache.setdefault(cache_key, []).append(data)
        return data
    except:
        return data
    finally:
        if callback:
            callback()


def sort_urls_key(item):
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
              logger=None):
    """
    Sort the urls with info
    """
    filter_data = []
    for url, date, resolution, origin in data:
        result = {
            "url": remove_cache_info(url),
            "date": date,
            "delay": None,
            "speed": None,
            "resolution": resolution,
            "origin": origin
        }
        if origin == "whitelist":
            filter_data.append(result)
            continue
        cache_key_match = re.search(r"cache:(.*)", url.partition("$")[2])
        cache_key = cache_key_match.group(1) if cache_key_match else None
        if cache_key and cache_key in cache:
            cache_list = cache[cache_key]
            if cache_list:
                avg_speed = sum(item['speed'] or 0 for item in cache_list) / len(cache_list)
                avg_delay = max(int(sum(item['delay'] or -1 for item in cache_list) / len(cache_list)), -1)
                resolution = max((item['resolution'] for item in cache_list), key=get_resolution_value) or resolution
                try:
                    if logger:
                        logger.info(
                            f"Name: {name}, URL: {result["url"]}, Date: {date}, Delay: {avg_delay} ms, Speed: {avg_speed:.2f} M/s, Resolution: {resolution}"
                        )
                except Exception as e:
                    print(e)
                if (not supply and filter_speed and avg_speed < min_speed) or (
                        not supply and filter_resolution and get_resolution_value(resolution) < min_resolution) or (
                        supply and avg_delay < 0):
                    continue
                result["delay"] = avg_delay
                result["speed"] = avg_speed
                result["resolution"] = resolution
                filter_data.append(result)
    filter_data.sort(key=sort_urls_key, reverse=True)
    return [
        (item["url"], item["date"], item["resolution"], item["origin"])
        for item in filter_data
    ]
