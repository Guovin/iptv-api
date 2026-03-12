import asyncio
import json


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
            '-show_format',
            '-show_streams',
            '-print_format', 'json',
        ]
        if header_str:
            args += ['-headers', header_str]
        args += [url]

        proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        if out:
            data = json.loads(out.decode('utf-8'))
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
    except Exception:
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
    finally:
        if proc:
            try:
                await proc.wait()
            except Exception:
                pass
    return None


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
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
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
    finally:
        if proc:
            try:
                await proc.wait()
            except Exception:
                pass
    return None
