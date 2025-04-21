import pickle
import re
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time

from requests import get
from tqdm.asyncio import tqdm_asyncio

import updates.fofa.fofa_map as fofa_map
import utils.constants as constants
from updates.proxy import get_proxy, get_proxy_next
from utils.channel import format_channel_name
from utils.config import config
from utils.requests.tools import get_source_requests, close_session
from utils.retry import retry_func
from utils.tools import merge_objects, get_pbar_remaining, resource_path


def get_fofa_urls_from_region_list():
    """
    Get the FOFA url from region
    """
    urls = []
    region_url = getattr(fofa_map, "region_url")
    region_list = config.hotel_region_list
    if "all" in region_list or "ALL" in region_list or "全部" in region_list:
        urls = [
            (url, region)
            for region, url_list in region_url.items()
            for url in url_list
            if url
        ]
    else:
        for region in region_list:
            if region in region_url:
                urls.extend([(url, region) for url in region_url[region] if url])
    return urls


def update_fofa_region_result_tmp(result, multicast=False):
    """
    Update fofa region result tmp
    """
    tmp_result = get_fofa_region_result_tmp(multicast=multicast)
    total_result = merge_objects(tmp_result, result)
    with open(
            resource_path(
                f"updates/fofa/fofa_{'multicast' if multicast else 'hotel'}_region_result.pkl"
            ),
            "wb",
    ) as file:
        pickle.dump(total_result, file)


def get_fofa_region_result_tmp(multicast: False):
    try:
        with open(
                resource_path(
                    f"updates/fofa/fofa_{'multicast' if multicast else 'hotel'}_region_result.pkl"
                ),
                "rb",
        ) as file:
            return pickle.load(file)
    except:
        return {}


async def get_channels_by_fofa(urls=None, multicast=False, callback=None):
    """
    Get the channel by FOFA
    """
    fofa_results = {}
    if config.open_use_cache:
        fofa_results = get_fofa_region_result_tmp(multicast=multicast)
    if config.open_request:
        fofa_urls = urls if urls else get_fofa_urls_from_region_list()
        fofa_urls_len = len(fofa_urls)
        pbar = tqdm_asyncio(
            total=fofa_urls_len,
            desc=f"Processing fofa for {'multicast' if multicast else 'hotel'}",
        )
        start_time = time()
        mode_name = "组播" if multicast else "酒店"
        if callback:
            callback(
                f"正在获取Fofa{mode_name}源, 共{fofa_urls_len}个查询地址",
                0,
            )
        proxy = None
        open_proxy = config.open_proxy
        open_driver = config.open_driver
        if open_driver:
            from utils.driver.setup import setup_driver
        open_sort = config.open_sort
        if open_proxy:
            test_url = fofa_urls[0][0]
            proxy = await get_proxy(test_url, best=True, with_test=True)
        cancel_event = threading.Event()
        hotel_name = constants.origin_map["hotel"]

        def process_fofa_channels(fofa_info):
            nonlocal proxy
            if cancel_event.is_set():
                return {}
            fofa_url = fofa_info[0]
            results = defaultdict(lambda: defaultdict(list))
            driver = None
            try:
                if open_driver:
                    driver = setup_driver(proxy)
                    try:
                        retry_func(lambda: driver.get(fofa_url), name=fofa_url)
                    except Exception as e:
                        if open_proxy:
                            proxy = get_proxy_next()
                        driver.close()
                        driver.quit()
                        driver = setup_driver(proxy)
                        driver.get(fofa_url)
                    page_source = driver.page_source
                else:
                    page_source = retry_func(
                        lambda: get_source_requests(fofa_url), name=fofa_url
                    )
                if any(keyword in page_source for keyword in ["访问异常", "禁止访问", "资源访问每天限制"]):
                    cancel_event.set()
                    raise ValueError("Limited access to fofa page")
                fofa_source = re.sub(r"<!--.*?-->", "", page_source, flags=re.DOTALL)
                urls = set(re.findall(r"https?://[\w\.-]+:\d+", fofa_source))
                if multicast:
                    region = fofa_info[1]
                    type = fofa_info[2]
                    multicast_result = [(url, None, None) for url in urls]
                    results[region][type] = multicast_result
                else:
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        futures = [
                            executor.submit(
                                process_fofa_json_url,
                                url,
                                fofa_info[1],
                                open_sort,
                                hotel_name,
                            )
                            for url in urls
                        ]
                        for future in futures:
                            results = merge_objects(results, future.result())
                return results
            except ValueError as e:
                raise e
            except Exception as e:
                print(e)
            finally:
                if driver:
                    driver.close()
                    driver.quit()
                pbar.update()
                remain = fofa_urls_len - pbar.n
                if callback:
                    callback(
                        f"正在获取Fofa{mode_name}源, 剩余{remain}个查询地址待获取, 预计剩余时间: {get_pbar_remaining(n=pbar.n, total=pbar.total, start_time=start_time)}",
                        int((pbar.n / fofa_urls_len) * 100),
                    )

        max_workers = 3 if open_driver else 10
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_fofa_channels, fofa_url) for fofa_url in fofa_urls
            ]
            try:
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        fofa_results = merge_objects(fofa_results, result)
            except ValueError as e:
                if "Limited access to fofa page" in str(e):
                    for future in futures:
                        future.cancel()
        if fofa_results:
            update_fofa_region_result_tmp(fofa_results, multicast=multicast)
        pbar.n = fofa_urls_len
        pbar.update(0)
        if callback:
            callback(
                f"正在获取Fofa{mode_name}源",
                100,
            )
        if not open_driver:
            close_session()
        pbar.close()
    return fofa_results


def process_fofa_json_url(url, region, open_sort, hotel_name="酒店源"):
    """
    Process the FOFA json url
    """
    channels = {}
    try:
        final_url = url + "/iptv/live/1000.json?key=txiptv"
        # response = retry_func(
        #     lambda: get(final_url, timeout=timeout),
        #     name=final_url,
        # )
        response = get(final_url, timeout=config.request_timeout)
        try:
            json_data = response.json()
            if json_data["code"] == 0:
                try:
                    for item in json_data["data"]:
                        if isinstance(item, dict):
                            item_name = format_channel_name(item.get("name"))
                            item_url = item.get("url").strip()
                            if item_name and item_url:
                                data = {"url": f"{url}{item_url}", "extra_info": f"{region}{hotel_name}"}
                                if item_name not in channels:
                                    channels[item_name] = [data]
                                else:
                                    channels[item_name].append(data)
                except Exception as e:
                    # print(f"Error on fofa: {e}")
                    pass
        except Exception as e:
            # print(f"{url}: {e}")
            pass
    except Exception as e:
        # print(f"{url}: {e}")
        pass
    finally:
        return channels
