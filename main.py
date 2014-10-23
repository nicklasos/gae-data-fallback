from flask import Flask, request

try:
    from google.appengine.ext import ndb
except ImportError:
    pass

import json
import logging
import time


app = Flask(__name__)

DEFAULT_EVENTS_NAME = 'default_events'


def events_key(events_name=DEFAULT_EVENTS_NAME):
    return ndb.Key('Events', events_name)


class Event(ndb.Model):
    eventId = ndb.StringProperty(indexed=False)
    userid = ndb.StringProperty(indexed=False)
    json = ndb.TextProperty(indexed=False)
    ip = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def _get_kind(cls):
        return 'Events'


@app.route('/api/user/<user_id>', methods=['GET', 'POST'])
def data(user_id):
    """Store POST body to json field"""

    # region Save each event separated
    """
    try:
        json_content = request.json
        for e in json_content['events']:
            event = Event(parent=events_key())
            event.userid = user_id
            event.json = json.dumps(e)
            event.ip = request.remote_addr
            event.put()
    except (BadRequest, KeyError):
        return 'error'
    """
    # endregion

    if request.method == 'GET':
        logging.error('GET request')

    try:
        event = Event(parent=events_key())
        event.eventId = "%s-%s" % (user_id, time.time())
        event.userid = user_id
        event.json = request.data
        event.ip = request.remote_addr
        event.put()
    except Exception as e:
        logging.error('Data: %s' % request.data)
        # TODO: remove on prod
        # return make_response('error: %s' % e, 500)

    return 'success'


@app.route('/get/<user_id>')
def getuser(user_id):
    rows = request.args.get('rows', 20)
    # .order(-Event.date)
    user_events = Event.query(Event.userid == user_id).fetch(int(rows))
    return print_events(user_events)


@app.route('/get')
def getall():
    """Last 20 rows by default, use ?rows=15 to change it"""
    rows = request.args.get('rows', 20)
    # .order(-Event.date)
    events = Event.query().fetch(int(rows))
    return print_events(events)


@app.route('/count')
def count_events():
    return 'Events count: %s' % Event.query().count()


def print_events(events):
    result = []
    [result.append({'userId': event.userid,
                    'date': str(event.date),
                    'userData': json.loads(event.json)})
     for event in events]
    return json.dumps(result)


@app.errorhandler(404)
def page_not_found(e):
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def page_not_found(e):
    return 'Sorry, unexpected error: {}'.format(e), 500
