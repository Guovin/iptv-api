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
from utils.i18n import t
from utils.requests.tools import headers as request_headers
from utils.tools import get_resolution_value
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

min_measure_time = 1.0
stability_window = 4
stability_threshold = 0.12


async def get_speed_with_download(url: str, headers: dict = None, session: ClientSession = None,
                                  timeout: int = speed_test_timeout) -> dict[str, float | None]:
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

    speed_samples: list[float] = []
    try:
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
                        window = speed_samples[-stability_window:]
                        mean = sum(window) / len(window)
                        if mean > 0 and (max(window) - min(window)) / mean < stability_threshold:
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
        total_time = time() - start_time
        if created_session:
            await session.close()
        speed_value = total_size / total_time / 1024 / 1024 if total_time > 0 else 0.0
        return {
            'speed': speed_value,
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


def _try_extract_speed_from_ffmpeg_output(output: str) -> float | None:
    """
    Try to extract speed from ffmpeg output
    """

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

    try:
        total_bytes = 0.0
        m_video = re.search(r"video:\s*([0-9]+(?:\.[0-9]+)?)\s*(KiB|MiB|kB|B|kb|KB)?", output, re.IGNORECASE)
        m_audio = re.search(r"audio:\s*([0-9]+(?:\.[0-9]+)?)\s*(KiB|MiB|kB|B|kb|KB)?", output, re.IGNORECASE)
        if m_video:
            total_bytes += parse_size_value(m_video.group(1), m_video.group(2))
        if m_audio:
            total_bytes += parse_size_value(m_audio.group(1), m_audio.group(2))

        m_time = re.search(r"time=\s*([0-9:\.]+)", output)
        if total_bytes > 0 and m_time:
            secs = _parse_time_to_seconds(m_time.group(1))
            if secs > 0:
                return total_bytes / secs / 1024.0 / 1024.0
    except Exception:
        pass

    try:
        m_lsize = re.search(r"Lsize=\s*([0-9]+(?:\.[0-9]+)?)\s*(KiB|kB|MiB|B|kb|KB)?", output, re.IGNORECASE)
        m_size = re.search(r"size=\s*([0-9]+(?:\.[0-9]+)?)\s*(KiB|kB|MiB|B|kb|KB)?", output, re.IGNORECASE)
        m_time = re.search(r"time=\s*([0-9:\.]+)", output)
        size_bytes = 0.0
        if m_lsize and m_lsize.group(1).upper() != "N/A":
            size_bytes = parse_size_value(m_lsize.group(1), m_lsize.group(2))
        elif m_size:
            size_bytes = parse_size_value(m_size.group(1), m_size.group(2))
        if size_bytes > 0 and m_time:
            secs = _parse_time_to_seconds(m_time.group(1))
            if secs > 0:
                return size_bytes / secs / 1024.0 / 1024.0
    except Exception:
        pass

    try:
        m_bitrate = re.search(r"bitrate=\s*([0-9\.]+)\s*k?bits/s", output)
        if m_bitrate:
            kbps = float(m_bitrate.group(1))
            return kbps / 8.0 / 1024.0
    except Exception:
        pass

    return None


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
                start_time = time()
                tasks = [get_speed_with_download(ts_url, headers, session, timeout) for ts_url in segment_urls[:5]]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                total_size = sum(result['size'] for result in results if isinstance(result, dict))
                total_time = sum(result['time'] for result in results if isinstance(result, dict))
                info['speed'] = total_size / total_time / 1024 / 1024 if total_time > 0 else 0
                info['delay'] = int(round((time() - start_time) * 1000))
                try:
                    if round(info['speed'], 2) == 0 and info['delay'] != -1:
                        ff_out = await ffmpeg_url(url, headers, timeout)
                        if ff_out:
                            parsed_speed = _try_extract_speed_from_ffmpeg_output(ff_out)
                            if parsed_speed is not None and parsed_speed > 0:
                                info['speed'] = parsed_speed
                            try:
                                _, parsed_resolution = get_video_info(ff_out)
                                if parsed_resolution:
                                    info['resolution'] = parsed_resolution
                            except Exception:
                                pass
                except Exception:
                    pass
    except:
        pass
    finally:
        if not info['resolution'] and filter_resolution and not location and info['delay'] != -1:
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
        if status:
            print(t("msg.ffmpeg_installed"))
        else:
            print(t("msg.ffmpeg_not_installed"))
        return status


async def ffmpeg_url(url, headers=None, timeout=speed_test_timeout):
    """
    Get the ffmpeg output of the url
    """
    headers_str = "".join(f"{k}: {v}\r\n" for k, v in headers.items())

    args = ["ffmpeg", "-t", str(timeout)]
    if headers_str:
        args += ["-headers", headers_str]
    args += ["-http_persistent", "0", "-stats", "-i", url, "-f", "null", "-"]

    proc = None
    stderr_parts: list[bytes] = []
    speed_samples: list[float] = []
    bitrate_re = re.compile(r"bitrate=\s*([0-9\.]+)\s*k?bits/s", re.IGNORECASE)
    start = time()

    try:
        proc = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        while True:
            try:
                line = await asyncio.wait_for(proc.stderr.readline(), timeout=0.5)
            except asyncio.TimeoutError:
                line = b''
            now = time()
            elapsed = now - start

            if line == b'':
                if proc.returncode is None:
                    if elapsed >= timeout:
                        proc.kill()
                        await proc.wait()
                        break
                    await asyncio.sleep(0)
                    if proc.returncode is not None:
                        break
                    continue
                else:
                    break

            stderr_parts.append(line)

            try:
                text = line.decode(errors="ignore")
            except Exception:
                text = ""

            m = bitrate_re.search(text)
            if m:
                try:
                    kbps = float(m.group(1))
                    mbps = kbps / 8.0 / 1024.0
                    speed_samples.append(mbps)
                except Exception:
                    pass

            if elapsed >= min_measure_time and len(speed_samples) >= stability_window:
                window = speed_samples[-stability_window:]
                mean = sum(window) / len(window)
                if mean > 0 and (max(window) - min(window)) / mean < stability_threshold:
                    try:
                        proc.kill()
                    except Exception:
                        pass
                    await proc.wait()
                    break

        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=1)
            if err:
                stderr_parts.append(err)
            if out:
                stderr_parts.append(out)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
            await proc.wait()
    except asyncio.TimeoutError:
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
            await proc.wait()
    except Exception:
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
            await proc.wait()
    finally:
        stderr_bytes = b"".join(stderr_parts)
        try:
            return stderr_bytes.decode(errors="ignore")
        except Exception:
            return None


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
                    timeout=speed_test_timeout, logger=None, callback=None) -> TestResult:
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
        if logger:
            logger.info(
                f"Name: {data.get('name')}, URL: {data.get('url')}, From: {data.get('origin')}, IPv_Type: {data.get("ipv_type")}, Location: {data.get('location')}, ISP: {data.get('isp')}, Date: {data["date"]}, Delay: {result.get('delay') or -1} ms, Speed: {result.get('speed') or 0:.2f} M/s, Resolution: {result.get('resolution')}"
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


def clear_cache():
    """
    Clear the speed test cache
    """
    global cache
    cache = {}
