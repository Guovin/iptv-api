import atexit
import ctypes
import json
import os
import signal
import subprocess
import sys
import threading
import time
from collections import OrderedDict
from functools import lru_cache

import utils.constants as constants
from utils.config import config
from utils.db import ensure_result_data_schema
from utils.db import get_db_connection, return_db_connection
from utils.ffmpeg import probe_url_sync
from utils.i18n import t
from utils.tools import join_url, resource_path, render_nginx_conf

nginx_dir = resource_path(os.path.join('utils', 'nginx-rtmp-win32'))
nginx_conf_template = resource_path(os.path.join(nginx_dir, 'conf', 'nginx.conf.template'))
nginx_conf = resource_path(os.path.join(nginx_dir, 'conf', 'nginx.conf'))
nginx_path = resource_path(os.path.join(nginx_dir, 'nginx.exe'))
stop_path = resource_path(os.path.join(nginx_dir, 'stop.bat'))
app_rtmp_url = f"rtmp://127.0.0.1:{config.nginx_rtmp_port}"

hls_running_streams = OrderedDict()
STREAMS_LOCK = threading.Lock()
hls_last_access = {}
hls_starting_streams = set()
hls_starting_processes = {}
HLS_IDLE_TIMEOUT = config.rtmp_idle_timeout
HLS_WAIT_TIMEOUT = 30
HLS_WAIT_INTERVAL = 0.5
MAX_STREAMS = config.rtmp_max_streams
nginx_dir = resource_path(os.path.join('utils', 'nginx-rtmp-win32'))
hls_temp_path = resource_path(os.path.join(nginx_dir, 'temp', 'hls')) if sys.platform == "win32" else '/tmp/hls'

_hls_monitor_started_evt = threading.Event()
_hls_monitor_lock = threading.Lock()
_libc = ctypes.CDLL(None) if sys.platform.startswith("linux") else None


def _reserve_stream(channel_id):
    victims = []
    with STREAMS_LOCK:
        for running_channel_id, running_process in list(hls_running_streams.items()):
            if running_process.poll() is not None:
                hls_running_streams.pop(running_channel_id, None)
                hls_last_access.pop(running_channel_id, None)
        existing = hls_running_streams.get(channel_id)
        if existing and existing.poll() is None:
            hls_last_access[channel_id] = time.time()
            hls_running_streams.move_to_end(channel_id)
            return existing, False
        if existing:
            hls_running_streams.pop(channel_id, None)
            hls_last_access.pop(channel_id, None)
        if channel_id in hls_starting_streams:
            return None, False
        if MAX_STREAMS <= 0:
            return None, False

        while len(hls_running_streams) + len(hls_starting_streams) >= MAX_STREAMS:
            if not hls_running_streams:
                return None, False
            oldest_channel_id, oldest_process = hls_running_streams.popitem(last=False)
            hls_last_access.pop(oldest_channel_id, None)
            victims.append(oldest_process)
        hls_starting_streams.add(channel_id)

    for process in victims:
        _terminate_process_safe(process)
    return None, True


def _release_stream_reservation(channel_id):
    with STREAMS_LOCK:
        hls_starting_streams.discard(channel_id)
        process = hls_starting_processes.pop(channel_id, None)
    if process and process.poll() is None:
        _terminate_process_safe(process)


def _set_parent_death_signal(parent_pid):
    _libc.prctl(1, signal.SIGTERM)
    if os.getppid() != parent_pid:
        os.kill(os.getpid(), signal.SIGTERM)


def _start_ffmpeg_process(cmd, channel_id):
    with STREAMS_LOCK:
        if channel_id not in hls_starting_streams:
            raise RuntimeError
    kwargs = {}
    if sys.platform.startswith("linux"):
        parent_pid = os.getpid()
        kwargs["preexec_fn"] = lambda: _set_parent_death_signal(parent_pid)
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        **kwargs,
    )
    with STREAMS_LOCK:
        accepted = channel_id in hls_starting_streams
        if accepted:
            hls_starting_processes[channel_id] = process
    if not accepted:
        _terminate_process_safe(process)
        raise RuntimeError
    return process


