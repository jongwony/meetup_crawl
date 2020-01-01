import pickle
from contextlib import contextmanager

from common.chrome import init, wait_for
from common.io import config, script_path


def login(driver):
    driver.get('https://secure.meetup.com/login/?_locale=ko-KR')
    print('login...')
    wait_for(driver, 'link_text', '구글 계정으로 로그인하기').click()
    wait_for(driver, 'tag_name', 'input').send_keys(config('email'))
    wait_for(driver, 'id', 'identifierNext').click()
    wait_for(driver, 'css_selector', '#password input').send_keys(config('secret'))
    wait_for(driver, 'id', 'passwordNext').click()
    # wait for cookies load
    wait_for(driver, 'id', 'mainKeywords')
    print('success login!')


@contextmanager
def login_check(driver):
    if wait_for(driver, 'link_text', '로그인') is not None:
        login(driver)
    yield


@contextmanager
def driver_init(headless, user_data):
    driver = init(headless=headless, user_data=user_data)
    yield driver
    driver.quit()


def refresh_token(headless, user_data):
    with driver_init(headless, user_data) as driver:
        login(driver)
        with open(script_path(config('cookie')), 'wb') as f:
            cookies = driver.get_cookies()
            pickle.dump(cookies, f)
    return cookies


@contextmanager
def get_token(headless=True, user_data=False):
    try:
        with open(script_path(config('cookie')), 'rb') as f:
            yield pickle.load(f)
    except FileNotFoundError:
        yield refresh_token(headless, user_data)
