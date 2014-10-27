import webapp2
import os
import sys
import config
import urllib
import jinja2
import operator
import re
import logging

try:
    from google.appengine.api.files import records
    from google.appengine.datastore import entity_pb
    from google.appengine.api import datastore
    from google.appengine.api import urlfetch
    from google.appengine.api import taskqueue
    import cloudstorage as gcs
except:
    pass

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('utf8')

JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(['templates']))


class ExportBase(webapp2.RequestHandler):
    path = config.BACKUP_DIR
    backup_file_name = re.compile('backup_txt_')

    def group_files(self):
        """ Processes the path and returns all data files grouped by export name """

        def remove_bucket(file_name):
            return file_name.replace(config.BUCKET_NAME + '/', '')

        if config.GET_BACKUP_FROM == 'local':
            # For local files
            onlyfiles = [f for f in os.listdir(ExportBase.path) if os.path.isfile(os.path.join(ExportBase.path, f))]
        else:
            # For files from cloud storage
            onlyfiles = [remove_bucket(f.filename) for f in self.list_bucket() if
                         ExportBase.backup_file_name.search(f.filename) is None]

        files = {}
        for f in onlyfiles:
            if f.find('.') == -1:
                split = f.split('-')
                if split[0] not in files:
                    files[split[0]] = []
                split.append(f)
                files[split[0]].append(split)

        return files

    def get_grouped_files(self):
        try:
            files = self.group_files()
        except OSError:
            self.response.write('Create "data" folder')
            return None

        return files

    @staticmethod
    def list_bucket():
        """ List files in bucket (see config.py) """
        return gcs.listbucket(config.BUCKET_NAME)

    @staticmethod
    def entity_to_string(entity):
        return '{"userId":"%s","date":"%s","ip": "%s","json":%s}\n' % (entity['userid'],
                                                                       entity['date'],
                                                                       entity['ip'],
                                                                       entity['json'])


class ExportHandler(ExportBase):
    def get(self):
        """ Show grouped files in bucket """
        files = self.get_grouped_files()

        if not files:
            return

        if config.GET_BACKUP_FROM == 'local':
            path = ExportBase.path
        else:
            path = 'cloud'

        template_values = {'files': files,
                           'path': path}

        counter_template = JINJA_ENV.get_template('export.html')
        self.response.write(counter_template.render(template_values))

    def post(self):
        try:
            file_name = self.request.get('file')

            if config.GET_BACKUP_FROM == 'local':
                # We can't write to local file system, because of gae limitations
                # And we don't wont store data in cloud storage locally
                # So we just send data row by row to some server
                # See config.py (RESTORE_URL)
                worker_url = '/export/worker/http'
            else:
                worker_url = '/export/worker'

            taskqueue.add(url=worker_url,
                          params={'file': file_name})

            self.response.write('New task was added successfully. Url: %s' % worker_url)
        except:
            self.response.write('Error')


class ExportHttpWorker(ExportBase):
    """
    Export backup files
    Send data to http service (config.py RESTORE_URL and GET_BACKUP_FROM == 'local')
    """

    def send_to_restore(self, file_name, data):
        """
        Send row of data to restore service
        see config.py (RESTORE_URL)
        :param file_name: unique file name for backup
        :param data: entity from datastore
        """
        urlfetch.fetch(url=config.RESTORE_URL + '?name=' + file_name,
                       payload=urllib.urlencode({"data": self.entity_to_string(data)}),
                       method=urlfetch.POST)

    def post(self):
        files = self.get_grouped_files()
        file_name = self.request.get('file')

        if not files:
            return

        files = files[file_name]

        id_index = 3

        # convert the file id to an int
        for v in files:
            v[id_index] = int(v[id_index])

        # sort by file id (index:3)
        files = sorted(files, key=operator.itemgetter(3))

        try:
            for f in files:
                filename = ExportBase.path + f[-1]
                raw = open(filename)
                reader = records.RecordsReader(raw)
                for record in reader:
                    self.send_to_restore(file_name,
                                         datastore.Entity.FromPb(entity_pb.EntityProto(contents=record)))


        except Exception as e:
            logging.error("I'm dead. %s" % e.message)

        logging.info("I'm done.")


class ExportWorker(ExportBase):
    def post(self):
        """ Transform LevelDB format to plain text """
        files = self.get_grouped_files()
        file_name = self.request.get('file')

        if not files:
            return

        files = files[file_name]

        id_index = 3

        # convert the file id to an int
        for v in files:
            v[id_index] = int(v[id_index])

        # sort by file id (index:3)
        files = sorted(files, key=operator.itemgetter(id_index))

        gcs_file = gcs.open('%s/backup_txt_%s' % (config.BUCKET_NAME, file_name),
                            'w',
                            content_type='text/plain',
                            retry_params=gcs.RetryParams(backoff_factor=1.1))
        try:
            for f in files:
                file_name = config.BUCKET_NAME + '/' + f[-1]
                raw = gcs.open(file_name)
                reader = records.RecordsReader(raw)
                for record in reader:
                    entity = datastore.Entity.FromPb(entity_pb.EntityProto(contents=record))
                    result = str(self.entity_to_string(entity))

                    gcs_file.write(result + '\n')
                raw.close()
        finally:
            gcs_file.close()

        self.response.write("ok")


class BucketHandler(ExportBase):
    """
    Just for testing
    REMOVE ME
    """

    def get(self):
        """ List files from bucket """
        self.response.write('List of buckets')

        # self.write_file()

        stats = self.list_bucket()

        for stat in stats:
            # gcs.delete(stat.filename)
            self.response.write('<br />')
            self.response.write(stat.filename)
            self.response.write(': ')
            self.response.write(gcs.open(stat.filename).read())

    @staticmethod
    def write_file():
        """ Write test file to cloud storage """
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        for i in xrange(3):
            gcs_file = gcs.open(
                config.BUCKET_NAME + '/datastore_backup_datastore_backup_2014_10_23_3_Events-18-output-' +
                str(i) +
                '-attempt-1', 'w',
                content_type='text/plain',
                retry_params=write_retry_params)
            gcs_file.write('{"userId":"13","date":"1111","ip": "2222","json":{"s":"a"}}\n')
            gcs_file.close()