def _save_probe_metadata_to_db(channel_id: str, url: str, headers: dict | None, meta: dict | None):
    """
    Save probe metadata into result_data table (create full schema if needed).
    """
    if not meta:
        return
    conn = None
    try:
        ensure_result_data_schema(constants.rtmp_data_path)
        conn = get_db_connection(constants.rtmp_data_path)
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS result_data ("
            "id TEXT PRIMARY KEY, url TEXT, headers TEXT, video_codec TEXT, audio_codec TEXT, resolution TEXT, fps REAL)"
        )
        cursor.execute(
            "INSERT OR REPLACE INTO result_data (id, url, headers, video_codec, audio_codec, resolution, fps) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                str(channel_id),
                url,
                json.dumps(headers) if headers else None,
                meta.get('video_codec'),
                meta.get('audio_codec'),
                meta.get('resolution'),
                meta.get('fps')
            )
        )
        conn.commit()
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        print(t("msg.write_error").format(info=e))
    finally:
        if conn:
            return_db_connection(constants.rtmp_data_path, conn)


def ensure_hls_idle_monitor_started():
    if _hls_monitor_started_evt.is_set():
        return
    with _hls_monitor_lock:
        if _hls_monitor_started_evt.is_set():
            return
        try:
            thread = threading.Thread(target=hls_idle_monitor, daemon=True, name="hls-idle-monitor")
            thread.start()
            _hls_monitor_started_evt.set()
            print(t("msg.rtmp_hls_idle_monitor_start_success"))
        except Exception as e:
            print(t("msg.rtmp_hls_idle_monitor_start_fail").format(info=e))


@lru_cache(maxsize=1)
def _get_video_encoder_args():
    """
    Get the best available video encoder arguments based on the system's ffmpeg encoders.
    """
    preferred = ['h264_nvenc', 'h264_qsv', 'h264_amf', 'libx264']

    try:
        res = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'],
                             capture_output=True, text=True, timeout=10)
        enc_list = res.stdout
    except Exception:
        enc_list = ''

    for enc in preferred:
        if enc in enc_list:
            return ['-c:v', enc, '-preset', 'veryfast']

    return ['-c:v', 'libx264', '-preset', 'veryfast']


def invalidate_video_encoder_args_cache():
    """
    Invalidate the cached video encoder arguments, forcing a re-check of available encoders on next use.
    """
    try:
        _get_video_encoder_args.cache_clear()
    except Exception:
        pass


@lru_cache(maxsize=1)
def _get_video_encoder_candidates():
    """
    Probe ffmpeg for available encoders and return a list of encoder argument lists in preferred order.
    This is used to try fallbacks when a chosen encoder fails at runtime.
    """
    preferred = ['h264_nvenc', 'h264_qsv', 'h264_amf', 'libx264']
    candidates = []
    try:
        res = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], capture_output=True, text=True, timeout=10)
        enc_list = res.stdout or ''
    except Exception:
        enc_list = ''

    for enc in preferred:
        if enc in enc_list:
            candidates.append(['-c:v', enc, '-preset', 'veryfast'])

    if not any('libx264' in ' '.join(c) for c in candidates):
        candidates.append(['-c:v', 'libx264', '-preset', 'veryfast'])

    return candidates


def start_hls_to_rtmp(host, channel_id, client_user_agent: str | None = None):
    ensure_hls_idle_monitor_started()
    if not host:
        return None
    if not channel_id:
        print(t("msg.error_channel_id_not_found"))
        return None

    existing, reserved = _reserve_stream(channel_id)
    if existing:
        print(t("msg.rtmp_hls_stream_already_running"))
        return existing
    if not reserved:
        return None

    try:
        return _start_reserved_hls_to_rtmp(host, channel_id, client_user_agent)
    finally:
        _release_stream_reservation(channel_id)


