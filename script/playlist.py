import re
import requests
from collections import defaultdict

# ===== 配置 =====
M3U_URLS = [
    "https://gh-proxy.com/https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
    "https://gh-proxy.org/https://raw.githubusercontent.com/vbskycn/iptv/refs/heads/master/tv/iptv4.m3u"
] 
BLACKLIST_FILE = "config/blackgroup.txt"
OUTPUT_FILE = "config/demo.txt"

EMOJI_MAP = {
    "电影频道": "🎬",
    "春晚频道": "🚗",
}
# 固定央视频道列表
CCTV_CHANNELS = [
    "CCTV-1","CCTV-2","CCTV-3","CCTV-4","CCTV-5","CCTV-5+","CCTV-6","CCTV-7","CCTV-8",
    "CCTV-9","CCTV-10","CCTV-11","CCTV-12","CCTV-13","CCTV-14","CCTV-15","CCTV-16","CCTV-17",
    "CETV-1","CETV-2","CETV-3","CETV-4"
]
pattern = re.compile(r'tvg-name="(.*?)".*?group-title="(.*?)"')

groups = defaultdict(list)
groups_seen = defaultdict(set)   # ⭐ 关键：用于组内去重

# ⭐ 去除 emoji 的函数
def clean_group_title(title):
    return re.sub(r'[^\w\u4e00-\u9fff]+', '', title)

# ⭐ 读取黑名单
def load_blacklist():
    try:
        with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        print("未找到黑名单文件，跳过过滤")
        return set()

BLOCK_GROUPS = load_blacklist()

# ===== 先写入固定央视频道 =====
groups["央视频道"] = CCTV_CHANNELS.copy()


# ===== 读取多个m3u =====
for url in M3U_URLS:
    try:
        print("正在读取:", url)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text

        for line in content.splitlines():
            if line.startswith("#EXTINF"):
                match = pattern.search(line)
                if match:
                    tvg_name, group_title = match.groups()
                    # ⭐ 清洗分组名称
                    group_title = clean_group_title(group_title)
                    # ⭐ 屏蔽黑名单分组
                    if group_title in BLOCK_GROUPS:
                        continue
                    # 跳过央视频道，已固定
                    if group_title == "央视频道":
                        continue
                    # ⭐ 去重逻辑
                    if tvg_name not in groups_seen[group_title]:
                        groups[group_title].append(tvg_name)
                        groups_seen[group_title].add(tvg_name)

    except Exception as e:
        print("读取失败:", url, e)

# ===== 保存TXT =====
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for group_title, channels in groups.items():
        emoji = EMOJI_MAP.get(group_title, "")
        f.write(f"{emoji}{group_title},#genre#\n")
        for name in channels:
            f.write(f"{name}\n")
        f.write("\n")

print("已保存到", OUTPUT_FILE)
