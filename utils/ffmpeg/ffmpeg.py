import asyncio
import re
import subprocess
from time import time

from utils.i18n import t

min_measure_time = 1.0
stability_window = 4
stability_threshold = 0.12


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


async def ffmpeg_url(url, headers=None, timeout=10):
    """
    Async wrapper that runs ffmpeg similar to old implementation and returns stderr output as text.
    """
    headers_str = "".join(f"{k}: {v}\r\n" for k, v in (headers or {}).items())

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
        proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)

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
