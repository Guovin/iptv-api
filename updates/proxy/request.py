from asyncio import Semaphore
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from utils.config import config
from utils.driver.tools import get_soup_driver
from utils.requests.tools import get_soup_requests
from utils.retry import retry_func
from utils.speed import get_delay_requests


def get_proxy_list(page_count=1):
    """
    Get proxy list, parameter page_count is the number of pages to get
    """
    url_pattern = [
        "https://www.zdaye.com/free/{}/",
        "https://www.kuaidaili.com/free/inha/{}/",
        "https://www.kuaidaili.com/free/intr/{}/",
    ]
    proxy_list = []
    urls = []
    open_driver = config.open_driver
    for page_index in range(1, page_count + 1):
        for pattern in url_pattern:
            url = pattern.format(page_index)
            urls.append(url)
    pbar = tqdm(total=len(urls), desc="Getting proxy list")

    def get_proxy(url):
        proxys = []
        try:
            if open_driver:
                soup = retry_func(lambda: get_soup_driver(url), name=url)
            else:
                try:
                    soup = retry_func(lambda: get_soup_requests(url), name=url)
                except Exception as e:
                    print(f"Error fetching {url} with requests: {e}")
            table = soup.find("table")
            trs = table.find_all("tr") if table else []
            for tr in trs[1:]:
                tds = tr.find_all("td")
                ip = tds[0].get_text().strip()
                port = tds[1].get_text().strip()
                proxy = f"http://{ip}:{port}"
                proxys.append(proxy)
        finally:
            pbar.update()
            return proxys

    max_workers = 3 if open_driver else 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(get_proxy, url) for url in urls]
        for future in futures:
            proxy_list.extend(future.result())
    pbar.close()
    return proxy_list


async def get_proxy_list_with_test(base_url, proxy_list):
    """
    Get the proxy list with speed test
    """
    if not proxy_list:
        print("No valid proxy found")
        return []
    semaphore = Semaphore(100)

    async def get_speed_task(url, timeout, proxy):
        async with semaphore:
            return await get_delay_requests(url, timeout=timeout, proxy=proxy)

    response_times = await tqdm_asyncio.gather(
        *(get_speed_task(base_url, timeout=30, proxy=url) for url in proxy_list),
        desc="Testing proxy speed",
    )
    proxy_list_with_test = [
        (proxy, response_time)
        for proxy, response_time in zip(proxy_list, response_times)
        if response_time != float("inf")
    ]
    if not proxy_list_with_test:
        print("No valid proxy found")
        return []
    proxy_list_with_test.sort(key=lambda x: x[1])
    proxy_urls = [url for url, _ in proxy_list_with_test]
    print(f"Valid proxy found: {len(proxy_urls)}")
    return proxy_urls
