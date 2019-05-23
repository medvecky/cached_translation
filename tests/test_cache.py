# from redis_cache import RedisCache
from ..redis_cache_20 import RedisCache


class TestCache:
    def test_save_get_value(self):
        cache = RedisCache()
        cache.flushall()
        assert not cache.check_cache("text", "en", "ru")

        translation = {"translatedText": "text Translated",
                       "input": "text"}

        cache.save_to_cache(translation, "en", "ru")

        assert cache.check_cache("text", "en", "ru")

        test_value = cache.get_from_cache("text", "en", "ru")

        print(test_value)

        assert test_value[0] == "text Translated"
        assert test_value[1] == "en"

    def test_save_get_value_without_source(self):
        cache = RedisCache()
        cache.flushall()
        assert not cache.check_cache("text", "", "ru")

        translation = {"translatedText": "text Translated",
                       "detectedSourceLanguage": "en",
                       "input": "text"}

        cache.save_to_cache(translation, "en", "ru")

        assert cache.check_cache("text", "", "ru")

        test_value = cache.get_from_cache("text", "", "ru")

        print(test_value)

        assert test_value[0] == "text Translated"
        assert test_value[1] == "en"

    def test_save_get_value_without_source_second_layer(self):
        cache = RedisCache()
        cache.flushall()
        assert not cache.check_cache("text", "", "ru")
        assert not cache.check_cache("text", "", "uk")

        translation = {"translatedText": "text Translated",
                       "detectedSourceLanguage": "en",
                       "input": "text"}
        translation_uk = {"translatedText": "text Translated uk",
                          "detectedSourceLanguage": "en",
                          "input": "text"}

        cache.save_to_cache(translation, "en", "ru")
        cache.save_to_cache(translation_uk, "en", "uk")

        assert cache.check_cache("text", "", "ru")

        test_value = cache.get_from_cache("text", "", "ru")

        print(test_value)

        assert test_value[0] == "text Translated"
        assert test_value[1] == "en"

        test_value = cache.get_from_cache("text", "", "uk")

        print(test_value)

        assert test_value[0] == "text Translated uk"
        assert test_value[1] == "en"

    def test_save_get_value_second_layer(self):
        cache = RedisCache()
        cache.flushall()


        assert not cache.check_cache("text", "en", "ru")
        assert not cache.check_cache("text", "en", "uk")

        translation = {"translatedText": "text Translated",
                       "input": "text"}

        translation_uk = {"translatedText": "text Translated uk",
                          "input": "text"}

        cache.save_to_cache(translation, "en", "ru")
        cache.save_to_cache(translation_uk, "en", "uk")

        assert cache.check_cache("text", "en", "ru")
        assert cache.check_cache("text", "en", "uk")

        test_value = cache.get_from_cache("text", "en", "ru")

        print(test_value)

        assert test_value[0] == "text Translated"
        assert test_value[1] == "en"

        test_value = cache.get_from_cache("text", "en", "uk")

        print(test_value)

        assert test_value[0] == "text Translated uk"
        assert test_value[1] == "en"