def _start_reserved_hls_to_rtmp(host, channel_id, client_user_agent: str | None = None):
    """
    Start a HLS -> RTMP forwarding process for a given channel.
    Optimized: clearer early returns, reduced duplicated checks, use wait(timeout)
    to detect quick ffmpeg failures instead of manual poll loops.
    """
    data = get_channel_data(channel_id)
    url = data.get("url", "")
    if not url:
        print(t("msg.error_channel_url_not_found"))
        return None

    headers = data.get("headers", None)
    headers_str = ''.join(f'{k}: {v}\r\n' for k, v in headers.items()) if headers else ''

    meta = {
        'video_codec': data.get('video_codec'),
        'audio_codec': data.get('audio_codec'),
        'resolution': data.get('resolution'),
        'fps': data.get('fps'),
    }

    if config.rtmp_transcode_mode != 'copy' and (
            not meta.get('video_codec') or not meta.get('audio_codec')):
        try:
            probed = probe_url_sync(url, headers, timeout=10)
            if probed:
                meta.update(probed)
                _save_probe_metadata_to_db(channel_id, url, headers, probed)
        except Exception:
            pass

    def _client_needs_transcode_for_codec(user_agent: str | None, video_codec: str | None) -> bool:
        if not user_agent or not video_codec:
            return False
        ua = user_agent.lower()
        vc = (video_codec or '').lower()
        if vc in {'hevc', 'h265', 'x265', 'av1'}:
            if any(k in ua for k in ('iphone', 'ipad', 'mobile safari')) or ('safari' in ua and 'chrome' not in ua):
                return True
            if any(k in ua for k in ('chrome', 'firefox', 'edge')):
                return True
        return False

    if config.rtmp_transcode_mode == 'copy':
        client_forces_transcode = False
    else:
        client_forces_transcode = bool(
            client_user_agent and _client_needs_transcode_for_codec(client_user_agent, meta.get('video_codec')))

    base_cmd = ['ffmpeg', '-loglevel', 'error', '-re']

    local_loop = False
    try:
        parsed_url = url.partition('$')[0]
        if parsed_url.startswith('file://'):
            local_path = parsed_url[len('file://'):]
            if os.path.exists(local_path) and not local_path.lower().endswith('.m3u8'):
                local_loop = True
                url_input = local_path
            else:
                url_input = parsed_url
        else:
            url_input = parsed_url
            if os.path.exists(url_input) and not url_input.lower().endswith('.m3u8'):
                local_loop = True
    except Exception:
        url_input = url.partition('$')[0]

    if headers_str and not local_loop:
        base_cmd += ['-headers', headers_str]

    if local_loop:
        base_cmd += ['-stream_loop', '-1']

    base_cmd += ['-i', url_input]

    output_url = join_url(host, channel_id)

    rest_args = ['-c:a', 'aac', '-b:a', '128k', '-f', 'flv', '-flvflags', 'no_duration_filesize', output_url]

    def _build_copy_cmd(copy_audio: bool = True):
        if copy_audio:
            return base_cmd + ['-c:v', 'copy', '-c:a', 'copy', '-f', 'flv', '-flvflags', 'no_duration_filesize',
                               output_url]
        else:
            return base_cmd + ['-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-f', 'flv', '-flvflags',
                               'no_duration_filesize', output_url]

    def _audio_compatible_with_flv(audio_codec: str | None) -> bool:
        if not audio_codec:
            return False
        return (audio_codec or '').lower() in {'aac', 'mp3'}

    def _register_process(proc, mode, video_codec, audio_codec):
        try:
            print(
                t("msg.rtmp_publish").format(channel_id=channel_id, source=url)
                + f", {t('name.fps')}: {meta.get('fps') or t('name.unknown')}, [{mode}]: {t('name.video_codec')}: {video_codec}, {t('name.audio_codec')}: {audio_codec}"
            )
        except Exception:
            pass

        with STREAMS_LOCK:
            hls_starting_processes.pop(channel_id, None)
            hls_starting_streams.discard(channel_id)
            hls_running_streams[channel_id] = proc
            hls_last_access[channel_id] = time.time()

        threading.Thread(
            target=monitor_stream_process,
            args=(hls_running_streams, proc, channel_id),
            daemon=True
        ).start()

    def _start_copy_trial(wait_seconds=3, copy_audio: bool = True):
        cmd = _build_copy_cmd(copy_audio=copy_audio)
        try:
            copy_p = _start_ffmpeg_process(cmd, channel_id)
        except Exception as copy_e:
            print(t("msg.error_start_ffmpeg_failed").format(info=copy_e))
            return None, False

        try:
            copy_p.wait(timeout=wait_seconds)
            copy_succeeded = False
        except subprocess.TimeoutExpired:
            copy_succeeded = True

        if not copy_succeeded or copy_p.poll() is not None:
            try:
                _terminate_process_safe(copy_p)
            except Exception:
                pass
            return None, False

        _vid_codec = meta.get('video_codec') or t('name.unknown')
        _aud_codec = 'aac' if not copy_audio else (meta.get('audio_codec') or t('name.unknown'))
        mode_name = 'copy' if copy_audio else 'copy(video)+transcode(audio)'
        _register_process(copy_p, mode_name, _vid_codec, _aud_codec)
        return copy_p, True

    if config.rtmp_transcode_mode == 'copy':
        p, ok = _start_copy_trial(copy_audio=True)
        if ok:
            return p
        p, ok = _start_copy_trial(copy_audio=False)
        if ok:
            return p
        print(t("msg.rtmp_all_encoders_failed"))
        return None

    if not client_forces_transcode:
        _v = (meta.get('video_codec') or '').lower()
        if _v == 'avc1':
            _v = 'h264'
        _a = (meta.get('audio_codec') or '').lower() if meta.get('audio_codec') else None

        if _v == 'h264':
            if _a and _audio_compatible_with_flv(_a):
                p, ok = _start_copy_trial(copy_audio=True)
                if ok:
                    return p
            p, ok = _start_copy_trial(copy_audio=False)
            if ok:
                return p

    candidates = _get_video_encoder_candidates()
    process = None
    chosen_encoder = None
    grace_seconds = 3

    for enc_args in candidates:
        enc_name = enc_args[1] if len(enc_args) > 1 else str(enc_args)
        print(t("msg.rtmp_try_encoder").format(encoder=enc_name, channel_id=channel_id))
        cmd_try = base_cmd + enc_args + rest_args
        try:
            p = _start_ffmpeg_process(cmd_try, channel_id)
        except Exception as e:
            print(t("msg.rtmp_encoder_start_failed").format(encoder=enc_name, info=e))
            continue

        try:
            p.wait(timeout=grace_seconds)
            succeeded = False
        except subprocess.TimeoutExpired:
            succeeded = True

        if succeeded and p.poll() is None:
            process = p
            chosen_encoder = enc_name
            break
        else:
            try:
                _terminate_process_safe(p)
            except Exception:
                pass
            print(t("msg.rtmp_encoder_quick_fail").format(encoder=enc_name))

    if not process:
        print(t("msg.rtmp_all_encoders_failed"))
        p, ok = _start_copy_trial()
        if ok:
            return p
        return None

    target_video_codec = chosen_encoder or 'libx264'
    target_audio_codec = 'aac'
    target_mode = 'transcode'
    _register_process(process, target_mode, target_video_codec, target_audio_codec)
    return process


