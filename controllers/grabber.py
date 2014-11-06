# coding=utf-8
import webapp2
import services.grabber as grab
import services.files as fi


class GrabberHandler(webapp2.RequestHandler):
    def get(self):
        grab.grab()

        # self.response.write(fi.list_content())

        self.response.write('ok')
