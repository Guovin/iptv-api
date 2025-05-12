import re

import requests
from bs4 import BeautifulSoup

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
    proxies = {"http": proxy}
    if data:
        response = session.post(
            url, headers=headers, data=data, proxies=proxies, timeout=timeout
        )
    else:
        response = session.get(url, headers=headers, proxies=proxies, timeout=timeout)
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


def close_session():
    """
    Close the requests session
    """
    session.close()
