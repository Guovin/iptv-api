import asyncio
import json
import subprocess


def _parse_probe_data(data: dict) -> dict | None:
    """
    Parse ffprobe JSON dict and return metadata dict with keys:
    video_codec, audio_codec, resolution, fps
    """
    if not data:
        return None
    streams = data.get('streams', [])
    video = None
    audio = None
    for s in streams:
        if s.get('codec_type') == 'video' and video is None:
            video = s
        elif s.get('codec_type') == 'audio' and audio is None:
            audio = s

    def _safe_get(d, key, default=None):
        if not d:
            return default
        return d.get(key, default)

    def _parse_rate(rate_str):
        try:
            if not rate_str:
                return None
            if isinstance(rate_str, (int, float)):
                return float(rate_str)
            if '/' in rate_str:
                num, den = rate_str.split('/')
                return float(num) / float(den) if float(den) != 0 else None
            return float(rate_str)
        except Exception:
            return None

    frame_rate_val = _parse_rate(_safe_get(video, 'avg_frame_rate') or _safe_get(video, 'r_frame_rate'))

    res = None
    try:
        w = _safe_get(video, 'width')
        h = _safe_get(video, 'height')
        if w and h:
            res = f"{w}x{h}"
    except Exception:
        res = None

    meta = {
        'video_codec': _safe_get(video, 'codec_name'),
        'audio_codec': _safe_get(audio, 'codec_name'),
        'resolution': res,
        'fps': frame_rate_val,
    }

    return meta


async def probe_url(url: str, headers: dict = None, timeout: int = 10) -> dict | None:
    """
    Use ffprobe to get metadata for the first video and audio streams.
    Returns a dict with keys: video_codec, audio_codec, resolution, fps
    """
    proc = None
    try:
        header_str = ''.join(f'{k}: {v}\r\n' for k, v in (headers or {}).items()) if headers else ''
        args = [
            'ffprobe',
            '-v', 'error',
            '-probesize', '512000',
            '-analyzeduration', '1000000',
            '-show_entries',
            'stream=codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate',
            '-print_format', 'json',
        ]
        if header_str:
            args += ['-headers', header_str]
        args += [url]

        proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                await proc.wait()
            except Exception:
                pass
            return None
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                await proc.wait()
            except Exception:
                pass
            return None

        if out:
            try:
                data = json.loads(out.decode('utf-8'))
                meta = _parse_probe_data(data)
                if meta:
                    return meta
            except Exception:
                pass
    except Exception:
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                await proc.wait()
            except Exception:
                pass
    finally:
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                await proc.wait()
            except Exception:
                pass
    return None


def probe_url_sync(url: str, headers: dict = None, timeout: int = 10) -> dict | None:
    """
    Synchronous wrapper around ffprobe to obtain metadata for the first video and audio streams.
    This uses subprocess.run and returns the same dict structure as the async `probe_url`.
    """
    header_str = ''.join(f'{k}: {v}\r\n' for k, v in (headers or {}).items()) if headers else ''
    args = [
        'ffprobe',
        '-v', 'error',
        '-show_format',
        '-show_streams',
        '-print_format', 'json',
    ]
    if header_str:
        args += ['-headers', header_str]
    args += [url]

    try:
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    except FileNotFoundError:
        return None
    except Exception:
        return None

    out = (res.stdout or '').strip()
    err = (res.stderr or '').strip()

    candidate = out if out else err
    if not candidate:
        return None

    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        idx = candidate.find('{')
        if idx == -1:
            return None
        try:
            data = json.loads(candidate[idx:])
        except Exception:
            return None
    except Exception:
        return None

    return _parse_probe_data(data)


async def get_resolution_ffprobe(url: str, headers: dict = None, timeout: int = 10) -> str | None:
    """
    Use ffprobe to get width and height of the first video stream and return as 'WIDTHxHEIGHT', or None if not found.
    """
    proc = None
    try:
        header_str = ''.join(f'{k}: {v}\r\n' for k, v in (headers or {}).items()) if headers else ''
        args = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-print_format', 'json',
        ]
        if header_str:
            args += ['-headers', header_str]
        args += [url]

        proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                await proc.wait()
            except Exception:
                pass
            return None
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                await proc.wait()
            except Exception:
                pass
            return None

        if out:
            j = json.loads(out.decode('utf-8'))
            streams = j.get('streams') or []
            if streams:
                s = streams[0]
                w = s.get('width')
                h = s.get('height')
                if w and h:
                    return f"{w}x{h}"
    except Exception:
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                await proc.wait()
            except Exception:
                pass
    finally:
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                await proc.wait()
            except Exception:
                pass
    return None
