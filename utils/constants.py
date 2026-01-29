import os
import re

from utils.i18n import t

config_dir = "config"

output_dir = "output"

hls_path = os.path.join(config_dir, "hls")

local_dir_path = os.path.join(config_dir, "local")

local_path = os.path.join(config_dir, "local.txt")

channel_logo_path = os.path.join(config_dir, "logo")

alias_path = os.path.join(config_dir, "alias.txt")

epg_path = os.path.join(config_dir, "epg.txt")

whitelist_path = os.path.join(config_dir, "whitelist.txt")

blacklist_path = os.path.join(config_dir, "blacklist.txt")

subscribe_path = os.path.join(config_dir, "subscribe.txt")

epg_result_path = os.path.join(output_dir, "epg/epg.xml")

epg_gz_result_path = os.path.join(output_dir, "epg/epg.gz")

ipv4_result_path = os.path.join(output_dir, "ipv4/result.txt")

ipv6_result_path = os.path.join(output_dir, "ipv6/result.txt")

rtmp_data_path = os.path.join(output_dir, "data/rtmp.db")

hls_result_path = os.path.join(output_dir, "hls.txt")

hls_ipv4_result_path = os.path.join(output_dir, "ipv4/hls.txt")

hls_ipv6_result_path = os.path.join(output_dir, "ipv6/hls.txt")

cache_path = os.path.join(output_dir, "data/cache.gz")

frozen_path = os.path.join(output_dir, "data/frozen.gz")

speed_test_log_path = os.path.join(output_dir, "log/speed_test.log")

result_log_path = os.path.join(output_dir, "log/result.log")

statistic_log_path = os.path.join(output_dir, "log/statistic.log")

nomatch_log_path = os.path.join(output_dir, "log/nomatch.log")

log_path = os.path.join(output_dir, "log/log.log")

url_host_pattern = re.compile(r"((https?|rtmp|rtsp)://)?([^:@/]+(:[^:@/]*)?@)?(\[[0-9a-fA-F:]+]|([\w-]+\.)+[\w-]+)")

url_pattern = re.compile(
    r"(?P<url>" + url_host_pattern.pattern + r"\S*)")

rt_url_pattern = re.compile(r"^(rtmp|rtsp)://.*$")

demo_txt_pattern = re.compile(r"^(?P<name>[^,，]+)[,，]?(?!#genre#)(?P<value>.+)?$")

txt_pattern = re.compile(r"^(?P<name>[^,，]+)[,，](?!#genre#)(?P<value>.+)$")

multiline_txt_pattern = re.compile(r"^(?P<name>[^,，]+)[,，](?!#genre#)(?P<value>.+)$", re.MULTILINE)

m3u_pattern = re.compile(r"^#EXTINF:-1[\s+,，](?P<attributes>[^,，]+)[，,](?P<name>.*?)\n(?P<value>.+)$")

multiline_m3u_pattern = re.compile(
    r"^#EXTINF:-1[\s+,，](?P<attributes>[^,，]+)[，,](?P<name>.*?)\n(?P<options>(#EXTVLCOPT:.*\n)*?)(?P<value>.+)$",
    re.MULTILINE)

key_value_pattern = re.compile(r'(?P<key>\w+)=(?P<value>\S+)')

sub_pattern = re.compile(
    r"-|_|\((.*?)\)|（(.*?)）|\[(.*?)]|「(.*?)」| |｜|频道|普清|标清|高清|HD|hd|超清|超高|超高清|4K|4k|中央|央视|电视台|台|电信|联通|移动")

replace_dict = {
    "plus": "+",
    "PLUS": "+",
    "＋": "+",
}

origin_map = {
    "subscribe": t("name.subscribe"),
    "whitelist": t("name.whitelist"),
    "local": t("name.local"),
}

ipv6_proxy = "http://www.ipv6proxy.net/go.php?u="

waiting_tip = t("msg.waiting_tip")
