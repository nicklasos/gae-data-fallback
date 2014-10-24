import webapp2
import config
from os import listdir
from os.path import isfile, join
from operator import itemgetter
import urllib

from google.appengine.api.files import records
from google.appengine.datastore import entity_pb
from google.appengine.api import datastore
from google.appengine.api import urlfetch


class Export(webapp2.RequestHandler):
    path = config.BACKUP_DIR

    @staticmethod
    def group_files():
        """processes the path and returns all data files grouped by export name"""
        onlyfiles = [f for f in listdir(Export.path) if isfile(join(Export.path, f))]
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
        self.response.write('<h1>Exports</h1>')

        files = self.get_files()

        if not files:
            return

        self.response.write('<h3>%s export(s) found in %s</h3>' % (len(files.keys()), Export.path))

        lst = '<ul>'
        for ename in files.keys():
            lst += '<a href="/export/%s">' % ename
            lst += '<li>%s (%s files)' % (ename, len(files[ename]))
            lst += '</a>'
        lst += '</ul>'

        self.response.write(lst)


class ExportHandler(Export):
    def get(self, ename):
        files = self.get_files()

        if not files:
            return

        files = files[ename]

        # convert the file id to an int
        for v in files:
            v[3] = int(v[3])

        # sort by file id (index:3)
        files = sorted(files, key=itemgetter(3))

        for f in files:
            filename = Export.path + f[6]
            raw = open(filename, 'r')
            reader = records.RecordsReader(raw)
            for record in reader:
                entity = datastore.Entity.FromPb(entity_pb.EntityProto(contents=record))

                result = '{"userId":"%s","date":"%s","ip": "%s","json":%s}\n' % (entity['userId'],
                                                                                 entity['date'],
                                                                                 entity['ip'],
                                                                                 entity['json'])

                form_data = urllib.urlencode({"data": result})

                urlfetch.fetch(url=config.RESTORE_URL,
                               payload=form_data,
                               method=urlfetch.POST)

        self.response.write("ok")
