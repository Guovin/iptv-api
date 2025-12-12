import configparser
import os
import re
import shutil
import socket
import sys


def resource_path(relative_path, persistent=False):
    """
    Get the resource path
    """
    base_path = os.path.abspath(".")
    total_path = os.path.join(base_path, relative_path)
    if persistent or os.path.exists(total_path):
        return total_path
    else:
        try:
            base_path = sys._MEIPASS
            return os.path.join(base_path, relative_path)
        except Exception:
            return total_path


def get_resolution_value(resolution_str):
    """
    Get resolution value from string
    """
    pattern = r"(\d+)[xX*](\d+)"
    match = re.search(pattern, resolution_str)
    if match:
        width, height = map(int, match.groups())
        return width * height
    else:
        return 0


class ConfigManager:

    def __init__(self):
        self.config = None
        self.load()
        self.override_config_with_env()

    def __getattr__(self, name, *args, **kwargs):
        return getattr(self.config, name, *args, **kwargs)

    @property
    def open_service(self):
        return self.config.getboolean("Settings", "open_service", fallback=True)

    @property
    def open_update(self):
        return self.config.getboolean("Settings", "open_update", fallback=True)

    @property
    def open_use_cache(self):
        return self.config.getboolean("Settings", "open_use_cache", fallback=True)

    @property
    def open_request(self):
        return self.config.getboolean("Settings", "open_request", fallback=False)

    @property
    def open_filter_speed(self):
        return self.config.getboolean(
            "Settings", "open_filter_speed", fallback=True
        )

    @property
    def open_filter_resolution(self):
        return self.config.getboolean(
            "Settings", "open_filter_resolution", fallback=True
        )

    @property
    def ipv_type(self):
        return self.config.get("Settings", "ipv_type", fallback="全部").lower()

    @property
    def open_ipv6(self):
        return (
                "ipv6" in self.ipv_type or "all" in self.ipv_type or "全部" in self.ipv_type
        )

    @property
    def ipv_type_prefer(self):
        return [
            ipv_type_value.lower()
            for ipv_type in self.config.get(
                "Settings", "ipv_type_prefer", fallback=""
            ).split(",")
            if (ipv_type_value := ipv_type.strip())
        ]

    @property
    def ipv4_num(self):
        try:
            return self.config.getint("Settings", "ipv4_num", fallback=5)
        except:
            return ""

    @property
    def ipv6_num(self):
        try:
            return self.config.getint("Settings", "ipv6_num", fallback=5)
        except:
            return ""

    @property
    def ipv6_support(self):
        return self.config.getboolean("Settings", "ipv6_support", fallback=False)

    @property
    def ipv_limit(self):
        return {
            "all": self.urls_limit,
            "ipv4": self.ipv4_num,
            "ipv6": self.ipv6_num,
        }

    @property
    def origin_type_prefer(self):
        return [
            origin_value.lower()
            for origin in self.config.get(
                "Settings",
                "origin_type_prefer",
                fallback="",
            ).split(",")
            if (origin_value := origin.strip())
        ]

    @property
    def hotel_num(self):
        return self.config.getint("Settings", "hotel_num", fallback=10)

    @property
    def multicast_num(self):
        return self.config.getint("Settings", "multicast_num", fallback=10)

    @property
    def subscribe_num(self):
        return self.config.getint("Settings", "subscribe_num", fallback=10)

    @property
    def online_search_num(self):
        return self.config.getint("Settings", "online_search_num", fallback=10)

    @property
    def source_limits(self):
        return {
            "all": self.urls_limit,
            "local": self.local_num,
            "hotel": self.hotel_num,
            "multicast": self.multicast_num,
            "subscribe": self.subscribe_num,
            "online_search": self.online_search_num,
        }

    @property
    def min_speed(self):
        return self.config.getfloat("Settings", "min_speed", fallback=0.5)

    @property
    def min_resolution(self):
        return self.config.get("Settings", "min_resolution", fallback="1920x1080")

    @property
    def min_resolution_value(self):
        return get_resolution_value(self.min_resolution)

    @property
    def max_resolution(self):
        return self.config.get("Settings", "max_resolution", fallback="1920x1080")

    @property
    def max_resolution_value(self):
        return get_resolution_value(self.max_resolution)

    @property
    def urls_limit(self):
        return self.config.getint("Settings", "urls_limit", fallback=30)

    @property
    def open_url_info(self):
        return self.config.getboolean("Settings", "open_url_info", fallback=True)

    @property
    def recent_days(self):
        return self.config.getint("Settings", "recent_days", fallback=30)

    @property
    def source_file(self):
        return self.config.get("Settings", "source_file", fallback="config/demo.txt")

    @property
    def final_file(self):
        return self.config.get("Settings", "final_file", fallback="output/result.txt")

    @property
    def open_m3u_result(self):
        return self.config.getboolean("Settings", "open_m3u_result", fallback=True)

    @property
    def open_subscribe(self):
        return self.config.getboolean("Settings", f"open_subscribe", fallback=True)

    @property
    def open_hotel(self):
        return self.config.getboolean("Settings", f"open_hotel", fallback=True)

    @property
    def open_hotel_fofa(self):
        return self.config.getboolean("Settings", f"open_hotel_fofa", fallback=True)

    @property
    def open_hotel_foodie(self):
        return self.config.getboolean("Settings", f"open_hotel_foodie", fallback=True)

    @property
    def open_multicast(self):
        return self.config.getboolean("Settings", f"open_multicast", fallback=True)

    @property
    def open_multicast_fofa(self):
        return self.config.getboolean("Settings", f"open_multicast_fofa", fallback=True)

    @property
    def open_multicast_foodie(self):
        return self.config.getboolean(
            "Settings", f"open_multicast_foodie", fallback=True
        )

    @property
    def open_online_search(self):
        return self.config.getboolean("Settings", f"open_online_search", fallback=True)

    @property
    def open_method(self):
        return {
            "epg": self.open_epg,
            "local": self.open_local,
            "subscribe": self.open_subscribe,
            "hotel": self.open_hotel,
            "multicast": self.open_multicast,
            "online_search": self.open_online_search,
            "hotel_fofa": self.open_hotel and self.open_hotel_fofa,
            "hotel_foodie": self.open_hotel and self.open_hotel_foodie,
            "multicast_fofa": self.open_multicast and self.open_multicast_fofa,
            "multicast_foodie": self.open_multicast and self.open_multicast_foodie,
        }

    @property
    def open_history(self):
        return self.config.getboolean("Settings", "open_history", fallback=True)

    @property
    def open_speed_test(self):
        return self.config.getboolean("Settings", "open_speed_test", fallback=True)

    @property
    def open_update_time(self):
        return self.config.getboolean("Settings", "open_update_time", fallback=True)

    @property
    def multicast_region_list(self):
        return [
            region.strip()
            for region in self.config.get(
                "Settings", "multicast_region_list", fallback="全部"
            ).split(",")
            if region.strip()
        ]

    @property
    def hotel_region_list(self):
        return [
            region.strip()
            for region in self.config.get(
                "Settings", "hotel_region_list", fallback="全部"
            ).split(",")
            if region.strip()
        ]

    @property
    def request_timeout(self):
        return self.config.getint("Settings", "request_timeout", fallback=10)

    @property
    def speed_test_timeout(self):
        return self.config.getint("Settings", "speed_test_timeout", fallback=10)

    @property
    def open_driver(self):
        return self.config.getboolean(
            "Settings", "open_driver", fallback=False
        )

    @property
    def hotel_page_num(self):
        return self.config.getint("Settings", "hotel_page_num", fallback=1)

    @property
    def multicast_page_num(self):
        return self.config.getint("Settings", "multicast_page_num", fallback=1)

    @property
    def online_search_page_num(self):
        return config.getint("Settings", "online_search_page_num", fallback=1)

    @property
    def open_empty_category(self):
        return self.config.getboolean("Settings", "open_empty_category", fallback=True)

    @property
    def app_port(self):
        return self.config.getint("Settings", "app_port", fallback=5180)

    @property
    def nginx_http_port(self):
        return self.config.getint("Settings", "nginx_http_port", fallback=8080)

    @property
    def nginx_rtmp_port(self):
        return self.config.getint("Settings", "nginx_rtmp_port", fallback=1935)

    @property
    def open_supply(self):
        return self.config.getboolean("Settings", "open_supply", fallback=True)

    @property
    def update_time_position(self):
        return self.config.get("Settings", "update_time_position", fallback="top")

    @property
    def time_zone(self):
        return self.config.get("Settings", "time_zone", fallback="Asia/Shanghai")

    @property
    def open_local(self):
        return self.config.getboolean("Settings", "open_local", fallback=True)

    @property
    def local_file(self):
        return self.config.get("Settings", "local_file", fallback="config/local.txt")

    @property
    def local_num(self):
        return self.config.getint("Settings", "local_num", fallback=10)

    @property
    def speed_test_filter_host(self):
        return self.config.getboolean("Settings", "speed_test_filter_host", fallback=False)

    @property
    def cdn_url(self):
        return self.config.get("Settings", "cdn_url", fallback="")

    @property
    def open_rtmp(self):
        return not os.getenv("GITHUB_ACTIONS") and self.config.getboolean("Settings", "open_rtmp", fallback=True)

    @property
    def open_headers(self):
        return self.config.getboolean("Settings", "open_headers", fallback=False)

    @property
    def open_epg(self):
        return self.config.getboolean("Settings", "open_epg", fallback=True)

    @property
    def speed_test_limit(self):
        return self.config.getint("Settings", "speed_test_limit", fallback=10)

    @property
    def location(self):
        return [
            l.strip()
            for l in self.config.get(
                "Settings", "location", fallback=""
            ).split(",")
            if l.strip()
        ]

    @property
    def isp(self):
        return [
            i.strip()
            for i in self.config.get(
                "Settings", "isp", fallback=""
            ).split(",")
            if i.strip()
        ]

    @property
    def update_mode(self):
        return self.config.get("Settings", "update_mode", fallback="interval")

    @property
    def update_interval(self):
        return self.config.getfloat("Settings", "update_interval", fallback=12)

    @property
    def update_times(self):
        return self.config.get("Settings", "update_times", fallback="")

    @property
    def update_startup(self):
        return self.config.getboolean("Settings", "update_startup", fallback=True)

    @property
    def logo_url(self):
        return self.config.get("Settings", "logo_url", fallback="")

    @property
    def logo_type(self):
        return self.config.get("Settings", "logo_type", fallback="png")

    @property
    def rtmp_idle_timeout(self):
        return self.config.getint("Settings", "rtmp_idle_timeout", fallback=60)

    @property
    def rtmp_max_streams(self):
        return self.config.getint("Settings", "rtmp_max_streams", fallback=10)

    @property
    def public_scheme(self):
        return self.config.get("Settings", "public_scheme", fallback="http") or "http"

    @property
    def public_domain(self):
        cfg = self.config.get("Settings", "public_domain", fallback="127.0.0.1")
        if cfg and cfg != "127.0.0.1":
            return cfg
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            finally:
                s.close()
            if ip and not ip.startswith("127."):
                return ip
        except Exception:
            pass
        return cfg

    @property
    def language(self):
        return self.config.get("Settings", "language", fallback="zh_CN")

    def load(self):
        """
        Load the config
        """
        self.config = configparser.ConfigParser()
        user_config_path = resource_path("config/user_config.ini")
        default_config_path = resource_path("config/config.ini")

        # user config overwrites default config
        config_files = [default_config_path, user_config_path]
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    self.config.read_file(f)

    def override_config_with_env(self):
        for section in self.config.sections():
            for key in self.config[section]:
                section_key = f"{section}_{key}"
                candidates = (key, key.upper(), section_key, section_key.upper())
                for env_name in candidates:
                    env_val = os.getenv(env_name)
                    if env_val is not None:
                        self.config.set(section, key, env_val)
                        break

    def set(self, section, key, value):
        """
        Set the config
        """
        self.config.set(section, key, value)

    def save(self):
        """
        Save config with write
        """
        user_config_file = "config/" + (
            "user_config.ini"
            if os.path.exists(resource_path("user_config.ini"))
            else "config.ini"
        )
        user_config_path = resource_path(user_config_file, persistent=True)
        if not os.path.exists(user_config_path):
            os.makedirs(os.path.dirname(user_config_path), exist_ok=True)
        with open(user_config_path, "w", encoding="utf-8") as configfile:
            self.config.write(configfile)

    def copy(self, path="config"):
        """
        Copy config files to current directory
        """
        dest_folder = os.path.join(os.getcwd(), path)
        try:
            src_dir = resource_path(path)
            if os.path.exists(src_dir):
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder, exist_ok=True)

                for root, _, files in os.walk(src_dir):
                    for file in files:
                        src_file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(src_file_path, src_dir)
                        dest_file_path = os.path.join(dest_folder, relative_path)

                        dest_file_dir = os.path.dirname(dest_file_path)
                        if not os.path.exists(dest_file_dir):
                            os.makedirs(dest_file_dir, exist_ok=True)

                        if not os.path.exists(dest_file_path):
                            shutil.copy(src_file_path, dest_file_path)
        except Exception as e:
            print(f"Failed to copy files: {str(e)}")


config = ConfigManager()