def _terminate_process_safe(process):
    try:
        process.terminate()
        process.wait(timeout=5)
    except Exception:
        try:
            process.kill()
            process.wait(timeout=5)
        except Exception:
            pass


def cleanup_streams(streams):
    victims = []
    with STREAMS_LOCK:
        for channel_id, process in list(streams.items()):
            if process.poll() is not None:
                streams.pop(channel_id, None)
                hls_last_access.pop(channel_id, None)

        while len(streams) > MAX_STREAMS:
            try:
                oldest_channel_id, oldest_proc = streams.popitem(last=False)
                hls_last_access.pop(oldest_channel_id, None)
                victims.append(oldest_proc)
            except KeyError:
                break
    for process in victims:
        _terminate_process_safe(process)


def monitor_stream_process(streams, process, channel_id):
    try:
        process.wait()
    except Exception:
        pass
    with STREAMS_LOCK:
        if channel_id in streams and streams[channel_id] is process:
            del streams[channel_id]
            hls_last_access.pop(channel_id, None)


def hls_idle_monitor():
    while True:
        now = time.time()
        to_stop = []

        with STREAMS_LOCK:
            for channel_id, last_ts in list(hls_last_access.items()):
                proc = hls_running_streams.get(channel_id)
                if proc and proc.poll() is None:
                    if now - last_ts > HLS_IDLE_TIMEOUT:
                        print(t("msg_rtmp_hls_idle_will_stop").format(channel_id=channel_id,
                                                                      second=f"{now - last_ts:.1f}"))
                        to_stop.append(channel_id)

        for cid in to_stop:
            stop_stream(cid)
            with STREAMS_LOCK:
                hls_last_access.pop(cid, None)

        time.sleep(5)


