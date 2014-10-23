import webapp2
import logging
import time
import json
from restore import ShowExportHandler, ExportHandler

try:
    from google.appengine.ext import ndb
except ImportError:
    pass

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


class SaveEventsHandler(webapp2.RequestHandler):
    def get(self, user_id):
        logging.error('GET request')
        self.post(user_id)

    def post(self, user_id):
        self.response.headers['Content-Type'] = 'text/plain'
        try:
            event = Event(parent=events_key())
            event.eventId = "%s-%s" % (user_id, time.time())
            event.userid = user_id
            event.json = self.request.body
            event.ip = self.request.remote_addr
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
    [result.append({'userId': event.userid,
                    'date': str(event.date),
                    'userData': json.loads(event.json)})
     for event in events]
    return json.dumps(result)


app = webapp2.WSGIApplication([(r'/api/user/(\w+)', SaveEventsHandler),
                               (r'/get', LastEventsHandler),
                               (r'/export', ShowExportHandler),
                               (r'/export/(\w+)', ExportHandler)], debug=True)


def handle_404(request, response, exception):
    logging.exception(exception)
    response.write('Oops! I could swear this page was here!')
    response.set_status(404)


def handle_500(request, response, exception):
    logging.exception(exception)
    response.write('success')
    response.set_status(200)


app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500


