import os
import platform

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from common.io import script_path


def wait_for(driver, by, value, timeout=3):
    """
    class By(object):
        ID = "id"
        XPATH = "xpath"
        LINK_TEXT = "link text"
        PARTIAL_LINK_TEXT = "partial link text"
        NAME = "name"
        TAG_NAME = "tag name"
        CLASS_NAME = "class name"
        CSS_SELECTOR = "css selector"
    """
    try:
        return WebDriverWait(driver, timeout).until(
            presence_of_element_located((getattr(By, by.upper()), value))
        )
    except TimeoutException:
        print(f'timeout: {value} not found')


def user_data_dir():
    home = os.path.expanduser
    join = os.path.join
    return {
        'Darwin': home(join('~', 'Library', 'Application Support', 'Google', 'Chrome')),
        'Linux': home(join('~', '.config', 'google-chrome')),
        'Windows': home(join('~', 'AppData', 'Local', 'Google', 'Chrome', 'User Data')),
    }.get(platform.system())


def init(headless=True, user_data=False):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36")
    options.add_argument("lang=ko_KR")

    if user_data:
        options.add_argument(f'user-data-dir={user_data_dir()}')
        options.add_argument('start-maximized')

    return webdriver.Chrome(
        script_path('common', 'chromedriver'),
        options=options,
    )
