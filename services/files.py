# coding=utf-8
import config
import os
import re

try:
    import cloudstorage as gcs
except:
    pass


def list_bucket():
    """ List files in bucket (see config.py) """
    return gcs.listbucket(config.BUCKET_NAME)


def group_files():
    """ Processes the path and returns all data files grouped by export name """
    skip_backup = re.compile('backup_txt_')

    def remove_bucket(file_name):
        return file_name.replace(config.BUCKET_NAME + '/', '')

    if config.GET_BACKUP_FROM == 'local':
        # For local files
        onlyfiles = [f for f in os.listdir(config.BACKUP_DIR) if os.path.isfile(os.path.join(config.BACKUP_DIR, f))]
    else:
        # For files from cloud storage
        onlyfiles = [remove_bucket(f.filename) for f in list_bucket() if skip_backup.search(f.filename) is None]

    files = {}
    for f in onlyfiles:
        if f.find('.') == -1:
            split = f.split('-')
            if split[0] not in files:
                files[split[0]] = []
            split.append(f)
            files[split[0]].append(split)

    return files
