import webapp2
import logging
import time

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


class SaveEvents(webapp2.RequestHandler):
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
            # event.ip = request.remote_addr
            event.put()
        except:
            logging.error('Data: %s' % self.request.body)

        self.response.write('success')


app = webapp2.WSGIApplication([(r'/api/user/(\w+)', SaveEvents),
                               ], debug=True)


def handle_404(request, response, exception):
    logging.exception(exception)
    response.write('Oops! I could swear this page was here!')
    response.set_status(404)


def handle_500(request, response, exception):
    logging.exception(exception)
    response.write('error')
    response.set_status(500)


app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

