import json
import os
import subprocess
import sys
import threading
import time
from collections import OrderedDict

import utils.constants as constants
from utils.config import config
from utils.db import get_db_connection, return_db_connection
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
HLS_IDLE_TIMEOUT = config.rtmp_idle_timeout
HLS_WAIT_TIMEOUT = 15
HLS_WAIT_INTERVAL = 0.5
MAX_STREAMS = config.rtmp_max_streams
nginx_dir = resource_path(os.path.join('utils', 'nginx-rtmp-win32'))
hls_temp_path = resource_path(os.path.join(nginx_dir, 'temp', 'hls')) if sys.platform == "win32" else '/tmp/hls'

_hls_monitor_started_evt = threading.Event()
_hls_monitor_lock = threading.Lock()


def ensure_hls_idle_monitor_started():
    if _hls_monitor_started_evt.is_set():
        return
    with _hls_monitor_lock:
        if _hls_monitor_started_evt.is_set():
            return
        try:
            if not config.open_rtmp:
                return
            thread = threading.Thread(target=hls_idle_monitor, daemon=True, name="hls-idle-monitor")
            thread.start()
            _hls_monitor_started_evt.set()
            print(t("msg.rtmp_hls_idle_monitor_start_success"))
        except Exception as e:
            print(t("msg.rtmp_hls_idle_monitor_start_fail").format(info=e))


def start_hls_to_rtmp(host, channel_id):
    ensure_hls_idle_monitor_started()

    if not host:
        return None
    if not channel_id:
        return print(t("msg.error_channel_id_not_found"))

    data = get_channel_data(channel_id)
    url = data.get("url", "")
    if not url:
        return print(t("msg.error_channel_url_not_found"))

    with STREAMS_LOCK:
        if channel_id in hls_running_streams:
            process = hls_running_streams[channel_id]
            if process.poll() is None:
                return print(t("msg.rtmp_hls_stream_already_running"))
            else:
                del hls_running_streams[channel_id]

    cleanup_streams(hls_running_streams)

    headers = data.get("headers", None)
    headers_str = ''.join(f'{k}: {v}\r\n' for k, v in headers.items()) if headers else ''
    cmd = [
        'ffmpeg',
        '-loglevel', 'error',
        '-re',
        '-headers', headers_str,
        '-i', url.partition('$')[0],
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-f', 'flv',
        '-flvflags', 'no_duration_filesize',
        join_url(host, channel_id)
    ]
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
    except Exception as e:
        return print(t("msg.error_start_ffmpeg_failed").format(info=e))

    threading.Thread(
        target=monitor_stream_process,
        args=(hls_running_streams, process, channel_id),
        daemon=True
    ).start()

    with STREAMS_LOCK:
        hls_running_streams[channel_id] = process


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
    with STREAMS_LOCK:
        to_delete = []
        for channel_id, process in list(streams.items()):
            if process.poll() is not None:
                to_delete.append(channel_id)
        for channel_id in to_delete:
            streams.pop(channel_id, None)

        while len(streams) > MAX_STREAMS:
            try:
                oldest_channel_id, oldest_proc = streams.popitem(last=False)
                _terminate_process_safe(oldest_proc)
            except KeyError:
                break


def monitor_stream_process(streams, process, channel_id):
    try:
        process.wait()
    except Exception:
        pass
    with STREAMS_LOCK:
        if channel_id in streams and streams[channel_id] is process:
            del streams[channel_id]


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
    conn = get_db_connection(constants.rtmp_data_path)
    channel_data = {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT url, headers FROM result_data WHERE id=?", (channel_id,))
        data = cursor.fetchone()
        if data:
            channel_data = {
                'url': data[0],
                'headers': json.loads(data[1]) if data[1] else None
            }
    except Exception as e:
        print(t("msg.error_get_channel_data_from_database").format(info=e))
    finally:
        return_db_connection(constants.rtmp_data_path, conn)
    return channel_data


def stop_stream(channel_id):
    with STREAMS_LOCK:
        process = hls_running_streams.get(channel_id)
        if process and process.poll() is None:
            try:
                _terminate_process_safe(process)
            except Exception as e:
                print(t("msg.error_stop_channel_stream").format(channel_id=channel_id, info=e))
        hls_running_streams.pop(channel_id, None)


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
