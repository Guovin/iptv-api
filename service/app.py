import os
import sys

sys.path.append(os.path.dirname(sys.path[0]))
from flask import Flask, send_from_directory, make_response, jsonify, redirect
from utils.tools import get_result_file_content, get_ip_address, resource_path
from utils.config import config
import utils.constants as constants
from utils.db import get_db_connection, return_db_connection
import subprocess
import atexit

app = Flask(__name__)
nginx_dir = resource_path(os.path.join('utils', 'nginx-rtmp-win32'))
nginx_path = resource_path(os.path.join(nginx_dir, 'nginx.exe'))
stop_path = resource_path(os.path.join(nginx_dir, 'stop.bat'))
os.makedirs(f"{constants.output_dir}/data", exist_ok=True)


@app.route("/")
def show_index():
    return get_result_file_content(
        path=constants.rtmp_result_path if config.open_rtmp else config.final_file,
        file_type="m3u" if config.open_m3u_result else "txt"
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(resource_path('static/images'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route("/txt")
def show_txt():
    return get_result_file_content(path=config.final_file, file_type="txt")


@app.route("/ipv4/txt")
def show_ipv4_txt():
    return get_result_file_content(path=constants.ipv4_result_path, file_type="txt")


@app.route("/ipv6/txt")
def show_ipv6_txt():
    return get_result_file_content(path=constants.ipv6_result_path, file_type="txt")


@app.route("/rtmp")
def show_rtmp():
    return get_result_file_content(path=constants.rtmp_result_path,
                                   file_type="m3u" if config.open_m3u_result else "txt")


@app.route("/rtmp-txt")
def show_rtmp_txt():
    return get_result_file_content(path=constants.rtmp_result_path, file_type="txt")


@app.route("/ipv4/rtmp-txt")
def show_ipv4_rtmp_txt():
    return get_result_file_content(path=constants.ipv4_rtmp_result_path, file_type="txt")


@app.route("/ipv6/rtmp-txt")
def show_ipv6_rtmp_txt():
    return get_result_file_content(path=constants.ipv6_rtmp_result_path, file_type="txt")


@app.route("/m3u")
def show_m3u():
    return get_result_file_content(path=config.final_file, file_type="m3u")


@app.route("/rtmp-m3u")
def show_rtmp_m3u():
    return get_result_file_content(path=constants.rtmp_result_path, file_type="m3u")


@app.route("/ipv4/m3u")
def show_ipv4_m3u():
    return get_result_file_content(path=constants.ipv4_result_path, file_type="m3u")


@app.route("/ipv4")
def show_ipv4_result():
    return get_result_file_content(
        path=constants.ipv4_rtmp_result_path if config.open_rtmp else constants.ipv4_result_path,
        file_type="m3u" if config.open_m3u_result else "txt"
    )


@app.route("/ipv6/m3u")
def show_ipv6_m3u():
    return get_result_file_content(path=constants.ipv6_result_path, file_type="m3u")


@app.route("/ipv6")
def show_ipv6_result():
    return get_result_file_content(
        path=constants.ipv6_rtmp_result_path if config.open_rtmp else constants.ipv6_result_path,
        file_type="m3u" if config.open_m3u_result else "txt"
    )


@app.route("/ipv4/rtmp-m3u")
def show_ipv4_rtmp_m3u():
    return get_result_file_content(path=constants.ipv4_rtmp_result_path, file_type="m3u")


@app.route("/ipv6/rtmp-m3u")
def show_ipv6_rtmp_m3u():
    return get_result_file_content(path=constants.ipv6_rtmp_result_path, file_type="m3u")


@app.route("/content")
def show_content():
    return get_result_file_content(
        path=constants.rtmp_result_path if config.open_rtmp else config.final_file,
        file_type="m3u" if config.open_m3u_result else "txt",
        show_content=True
    )


@app.route("/log")
def show_log():
    if os.path.exists(constants.sort_log_path):
        with open(constants.sort_log_path, "r", encoding="utf-8") as file:
            content = file.read()
    else:
        content = constants.waiting_tip
    response = make_response(content)
    response.mimetype = "text/plain"
    return response


@app.route('/rtmp/<channel_id>', methods=['GET'])
def run_rtmp(channel_id):
    if not channel_id:
        return jsonify({'Error': 'Channel ID is required'}), 400
    conn = get_db_connection(constants.rtmp_data_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM result_data WHERE id=?", (channel_id,))
        data = cursor.fetchone()
        url = data[1] if data else ''
    finally:
        return_db_connection(constants.rtmp_data_path, conn)
    if not url:
        return jsonify({'Error': 'Url not found'}), 400
    cmd = [
        'ffmpeg',
        '-i', url.partition('$')[0],
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-b:v', '2500k',
        '-maxrate', '2500k',
        '-bufsize', '5000k',
        '-g', '50',
        '-c:a', 'aac',
        '-f', 'flv',
        f'rtmp://localhost:1935/live/{channel_id}'
    ]
    try:
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return redirect(f'rtmp://localhost:1935/live/{channel_id}')
    except Exception as e:
        return jsonify({'Error': str(e)}), 500


def stop_rtmp_service():
    if sys.platform == "win32":
        try:
            os.chdir(nginx_dir)
            subprocess.Popen([stop_path], shell=True)
        except Exception as e:
            print(f"❌ Rtmp service stop failed: {e}")


def run_service():
    try:
        if not os.environ.get("GITHUB_ACTIONS"):
            if config.open_rtmp and sys.platform == "win32":
                original_dir = os.getcwd()
                try:
                    os.chdir(nginx_dir)
                    subprocess.Popen([nginx_path], shell=True)
                except Exception as e:
                    print(f"❌ Rtmp service start failed: {e}")
                finally:
                    os.chdir(original_dir)
            ip_address = get_ip_address()
            print(f"📄 Result content: {ip_address}/content")
            print(f"📄 Log content: {ip_address}/log")
            if config.open_m3u_result:
                print(f"🚀 M3u api: {ip_address}/m3u")
            print(f"🚀 Txt api: {ip_address}/txt")
            if config.open_rtmp:
                if config.open_m3u_result:
                    print(f"🚀 Rtmp M3u api: {ip_address}/rtmp-m3u")
                print(f"🚀 Rtmp Txt api: {ip_address}/rtmp-txt")
            print(f"🚀 IPv4 Txt api: {ip_address}/ipv4")
            print(f"🚀 IPv6 Txt api: {ip_address}/ipv6")
            print(f"✅ You can use this url to watch IPTV 📺: {ip_address}")
            app.run(host="0.0.0.0", port=config.app_port)
    except Exception as e:
        print(f"❌ Service start failed: {e}")


if __name__ == "__main__":
    if config.open_rtmp:
        atexit.register(stop_rtmp_service)
    run_service()
