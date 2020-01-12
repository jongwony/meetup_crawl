from urllib.parse import quote_plus

import requests

from crawl import get_token


class MeetUpSession(requests.Session):
    def __init__(self, event_id):
        super().__init__()
        self.event_id = event_id
        self.member_id = None
        self.amount = None
        self.api_url = 'https://www.meetup.com/mu_api/urlname/events/eventId/attendees'
        self.req_headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'content-type': 'application/json; charset=utf-8',
            'cache-control': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-meetup-activity': 'standardized_url=%2Furlname%2Fevents%2FeventId%2Fattendees&'
                                 'standardized_referer=%2Furlname%2Fevents%2FeventId',
            'referer': f'https://www.meetup.com/ko-KR/awskrug/events/{self.event_id}/attendees/',
        }
        with get_token(self.event_id, headless=False) as cookies:
            for cookie in cookies:
                self.cookies.set(cookie['name'], cookie['value'], domain='.meetup.com')

    def set_member_id(self, member_id):
        self.member_id = member_id

    def set_amount(self, amount):
        self.amount = amount

    def set_cookies(self, response):
        set_cookie = response.headers['set-cookie']
        dict_cookies = dict([
            cookie for x in set_cookie.split()
            if len(cookie := x.strip(';').split('=')) == 2
        ])
        self.req_headers['x-mwp-csrf'] = dict_cookies['x-mwp-csrf-header']
        for k, v in dict_cookies.items():
            self.cookies.set(k, v, domain='.meetup.com')

    def get(self, **kwargs):
        assert self.event_id is not None
        get_attendee_params = {
            'queries': f"(endpoint:awskrug/events/{self.event_id}/rsvps,"
                       f"meta:(method:get),"
                       f"params:(desc:!t,fields:'answers,pay_status,self,web_actions,attendance_status',"
                       f"only:'answers,response,attendance_status,guests,member,pay_status,updated',order:time),"
                       f"ref:eventAttendees_awskrug_{self.event_id},"
                       f"type:attendees)"
        }
        response = super().get(
            self.api_url,
            params=get_attendee_params,
            headers=self.req_headers,
        )
        self.set_cookies(response)
        return response

    def post(self, **kwargs):
        assert self.member_id is not None
        assert self.amount is not None
        post_attendee_data = quote_plus(
            f"(endpoint:awskrug/events/{self.event_id}/payments,"
            f"meta:(method:post),"
            f"params:(amount:{self.amount},eventId:'{self.event_id}',member:{self.member_id},urlname:awskrug),"
            f"ref:markAsPaid)"
        )
        self.req_headers['content-type'] = 'application/x-www-form-urlencoded'

        response = super().post(
            self.api_url,
            data=b'queries=' + bytes(post_attendee_data, 'utf-8'),
            headers=self.req_headers,
        )
        self.set_cookies(response)
        return response
