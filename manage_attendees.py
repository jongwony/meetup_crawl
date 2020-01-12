from json import JSONDecodeError
from pprint import pprint

import jmespath

from session_control import MeetUpSession


def ack(session: MeetUpSession, method: str, *args, **kwargs):
    response = getattr(session, method)(*args, **kwargs)
    try:
        return response.json()
    except JSONDecodeError:
        return response.content


def get_attendees(session: MeetUpSession):
    response = ack(session, 'get')
    filter_query = "responses[0].value[].{updated: updated, id: member.id, name: member.name, " \
                   "pay_status: pay_status, response: response, bio: answers[0].answer}"
    return jmespath.search(filter_query, response)


def set_paid(session: MeetUpSession, member_id, amount):
    session.set_member_id(member_id)
    session.set_amount(amount)
    response = ack(session, 'post')
    pprint(response)


if __name__ == '__main__':
    # call attendees api
    event = MeetUpSession(267489117)
    attendees_data = get_attendees(event)
    pprint(attendees_data)

    # post
    '''
    {"responses":[{"ref":"markAsPaid","value":{"id":"43401196","confirm_code":"M43401196"},"meta":{"server":"ip-10-192-12-176","requestId":"210497bc-89a3-4712-9418-4e3de626d00c","endpoint":"awskrug/events/267489117/payments","statusCode":200}}]}
    '''
    # post_response = set_paid(event, 251549990, 5000)
    # pprint(post_response)
