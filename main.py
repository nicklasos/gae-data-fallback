# coding=utf-8
import webapp2
import logging

from controllers.restore import ExportHandler, ExportHttpWorker, ExportWorker
from controllers.event import SaveEventsHandler, LastEventsHandler, UserEventsHandler, EventsCountHandler


class BlankPageHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('')


app = webapp2.WSGIApplication([(r'/', BlankPageHandler),
                               (r'/api/user/(\w+)', SaveEventsHandler),
                               (r'/count', EventsCountHandler),
                               (r'/get', LastEventsHandler),
                               (r'/get/(\w+)', UserEventsHandler),
                               (r'/export/worker/http', ExportHttpWorker),
                               (r'/export/worker', ExportWorker),
                               (r'/export', ExportHandler)], debug=True)


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


