import webapp2
import os
import sys
import config
import urllib
import jinja2
import operator

from controllers.event import Event

from google.appengine.api.files import records
from google.appengine.datastore import entity_pb
from google.appengine.api import datastore
from google.appengine.api import urlfetch

import cloudstorage as gcs

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('utf8')

JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(['templates']))


class Export(webapp2.RequestHandler):
    path = config.BACKUP_DIR

    @staticmethod
    def group_files():
        """processes the path and returns all data files grouped by export name"""
        onlyfiles = [f for f in os.listdir(Export.path) if os.path.isfile(os.path.join(Export.path, f))]
        files = {}
        for f in onlyfiles:
            if f.find('.') == -1:
                split = f.split('-')
                if split[0] not in files:
                    files[split[0]] = []
                split.append(f)
                files[split[0]].append(split)

        return files

    def get_files(self):
        try:
            files = self.group_files()
        except OSError:
            self.response.write('Create "data" folder')
            return None

        return files


class ShowExportHandler(Export):
    def get(self):
        files = self.get_files()

        if not files:
            return

        template_values = {'files': files,
                           'path': Export.path}

        counter_template = JINJA_ENV.get_template('export.html')
        self.response.write(counter_template.render(template_values))


class ExportHandler(Export):
    def post(self, ename):
        files = self.get_files()

        if not files:
            return

        files = files[ename]

        # convert the file id to an int
        for v in files:
            v[3] = int(v[3])

        # sort by file id (index:3)
        files = sorted(files, key=operator.itemgetter(3))

        for f in files:
            filename = Export.path + f[6]
            raw = open(filename)
            reader = records.RecordsReader(raw)
            for record in reader:
                entity = datastore.Entity.FromPb(entity_pb.EntityProto(contents=record))
                result = '{"userId":"%s","date":"%s","ip": "%s","json":%s}\n' % (entity['userid'],
                                                                                 entity['date'],
                                                                                 entity['ip'],
                                                                                 entity['json'])

                form_data = urllib.urlencode({"data": result})

                urlfetch.fetch(url=config.RESTORE_URL,
                               payload=form_data,
                               method=urlfetch.POST)

        self.response.write("ok")


class BucketHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('List of buckets')

        stats = list_files()

        for stat in stats:
            self.response.write(gcs.open(stat.filename).read())
            self.response.write('\n')


def list_files():
    stats = gcs.listbucket(config.BUCKET_NAME)
    return stats


def write_file():
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    gcs_file = gcs.open(config.BUCKET_NAME + '/testfile3',
                        'w',
                        content_type='text/plain',
                        retry_params=write_retry_params)
    gcs_file.write('foo\n')
    gcs_file.write('f' * 1024 * 4 + '\n')
    gcs_file.close()
