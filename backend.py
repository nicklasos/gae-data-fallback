# coding=utf-8
import webapp2

from controllers.grabber import GrabberHandler

app = webapp2.WSGIApplication([(r'/cron/grabber', GrabberHandler)], debug=True)
