import webapp2
import time
import json
import logging

try:
    from google.appengine.ext import ndb
except ImportError:
    pass

DEFAULT_EVENTS_NAME = 'default_events'


def events_key(events_name=DEFAULT_EVENTS_NAME):
    return ndb.Key('Events', events_name)


class Event(ndb.Model):
    kind_name = 'Events'

    eventId = ndb.StringProperty(indexed=False)
    userid = ndb.StringProperty(indexed=False)
    json = ndb.TextProperty(indexed=False)
    ip = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def _get_kind(cls):
        return cls.kind_name

    @staticmethod
    def set_kind_name(name):
        Event.kind_name = name


class SaveEventsHandler(webapp2.RequestHandler):
    def get(self, user_id):
        logging.error('GET request')
        self.post(user_id)

    def post(self, user_id):
        self.response.headers['Content-Type'] = 'text/plain'
        try:
            Event.set_kind_name('Events-1')
            event = Event(parent=events_key(),
                          eventId="%s-%s" % (user_id, time.time()),
                          userid=user_id,
                          json=self.request.body,
                          ip=self.request.remote_addr)
            event.put()
        except:
            logging.error('Data: %s' % self.request.body)

        self.response.write('success')


class LastEventsHandler(webapp2.RequestHandler):
    def get(self):
        events = Event.query().order(-Event.date).fetch(20)
        self.response.write(print_events(events))


def print_events(events):
    result = []
    [result.append({'userId': event.userId,
                    'date': str(event.date),
                    'userData': json.loads(event.json)})
     for event in events]
    return json.dumps(result)

