# coding=utf-8
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

    def __getitem__(self, index):
        return getattr(self, index)
