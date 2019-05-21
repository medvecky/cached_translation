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
        if not self.redis.get("id_key"):
            self.redis.set("id_key", 1)

    def check_cache(self, key):
        return self.redis.exists(key)

    def save_to_cache(self, translation, target, source=""):
        if source:
            if self.redis.hmget(source, translation["input"]):
                id_key = self.redis.hmget(source, translation["input"])
                self.redis.hmset(id_key, {target: translation["translatedText"]})
            else:
                self.redis.incr("id_key")
                id_key = self.redis.get("id_key")
                self.redis.hmset(source, {translation["input"]: id})
                self.redis.hmset(id_key, {target: translation["translatedText"]})
        else:
            if self.redis.hmget(translation["detectedSourceLanguage"], translation["input"]):
                id_key = self.redis.hmget(translation["detectedSourceLanguage"], translation["input"])
                self.redis.hmset(id_key, {target: translation["translatedText"]})
            else:
                self.redis.incr("id_key")
                id_key = self.redis.get("id_key")
                self.redis.hmset(translation["detectedSourceLanguage"], {translation["input"]: id})
                self.redis.hmset(id_key, {target: translation["translatedText"]})

    def get_from_cache(self, key):
        return self.redis.hgetall(key)
