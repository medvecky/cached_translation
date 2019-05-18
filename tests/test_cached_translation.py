import grpc

import cached_translation_pb2
import cached_translation_pb2_grpc

from redis_cache import RedisCache


class TestCachedTranslation:

    def test_from_cloud_without_source(self):
        cache = RedisCache()
        key = "Hello world:ru"
        if cache.check_cache(key):
            cache.redis.delete(key)

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

            response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
                texts=["Hello world"],
                targetLanguage="ru",
                sourceLanguage=""))

        print("translatedText: " + str(response.translations[0].translatedText))
        print("detectedSourceLanguage: " + str(response.translations[0].detectedSourceLanguage))
        print("input: " + response.translations[0].input)
        assert response.translations[0].translatedText == "Привет, мир"
        assert response.translations[0].detectedSourceLanguage == "en"
        assert response.translations[0].input == "Hello world"
        assert cache.check_cache(key)

    def test_from_cloud_with_source(self):
        cache = RedisCache()
        key = "Hello world:ru:en"
        if cache.check_cache(key):
            cache.redis.delete(key)

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

            response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
                texts=["Hello world"],
                targetLanguage="ru",
                sourceLanguage="en"))

        print("translatedText: " + response.translations[0].translatedText)
        print("detectedSourceLanguage: " + response.translations[0].detectedSourceLanguage)
        print("input: " + response.translations[0].input)
        assert response.translations[0].translatedText == "Привет, мир"
        assert response.translations[0].detectedSourceLanguage == ""
        assert response.translations[0].input == "Hello world"
        assert cache.check_cache(key)

    def test_from_cache_without_source(self):
        cache = RedisCache()
        key = "Hello world:ru"

        translation = {"translatedText": "Привет, мир [cached]",
                       "detectedSourceLanguage": "en[cached]",
                       "input": "Hello world[cached]"}

        if cache.check_cache(key):
            cache.redis.delete(key)

        cache.save_to_cache(key, translation)

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

            response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
                texts=["Hello world"],
                targetLanguage="ru",
                sourceLanguage=""))

        print("translatedText: " + response.translations[0].translatedText)
        print("detectedSourceLanguage: " + response.translations[0].detectedSourceLanguage)
        print("input: " + response.translations[0].input)
        assert response.translations[0].translatedText == "Привет, мир [cached]"
        assert response.translations[0].detectedSourceLanguage == "en[cached]"
        assert response.translations[0].input == "Hello world[cached]"
        assert cache.check_cache(key)

    def test_from_cache_with_source(self):
        cache = RedisCache()
        key = "Hello world:ru:en"

        translation = {"translatedText": "Привет, мир [cached]",
                       "input": "Hello world[cached]"}

        if cache.check_cache(key):
            cache.redis.delete(key)

        cache.save_to_cache(key, translation)

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

            response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
                texts=["Hello world"],
                targetLanguage="ru",
                sourceLanguage="en"))

        print("translatedText: " + response.translations[0].translatedText)
        print("detectedSourceLanguage: " + response.translations[0].detectedSourceLanguage)
        print("input: " + response.translations[0].input)
        assert response.translations[0].translatedText == "Привет, мир [cached]"
        assert response.translations[0].detectedSourceLanguage == ""
        assert response.translations[0].input == "Hello world[cached]"
        assert cache.check_cache(key)

    def test_empty_text(self):
        cache = RedisCache()
        key = ":ru:en"

        if cache.check_cache(key):
            cache.redis.delete(key)

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

            response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
                texts="Hello world",
                targetLanguage="",
                sourceLanguage="en"))

        print("translatedText: " + response.translations[0].translatedText)
        print("detectedSourceLanguage: " + response.translations[0].detectedSourceLanguage)
        print("input: " + response.translations[0].input)
        assert response.translations[0].translatedText == ""
        assert response.translations[0].detectedSourceLanguage == ""
        assert response.translations[0].input == "BAD ARGUMENT"
        assert not cache.check_cache(key)

    def test_empty_target(self):
        cache = RedisCache()
        key = "Hello world::en"

        if cache.check_cache(key):
            cache.redis.delete(key)

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

            response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
                texts=["Hello world"],
                targetLanguage="",
                sourceLanguage="en"))

        print("translatedText: " + response.translations[0].translatedText)
        print("detectedSourceLanguage: " + response.translations[0].detectedSourceLanguage)
        print("input: " + response.translations[0].input)
        assert response.translations[0].translatedText == ""
        assert response.translations[0].detectedSourceLanguage == ""
        assert response.translations[0].input == "BAD ARGUMENT"
        assert not cache.check_cache(key)
