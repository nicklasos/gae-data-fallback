# coding=utf-8
import webapp2
import logging
import services.event

try:
    from google.appengine.ext import ndb
except ImportError:
    pass


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
        services.event.save(user_id,
                            self.request.body,
                            self.request.remote_addr)
        self.response.write('success')


class EventsCountHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(services.event.count_events())


class LastEventsHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(services.event.get_last_events())


class UserEventsHandler(webapp2.RequestHandler):
    def get(self, user_id):
        self.response.write(services.event.get_last_user_events(user_id))
