# Imports the Google Cloud client library
from google.cloud import translate
import os
import urllib
import redis

url = urllib.parse.urlparse(os.environ.get('REDISCLOUD_URL'))
r = redis.Redis(
    host=url.hostname,
    port=url.port,
    password=url.password,
    charset="utf-8",
    decode_responses=True)

r.set('HEllo world фывафыва фывафывавы ываыфвавфыа фывавыав ыфвавыа вф', 'Привет')

print(r.get('HEllo world фывафыва фывафывавы ываыфвавфыа фывавыав ыфвавыа вф'))
