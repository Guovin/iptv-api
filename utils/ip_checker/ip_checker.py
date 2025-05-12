import socket
from urllib.parse import urlparse

import ipdb

from utils.tools import resource_path


class IPChecker:
    def __init__(self):
        self.db = ipdb.City(resource_path("utils/ip_checker/data/qqwry.ipdb"))
        self.url_host = {}
        self.host_ip = {}
        self.host_ipv_type = {}

    def get_host(self, url: str) -> str:
        """
        Get the host from a URL
        """
        if url in self.url_host:
            return self.url_host[url]

        host = urlparse(url).hostname or url
        self.url_host[url] = host
        return host

    def get_ip(self, url: str) -> str | None:
        """
        Get the IP from a URL
        """
        host = self.get_host(url)
        if host in self.host_ip:
            return self.host_ip[host]

        self.get_ipv_type(url)
        return self.host_ip.get(host)

    def get_ipv_type(self, url: str) -> str:
        """
        Get the IPv type of URL
        """
        host = self.get_host(url)
        if host in self.host_ipv_type:
            return self.host_ipv_type[host]

        try:
            addr_info = socket.getaddrinfo(host, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            ip = next((info[4][0] for info in addr_info if info[0] == socket.AF_INET6), None)
            if not ip:
                ip = next((info[4][0] for info in addr_info if info[0] == socket.AF_INET), None)
            ipv_type = "ipv6" if any(info[0] == socket.AF_INET6 for info in addr_info) else "ipv4"
        except socket.gaierror:
            ip = None
            ipv_type = "ipv4"

        self.host_ip[host] = ip
        self.host_ipv_type[host] = ipv_type
        return ipv_type

    def find_map(self, ip: str) -> tuple[str | None, str | None]:
        """
        Find the IP address and return the location and ISP
        :param ip: The IP address to find
        :return: A tuple of (location, ISP)
        """
        try:
            result = self.db.find_map(ip, "CN")
            if not result:
                return None, None

            location_parts = [
                result.get('country_name', ''),
                result.get('region_name', ''),
                result.get('city_name', '')
            ]
            location = "-".join(filter(None, location_parts))
            isp = result.get('isp_domain', None)

            return location, isp
        except Exception as e:
            print(f"Error on finding ip location and ISP: {e}")
            return None, None
