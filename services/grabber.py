# coding=utf-8
import logging
import services.event
import config
import sys
from datetime import datetime
from models.event import Event
from services.files import get_file_handler

try:
    import cloudstorage as gcs
    from google.appengine.ext import ndb
except ImportError:
    pass

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('utf8')


def create_file_name():
    now = datetime.now()
    return now.strftime("%y/%m/%d/") + now.strftime('%H_%M_%S')


def grab():
    gcs_file = get_file_handler(create_file_name())
    count_rows = services.event.count_events()
    i = 0
    try:
        while i < count_rows:
            keys = []

            # if entities in db are less than needed per query
            # and sori fo mai inglish
            if count_rows - i < config.ENTITIES_PER_QUERY:
                rows = count_rows - i
            else:
                rows = config.ENTITIES_PER_QUERY

            for e in Event.query().order(Event.date).fetch(rows):
                i += 1
                gcs_file.write(str(services.event.entity_to_string(e)))
                keys.append(e.key)

            ndb.delete_multi(keys)
    finally:
        gcs_file.close()
