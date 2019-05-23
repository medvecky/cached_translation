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

    def check_cache(self, text, source, target):
        if source:
            source_key = "source_lang:" + source
            return self.check_source_key(text, source_key, target)
        else:
            for source_key in self.redis.scan_iter("source_lang:*"):
                if self.check_source_key(text, source_key, target):
                    return True
            return False

    def save_to_cache(self, translation, source, target):
        source_key = "source_lang:" + source
        print(source_key)

        if self.redis.hexists(source_key, translation["input"]):
            id_key = str(self.redis.hget(source_key, translation["input"]))
            self.redis.hset(id_key, target, translation["translatedText"])
            print("id_key: {}, target: {}".format(id_key, target))
        else:
            id_key = str(self.redis.get("id_key"))
            self.redis.hset(source_key, translation["input"],id_key)
            self.redis.hset(id_key, target, translation["translatedText"])
            print("id_key: {}, target: {}".format(id_key, target))
            self.redis.incr("id_key")

    def get_from_cache(self, text, source, target):
        if not source:
            for source_key in self.redis.scan_iter("source_lang:*"):
                if self.check_source_key(text, source_key, target):
                    source = source_key[12:]
                    break

        source_key = "source_lang:" + source
        id_key = str(self.redis.hget(source_key, text))
        return self.redis.hget(id_key, target), source

    def check_source_key(self, text, source_key, target):

        if self.redis.hexists(source_key, text):
            id_key = self.redis.hget(source_key, text)
            if self.redis.hexists(id_key, target):
                return True
            else:
                return False
        else:
            return False

    def flushall(self):
        self.redis.flushall()
        self.redis.flushdb()


