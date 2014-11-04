# coding=utf-8
import services.files
import logging
import config
import operator
import urllib
import sys
import services.event

try:
    from google.appengine.api.files import records
    from google.appengine.datastore import entity_pb
    from google.appengine.api import datastore
    from google.appengine.api import urlfetch
    import cloudstorage as gcs
except ImportError:
    pass

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('utf8')


def send_to_restore(file_name, data):
    """
    Send row of data to restore service
    see config.py (RESTORE_URL)
    :param file_name: unique file name for backup
    :param data: entity from datastore
    """
    urlfetch.fetch(url=config.RESTORE_URL + '?name=' + file_name + '&source=db&packet',
                   payload=urllib.urlencode({"data": services.event.entity_to_string(data)}),
                   method=urlfetch.POST)


def export_backup_to_http_service(file_name):
    def progress(i):
        if i % 500 == 0:
            logging.info('Proceed %s rows' % i)

    files = services.files.group_files()
    files = files[file_name]

    id_index = 4

    # convert the file id to an int
    for v in files:
        v[id_index] = int(v[id_index])

    # sort by file id (index:3)
    files = sorted(files, key=operator.itemgetter(3))

    try:
        row = 0
        for f in files:
            filename = config.BACKUP_DIR + f[-1]
            raw = open(filename)
            reader = records.RecordsReader(raw)
            for record in reader:
                send_to_restore(file_name,
                                datastore.Entity.FromPb(entity_pb.EntityProto(contents=record)))
                row += 1
                progress(row)

    except Exception as e:
        logging.error("I'm dead. %s" % e.message)

    logging.info("I'm done.")


def export_backup_from_local(file_name):
    """ Transform LevelDB format to plain text """
    files = services.files.group_files()

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
                result = str(services.event.entity_to_string(entity))

                gcs_file.write(result + '\n')
            raw.close()
    finally:
        gcs_file.close()
