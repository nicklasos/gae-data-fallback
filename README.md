##СДЕЛАЙ СВОЙ БЭКАП ДОРОГО
### Python Skeleton for Google App Engine and Cloud Datastore

#deploy
```
appcfg.py -A <YOUR_APP_ID> --oauth2 update .
```

#install
```
pip install -r requirements.txt -t lib
pip install GoogleAppEngineCloudStorageClient -t lib
```

#download backup
```
gsutil cp -R gs://datastore_backup-1 data
```

#links
* AppEngine, create backups here: https://appengine.google.com
* Developers console: https://console.developers.google.com
