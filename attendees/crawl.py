import pickle
from contextlib import contextmanager

from attendees.common.chrome import init, wait_for
from attendees.common.io import config, script_path


def login(driver, event_id):
    driver.get('https://secure.meetup.com/login/?_locale=ko-KR')
    print('login...')
    wait_for(driver, 'link_text', '구글 계정으로 로그인하기').click()
    wait_for(driver, 'tag_name', 'input').send_keys(config('email'))
    wait_for(driver, 'id', 'identifierNext').click()
    wait_for(driver, 'css_selector', '#password input').send_keys(config('secret'))
    wait_for(driver, 'id', 'passwordNext').click()
    # wait for cookies load
    wait_for(driver, 'id', 'mainKeywords')
    driver.get(f'https://www.meetup.com/ko-KR/awskrug/events/{event_id}/attendees/')
    wait_for(driver, 'css_selector', 'ul.list--infinite-scroll.attendees-list.list')
    print('success login!')


@contextmanager
def driver_init(headless, user_data):
    driver = init(headless=headless, user_data=user_data)
    yield driver
    driver.quit()


def refresh_token(event_id, headless, user_data):
    with driver_init(headless, user_data) as driver:
        login(driver, event_id)
        with open(script_path(config('cookie')), 'wb') as f:
            cookies = driver.get_cookies()
            pickle.dump(cookies, f)
    return cookies


@contextmanager
def get_token(event_id, headless=True, user_data=False):
    try:
        with open(script_path(config('cookie')), 'rb') as f:
            yield pickle.load(f)
    except FileNotFoundError:
        yield refresh_token(event_id, headless, user_data)
