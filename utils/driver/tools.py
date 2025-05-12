import re
from time import sleep

from bs4 import BeautifulSoup

from utils.config import config
from utils.retry import (
    retry_func,
    locate_element_with_retry,
    find_clickable_element_with_retry,
)

if config.open_driver:
    try:
        from selenium.webdriver.common.by import By
    except:
        pass


def get_soup_driver(url):
    """
    Get the soup by driver
    """
    from utils.driver.setup import setup_driver

    driver = setup_driver()
    retry_func(lambda: driver.get(url), name=url)
    sleep(1)
    source = re.sub(
        r"<!--.*?-->",
        "",
        driver.page_source,
        flags=re.DOTALL,
    )
    soup = BeautifulSoup(source, "html.parser")
    driver.close()
    driver.quit()
    return soup


def search_submit(driver, name):
    """
    Input key word and submit with driver
    """
    search_box = locate_element_with_retry(driver, (By.XPATH, '//input[@type="text"]'))
    if not search_box:
        return
    search_box.clear()
    search_box.send_keys(name)
    submit_button = find_clickable_element_with_retry(
        driver, (By.XPATH, '//input[@type="submit"]')
    )
    if not submit_button:
        return
    driver.execute_script("arguments[0].click();", submit_button)
