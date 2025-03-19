import os
import re

config_dir = "config"

output_dir = "output"

whitelist_path = os.path.join(config_dir, "whitelist.txt")

blacklist_path = os.path.join(config_dir, "blacklist.txt")

subscribe_path = os.path.join(config_dir, "subscribe.txt")

ipv4_result_path = os.path.join(output_dir, "ipv4/result.txt")

ipv6_result_path = os.path.join(output_dir, "ipv6/result.txt")

rtmp_result_path = os.path.join(output_dir, "rtmp.txt")

ipv4_rtmp_result_path = os.path.join(output_dir, "ipv4/rtmp.txt")

ipv6_rtmp_result_path = os.path.join(output_dir, "ipv6/rtmp.txt")

rtmp_data_path = os.path.join(output_dir, "data/rtmp.db")

cache_path = os.path.join(output_dir, "data/cache.pkl")

sort_log_path = os.path.join(output_dir, "log/sort.log")

log_path = os.path.join(output_dir, "log/log.log")

url_host_pattern = re.compile(r"((https?|rtmp|rtsp)://)?([^:@/]+(:[^:@/]*)?@)?(\[[0-9a-fA-F:]+]|([\w-]+\.)+[\w-]+)")

url_pattern = re.compile(url_host_pattern.pattern + r"(.*)?")

rt_url_pattern = re.compile(r"^(rtmp|rtsp)://.*$")

rtp_pattern = re.compile(r"^([^,，]+)[,，]?(rtp://.*)$")

demo_txt_pattern = re.compile(r"^([^,，]+)[,，]?(?!#genre#)" + r"(" + url_pattern.pattern + r")?")

txt_pattern = re.compile(r"^([^,，]+)[,，](?!#genre#)" + r"(" + url_pattern.pattern + r")")

multiline_txt_pattern = re.compile(r"^([^,，]+)[,，](?!#genre#)" + r"(" + url_pattern.pattern + r")", re.MULTILINE)

m3u_pattern = re.compile(r"^#EXTINF:-1.*?[，,](.*?)\n" + r"(" + url_pattern.pattern + r")")

multiline_m3u_pattern = re.compile(r"^#EXTINF:-1.*?[，,](.*?)\n" + r"(" + url_pattern.pattern + r")", re.MULTILINE)

sub_pattern = re.compile(
    r"-|_|\((.*?)\)|（(.*?)）|\[(.*?)]|「(.*?)」| |｜|频道|普清|标清|高清|HD|hd|超清|超高|超高清|中央|央视|电视台|台|电信|联通|移动")

replace_dict = {
    "plus": "+",
    "PLUS": "+",
    "＋": "+",
    "CCTV1综合": "CCTV1",
    "CCTV2财经": "CCTV2",
    "CCTV3综艺": "CCTV3",
    "CCTV4国际": "CCTV4",
    "CCTV4中文国际": "CCTV4",
    "CCTV4欧洲": "CCTV4",
    "CCTV5体育": "CCTV5",
    "CCTV5+体育赛视": "CCTV5+",
    "CCTV5+体育赛事": "CCTV5+",
    "CCTV5+体育": "CCTV5+",
    "CCTV6电影": "CCTV6",
    "CCTV7军事": "CCTV7",
    "CCTV7军农": "CCTV7",
    "CCTV7农业": "CCTV7",
    "CCTV7国防军事": "CCTV7",
    "CCTV8电视剧": "CCTV8",
    "CCTV9记录": "CCTV9",
    "CCTV9纪录": "CCTV9",
    "CCTV10科教": "CCTV10",
    "CCTV11戏曲": "CCTV11",
    "CCTV12社会与法": "CCTV12",
    "CCTV13新闻": "CCTV13",
    "CCTV新闻": "CCTV13",
    "CCTV14少儿": "CCTV14",
    "CCTV15音乐": "CCTV15",
    "CCTV16奥林匹克": "CCTV16",
    "CCTV17农业农村": "CCTV17",
    "CCTV17农业": "CCTV17",
}

region_list = [
    "广东",
    "北京",
    "湖南",
    "湖北",
    "浙江",
    "上海",
    "天津",
    "江苏",
    "山东",
    "河南",
    "河北",
    "山西",
    "陕西",
    "安徽",
    "重庆",
    "福建",
    "江西",
    "辽宁",
    "黑龙江",
    "吉林",
    "四川",
    "云南",
    "香港",
    "内蒙古",
    "甘肃",
    "海南",
    "云南",
]

origin_map = {
    "hotel": "酒店源",
    "multicast": "组播源",
    "subscribe": "订阅源",
    "online_search": "关键字源",
    "whitelist": "白名单",
    "local": "本地源",
}

ipv6_proxy = "http://www.ipv6proxy.net/go.php?u="

foodie_url = "http://www.foodieguide.com/iptvsearch/"

foodie_hotel_url = "http://www.foodieguide.com/iptvsearch/hoteliptv.php"

waiting_tip = "🔍️未找到结果文件，若已启动更新，请耐心等待更新完成..."
