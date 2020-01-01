from json import JSONDecodeError
from urllib.parse import quote_plus
from pprint import pprint

import jmespath
import requests

from crawl import get_token

if __name__ == '__main__':
    # call attendees api
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'content-type': 'application/json; charset=utf-8',
        'cache-control': 'no-cache',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }
    api_url = 'https://www.meetup.com/mu_api/urlname/events/eventId/attendees'
    event_id = '267489117'
    amount = 5000
    member_id = 250533185

    get_attendee_params = {'queries': f"(endpoint:awskrug/events/{event_id}/rsvps,meta:(method:get),params:(desc:!t,fields:'answers,pay_status,self,web_actions,attendance_status',only:'answers,response,attendance_status,guests,member,pay_status,updated',order:time),ref:eventAttendees_awskrug_{event_id},type:attendees)"}
    with get_token(headless=False) as cookies:
        sess = requests.Session()
        for cookie in cookies:
            sess.cookies.set(cookie['name'], cookie['value'])
        resp = sess.get(
            api_url,
            params=get_attendee_params,
            headers=headers,
        )
        attendees = resp.json()

    get_attendee_query = 'responses[0].value[].{updated: updated, id: member.id, name: member.name, pay_status: pay_status, response: response, bio: answers[0].answer}'
    attendees_data = jmespath.search(get_attendee_query, attendees)
    pprint(attendees_data)

    # post
    '''
{"responses":[{"ref":"markAsPaid","value":{"id":"43401196","confirm_code":"M43401196"},"meta":{"server":"ip-10-192-12-176","requestId":"210497bc-89a3-4712-9418-4e3de626d00c","endpoint":"awskrug/events/267489117/payments","statusCode":200}}]}
    '''
    headers['content-type'] = 'application/x-www-form-urlencoded'
    headers['sec-fetch-mode'] = 'cors'
    headers['sec-fetch-site'] = 'same-origin'
    headers['x-meetup-activity'] = 'standardized_url=%2Furlname%2Fevents%2FeventId%2Fattendees&standardized_referer=%2Furlname%2Fevents%2FeventId'

    post_attendee_data = quote_plus(f"(endpoint:awskrug/events/{event_id}/payments,meta:(method:post),params:(amount:{amount},eventId:'{event_id}',member:{member_id},urlname:awskrug),ref:markAsPaid)")
    print(post_attendee_data)
    with get_token(headless=False) as cookies:
        sess = requests.Session()
        for cookie in cookies:
            sess.cookies.set(cookie['name'], cookie['value'])
        print(b'queries=' + bytes(post_attendee_data, 'utf-8'))
        resp = sess.post(
            api_url,
            data=b'queries=' + bytes(post_attendee_data, 'utf-8'),
            headers=headers,
        )
        print(resp.request.headers)
        try:
            ack = resp.json()
        except JSONDecodeError:
            ack = resp.content
    pprint(ack)
