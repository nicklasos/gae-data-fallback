##СДЕЛАЙ СВОЙ БЭКАП ДОРОГО
### Python Skeleton for Google App Engine and Cloud Datastore

#todo
Сделать бэкап через google cloud store, а не через жопу

#deploy
```
appcfg.py -A <APP_ID> --oauth2 update .
```

#install
```
pip install -r requirements.txt -t lib
pip install GoogleAppEngineCloudStorageClient -t lib
```

#download backup
```
gsutil cp -R gs://<BUCKET_NAME> data
```