def get_channel_data(channel_id):
    channel_data = {}
    conn = None
    try:
        ensure_result_data_schema(constants.rtmp_data_path)
        conn = get_db_connection(constants.rtmp_data_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT url, headers, video_codec, audio_codec, resolution, fps FROM result_data WHERE id=?",
            (channel_id,)
        )
        data = cursor.fetchone()
        if data:
            channel_data = {
                'url': data[0],
                'headers': json.loads(data[1]) if data[1] else None,
                'video_codec': data[2] if len(data) > 2 else None,
                'audio_codec': data[3] if len(data) > 3 else None,
                'resolution': data[4] if len(data) > 4 else None,
                'fps': data[5] if len(data) > 5 else None,
            }
    except Exception as e:
        print(t("msg.error_get_channel_data_from_database").format(info=e))
    finally:
        if conn:
            return_db_connection(constants.rtmp_data_path, conn)
    return channel_data


def stop_stream(channel_id):
    with STREAMS_LOCK:
        process = hls_running_streams.pop(channel_id, None)
        starting_process = hls_starting_processes.pop(channel_id, None)
        hls_starting_streams.discard(channel_id)
        hls_last_access.pop(channel_id, None)
    for target in (process, starting_process):
        if target and target.poll() is None:
            try:
                _terminate_process_safe(target)
            except Exception as e:
                print(t("msg.error_stop_channel_stream").format(channel_id=channel_id, info=e))


def stop_all_streams():
    with STREAMS_LOCK:
        processes = list(hls_running_streams.values()) + list(hls_starting_processes.values())
        hls_running_streams.clear()
        hls_starting_processes.clear()
        hls_starting_streams.clear()
        hls_last_access.clear()
    seen = set()
    for process in processes:
        if process.pid in seen:
            continue
        seen.add(process.pid)
        if process.poll() is None:
            _terminate_process_safe(process)


def start_rtmp_service():
    render_nginx_conf(nginx_conf_template, nginx_conf)
    original_dir = os.getcwd()
    try:
        os.chdir(nginx_dir)
        subprocess.Popen([nginx_path], shell=True)
    except Exception as e:
        print(t("msg.error_rtmp_service_start_failed").format(info=e))
    finally:
        os.chdir(original_dir)


def stop_rtmp_service():
    try:
        os.chdir(nginx_dir)
        subprocess.Popen([stop_path], shell=True)
    except Exception as e:
        print(t("msg.error_rtmp_service_stop_failed").format(info=e))


atexit.register(stop_all_streams)
