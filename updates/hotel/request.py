import pickle
import urllib.parse as urlparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
from urllib.parse import parse_qs

from tqdm.asyncio import tqdm_asyncio

import updates.fofa.fofa_map as fofa_map
import utils.constants as constants
from updates.subscribe import get_channels_by_subscribe_urls
from utils.channel import (
    get_results_from_multicast_soup,
    get_results_from_multicast_soup_requests,
)
from utils.config import config
from utils.driver.setup import setup_driver
from utils.driver.tools import search_submit
from utils.i18n import t
from utils.requests.tools import get_soup_requests
from utils.retry import (
    retry_func,
    find_clickable_element_with_retry,
)
from utils.tools import get_pbar_remaining, get_soup, merge_objects, resource_path

if config.open_driver:
    try:
        from selenium.webdriver.common.by import By
    except:
        pass


async def get_channels_by_hotel(callback=None):
    """
    Get the channels by hotel
    """
    channels = {}
    if config.open_use_cache:
        try:
            with open(
                    resource_path("updates/hotel/cache.pkl"),
                    "rb",
            ) as file:
                channels = pickle.load(file) or {}
        except:
            pass
    if config.open_request:
        page_url = constants.foodie_hotel_url
        open_driver = config.open_driver
        page_num = config.hotel_page_num
        region_list = config.hotel_region_list
        if "all" in region_list or "ALL" in region_list or "全部" in region_list:
            region_list = list(getattr(fofa_map, "region_url").keys())
        start_time = time()

        def process_region_by_hotel(region):
            name = f"{region}"
            info_list = []
            driver = None
            page_soup = None
            code = None
            try:
                if open_driver:
                    driver = setup_driver()
                    try:
                        retry_func(
                            lambda: driver.get(page_url),
                            name=t("msg.mode_search_name").format(mode=t("name.hotel_foodie"), name=name)
                        )
                    except Exception as e:
                        print(e)
                        driver.close()
                        driver.quit()
                        driver = setup_driver()
                        driver.get(page_url)
                    search_submit(driver, name)
                else:
                    post_form = {"saerch": name}
                    try:
                        page_soup = retry_func(
                            lambda: get_soup_requests(page_url, data=post_form),
                            name=t("msg.mode_search_name").format(mode=t("name.hotel_foodie"), name=name)
                        )
                    except Exception as e:
                        print(e)
                    if not page_soup:
                        print(t("msg.request_failed").format(name=name))
                        return info_list
                    else:
                        a_tags = page_soup.find_all("a", href=True)
                        for a_tag in a_tags:
                            href_value = a_tag["href"]
                            parsed_url = urlparse.urlparse(href_value)
                            code = parse_qs(parsed_url.query).get("code", [None])[0]
                            if code:
                                break
                # retry_limit = 3
                for page in range(1, page_num + 1):
                    # retries = 0
                    # if not open_driver and page == 1:
                    #     retries = 2
                    # while retries < retry_limit:
                    try:
                        if page > 1:
                            if open_driver:
                                page_link = find_clickable_element_with_retry(
                                    driver,
                                    (
                                        By.XPATH,
                                        f'//a[contains(@href, "={page}") and contains(@href, "{name}")]',
                                    ),
                                )
                                if not page_link:
                                    break
                                driver.execute_script("arguments[0].click();", page_link)
                            else:
                                request_url = (
                                    f"{page_url}?net={name}&page={page}&code={code}"
                                )
                                page_soup = retry_func(
                                    lambda: get_soup_requests(request_url),
                                    name=t("msg.mode_search_name_page").format(mode=t("name.hotel_foodie"), name=name,
                                                                               page=page)
                                )
                        soup = get_soup(driver.page_source) if open_driver else page_soup
                        if soup:
                            if "About 0 results" in soup.text:
                                break
                            results = (
                                get_results_from_multicast_soup(soup, hotel=True)
                                if open_driver
                                else get_results_from_multicast_soup_requests(
                                    soup, hotel=True
                                )
                            )
                            print(t("msg.name_page_results_number").format(name=name, page=page, number=len(results)))
                            if len(results) == 0:
                                print(t("msg.name_no_results").format(name=name))
                            info_list = info_list + results
                        else:
                            print(t("msg.name_page_element_empty").format(name=name))
                            if page != page_num and open_driver:
                                driver.refresh()
                    except Exception as e:
                        print(t("msg.name_page_error_info").format(name=name, page=page, info=e))
                        continue
            except Exception as e:
                print(t("msg.name_search_error_info").format(name=name, info=e))
                pass
            finally:
                if driver:
                    driver.close()
                    driver.quit()
                pbar.update()
                if callback:
                    callback(
                        t("msg.progress_desc").format(name=t("name.hotel_foodie"),
                                                      remaining_total=region_list_len - pbar.n,
                                                      item_name=t("name.region"),
                                                      remaining_time=get_pbar_remaining(n=pbar.n, total=pbar.total,
                                                                                        start_time=start_time)),
                        int((pbar.n / region_list_len) * 100),
                    )
                return info_list

        region_list_len = len(region_list)
        pbar = tqdm_asyncio(total=region_list_len, desc=t("pbar.name_search").format(name=t("name.hotel_foodie")))
        if callback:
            callback(f"{t("pbar.getting_name").format(name=t("name.hotel_foodie"))}", 0)
        search_region_result = defaultdict(list)
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(process_region_by_hotel, region): region
                for region in region_list
            }

            for future in as_completed(futures):
                region = futures[future]
                result = future.result()

                if result:
                    for item in result:
                        url = item.get("url")
                        date = item.get("date")
                        if url:
                            search_region_result[region].append({"url": url, "date": date})
        urls = [
            {"region": region, "url": f"http://{item["url"]}/ZHGXTV/Public/json/live_interface.txt"}
            for region, result in search_region_result.items()
            for item in result
        ]
        request_channels = await get_channels_by_subscribe_urls(
            urls, hotel=True, retry=False, error_print=False, pbar_desc=t("msg.processing_get_hotel_json")
        )
        channels = merge_objects(channels, request_channels)
        pbar.close()
    return channels
