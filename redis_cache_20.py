import os
import urllib
import redis
import re


class RedisCache():
    def __init__(self):
        url = urllib.parse.urlparse(os.environ.get('REDISCLOUD_URL'))
        self.redis = redis.Redis(
            host=url.hostname,
            port=url.port,
            password=url.password,
            encoding="utf-8",
            decode_responses=True)

    def check_cache(self, text, source, target):
        if source:
            key = source + ":" + target
            return self.check_source_key(text, key, target)
        else:
            for key in self.redis.scan_iter("*"):
                if self.check_source_key(text, key, target):
                    return True
            return False

    def save_to_cache(self, translation, source, target):
        print("Saved to cache")
        key = source + ":" + target
        print(key)
        self.redis.hset(key,translation["input"], translation["translatedText"])

    def get_from_cache(self, text, source, target):
        print("From cache")
        if not source:
            for key in self.redis.scan_iter("*"):
                if self.check_source_key(text, key, target):
                    match_obj = re.match( r'(.*):', key)
                    source = match_obj.group(1)
        key = source + ":" + target
        return self.redis.hget(key, text), source

    def check_source_key(self, text, key, target):
        if self.redis.hexists(key, text):
            return True
        return False

    def flushall(self):
        self.redis.flushall()
        self.redis.flushdb()


