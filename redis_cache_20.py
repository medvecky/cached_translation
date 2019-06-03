import os
import urllib
import redis
import re
import json


class RedisCache():
    def __init__(self):
        url = urllib.parse.urlparse(os.environ.get('REDISCLOUD_URL'))
        self.redis = redis.Redis(
            host=url.hostname,
            port=url.port,
            password=url.password,
            encoding="utf-8",
            decode_responses=True)

    def save_to_cache(self, translations, source, target):
        print("Saved to cache")
        key = source + ":" + target
        print(key)
        set_for_caching = {}
        for translation in translations:
            if source == "auto":
                set_for_caching[translation["input"]] = \
                    json.dumps({"translatedText": translation["translatedText"],
                                "detectedSourceLanguage": translation["detectedSourceLanguage"]})
            else:
                set_for_caching[translation["input"]] = translation["translatedText"]
        self.redis.hmset(key, set_for_caching)

    def get_from_cache(self, texts, source, target):
        print("From cache")
        key = source + ":" + target
        cache_response = self.redis.hmget(key, texts)
        results_from_cache = dict(zip(texts, cache_response))
        cached_translations = {}
        not_translated_texts = []
        for text in texts:
            if results_from_cache[text]:
                if source == "auto":
                    translation = json.loads(results_from_cache[text])
                    cached_translations[text] = (translation["translatedText"], translation["detectedSourceLanguage"])
                else:
                    translation = results_from_cache[text]
                    cached_translations[text] = (translation["translatedText"], source)
            else:
                not_translated_texts.append(text)

        return cached_translations, not_translated_texts

    def flushall(self):
        self.redis.flushall()
        self.redis.flushdb()
