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

session = requests.Session()


def get_source_requests(url, data=None, proxy=None, timeout=30):
    """
    Get the source by requests
    """

    if (proxy == None and config.have_local_proxy())
    {
        proxy = get_local_proxy()
    }
    if data:
        response = session.post(
            url, headers=headers, data=data, proxies=proxy, timeout=timeout
        )
    else:
        response = session.get(url, headers=headers, proxies=proxy, timeout=timeout)
    source = re.sub(
        r"<!--.*?-->",
        "",
        response.text,
        flags=re.DOTALL,
    )
    return source


def get_soup_requests(url, data=None, proxy=None, timeout=30):
    """
    Get the soup by requests
    """
    source = get_source_requests(url, data, proxy, timeout)
    soup = BeautifulSoup(source, "html.parser")
    return soup

def get_local_proxy():
    """
    Get the peoxy from config.ini
    """
    open_driver = config.open_driver

    http_proxy = config.http_proxy
    https_proxy = config.https_proxy
    socks_proxy = config.socks_proxy

    proxies = []

    if socks_proxy:
        proxies['http'] = socks_proxy
        proxies['https'] = socks_proxy
    elif http_proxy and https_proxy:
            proxies['http'] = http_proxy
            proxies['https'] = https_proxy
    elif http_proxy:
            proxies['http'] = http_proxy
            proxies['https'] = http_proxy
    elif https_proxy:
            proxies['http'] = https_proxy
            proxies['https'] = https_proxy
    else:
        return None

    return proxies

def close_session():
    """
    Close the requests session
    """
    session.close()
