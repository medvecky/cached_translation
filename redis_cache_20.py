import os
import urllib
import redis
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
        if source:
            key = source + ":" + target
        else:
            key = "auto:" + target
        print(key)
        set_for_caching = {}
        for translation in translations:
            if not source:
                set_for_caching[translation["input"]] = \
                    json.dumps({"translatedText": translation["translatedText"],
                                "detectedSourceLanguage": translation["detectedSourceLanguage"]})
            else:
                set_for_caching[translation["input"]] = translation["translatedText"]
        print("Set for caching")
        print(set_for_caching)
        self.redis.hmset(key, set_for_caching)

    def get_from_cache(self, texts, source, target):
        print("From cache")
        if source:
            key = source + ":" + target
        else:
            key = "auto:" + target
        cache_response = self.redis.hmget(key, texts)
        print("Cache response")
        print(cache_response)
        results_from_cache = dict(zip(texts, cache_response))
        print("Results from cache")
        print(results_from_cache)
        cached_translations = {}
        not_translated_texts = []
        for text in texts:
            if results_from_cache[text]:
                if not source:
                    translation = json.loads(results_from_cache[text])
                    cached_translations[text] = (translation["translatedText"], translation["detectedSourceLanguage"])
                else:
                    translation = results_from_cache[text]
                    cached_translations[text] = (translation, source)
            else:
                not_translated_texts.append(text)

        return cached_translations, not_translated_texts

    def flushall(self):
        self.redis.flushall()
        self.redis.flushdb()
