from concurrent.futures import ThreadPoolExecutor
from time import time

from tqdm.asyncio import tqdm_asyncio

import utils.constants as constants
from utils.channel import (
    format_channel_name,
    get_results_from_soup,
    get_results_from_soup_requests,
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
from utils.tools import (
    get_pbar_remaining,
    get_soup
)

if config.open_driver:
    try:
        from selenium.webdriver.common.by import By
    except:
        pass


async def get_channels_by_online_search(names, callback=None):
    """
    Get the channels by online search
    """
    channels = {}
    pageUrl = constants.foodie_url
    if not pageUrl:
        return channels
    open_driver = config.open_driver
    page_num = config.online_search_page_num
    start_time = time()

    def process_channel_by_online_search(name):
        info_list = []
        driver = None
        page_soup = None
        try:
            if open_driver:
                driver = setup_driver()
                try:
                    retry_func(
                        lambda: driver.get(pageUrl),
                        name=t("msg.mode_search_name").format(mode=t("name.online_search"), name=name)
                    )
                except Exception as e:
                    print(e)
                    driver.close()
                    driver.quit()
                    driver = setup_driver()
                    driver.get(pageUrl)
                search_submit(driver, name)
            else:
                request_url = f"{pageUrl}?s={name}"
                try:
                    page_soup = retry_func(
                        lambda: get_soup_requests(request_url),
                        name=t("msg.mode_search_name").format(mode=t("name.online_search"), name=name)
                    )
                except Exception as e:
                    print(e)
                if not page_soup:
                    print(t("msg.request_failed").format(name=name))
                    return
            retry_limit = 3
            for page in range(1, page_num + 1):
                retries = 0
                if not open_driver and page == 1:
                    retries = 2
                while retries < retry_limit:
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
                                driver.execute_script(
                                    "arguments[0].click();", page_link
                                )
                            else:
                                request_url = f"{pageUrl}?s={name}&page={page}"
                                page_soup = retry_func(
                                    lambda: get_soup_requests(request_url),
                                    name=t("msg.mode_search_name_page").format(mode=t("name.online_search"), name=name,
                                                                               page=page)
                                )
                        soup = (
                            get_soup(driver.page_source) if open_driver else page_soup
                        )
                        if soup:
                            if "About 0 results" in soup.text:
                                retries += 1
                                continue
                            results = (
                                get_results_from_soup(soup, name)
                                if open_driver
                                else get_results_from_soup_requests(soup, name)
                            )
                            print(t("msg.name_page_results_number").format(name=name, page=page, number=len(results)))
                            if len(results) == 0:
                                print(
                                    t("msg.name_no_results_refresh_retrying").format(name=name)
                                )
                                if open_driver:
                                    driver.refresh()
                                retries += 1
                                continue
                            elif len(results) <= 3:
                                if open_driver:
                                    next_page_link = find_clickable_element_with_retry(
                                        driver,
                                        (
                                            By.XPATH,
                                            f'//a[contains(@href, "={page + 1}") and contains(@href, "{name}")]',
                                        ),
                                        retries=1,
                                    )
                                    if next_page_link:
                                        driver.close()
                                        driver.quit()
                                        driver = setup_driver()
                                        search_submit(driver, name)
                                retries += 1
                                continue
                            for result in results:
                                url = result["url"]
                                if url:
                                    info_list.append({
                                        "url": url,
                                        "date": result["date"],
                                        "resolution": result["resolution"]
                                    })
                            break
                        else:
                            print(
                                t("msg.name_no_elements_refresh_retrying").format(name=name)
                            )
                            if open_driver:
                                driver.refresh()
                            retries += 1
                            continue
                    except Exception as e:
                        print(t("msg.name_page_error_info").format(name=name, page=page, info=e))
                        break
                if retries == retry_limit:
                    print(t("msg.reach_retry_limit_jump_next").format(name=name))
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
                    t("msg.progress_desc").format(name=t("name.online_search"),
                                                  remaining_total=names_len - pbar.n,
                                                  item_name=t("name.channel"),
                                                  remaining_time=get_pbar_remaining(n=pbar.n, total=pbar.total,
                                                                                    start_time=start_time)),
                    int((pbar.n / names_len) * 100),
                )
            return {"name": format_channel_name(name), "data": info_list}

    names_len = len(names)
    pbar = tqdm_asyncio(total=names_len, desc=t("pbar.name_search").format(name=t("name.online_search")))
    if callback:
        callback(f"{t("pbar.getting_name").format(name=t("name.online_search"))}", 0)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(process_channel_by_online_search, name) for name in names
        ]
        for future in futures:
            result = future.result()
            name = result.get("name")
            data = result.get("data", [])
            if name:
                channels[name] = data
    pbar.close()
    return channels
