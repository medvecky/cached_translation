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

trans = {"Field1":"Value1", "Field2": "Value2"}

r.delete("test")


r.rpush('test', "translation")
r.rpush('test', "language")
r.rpush('test', "input")


if r.exists('test'):
    print(r.lrange('test', 0, -1))
else:
    print("no entry")
