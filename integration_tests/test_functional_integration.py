import grpc

import cached_translation_pb2
import cached_translation_pb2_grpc
import pytest

from redis_cache import RedisCache


class TestCachedTranslation:

    @pytest.fixture()
    def cache(self):
        cache = RedisCache()
        cache.flushall()
        return cache

    def test_from_cloud_without_source(self, cache):
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

    def test_from_cloud_with_source(self, cache):
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

    def test_from_cache_without_source(self, cache):
        translation = {"translatedText": "Привет, мир [cached]",
                       "detectedSourceLanguage": "en",
                       "input": "Hello world"}

        cache.save_to_cache([translation], "", "ru")

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
        assert response.translations[0].detectedSourceLanguage == "en"
        assert response.translations[0].input == "Hello world"

    def test_page_without_source(self, cache):
        translation = {"translatedText": "Привет, мир [cached]",
                       "detectedSourceLanguage": "en",
                       "input": "Hello world"}

        cache.save_to_cache([translation], "", "ru")

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

            response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
                texts=["Hello world", "Hello world guys"],
                targetLanguage="ru",
                sourceLanguage=""))

        print("translatedText: " + response.translations[0].translatedText)
        print("detectedSourceLanguage: " + response.translations[0].detectedSourceLanguage)
        print("input: " + response.translations[0].input)
        assert response.translations[0].translatedText == "Привет, мир [cached]"
        assert response.translations[0].detectedSourceLanguage == "en"
        assert response.translations[0].input == "Hello world"
        assert response.translations[1].translatedText == "Привет, мир, ребята"
        assert response.translations[1].detectedSourceLanguage == "en"
        assert response.translations[1].input == "Hello world guys"

    def test_page_with_source(self, cache):
        translation = {"translatedText": "Привет, мир [cached]",
                       "input": "Hello world"}

        cache.save_to_cache([translation], "en", "ru")

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

            response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
                texts=["Hello world", "Hello world guys"],
                targetLanguage="ru",
                sourceLanguage="en"))

        print("translatedText: " + response.translations[0].translatedText)
        print("detectedSourceLanguage: " + response.translations[0].detectedSourceLanguage)
        print("input: " + response.translations[0].input)
        assert response.translations[0].translatedText == "Привет, мир [cached]"
        assert response.translations[0].detectedSourceLanguage == "en"
        assert response.translations[0].input == "Hello world"
        assert response.translations[1].translatedText == "Привет, мир, ребята"
        assert response.translations[1].detectedSourceLanguage == ""
        assert response.translations[1].input == "Hello world guys"

    def test_from_cache_with_source(self, cache):
        translation = {"translatedText": "Привет, мир [cached]",
                       "input": "Hello world"}

        cache.save_to_cache([translation], "en", "ru")

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
        assert response.translations[0].detectedSourceLanguage == "en"
        assert response.translations[0].input == "Hello world"

    def test_empty_text(self, cache):
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

            response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
                texts=[""],
                targetLanguage="ru",
                sourceLanguage=""))

        print("translatedText: " + str(response.translations[0].translatedText))
        print("detectedSourceLanguage: " + str(response.translations[0].detectedSourceLanguage))
        print("input: " + response.translations[0].input)
        assert response.translations[0].translatedText == ""
        assert response.translations[0].detectedSourceLanguage == "en"
        assert response.translations[0].input == ""

    def test_empty_translation_request(self, cache):
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

            response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
                texts=[],
                targetLanguage="ru",
                sourceLanguage=""))

        print("translatedText: " + str(response.translations[0].translatedText))
        print("detectedSourceLanguage: " + str(response.translations[0].detectedSourceLanguage))
        print("input: " + response.translations[0].input)
        assert response.translations[0].translatedText == ""
        assert response.translations[0].detectedSourceLanguage == ""
        assert response.translations[0].input == "BAD ARGUMENT"

    def test_empty_target(self, cache):
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

            response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
                texts=["Hello world"],
                targetLanguage="",
                sourceLanguage=""))

        print("translatedText: " + str(response.translations[0].translatedText))
        print("detectedSourceLanguage: " + str(response.translations[0].detectedSourceLanguage))
        print("input: " + response.translations[0].input)
        assert response.translations[0].translatedText == ""
        assert response.translations[0].detectedSourceLanguage == ""
        assert response.translations[0].input == "BAD ARGUMENT"
