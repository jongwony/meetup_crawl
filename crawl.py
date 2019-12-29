from contextlib import contextmanager

from common.chrome import init, wait_for
from common.io import config


def login():
    driver.get('https://secure.meetup.com/login/?_locale=ko-KR')
    wait_for(driver, 'link_text', '구글 계정으로 로그인하기').click()
    wait_for(driver, 'tag_name', 'input').send_keys(config('email'))
    wait_for(driver, 'id', 'identifierNext').click()
    wait_for(driver, 'css_selector', '#password input').send_keys(config('secret'))
    wait_for(driver, 'id', 'passwordNext').click()


@contextmanager
def login_check():
    if wait_for(driver, 'link_text', '로그인') is not None:
        login()
    yield


if __name__ == '__main__':
    user_data = True
    driver = init(headless=False, user_data=user_data)

    # init meet-up
    if not user_data:
        login()
    else:
        driver.get('https://www.meetup.com/ko-KR')

    with login_check():
        # driver.get('https://www.meetup.com/ko-KR/awskrug/events/267489117/')
        driver.get('https://www.meetup.com/ko-KR/awskrug/events/263931822/attendees/')

        # scroll down
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        source = driver.page_source
        cookies = driver.get_cookies()

    driver.quit()
