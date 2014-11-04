# coding=utf-8
import models.event
import time
import logging
import json


def save(user_id, data, ip='undefined'):
    try:
        event = models.event.Event(parent=models.event.events_key(),
                                   eventId="%s-%s" % (user_id, time.time()),
                                   userid=user_id,
                                   json=data,
                                   ip=ip)
        event.put()
        return True

    except Exception:
        logging.error('Data: %s' % data)

    return False


def get_last_user_events(user_id, rows=20):
    user_events = models.event.Event.query(models.event.Event.userid == user_id).fetch(rows)
    return printable_events(user_events)


def get_last_events(rows=20):
    events = models.event.Event.query().order(-models.event.Event.date).fetch(rows)
    return printable_events(events)


def printable_events(events):
    result = []
    [result.append({'userId': event.userid,
                    'date': str(event.date),
                    'userData': json.loads(event.json)})
     for event in events]
    return json.dumps(result)


def entity_to_string(entity):
    return '{"userId":"%s","date":"%s","ip": "%s","json":%s}\n' % (entity['userid'],
                                                                   entity['date'],
                                                                   entity['ip'],
                                                                   entity['json'])
