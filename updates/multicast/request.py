import pickle
import urllib.parse as urlparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
from urllib.parse import parse_qs

from tqdm.asyncio import tqdm_asyncio

import utils.constants as constants
from updates.fofa import get_channels_by_fofa
from utils.channel import (
    get_results_from_multicast_soup,
    get_results_from_multicast_soup_requests,
    get_channel_multicast_name_region_type_result,
    get_channel_multicast_region_type_list,
    get_channel_multicast_result,
    get_multicast_fofa_search_urls,
    format_channel_name
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
from .update_tmp import get_multicast_region_result_by_rtp_txt

if config.open_driver:
    try:
        from selenium.webdriver.common.by import By
    except:
        pass


async def get_channels_by_multicast(names, callback=None):
    """
    Get the channels by multicast
    """
    channels = {}
    format_names = [format_channel_name(name) for name in names]
    if config.open_use_cache:
        try:
            with open(
                    resource_path("updates/multicast/cache.pkl"),
                    "rb",
            ) as file:
                cache = pickle.load(file) or {}
                for name in format_names:
                    channels[name] = cache.get(name, [])
        except:
            pass
    if config.open_request:
        pageUrl = constants.foodie_hotel_url
        open_driver = config.open_driver
        page_num = config.multicast_page_num
        multicast_region_result = get_multicast_region_result_by_rtp_txt(callback=callback)
        name_region_type_result = get_channel_multicast_name_region_type_result(
            multicast_region_result, format_names
        )
        region_type_list = get_channel_multicast_region_type_list(name_region_type_result)
        search_region_type_result = defaultdict(lambda: defaultdict(list))
        if config.open_multicast_fofa:
            fofa_search_urls = get_multicast_fofa_search_urls()
            fofa_result = await get_channels_by_fofa(
                fofa_search_urls, multicast=True, callback=callback
            )
            search_region_type_result = merge_objects(search_region_type_result, fofa_result)

        def process_channel_by_multicast(region, type):
            name = f"{region}{type}"
            info_list = []
            driver = None
            page_soup = None
            code = None
            try:
                if open_driver:
                    driver = setup_driver()
                    try:
                        retry_func(
                            lambda: driver.get(pageUrl),
                            name=t("msg.mode_search_name").format(mode=t("name.multicast"), name=name)
                        )
                    except Exception as e:
                        print(e)
                        driver.close()
                        driver.quit()
                        driver = setup_driver()
                        driver.get(pageUrl)
                    search_submit(driver, name)
                else:
                    post_form = {"saerch": name}
                    try:
                        page_soup = retry_func(
                            lambda: get_soup_requests(pageUrl, data=post_form),
                            name=t("msg.mode_search_name").format(mode=t("name.multicast"), name=name)
                        )
                    except Exception as e:
                        print(e)
                    if not page_soup:
                        print(t("msg.request_failed").format(name=name))
                        return {"region": region, "type": type, "data": info_list}
                    else:
                        a_tags = page_soup.find_all("a", href=True)
                        for a_tag in a_tags:
                            href_value = a_tag["href"]
                            parsed_url = urlparse.urlparse(href_value)
                            code = parse_qs(parsed_url.query).get("code", [None])[0]
                            if code:
                                break
                for page in range(1, page_num + 1):
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
                                    f"{pageUrl}?net={name}&page={page}&code={code}"
                                )
                                page_soup = retry_func(
                                    lambda: get_soup_requests(request_url),
                                    name=t("msg.mode_search_name_page").format(mode=t("name.multicast"), name=name,
                                                                               page=page)
                                )
                        soup = get_soup(driver.page_source) if open_driver else page_soup
                        if soup:
                            if "About 0 results" in soup.text:
                                break
                            results = (
                                get_results_from_multicast_soup(soup)
                                if open_driver
                                else get_results_from_multicast_soup_requests(soup)
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
                        t("msg.progress_desc").format(name=t("name.multicast"),
                                                      remaining_total=region_type_list_len - pbar.n,
                                                      item_name=t("name.region"),
                                                      remaining_time=get_pbar_remaining(n=pbar.n, total=pbar.total,
                                                                                        start_time=start_time)),
                        int((pbar.n / region_type_list_len) * 100),
                    )
                return {"region": region, "type": type, "data": info_list}

        if config.open_multicast_foodie:
            region_type_list_len = len(region_type_list)
            pbar = tqdm_asyncio(total=region_type_list_len, desc=t("pbar.name_search").format(name=t("name.multicast")))
            if callback:
                callback(
                    f"{t("pbar.getting_name").format(name=t("name.multicast"))}",
                    0,
                )
            start_time = time()
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(process_channel_by_multicast, region, type): (
                        region,
                        type,
                    )
                    for region, type in region_type_list
                }

                for future in as_completed(futures):
                    region, type = futures[future]
                    result = future.result()
                    data = result.get("data")

                    if data:
                        for item in data:
                            url = item.get("url")
                            date = item.get("date")
                            if url:
                                search_region_type_result[region][type].append(
                                    {"url": url, "date": date}
                                )
            pbar.close()
        request_channels = get_channel_multicast_result(
            name_region_type_result, search_region_type_result
        )
        channels = merge_objects(channels, request_channels)
    return channels
