# coding=utf-8
import webapp2
import sys
import config
import services.files
import services.event
import services.restore

from services.template import render

try:
    from google.appengine.api import taskqueue
except ImportError:
    pass

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('utf8')


class ExportHandler(webapp2.RequestHandler):
    def get(self):
        """ Show grouped files in bucket """

        try:
            files = services.files.group_files()
        except OSError:
            self.response.write('Create "data" folder')
            return

        if config.GET_BACKUP_FROM == 'local':
            path = config.BACKUP_DIR
        else:
            path = 'cloud'

        self.response.write(render('export.html', {'files': files,
                                                   'path': path}))

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
        except Exception as e:
            self.response.write('Error: %s' % e.message)


class ExportHttpWorker(webapp2.RequestHandler):
    """
    Export backup files
    Send data to http service (config.py RESTORE_URL and GET_BACKUP_FROM == 'local')
    """

    def post(self):
        try:
            services.restore.export_backup_to_http_service(self.request.get('file'))
        except OSError:
            self.response.write('Create "data" folder')
            return
        except Exception as e:
            self.response.write('Error %s' % e.message)
            return

        self.response.write('ok')


class ExportWorker(webapp2.RequestHandler):
    def post(self):
        try:
            services.restore.export_backup_from_local(self.request.get('file'))
        except OSError:
            self.response.write('Create "data" folder')
            return
        except Exception as e:
            self.response.write('Error: %s' % e.message)

        self.response.write('ok')

