### Python Skeleton for Google App Engine and Cloud Datastore

##СДЕЛАЙ СВОЙ БЭКАП ДОРОГО И ЧЕРЕЗ ЖОПУ!

#todo
Сделать бэкап через google cloud store, а не через жопу

#deploy
```
appcfg.py -A plarium-ed-1 --oauth2 update .
```

#install
```
pip install -r requirements.txt -t lib
```

#download backup
```
gsutil cp -R gs://datastore_backup-1 data
```
