import os
import urllib
import redis


class RedisCache():
    def __init__(self):
        url = urllib.parse.urlparse(os.environ.get('REDISCLOUD_URL'))
        self.redis = redis.Redis(
            host=url.hostname,
            port=url.port,
            password=url.password,
            encoding="utf-8",
            decode_responses=True)

    def check_cache(self, key):
        return self.redis.exists(key)

    def save_to_cache(self, key, translation):
        self.redis.hmset(key, translation)

    def get_from_cache(self, key):
        return self.redis.hgetall(key)
