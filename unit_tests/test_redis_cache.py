import redis

import pytest
import redis_cache_20
from unittest.mock import MagicMock


class TestRedisCache:

    @pytest.fixture()
    def redis_mock(self):
        redis_mock = MagicMock()
        return redis_mock

    @pytest.fixture()
    def redis_mock_hmset(self, redis_mock, monkeypatch):
        redis_mock.hmset = MagicMock()
        monkeypatch.setattr(redis.Redis, "hmset", redis_mock.hmset)

    def test_save_to_cache_with_source(self, redis_mock, redis_mock_hmset):
        cache = redis_cache_20.RedisCache()

        translation = {"translatedText": "text Translated",
                       "input": "text"}

        cache.save_to_cache([translation], "en", "ru")

        redis_mock.hmset.assert_called_with('en:ru', {'text': 'text Translated'})

    def test_save_to_cache_without_source(self, redis_mock, redis_mock_hmset):
        cache = redis_cache_20.RedisCache()

        translation = {"translatedText": "text Translated",
                       "detectedSourceLanguage": "en",
                       "input": "text"}

        cache.save_to_cache([translation], "", "ru")

        redis_mock.hmset.assert_called_with(
            'auto:ru',
            {'text': '{"translatedText": "text Translated", "detectedSourceLanguage": "en"}'})

    def test_get_from_cache_translated_with_source(self, redis_mock, monkeypatch):
        redis_mock.hmget = MagicMock(return_value=['text Translated'])
        monkeypatch.setattr(redis.Redis, "hmget", redis_mock.hmget)
        cache = redis_cache_20.RedisCache()
        cached_translations, not_translated_texts = cache.get_from_cache(["text"], "en", "ru")
        redis_mock.hmget.assert_called_with('en:ru', ['text'])
        assert cached_translations["text"][0] == "text Translated"
        assert cached_translations["text"][1] == "en"
        assert not_translated_texts == []

    def test_get_from_cache_translated_without_source(self, redis_mock, monkeypatch):
        redis_mock.hmget = MagicMock(
            return_value=['{"translatedText": "text Translated", "detectedSourceLanguage": "en"}'])
        monkeypatch.setattr(redis.Redis, "hmget", redis_mock.hmget)
        cache = redis_cache_20.RedisCache()
        cached_translations, not_translated_texts = cache.get_from_cache(["text"], "", "ru")
        redis_mock.hmget.assert_called_with('auto:ru', ['text'])
        assert cached_translations["text"][0] == "text Translated"
        assert cached_translations["text"][1] == "en"
        assert not_translated_texts == []

    def test_get_from_cache_not_translated(self, redis_mock, monkeypatch):
        redis_mock.hmget = MagicMock(return_value=[None])
        monkeypatch.setattr(redis.Redis, "hmget", redis_mock.hmget)
        cache = redis_cache_20.RedisCache()
        cached_translations, not_translated_texts = cache.get_from_cache(["text"], "", "ru")
        redis_mock.hmget.assert_called_with('auto:ru', ['text'])
        assert cached_translations == {}
        assert not_translated_texts == ['text']

    def test_get_from_cache_mixed(self, redis_mock, monkeypatch):
        redis_mock.hmget = MagicMock(
            return_value=[None,
                          '{"translatedText": "text Translated", "detectedSourceLanguage": "en"}'])
        monkeypatch.setattr(redis.Redis, "hmget", redis_mock.hmget)
        cache = redis_cache_20.RedisCache()
        cached_translations, not_translated_texts = cache.get_from_cache(["text", "text translated"], "", "ru")
        redis_mock.hmget.assert_called_with('auto:ru', ['text', 'text translated'])
        assert cached_translations["text translated"][0] == "text Translated"
        assert cached_translations["text translated"][1] == "en"
        assert not_translated_texts == ['text']
