import webapp2
import time
import json
import logging
import config

try:
    from google.appengine.ext import ndb
except ImportError:
    pass

DEFAULT_EVENTS_NAME = 'default_events'


def events_key(events_name=DEFAULT_EVENTS_NAME):
    return ndb.Key('Events', events_name)


def get_kind_name():
    return config.EVENTS_KIND_NAME


class Event(ndb.Model):
    eventId = ndb.StringProperty(indexed=False)
    userid = ndb.StringProperty(indexed=False)
    json = ndb.TextProperty(indexed=False)
    ip = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def _get_kind(cls):
        return get_kind_name()


class SaveEventsHandler(webapp2.RequestHandler):
    """ Save events to datastore """

    def get(self, user_id):
        """
        Mark get requests as error and run post method
        :param user_id: hash
        """
        logging.error('GET request')
        self.post(user_id)

    def post(self, user_id):
        """
        Save post body to json field in Event kind
        :param user_id: hash
        """
        self.response.headers['Content-Type'] = 'text/plain'
        try:
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


class UserEventsHandler(webapp2.RequestHandler):
    def get(self, user_id):
        user_events = Event.query(Event.userid == user_id).fetch(20)
        return print_events(user_events)


def print_events(events):
    result = []
    [result.append({'userId': event.userid,
                    'date': str(event.date),
                    'userData': json.loads(event.json)})
     for event in events]
    return json.dumps(result)

