from json import JSONDecodeError
from pprint import pprint
from urllib.parse import quote_plus

import jmespath
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
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-meetup-activity': 'standardized_url=%2Furlname%2Fevents%2FeventId%2Fattendees&standardized_referer=%2Furlname%2Fevents%2FeventId',
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
        get_attendee_params = {'queries': f"(endpoint:awskrug/events/{self.event_id}/rsvps,meta:(method:get),params:(desc:!t,fields:'answers,pay_status,self,web_actions,attendance_status',only:'answers,response,attendance_status,guests,member,pay_status,updated',order:time),ref:eventAttendees_awskrug_{self.event_id},type:attendees)"}
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
        assert self.event_id is not None
        post_attendee_data = quote_plus(f"(endpoint:awskrug/events/{self.event_id}/payments,meta:(method:post),params:(amount:{self.amount},eventId:'{self.event_id}',member:{self.member_id},urlname:awskrug),ref:markAsPaid)")
        self.req_headers['content-type'] = 'application/x-www-form-urlencoded'

        response = super().post(
            self.api_url,
            data=b'queries=' + bytes(post_attendee_data, 'utf-8'),
            headers=self.req_headers,
        )
        self.set_cookies(response)
        return response


if __name__ == '__main__':
    # call attendees api
    session = MeetUpSession('267489117')

    resp = session.get()
    attendees = resp.json()
    get_attendee_query = 'responses[0].value[].{updated: updated, id: member.id, name: member.name, pay_status: pay_status, response: response, bio: answers[0].answer}'
    attendees_data = jmespath.search(get_attendee_query, attendees)
    pprint(attendees_data)

    # post
    '''
    {"responses":[{"ref":"markAsPaid","value":{"id":"43401196","confirm_code":"M43401196"},"meta":{"server":"ip-10-192-12-176","requestId":"210497bc-89a3-4712-9418-4e3de626d00c","endpoint":"awskrug/events/267489117/payments","statusCode":200}}]}
    '''
    session.set_amount(5000)
    session.set_member_id(251549990)
    resp = session.post()
    try:
        ack = resp.json()
    except JSONDecodeError:
        ack = resp.content
    pprint(ack)
