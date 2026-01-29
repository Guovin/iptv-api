import re

import requests
from bs4 import BeautifulSoup

from utils.config import config

headers = {
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}


def get_requests(url, data=None, proxy=None, timeout=30):
    """
    Get the response by requests
    """
    if proxy is None:
        proxy = config.http_proxy
    proxies = {"http": proxy, "https": proxy} if proxy else None
    response = None
    try:
        with requests.Session() as session:
            if data:
                response = session.post(
                    url, headers=headers, data=data, proxies=proxies, timeout=timeout
                )
            else:
                response = session.get(url, headers=headers, proxies=proxies, timeout=timeout)
    except requests.RequestException as e:
        raise e

    if response is None:
        raise requests.RequestException(f"No response from {url}")

    text = re.sub(r"<!--.*?-->", "", response.text or "", flags=re.DOTALL)
    if not text.strip():
        raise requests.RequestException(f"Empty response from {url}")

    return response


def get_soup_requests(url, data=None, proxy=None, timeout=30):
    """
    Get the soup by requests
    """
    response = get_requests(url, data, proxy, timeout)
    source = re.sub(r"<!--.*?-->", "", response.text or "", flags=re.DOTALL)
    soup = BeautifulSoup(source, "html.parser")
    return soup
